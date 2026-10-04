// SPDX-License-Identifier: Apache-2.0
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { CalendarWorkflow } from "./workflow";
import { WorkflowError } from "./errors";
import type { Permission } from "./capability";
import type { DemoFault } from "./model";
import { CalendarWorkflowCapability } from "../integrations/calendarCapability";
import { DemoCalendarAdapter, resetDemoCalendar } from "../integrations/demoCalendar";
import { changeDemoWeather, demoWeatherSnapshot } from "../integrations/demoWeather";

const now = new Date(2026, 8, 30, 8).getTime();
const store = new Map<string, string>();
beforeEach(() => {
  store.clear();
  vi.useFakeTimers();
  vi.setSystemTime(now);
  vi.stubGlobal("window", { localStorage: {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => { store.set(key, value); },
  } });
  resetDemoCalendar(new Date(now));
});
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });

function fixture(fault: DemoFault = "none", permission: Exclude<Permission, "READ"> = "WRITE_REVERSIBLE") {
  const adapter = new DemoCalendarAdapter(fault);
  const write = vi.spyOn(adapter, "updateEvent");
  let weather = demoWeatherSnapshot(new Date(now));
  const capability = new CalendarWorkflowCapability(() => adapter, async () => weather, permission);
  const workflow = new CalendarWorkflow(capability);
  return { adapter, write, capability, workflow, changeWeather: () => { weather = changeDemoWeather(weather); },
    blockDrySlots: () => { weather = { ...weather, hours: weather.hours.map((hour) => ({ ...hour, weatherCode: 65 })) }; } };
}

describe("competition calendar workflow", () => {
  it("reports a detected conflict even when there is no dry alternative and makes no write", async () => {
    const f = fixture();
    f.blockDrySlots();
    await f.workflow.detect();
    expect(f.workflow.snapshot()).toMatchObject({ status: "UNDERSTOOD", eventId: "demo-outdoor-tennis",
      impact: { eventId: "demo-outdoor-tennis", severity: "heavy rain" } });
    expect(f.workflow.snapshot().message).toContain("冲突");
    expect(f.workflow.snapshot().proposal).toBeUndefined();
    expect(f.write).not.toHaveBeenCalled();
  });

  it("happy-path executes only after consent and completes only after an independent state read", async () => {
    const f = fixture();
    const reads = vi.spyOn(f.capability, "readState");
    await f.workflow.detect();
    expect(f.workflow.snapshot().status).toBe("AWAITING_APPROVAL");
    expect(f.write).not.toHaveBeenCalled();
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot()).toMatchObject({ status: "COMPLETED", action: { result: "success" }, verification: { verified: true } });
    expect(f.workflow.snapshot().history).toEqual(["DETECTED", "UNDERSTOOD", "PROPOSED", "AWAITING_APPROVAL", "EXECUTING", "VERIFYING", "COMPLETED"]);
    expect(f.write).toHaveBeenCalledTimes(1);
    expect(reads).toHaveBeenCalledTimes(3);
    expect(reads.mock.invocationCallOrder[2]).toBeGreaterThan(f.write.mock.invocationCallOrder[0]);
  });

  it("approval-rejected never invokes a write, including a later approval attempt", async () => {
    const f = fixture();
    await f.workflow.detect();
    f.workflow.decline();
    expect(f.workflow.snapshot()).toMatchObject({ status: "DECLINED", error: { code: "USER_DECLINED", retryable: false } });
    await expect(f.workflow.approve({ confirmed: true, explicit: true })).rejects.toMatchObject({ code: "PERMISSION_DENIED" });
    expect(f.write).not.toHaveBeenCalled();
  });

  it("execution-failed preserves the event and exposes failure rather than success", async () => {
    const f = fixture("write-failed");
    const [before] = await f.adapter.listEvents();
    await f.workflow.detect();
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot()).toMatchObject({ status: "FAILED", error: { code: "EXECUTION_FAILED", retryable: true } });
    expect(await f.adapter.getEvent(before.id)).toEqual(before);
    await f.workflow.recheck();
    expect(f.write).toHaveBeenCalledTimes(1);
    expect(f.workflow.snapshot().status).toBe("FAILED");
  });

  it("state-stale weather is rejected by execution preflight without a write", async () => {
    const f = fixture();
    await f.workflow.detect();
    f.changeWeather();
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot()).toMatchObject({ status: "STALE", error: { code: "STATE_STALE", retryable: false } });
    expect(f.write).not.toHaveBeenCalled();
  });

  it("refresh transitions changed facts to STALE and a read failure to FAILED", async () => {
    const f = fixture();
    await f.workflow.detect();
    f.changeWeather();
    await f.workflow.refresh();
    expect(f.workflow.snapshot().status).toBe("STALE");
    expect(f.write).not.toHaveBeenCalled();
    const broken = fixture();
    await broken.workflow.detect();
    vi.spyOn(broken.capability, "readState").mockRejectedValueOnce(new TypeError("offline"));
    await broken.workflow.refresh();
    expect(broken.workflow.snapshot()).toMatchObject({ status: "FAILED", error: { code: "DEPENDENCY_UNAVAILABLE" } });
  });

  it("verification-failed does not trust the adapter's successful acknowledgement", async () => {
    const f = fixture("verify-mismatch");
    await f.workflow.detect();
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot()).toMatchObject({ status: "FAILED", verification: { verified: false }, error: { code: "VERIFICATION_FAILED" } });
    expect(f.workflow.snapshot().action?.result).toBe("failed");
  });

  it("permission denial is distinct from the user declining and performs no mutation", async () => {
    const f = fixture("denied");
    await f.workflow.detect();
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot()).toMatchObject({ status: "FAILED", error: { code: "PERMISSION_DENIED", retryable: false } });
  });

  it("cancelled proposals cannot execute", async () => {
    const f = fixture();
    await f.workflow.detect();
    f.workflow.cancel();
    expect(f.workflow.snapshot().status).toBe("CANCELLED");
    await expect(f.workflow.approve({ confirmed: true, explicit: true })).rejects.toMatchObject({ code: "PERMISSION_DENIED" });
    expect(f.write).not.toHaveBeenCalled();
  });

  it("an expired proposal is stale even if external facts remain identical", async () => {
    const f = fixture();
    await f.workflow.detect();
    vi.advanceTimersByTime(10 * 60_000 + 1);
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot().status).toBe("STALE");
    expect(f.write).not.toHaveBeenCalled();
  });

  it("duplicate approvals cannot issue duplicate writes", async () => {
    const f = fixture();
    await f.workflow.detect();
    const first = f.workflow.approve({ confirmed: true, explicit: true });
    await expect(f.workflow.approve({ confirmed: true, explicit: true })).rejects.toMatchObject({ code: "PERMISSION_DENIED" });
    await first;
    expect(f.write).toHaveBeenCalledTimes(1);
  });

  it("write accepted but read-back unavailable stays PARTIAL; reconciliation reads without rewriting", async () => {
    const f = fixture();
    await f.workflow.detect();
    const read = f.capability.readState.bind(f.capability);
    vi.spyOn(f.capability, "readState").mockImplementationOnce(read)
      .mockRejectedValueOnce(new WorkflowError("DEPENDENCY_UNAVAILABLE", "read-back offline", true));
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot()).toMatchObject({ status: "PARTIAL", error: { code: "DEPENDENCY_UNAVAILABLE" } });
    await f.workflow.recheck();
    expect(f.workflow.snapshot().status).toBe("COMPLETED");
    expect(f.write).toHaveBeenCalledTimes(1);
  });

  it("partial time changes fail verification and remain PARTIAL", async () => {
    const f = fixture();
    const writer = new DemoCalendarAdapter();
    const update = writer.updateEvent.bind(writer);
    f.write.mockImplementation(async (id, state) => {
      const current = await f.adapter.getEvent(id);
      return update(id, { start: state.start, end: current!.end });
    });
    await f.workflow.detect();
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot()).toMatchObject({ status: "PARTIAL", verification: { verified: false }, error: { code: "VERIFICATION_FAILED" } });
  });

  it("snapshot edits do not change the actual proposed write", async () => {
    const f = fixture();
    await f.workflow.detect();
    const snapshot = f.workflow.snapshot();
    const expected = snapshot.proposal!.proposedState.start;
    snapshot.proposal!.proposedState.start = "2040-01-01T00:00:00Z";
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.write.mock.calls[0][1].start).toBe(expected);
  });

  it("initial dependency failure is a typed FAILED outcome", async () => {
    const f = fixture();
    vi.spyOn(f.adapter, "listEvents").mockRejectedValueOnce(new TypeError("offline"));
    await f.workflow.detect();
    expect(f.workflow.snapshot()).toMatchObject({ status: "FAILED", error: { code: "DEPENDENCY_UNAVAILABLE", retryable: true } });
    expect(f.write).not.toHaveBeenCalled();
  });
});

describe("capability permission boundary", () => {
  it.each(["WRITE_REVERSIBLE", "WRITE_SENSITIVE"] as const)("%s cannot execute without genuine approval", async (permission) => {
    const f = fixture("none", permission);
    const prepared = f.capability.prepareAction(await f.capability.readState())!;
    await expect(f.capability.executeAction(prepared)).rejects.toMatchObject({ code: "PERMISSION_DENIED" });
    await expect(f.capability.executeAction(prepared, { id: "forged" })).rejects.toMatchObject({ code: "PERMISSION_DENIED" });
    expect(f.write).not.toHaveBeenCalled();
  });

  it("sensitive writes require explicit consent, and grants are consumed once", async () => {
    const f = fixture("none", "WRITE_SENSITIVE");
    const prepared = f.capability.prepareAction(await f.capability.readState())!;
    expect(() => f.capability.approveAction(prepared, { confirmed: true, explicit: false })).toThrow(WorkflowError);
    const approval = f.capability.approveAction(prepared, { confirmed: true, explicit: true });
    await f.capability.executeAction(prepared, approval);
    await expect(f.capability.executeAction(prepared, approval)).rejects.toMatchObject({ code: "PERMISSION_DENIED" });
    expect(f.write).toHaveBeenCalledTimes(1);
  });

  it("a grant from another capability is not valid in this context", async () => {
    const first = fixture();
    const second = fixture();
    const a = first.capability.prepareAction(await first.capability.readState())!;
    const b = second.capability.prepareAction(await second.capability.readState())!;
    const grant = first.capability.approveAction(a, { confirmed: true, explicit: true });
    await expect(second.capability.executeAction(b, grant)).rejects.toMatchObject({ code: "PERMISSION_DENIED" });
    expect(second.write).not.toHaveBeenCalled();
  });

  it("prepared actions derive their version from facts rather than a forged version label", async () => {
    const f = fixture();
    const before = await f.capability.readState();
    before.weather.location = "forged location";
    const prepared = f.capability.prepareAction(before)!;
    const grant = f.capability.approveAction(prepared, { confirmed: true, explicit: true });
    await expect(f.capability.executeAction(prepared, grant)).rejects.toMatchObject({ code: "STATE_STALE" });
    expect(f.write).not.toHaveBeenCalled();
  });

  it("a freshest target GET detects changes missed by an older event list", async () => {
    const f = fixture();
    const [original] = await f.adapter.listEvents();
    await f.workflow.detect();
    vi.spyOn(f.adapter, "getEvent").mockResolvedValue({ ...original, title: "Changed outdoors" });
    await f.workflow.approve({ confirmed: true, explicit: true });
    expect(f.workflow.snapshot().status).toBe("STALE");
    expect(f.write).not.toHaveBeenCalled();
  });

  it("verification checks preserved identity and metadata as well as timestamps", async () => {
    const f = fixture();
    const before = await f.capability.readState();
    const prepared = f.capability.prepareAction(before)!;
    const after = structuredClone(before);
    after.events[0] = { ...after.events[0], ...prepared.proposal.proposedState, title: "Unexpected title" };
    expect(f.capability.verifyResult(before, after, prepared.proposal).verified).toBe(false);
  });
});

import { describe, expect, it } from "vitest";
import { canTransition, transition } from "./stateMachine";

describe("proposal lifecycle", () => {
  it("allows the complete consent, execution, and verification path", () => {
    const path = ["DETECTED", "UNDERSTOOD", "PROPOSED", "AWAITING_APPROVAL", "EXECUTING", "VERIFYING", "COMPLETED"] as const;
    for (let index = 0; index < path.length - 1; index += 1) {
      expect(transition(path[index], path[index + 1])).toBe(path[index + 1]);
    }
  });

  it("allows denial, failure retry, and proposal expiration", () => {
    expect(canTransition("AWAITING_APPROVAL", "DECLINED")).toBe(true);
    expect(canTransition("VERIFYING", "FAILED")).toBe(true);
    expect(canTransition("FAILED", "EXECUTING")).toBe(false);
    expect(canTransition("AWAITING_APPROVAL", "STALE")).toBe(true);
    expect(canTransition("STALE", "UNDERSTOOD")).toBe(false);
  });

  it("rejects execution without proposal consent and rejects success before verification", () => {
    expect(canTransition("PROPOSED", "EXECUTING")).toBe(false);
    expect(canTransition("EXECUTING", "COMPLETED")).toBe(false);
    expect(() => transition("PROPOSED", "EXECUTING")).toThrow("Invalid Ripple transition");
  });
});

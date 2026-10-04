// SPDX-License-Identifier: Apache-2.0
import { createProposal, makeSourceBundle, proposalExpired, verifyEvent } from "../domain/engine";
import { WorkflowError, workflowError } from "../domain/errors";
import type { ApprovalGrant, CalendarAdapter, CalendarCapability, Consent, Permission, PreparedAction } from "../domain/capability";
import type { ObservedSources, Proposal, VerificationResult, WeatherSnapshot } from "../domain/model";

function freeze<T>(value: T): T {
  if (value && typeof value === "object") {
    Object.values(value).forEach(freeze);
    Object.freeze(value);
  }
  return value;
}

export class CalendarWorkflowCapability implements CalendarCapability {
  private readonly adapter: () => CalendarAdapter;
  private readonly weather: () => Promise<WeatherSnapshot>;
  private readonly permission: Exclude<Permission, "READ">;
  private readonly now: () => number;
  private readonly prepared = new WeakSet<PreparedAction>();
  private readonly grants = new WeakMap<ApprovalGrant, PreparedAction>();
  private executing = false;

  constructor(adapter: () => CalendarAdapter, weather: () => Promise<WeatherSnapshot>,
    permission: Exclude<Permission, "READ">, now = Date.now) {
    this.adapter = adapter;
    this.weather = weather;
    this.permission = permission;
    this.now = now;
  }

  async readState(eventId?: string): Promise<ObservedSources> {
    try {
      const adapter = this.adapter();
      const [events, weather] = await Promise.all([adapter.listEvents(), this.weather()]);
      // A target GET remains available after moving an event before listEvents' timeMin.
      if (eventId) {
        const latest = await adapter.getEvent(eventId);
        const rest = events.filter((event) => event.id !== eventId);
        return structuredClone(makeSourceBundle(latest ? [...rest, latest] : rest, weather));
      }
      return structuredClone(makeSourceBundle(events, weather));
    } catch (error) {
      throw workflowError(error, "DEPENDENCY_UNAVAILABLE");
    }
  }

  prepareAction(before: ObservedSources): PreparedAction | undefined {
    // Derive the version from facts; never trust an externally supplied version label.
    before = makeSourceBundle(before.events, before.weather);
    for (const event of before.events) {
      const proposal = createProposal(before, event, this.now());
      if (!proposal) continue;
      const action = freeze(structuredClone({ proposal, before, permission: this.permission }));
      this.prepared.add(action);
      return action;
    }
    return undefined;
  }

  approveAction(action: PreparedAction, consent: Consent): ApprovalGrant {
    if (!this.prepared.has(action)) throw new WorkflowError("INVALID_INPUT", "提案不属于当前能力上下文。");
    if (!consent.confirmed) throw new WorkflowError("USER_DECLINED", "已拒绝更改，未执行日历写入。");
    if (action.permission === "WRITE_SENSITIVE" && !consent.explicit) {
      throw new WorkflowError("PERMISSION_DENIED", "真实日历更改需要显式确认。");
    }
    const grant = Object.freeze({ id: crypto.randomUUID() });
    this.grants.set(grant, action);
    return grant;
  }

  async executeAction(action: PreparedAction, approval?: ApprovalGrant): Promise<void> {
    if (!approval || this.grants.get(approval) !== action || this.executing) {
      throw new WorkflowError("PERMISSION_DENIED", "缺少有效的当前提案审批，未执行写入。");
    }
    this.grants.delete(approval);
    this.executing = true;
    try {
      const before = await this.readState(action.proposal.calendarEventId);
      const proposal = action.proposal;
      if (proposalExpired(proposal, before) || Date.parse(proposal.proposedState.start) <= this.now()
        || this.now() - Date.parse(proposal.createdAt) > 10 * 60_000) {
        throw new WorkflowError("STATE_STALE", "数据或时间已有变化，请重新计算并确认；未执行写入。");
      }
      const event = before.events.find((event) => event.id === proposal.calendarEventId);
      if (!event || !verifyEvent(event, proposal.currentState)) {
        throw new WorkflowError("STATE_STALE", "原活动已经变化，未执行写入。");
      }
      await this.adapter().updateEvent(event.id, proposal.proposedState, event.timeZone, event);
    } finally {
      this.executing = false;
    }
  }

  verifyResult(before: ObservedSources, after: ObservedSources, expected: Proposal): VerificationResult {
    const original = before.events.find((event) => event.id === expected.calendarEventId);
    const actual = after.events.find((event) => event.id === expected.calendarEventId);
    const preserved = original && actual && original.id === actual.id && original.title === actual.title
      && original.location === actual.location && original.timeZone === actual.timeZone
      && original.source === actual.source && Boolean(original.allDay) === Boolean(actual.allDay);
    const verified = Boolean(preserved) && verifyEvent(original, expected.currentState) && verifyEvent(actual, expected.proposedState);
    return {
      checkedAt: new Date(this.now()).toISOString(), eventId: expected.calendarEventId,
      expected: expected.proposedState, actual: actual ? { start: actual.start, end: actual.end } : undefined,
      verified, message: verified ? "日历回读确认了时间更改，原活动信息保持一致。" : "日历回读与确认的更改不一致，未记录为成功。",
    };
  }
}

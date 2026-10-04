// SPDX-License-Identifier: Apache-2.0
import type { CalendarCapability, Consent, PreparedAction } from "./capability";
import type { ActionRecord, AgentRun, AgentStatus, Impact, ObservedSources, Proposal, VerificationResult } from "./model";
import { WorkflowError, workflowError } from "./errors";
import { detectImpact, proposalExpired, verifyEvent } from "./engine";
import { transition } from "./stateMachine";

export interface WorkflowSnapshot extends AgentRun {
  sources?: ObservedSources;
  proposal?: Proposal;
  impact?: Impact;
  error?: { code: WorkflowError["code"]; retryable: boolean; message: string };
  history: AgentStatus[];
  canRecheck?: boolean;
}

export class CalendarWorkflow {
  private readonly capability: CalendarCapability;
  private readonly expose: (state: WorkflowSnapshot) => void;
  private state: WorkflowSnapshot;
  private prepared?: PreparedAction;
  private busy = false;
  private attempted = false;
  private reconcilable = false;

  constructor(capability: CalendarCapability, expose: (state: WorkflowSnapshot) => void = () => {}) {
    this.capability = capability;
    this.expose = expose;
    this.state = { runId: crypto.randomUUID(), startedAt: new Date().toISOString(), status: "DETECTED", history: ["DETECTED"] };
  }

  snapshot(): WorkflowSnapshot { return structuredClone({ ...this.state, canRecheck: this.reconcilable && ["FAILED", "PARTIAL"].includes(this.state.status) }); }

  private publish(): void { this.expose(this.snapshot()); }

  private move(status: AgentStatus): void {
    this.state.status = transition(this.state.status, status);
    this.state.history.push(status);
    if (this.state.proposal) this.state.proposal.status = status;
    this.publish();
  }

  private fail(error: unknown, fallback: WorkflowError["code"], partial = false): void {
    const failure = workflowError(error, fallback);
    this.state.error = { code: failure.code, retryable: failure.retryable, message: failure.message };
    this.state.message = partial ? `写入可能已发生，但结果未验证：${failure.message}` : failure.message;
    if (this.state.action) this.state.action = { ...this.state.action, result: "failed", message: this.state.message };
    this.move(failure.code === "STATE_STALE" && ["AWAITING_APPROVAL", "EXECUTING"].includes(this.state.status) ? "STALE"
      : failure.code === "USER_DECLINED" ? "DECLINED" : partial ? "PARTIAL" : "FAILED");
  }

  async detect(): Promise<void> {
    if (this.busy || this.state.status !== "DETECTED") return;
    this.busy = true;
    this.publish();
    try {
      this.state.sources = await this.capability.readState();
      this.move("UNDERSTOOD");
      this.prepared = this.capability.prepareAction(this.state.sources);
      this.state.impact = this.prepared?.proposal.impact ?? this.state.sources.events
        .map((event) => detectImpact(event, this.state.sources!.weather.hours)).find((impact) => impact);
      if (!this.prepared) {
        this.state.eventId = this.state.impact?.eventId;
        this.state.message = this.state.impact
          ? "检测到天气与户外活动冲突，但没有找到有完整预报且空闲的可用时段；日历未更改。"
          : "没有找到可执行的天气调整建议，日历未更改。";
        this.publish();
        return;
      }
      this.state.proposal = structuredClone(this.prepared.proposal);
      this.state.proposalId = this.prepared.proposal.proposalId;
      this.state.eventId = this.prepared.proposal.calendarEventId;
      this.move("PROPOSED");
      this.move("AWAITING_APPROVAL");
    } catch (error) { this.fail(error, "DEPENDENCY_UNAVAILABLE"); }
    finally { this.busy = false; }
  }

  decline(): void {
    if (this.busy || this.state.status !== "AWAITING_APPROVAL") return;
    this.fail(new WorkflowError("USER_DECLINED", "已保留原定时间，日历未作更改。"), "USER_DECLINED");
  }

  cancel(): void {
    if (this.busy || this.state.status !== "AWAITING_APPROVAL") return;
    this.state.message = "已取消本次更改，未执行日历写入。";
    this.move("CANCELLED");
  }

  async refresh(): Promise<void> {
    if (this.busy || this.state.status !== "AWAITING_APPROVAL") return;
    this.busy = true;
    try {
      const sources = await this.capability.readState(this.state.eventId);
      this.state.sources = sources;
      if (this.state.status === "AWAITING_APPROVAL" && this.prepared && proposalExpired(this.prepared.proposal, sources)) {
        this.fail(new WorkflowError("STATE_STALE", "当前数据已变化，请重新计算；日历未更改。"), "STATE_STALE");
      } else { this.publish(); }
    } catch (error) { this.fail(error, "DEPENDENCY_UNAVAILABLE"); }
    finally { this.busy = false; }
  }

  async approve(consent: Consent): Promise<void> {
    if (this.busy || this.state.status !== "AWAITING_APPROVAL" || !this.prepared) {
      throw new WorkflowError("PERMISSION_DENIED", "当前没有可审批的待执行提案。");
    }
    this.busy = true;
    try {
      const approval = this.capability.approveAction(this.prepared, consent);
      const proposal = this.prepared.proposal;
      const action: ActionRecord = {
        actionId: crypto.randomUUID(), proposalId: proposal.proposalId, requestedAt: new Date().toISOString(),
        eventId: proposal.calendarEventId, before: proposal.currentState, expected: proposal.proposedState, result: "pending",
      };
      this.state.action = action;
      this.move("EXECUTING");
      this.attempted = true;
      await this.capability.executeAction(this.prepared, approval);
      this.reconcilable = true;
      this.move("VERIFYING");
      await this.verify();
    } catch (error) {
      const failure = workflowError(error, this.snapshot().status === "VERIFYING" ? "VERIFICATION_FAILED" : "EXECUTION_FAILED");
      const uncertain = this.attempted && (this.snapshot().status === "VERIFYING" || failure.outcomeUnknown);
      this.reconcilable = uncertain;
      this.fail(failure, failure.code, uncertain);
    } finally { this.busy = false; }
  }

  private async verify(): Promise<void> {
    const prepared = this.prepared!;
    const after = await this.capability.readState(prepared.proposal.calendarEventId);
    const result: VerificationResult = this.capability.verifyResult(prepared.before, after, prepared.proposal);
    this.state.sources = after;
    this.state.verification = result;
    if (!result.verified) {
      const actual = after.events.find((event) => event.id === prepared.proposal.calendarEventId);
      this.fail(new WorkflowError("VERIFICATION_FAILED", result.message), "VERIFICATION_FAILED",
        !verifyEvent(actual, prepared.proposal.currentState));
      return;
    }
    this.state.error = undefined;
    this.state.message = result.message;
    this.state.action = { ...this.state.action!, result: "success", completedAt: result.checkedAt, message: result.message };
    this.move("COMPLETED");
  }

  // Reconcile uncertain execution through reads only. Any new write needs a new proposal and consent.
  async recheck(): Promise<void> {
    if (this.busy || !this.reconcilable || !this.prepared || !["FAILED", "PARTIAL"].includes(this.state.status)) return;
    this.busy = true;
    this.move("VERIFYING");
    try { await this.verify(); }
    catch (error) { this.fail(error, "VERIFICATION_FAILED", true); }
    finally { this.busy = false; }
  }
}

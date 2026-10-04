import type { AgentStatus } from "./model";

const TRANSITIONS: Record<AgentStatus, AgentStatus[]> = {
  DETECTED: ["UNDERSTOOD", "FAILED", "CANCELLED"],
  UNDERSTOOD: ["PROPOSED", "FAILED", "CANCELLED"],
  PROPOSED: ["AWAITING_APPROVAL", "FAILED", "CANCELLED"],
  AWAITING_APPROVAL: ["EXECUTING", "DECLINED", "STALE", "FAILED", "CANCELLED"],
  EXECUTING: ["VERIFYING", "FAILED", "STALE", "PARTIAL"],
  VERIFYING: ["COMPLETED", "FAILED", "PARTIAL"],
  COMPLETED: [],
  FAILED: ["VERIFYING"],
  DECLINED: [],
  PARTIAL: ["VERIFYING"],
  STALE: [],
  CANCELLED: [],
};

export function canTransition(from: AgentStatus, to: AgentStatus): boolean {
  return TRANSITIONS[from].includes(to);
}

export function transition(from: AgentStatus, to: AgentStatus): AgentStatus {
  if (!canTransition(from, to)) throw new Error(`Invalid Ripple transition: ${from} → ${to}`);
  return to;
}

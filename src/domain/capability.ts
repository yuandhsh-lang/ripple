// SPDX-License-Identifier: Apache-2.0
import type { CalendarEvent, EventState, ObservedSources, Proposal, VerificationResult } from "./model";

export type Permission = "READ" | "WRITE_REVERSIBLE" | "WRITE_SENSITIVE";
export interface Consent { confirmed: boolean; explicit: boolean }
export interface ApprovalGrant { readonly id: string }
export interface PreparedAction {
  readonly proposal: Proposal;
  readonly before: ObservedSources;
  readonly permission: Exclude<Permission, "READ">;
}

export interface CalendarAdapter {
  listEvents(): Promise<CalendarEvent[]>;
  getEvent(eventId: string): Promise<CalendarEvent | undefined>;
  updateEvent(eventId: string, expected: EventState, timeZone: string, before?: CalendarEvent): Promise<CalendarEvent>;
}

// A single application capability, not an agent runtime or a transport protocol.
export interface CalendarCapability {
  readState(eventId?: string): Promise<ObservedSources>;
  prepareAction(before: ObservedSources): PreparedAction | undefined;
  approveAction(action: PreparedAction, consent: Consent): ApprovalGrant;
  executeAction(action: PreparedAction, approval?: ApprovalGrant): Promise<void>;
  verifyResult(before: ObservedSources, after: ObservedSources, expected: Proposal): VerificationResult;
}

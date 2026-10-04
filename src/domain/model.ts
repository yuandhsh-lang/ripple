import { WorkflowError } from "./errors";

export type AgentStatus =
  | "DETECTED"
  | "UNDERSTOOD"
  | "PROPOSED"
  | "AWAITING_APPROVAL"
  | "EXECUTING"
  | "VERIFYING"
  | "COMPLETED"
  | "FAILED"
  | "DECLINED"
  | "PARTIAL"
  | "STALE"
  | "CANCELLED";

export type DataMode = "demo" | "real";

export interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  timeZone: string;
  location?: string;
  allDay?: boolean;
  source: "Demo calendar" | "Google Calendar";
  revision?: string;
}

export interface WeatherHour {
  start: string;
  end: string;
  precipitationMm: number;
  precipitationProbability: number;
  weatherCode: number;
}

export interface WeatherSnapshot {
  source: "Demo forecast" | "Open-Meteo";
  sourceType: DataMode;
  fetchedAt: string;
  location: string;
  hours: WeatherHour[];
}

export interface Impact {
  eventId: string;
  eventTitle: string;
  weatherStart: string;
  weatherEnd: string;
  severity: "rain" | "heavy rain" | "thunderstorm";
  peakPrecipitationProbability: number;
}

export interface EventState {
  start: string;
  end: string;
}

export interface Proposal {
  proposalId: string;
  createdAt: string;
  sourceStateVersion: string;
  calendarEventId: string;
  currentState: EventState;
  proposedState: EventState;
  reason: string;
  impact: Impact;
  status: AgentStatus;
}

export interface ActionRecord {
  actionId: string;
  proposalId: string;
  requestedAt: string;
  completedAt?: string;
  eventId: string;
  before: EventState;
  expected: EventState;
  result: "pending" | "success" | "failed" | "denied";
  message?: string;
}

export interface VerificationResult {
  checkedAt: string;
  eventId: string;
  expected: EventState;
  actual?: EventState;
  verified: boolean;
  message: string;
}

export interface SourceState {
  calendarSource: CalendarEvent["source"];
  calendarFetchedAt: string;
  calendarVersion: string;
  weatherSource: WeatherSnapshot["source"];
  weatherFetchedAt: string;
  weatherVersion: string;
  version: string;
}

export interface AgentRun {
  runId: string;
  startedAt: string;
  status: AgentStatus;
  eventId?: string;
  proposalId?: string;
  action?: ActionRecord;
  verification?: VerificationResult;
  message?: string;
}

export interface ObservedSources {
  events: CalendarEvent[];
  weather: WeatherSnapshot;
  sourceState: SourceState;
}

export type DemoFault = "none" | "denied" | "write-failed" | "verify-mismatch" | "source-changed";

export class CalendarPermissionError extends WorkflowError {
  constructor(message = "需要日历权限才能应用此更改。") {
    super("PERMISSION_DENIED", message);
    this.name = "CalendarPermissionError";
  }
}

export class CalendarApiError extends WorkflowError {
  constructor(message: string, retryable = true) {
    super("EXECUTION_FAILED", message, retryable);
    this.name = "CalendarApiError";
  }
}

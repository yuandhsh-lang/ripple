import type { CalendarEvent, DemoFault, EventState } from "../domain/model";
import { CalendarApiError, CalendarPermissionError } from "../domain/model";
import { demoScenarioDay } from "./demoDay";
import { WorkflowError } from "../domain/errors";

const STORAGE_KEY = "ripple-demo-event-v1";

function localEventTime(day: Date, hour: number, minute = 0): string {
  return new Date(day.getFullYear(), day.getMonth(), day.getDate(), hour, minute).toISOString();
}

function validDemoEvent(value: unknown): value is CalendarEvent {
  if (!value || typeof value !== "object") return false;
  const event = value as Partial<CalendarEvent>;
  if (typeof event.id !== "string" || !event.id || typeof event.title !== "string"
    || typeof event.start !== "string" || typeof event.end !== "string" || typeof event.timeZone !== "string"
    || event.source !== "Demo calendar" || !Number.isFinite(Date.parse(event.start))
    || !Number.isFinite(Date.parse(event.end)) || Date.parse(event.end) <= Date.parse(event.start)) return false;
  try { new Intl.DateTimeFormat("en", { timeZone: event.timeZone }).format(); }
  catch { return false; }
  return true;
}

export function resetDemoCalendar(now = new Date()): CalendarEvent[] {
  const day = demoScenarioDay(now);
  const event: CalendarEvent = {
    id: "demo-outdoor-tennis",
    title: "户外网球",
    start: localEventTime(day, 15),
    end: localEventTime(day, 16),
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    location: "滨江球场",
    source: "Demo calendar",
  };
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify([event]));
  return [event];
}

function readEvents(): CalendarEvent[] {
  try {
    const events: unknown = JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? "null");
    if (Array.isArray(events) && events.length && events.every(validDemoEvent)) {
      const sample = events.find((event) => event.id === "demo-outdoor-tennis");
      const sampleDay = sample ? new Date(sample.start) : undefined;
      const day = demoScenarioDay();
      // The calendar and forecast must describe the same repeatable scenario day.
      if (!sampleDay || sampleDay.getFullYear() !== day.getFullYear() || sampleDay.getMonth() !== day.getMonth()
        || sampleDay.getDate() !== day.getDate()) return resetDemoCalendar();
      const localizedEvents = events.map((event) => event.id === "demo-outdoor-tennis" && event.title === "Outdoor Tennis"
        ? { ...event, title: "户外网球", location: event.location === "Riverside courts" ? "滨江球场" : event.location }
        : event);
      if (localizedEvents.some((event, index) => event !== events[index])) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(localizedEvents));
      }
      return localizedEvents;
    }
  } catch {
    // A broken local demo record is replaced with the repeatable sample.
  }
  return resetDemoCalendar();
}

export class DemoCalendarAdapter {
  private readonly fault: DemoFault;

  constructor(fault: DemoFault = "none") {
    this.fault = fault;
  }

  async listEvents(): Promise<CalendarEvent[]> {
    return readEvents().map((event) => ({ ...event }));
  }

  async getEvent(eventId: string): Promise<CalendarEvent | undefined> {
    return readEvents().find((event) => event.id === eventId);
  }

  async updateEvent(eventId: string, state: EventState, _timeZone?: string, before?: CalendarEvent): Promise<CalendarEvent> {
    if (this.fault === "denied") throw new CalendarPermissionError();
    if (this.fault === "write-failed") throw new CalendarApiError("演示日历无法保存此次更改。");
    const events = readEvents();
    const current = events.find((event) => event.id === eventId);
    if (!current) throw new CalendarApiError("日历活动已不存在。", false);
    if (before && JSON.stringify(current) !== JSON.stringify(before)) {
      throw new WorkflowError("STATE_STALE", "演示活动已变化，未执行写入。");
    }
    if (this.fault === "verify-mismatch") return { ...current };

    const updated = { ...current, start: state.start, end: state.end };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(events.map((event) => event.id === eventId ? updated : event)));
    return updated;
  }
}

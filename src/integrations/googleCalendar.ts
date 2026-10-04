import type { CalendarEvent, EventState } from "../domain/model";
import { CalendarPermissionError } from "../domain/model";
import { WorkflowError } from "../domain/errors";

const CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.events";
const SCRIPT_URL = "https://accounts.google.com/gsi/client";
let accessToken: string | undefined;
let tokenExpiresAt = 0;
let authorizationGeneration = 0;
let scriptPromise: Promise<void> | undefined;

declare global {
  interface Window {
    google?: {
      accounts?: {
        oauth2?: {
          initTokenClient(options: {
            client_id: string;
            scope: string;
            callback: (response: { access_token?: string; expires_in?: number; error?: string }) => void;
            error_callback?: (error: { type?: string }) => void;
          }): { requestAccessToken(): void };
        };
      };
    };
  }
}

export function hasGoogleClientId(): boolean {
  return Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim());
}

export function connectGoogleCalendar(): Promise<void> {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim();
  if (!clientId) return Promise.reject(new WorkflowError("INVALID_INPUT", "请在 .env 中设置 VITE_GOOGLE_CLIENT_ID，再连接 Google Calendar。"));
  return loadIdentityScript().then(() => new Promise<void>((resolve, reject) => {
    const tokenClient = window.google?.accounts?.oauth2?.initTokenClient({
      client_id: clientId,
      scope: CALENDAR_SCOPE,
      callback: (response) => {
        if (!response.access_token) {
          reject(new CalendarPermissionError("尚未授予日历访问权限，未进行任何更改。"));
          return;
        }
        accessToken = response.access_token;
        authorizationGeneration += 1;
        tokenExpiresAt = Date.now() + Math.max(0, (response.expires_in ?? 3600) - 60) * 1000;
        resolve();
      },
      error_callback: () => reject(new CalendarPermissionError("尚未授予日历访问权限，未进行任何更改。")),
    });
    if (!tokenClient) {
      reject(new WorkflowError("DEPENDENCY_UNAVAILABLE", "Google Identity Services 加载失败，请检查网络后重试。", true));
      return;
    }
    tokenClient.requestAccessToken();
  }));
}

function loadIdentityScript(): Promise<void> {
  if (window.google?.accounts?.oauth2) return Promise.resolve();
  if (!scriptPromise) {
    scriptPromise = new Promise<void>((resolve, reject) => {
      const script = document.createElement("script");
      script.src = SCRIPT_URL;
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => { scriptPromise = undefined; script.remove(); reject(new WorkflowError("DEPENDENCY_UNAVAILABLE", "Google Identity Services 无法加载。", true)); };
      document.head.append(script);
    });
  }
  return scriptPromise;
}

function requireToken(expectedGeneration: number): string {
  if (expectedGeneration !== authorizationGeneration) {
    throw new WorkflowError("STATE_STALE", "日历授权上下文已变化，请重新计算并确认。");
  }
  if (!accessToken || Date.now() >= tokenExpiresAt) {
    accessToken = undefined;
    throw new CalendarPermissionError("日历授权已过期，请重新连接；本次请求未获授权。");
  }
  return accessToken;
}

function dayWindow(now: Date): { timeMin: string; timeMax: string } {
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  return { timeMin: now.toISOString(), timeMax: end.toISOString() };
}

interface GoogleEvent {
  id: string;
  etag?: string;
  summary?: string;
  location?: string;
  start?: { dateTime?: string; date?: string; timeZone?: string };
  end?: { dateTime?: string; date?: string; timeZone?: string };
}

function mapGoogleEvent(value: GoogleEvent): CalendarEvent | undefined {
  const start = value.start?.dateTime;
  const end = value.end?.dateTime;
  if (!value.id || !(start && end) && !(value.start?.date && value.end?.date)) return undefined;
  const timeZone = value.start?.timeZone || Intl.DateTimeFormat().resolvedOptions().timeZone;
  return {
    id: value.id,
    title: value.summary?.trim() || "未命名活动",
    start: start ?? new Date(`${value.start!.date}T00:00:00`).toISOString(),
    end: end ?? new Date(`${value.end!.date}T00:00:00`).toISOString(),
    timeZone,
    location: value.location,
    allDay: !start,
    source: "Google Calendar",
    revision: value.etag,
  };
}

async function requestGoogle<T>(path: string, init: RequestInit = {}, expectedGeneration: number): Promise<T> {
  const token = requireToken(expectedGeneration);
  let response: Response;
  try { response = await fetch(`https://www.googleapis.com/calendar/v3${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  }); } catch {
    throw new WorkflowError(init.method === "PATCH" ? "EXECUTION_FAILED" : "DEPENDENCY_UNAVAILABLE",
      "Google Calendar 网络请求失败；请读取日历确认结果。", true, init.method === "PATCH");
  }
  let body: unknown;
  try { body = await response.json(); }
  catch {
    if (response.ok) {
      throw new WorkflowError(init.method === "PATCH" ? "EXECUTION_FAILED" : "DEPENDENCY_UNAVAILABLE",
        "Google Calendar 响应无法读取，结果未验证。", true, init.method === "PATCH");
    }
  }
  if (response.status === 401 || response.status === 403) {
    throw new CalendarPermissionError("Google Calendar 拒绝了访问请求，请检查日历权限。");
  }
  if (!response.ok) {
    if (response.status === 412 || response.status === 404 || response.status === 410) {
      throw new WorkflowError("STATE_STALE", "日历活动已变化或不存在，请重新计算。");
    }
    throw new WorkflowError(init.method === "PATCH" ? "EXECUTION_FAILED" : "DEPENDENCY_UNAVAILABLE",
      `Google Calendar 请求失败（HTTP ${response.status}）。`, response.status === 429 || response.status >= 500,
      init.method === "PATCH" && response.status >= 500);
  }
  return body as T;
}

export class GoogleCalendarAdapter {
  private readonly authorizationGeneration = authorizationGeneration;
  async listEvents(now = new Date()): Promise<CalendarEvent[]> {
    const range = dayWindow(now);
    const params = new URLSearchParams({
      timeMin: range.timeMin,
      timeMax: range.timeMax,
      singleEvents: "true",
      orderBy: "startTime",
      maxResults: "250",
    });
    const events: CalendarEvent[] = [];
    const pages = new Set<string>();
    let nextPage: string | undefined;
    do {
      if (nextPage) {
        if (pages.has(nextPage)) throw new WorkflowError("DEPENDENCY_UNAVAILABLE", "日历分页响应不完整，无法安全检查空闲时段。", true);
        pages.add(nextPage);
        params.set("pageToken", nextPage);
      }
      const response = await requestGoogle<{ items?: GoogleEvent[]; nextPageToken?: string }>(`/calendars/primary/events?${params}`, {}, this.authorizationGeneration);
      events.push(...(response.items ?? []).map(mapGoogleEvent).filter((event): event is CalendarEvent => Boolean(event)));
      nextPage = response.nextPageToken;
    } while (nextPage);
    return events;
  }

  async getEvent(eventId: string): Promise<CalendarEvent | undefined> {
    try {
      const event = await requestGoogle<GoogleEvent>(`/calendars/primary/events/${encodeURIComponent(eventId)}`, {}, this.authorizationGeneration);
      return mapGoogleEvent(event);
    } catch (error) {
      if (error instanceof WorkflowError && error.code === "STATE_STALE") return undefined;
      throw error;
    }
  }

  async updateEvent(eventId: string, state: EventState, timeZone: string, before?: CalendarEvent): Promise<CalendarEvent> {
    if (before && !before.revision) throw new WorkflowError("STATE_STALE", "缺少日历事件版本，未执行写入。");
    const updated = await requestGoogle<GoogleEvent>(`/calendars/primary/events/${encodeURIComponent(eventId)}`, {
      method: "PATCH",
      headers: before ? { "If-Match": before.revision! } : {},
      body: JSON.stringify({
        start: { dateTime: state.start, timeZone },
        end: { dateTime: state.end, timeZone },
      }),
    }, this.authorizationGeneration);
    const event = mapGoogleEvent(updated);
    if (!event) throw new WorkflowError("EXECUTION_FAILED", "日历更新响应不完整，结果需要回读检查。", false, true);
    return event;
  }
}

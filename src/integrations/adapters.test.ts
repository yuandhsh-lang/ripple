import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { verifyEvent } from "../domain/engine";
import { CalendarApiError, CalendarPermissionError } from "../domain/model";
import { DemoCalendarAdapter, resetDemoCalendar } from "./demoCalendar";
import { connectGoogleCalendar, GoogleCalendarAdapter } from "./googleCalendar";
import { fetchOpenMeteo } from "./openMeteo";

const localStore = new Map<string, string>();

beforeEach(() => {
  localStore.clear();
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 8, 29, 8));
  vi.stubGlobal("window", {
    localStorage: {
      getItem: (key: string) => localStore.get(key) ?? null,
      setItem: (key: string, value: string) => { localStore.set(key, value); },
      removeItem: (key: string) => { localStore.delete(key); },
    },
    setTimeout,
  });
});
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks(); vi.unstubAllGlobals(); vi.unstubAllEnvs(); });

describe("Demo Calendar adapter", () => {
  it("refreshes yesterday's cached sample to match the current demo forecast day", async () => {
    resetDemoCalendar(new Date(2026, 8, 28, 8));
    const [event] = await new DemoCalendarAdapter().listEvents();
    expect(event.start).toBe(new Date(2026, 8, 29, 15).toISOString());
  });

  it("rolls calendar and weather to tomorrow after the same-day review cutoff", async () => {
    resetDemoCalendar();
    vi.setSystemTime(new Date(2026, 8, 29, 11, 45));
    const [event] = await new DemoCalendarAdapter().listEvents();
    expect(event.start).toBe(new Date(2026, 8, 30, 15).toISOString());
  });

  it("replaces a syntactically valid but malformed cached record", async () => {
    localStore.set("ripple-demo-event-v1", JSON.stringify([{ id: "demo-outdoor-tennis", title: "户外网球", start: "invalid" }]));
    const [event] = await new DemoCalendarAdapter().listEvents();
    expect(event.start).toBe(new Date(2026, 8, 29, 15).toISOString());
    expect(event.source).toBe("Demo calendar");
  });

  it("reads the repeatable sample, writes it, then verifies the re-read value", async () => {
    resetDemoCalendar(new Date(2026, 8, 29, 8, 0));
    const calendar = new DemoCalendarAdapter();
    const [before] = await calendar.listEvents();
    expect(before.title).toBe("户外网球");
    const expected = { start: new Date(2026, 8, 29, 12, 30).toISOString(), end: new Date(2026, 8, 29, 13, 30).toISOString() };
    await calendar.updateEvent(before.id, expected);
    const after = await calendar.getEvent(before.id);
    expect(verifyEvent(after, expected)).toBe(true);
  });

  it("updates a previously saved English demo sample to the Chinese copy", async () => {
    localStore.set("ripple-demo-event-v1", JSON.stringify([{
      id: "demo-outdoor-tennis",
      title: "Outdoor Tennis",
      start: "2026-09-29T07:00:00.000Z",
      end: "2026-09-29T08:00:00.000Z",
      timeZone: "Asia/Shanghai",
      location: "Riverside courts",
      source: "Demo calendar",
    }]));

    const [event] = await new DemoCalendarAdapter().listEvents();

    expect(event).toMatchObject({ title: "户外网球", location: "滨江球场" });
    expect(JSON.parse(localStore.get("ripple-demo-event-v1") ?? "[]")[0].title).toBe("户外网球");
  });

  it("denies writes without modifying the sample event", async () => {
    resetDemoCalendar(new Date(2026, 8, 29, 8, 0));
    const calendar = new DemoCalendarAdapter("denied");
    const [before] = await calendar.listEvents();
    await expect(calendar.updateEvent(before.id, { start: new Date(2026, 8, 29, 12, 30).toISOString(), end: new Date(2026, 8, 29, 13, 30).toISOString() })).rejects.toBeInstanceOf(CalendarPermissionError);
    expect((await calendar.getEvent(before.id))?.start).toBe(before.start);
  });

  it("surfaces API failure separately from permission denial", async () => {
    resetDemoCalendar(new Date(2026, 8, 29, 8, 0));
    const calendar = new DemoCalendarAdapter("write-failed");
    const [event] = await calendar.listEvents();
    await expect(calendar.updateEvent(event.id, { start: new Date(2026, 8, 29, 12, 30).toISOString(), end: new Date(2026, 8, 29, 13, 30).toISOString() })).rejects.toBeInstanceOf(CalendarApiError);
  });

  it("can return an acknowledged write without changing state to exercise failed read-back", async () => {
    resetDemoCalendar(new Date(2026, 8, 29, 8, 0));
    const calendar = new DemoCalendarAdapter("verify-mismatch");
    const [before] = await calendar.listEvents();
    const expected = { start: new Date(2026, 8, 29, 12, 30).toISOString(), end: new Date(2026, 8, 29, 13, 30).toISOString() };
    await calendar.updateEvent(before.id, expected);
    const reread = await calendar.getEvent(before.id);
    expect(verifyEvent(reread, expected)).toBe(false);
  });
});

describe("Google Calendar adapter", () => {
  it("reads only the remaining day, updates the approved time, and can re-read it", async () => {
    vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "public-test-client");
    vi.stubGlobal("window", {
      google: {
        accounts: {
          oauth2: {
            initTokenClient: ({ callback }: { callback: (response: { access_token: string; expires_in: number }) => void }) => ({
              requestAccessToken: () => callback({ access_token: "mock-access-token", expires_in: 3600 }),
            }),
          },
        },
      },
    });
    const event = {
      id: "google-event-1",
      summary: "Outdoor Tennis",
      location: "Riverside courts",
      start: { dateTime: "2026-09-29T15:00:00+08:00", timeZone: "Asia/Shanghai" },
      end: { dateTime: "2026-09-29T16:00:00+08:00", timeZone: "Asia/Shanghai" },
    };
    const movedEvent = {
      ...event,
      start: { dateTime: "2026-09-29T12:30:00+08:00", timeZone: "Asia/Shanghai" },
      end: { dateTime: "2026-09-29T13:30:00+08:00", timeZone: "Asia/Shanghai" },
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ items: [event] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => movedEvent })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => movedEvent });
    vi.stubGlobal("fetch", fetchMock);

    await connectGoogleCalendar();
    const adapter = new GoogleCalendarAdapter();
    const now = new Date(2026, 8, 29, 20);
    const [listed] = await adapter.listEvents(now);
    expect(listed).toMatchObject({ id: event.id, title: event.summary, timeZone: "Asia/Shanghai" });
    const listUrl = new URL(String(fetchMock.mock.calls[0][0]));
    expect(listUrl.searchParams.get("timeMin")).toBe(now.toISOString());
    expect(listUrl.searchParams.get("timeMax")).toBe(new Date(2026, 8, 30).toISOString());

    const expected = { start: "2026-09-29T04:30:00.000Z", end: "2026-09-29T05:30:00.000Z" };
    await adapter.updateEvent(event.id, expected, "Asia/Shanghai");
    const reread = await adapter.getEvent(event.id);
    expect(fetchMock.mock.calls[1][1]).toMatchObject({ method: "PATCH" });
    expect(JSON.parse(String(fetchMock.mock.calls[1][1]?.body))).toEqual({
      start: { dateTime: expected.start, timeZone: "Asia/Shanghai" },
      end: { dateTime: expected.end, timeZone: "Asia/Shanghai" },
    });
    expect(verifyEvent(reread, expected)).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });
});

describe("Open-Meteo response normalization", () => {
  it("normalizes hourly values as UTC instants and keeps source freshness", async () => {
    const responseBodies = [
      { results: [{ name: "Shanghai", country: "China", latitude: 31.23, longitude: 121.47, timezone: "Asia/Shanghai" }] },
      { hourly: { time: ["2026-09-29T06:00", "2026-09-29T07:00"], precipitation: [0, 8.2], precipitation_probability: [5, 91], weather_code: [65, 65] } },
    ];
    const fetchMock = vi.fn(async () => ({ ok: true, json: async () => responseBodies.shift() }));
    vi.stubGlobal("fetch", fetchMock);
    const snapshot = await fetchOpenMeteo("Shanghai");
    expect(snapshot.source).toBe("Open-Meteo");
    expect(snapshot.sourceType).toBe("real");
    expect(snapshot.hours[0]).toMatchObject({
      start: "2026-09-29T06:00:00.000Z",
      end: "2026-09-29T07:00:00.000Z",
      precipitationMm: 8.2,
      precipitationProbability: 91,
      weatherCode: 65,
    });
    expect(Date.parse(snapshot.fetchedAt)).not.toBeNaN();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("assigns precipitation to the preceding hour and never invents the last interval", async () => {
    const responseBodies = [
      { results: [{ name: "Shanghai", latitude: 31.23, longitude: 121.47 }] },
      { hourly: { time: ["2026-09-29T06:00", "2026-09-29T07:00"], precipitation: [8.2, 0], precipitation_probability: [91, 5], weather_code: [1, 1] } },
    ];
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: true, json: async () => responseBodies.shift() })));
    const snapshot = await fetchOpenMeteo("Shanghai");
    expect(snapshot.hours).toHaveLength(1);
    expect(snapshot.hours[0]).toMatchObject({ start: "2026-09-29T06:00:00.000Z", end: "2026-09-29T07:00:00.000Z", precipitationMm: 0, precipitationProbability: 5 });
  });

  it("does not combine precipitation across a missing forecast timestamp", async () => {
    const responseBodies = [
      { results: [{ name: "Shanghai", latitude: 31.23, longitude: 121.47 }] },
      { hourly: { time: ["2026-09-29T06:00", "2026-09-29T08:00"], precipitation: [0, 0], precipitation_probability: [5, 5], weather_code: [1, 1] } },
    ];
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: true, json: async () => responseBodies.shift() })));
    expect((await fetchOpenMeteo("Shanghai")).hours).toEqual([]);
  });

  it("reports unavailable weather responses rather than fabricating an empty forecast", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: false, status: 503, json: async () => ({}) })));
    await expect(fetchOpenMeteo("Shanghai")).rejects.toThrow("HTTP 503");
  });
});

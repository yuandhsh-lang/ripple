// SPDX-License-Identifier: Apache-2.0
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { connectGoogleCalendar, GoogleCalendarAdapter } from "./googleCalendar";
import { fetchOpenMeteo } from "./openMeteo";

const event = {
  id: "google-1", etag: '"revision-1"', summary: "Outdoor Tennis",
  start: { dateTime: "2026-09-30T15:00:00+08:00", timeZone: "Asia/Shanghai" },
  end: { dateTime: "2026-09-30T16:00:00+08:00", timeZone: "Asia/Shanghai" },
};
const response = (body: unknown, status = 200) => ({ ok: status >= 200 && status < 300, status, json: async () => body });

beforeEach(async () => {
  vi.stubEnv("VITE_GOOGLE_CLIENT_ID", "public-test-client");
  vi.stubGlobal("window", { google: { accounts: { oauth2: {
    initTokenClient: ({ callback }: { callback: (response: unknown) => void }) => ({
      requestAccessToken: () => callback({ access_token: "test-only-token", expires_in: 3600 }),
    }),
  } } } });
  await connectGoogleCalendar();
});
afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); vi.unstubAllEnvs(); });

describe("real adapter hardening using mocked HTTP", () => {
  it("retains all event pages for conflict detection", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(response({ items: [event], nextPageToken: "page-2" }))
      .mockResolvedValueOnce(response({ items: [{ ...event, id: "busy-2" }] }));
    vi.stubGlobal("fetch", fetchMock);
    const events = await new GoogleCalendarAdapter().listEvents();
    expect(events).toHaveLength(2);
    expect(new URL(fetchMock.mock.calls[1][0]).searchParams.get("pageToken")).toBe("page-2");
  });

  it("sends If-Match and rejects the concurrent-update 412 as STATE_STALE", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(response(event)).mockResolvedValueOnce(response({}, 412));
    vi.stubGlobal("fetch", fetchMock);
    const adapter = new GoogleCalendarAdapter();
    const before = (await adapter.getEvent(event.id))!;
    await expect(adapter.updateEvent(before.id, { start: "2026-09-30T04:30:00Z", end: "2026-09-30T05:30:00Z" }, before.timeZone, before))
      .rejects.toMatchObject({ code: "STATE_STALE", retryable: false });
    expect(fetchMock.mock.calls[1][1].headers["If-Match"]).toBe(event.etag);
  });

  it("does not issue PATCH when a prepared real event lacks its revision", async () => {
    const fetchMock = vi.fn().mockResolvedValue(response({ ...event, etag: undefined }));
    vi.stubGlobal("fetch", fetchMock);
    const adapter = new GoogleCalendarAdapter();
    const before = (await adapter.getEvent(event.id))!;
    await expect(adapter.updateEvent(before.id, before, before.timeZone, before)).rejects.toMatchObject({ code: "STATE_STALE" });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("missing GET event is absence rather than successful state", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({}, 404)));
    expect(await new GoogleCalendarAdapter().getEvent(event.id)).toBeUndefined();
  });

  it("a new OAuth context invalidates the previous adapter before any network call", async () => {
    const old = new GoogleCalendarAdapter();
    await connectGoogleCalendar();
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    await expect(old.listEvents()).rejects.toMatchObject({ code: "STATE_STALE" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("PATCH network failure is retryable but outcome remains unknown", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    await expect(new GoogleCalendarAdapter().updateEvent(event.id, { start: event.start.dateTime, end: event.end.dateTime }, "Asia/Shanghai"))
      .rejects.toMatchObject({ code: "EXECUTION_FAILED", retryable: true, outcomeUnknown: true });
  });

  it.each(["READ", "PATCH"])("malformed successful %s JSON cannot count as valid state", async (method) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true, status: 200, json: async () => { throw new SyntaxError("truncated JSON"); },
    }));
    const adapter = new GoogleCalendarAdapter();
    const operation = method === "READ" ? adapter.listEvents()
      : adapter.updateEvent(event.id, { start: event.start.dateTime, end: event.end.dateTime }, "Asia/Shanghai");
    await expect(operation).rejects.toMatchObject({
      code: method === "READ" ? "DEPENDENCY_UNAVAILABLE" : "EXECUTION_FAILED",
      retryable: true, outcomeUnknown: method === "PATCH",
    });
  });

  it("does not fabricate dry weather when probability or precipitation is missing", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(response({ results: [{ name: "Shanghai", latitude: 31, longitude: 121 }] }))
      .mockResolvedValueOnce(response({ hourly: { time: ["2026-09-30T04:00"], weather_code: [1] } })));
    await expect(fetchOpenMeteo("Shanghai")).rejects.toMatchObject({ code: "DEPENDENCY_UNAVAILABLE" });
  });

  it("skips null/invalid observations instead of interpreting them as dry", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(response({ results: [{ name: "Shanghai", latitude: 31, longitude: 121 }] }))
      .mockResolvedValueOnce(response({ hourly: { time: ["2026-09-30T04:00", "invalid"], weather_code: [1, 1], precipitation: [null, 0], precipitation_probability: [5, 5] } })));
    expect((await fetchOpenMeteo("Shanghai")).hours).toEqual([]);
  });
});

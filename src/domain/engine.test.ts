import { describe, expect, it } from "vitest";
import {
  createProposal,
  detectImpact,
  findAlternative,
  makeSourceBundle,
  overlaps,
  proposalExpired,
  sourceFingerprint,
  verifyEvent,
  weatherSeverity,
} from "./engine";
import type { CalendarEvent, WeatherHour, WeatherSnapshot } from "./model";

const event: CalendarEvent = {
  id: "tennis-1",
  title: "Outdoor Tennis",
  start: "2026-09-29T15:00:00+08:00",
  end: "2026-09-29T16:00:00+08:00",
  timeZone: "Asia/Shanghai",
  location: "Riverside courts",
  source: "Demo calendar",
};

const hours: WeatherHour[] = [
  { start: "2026-09-29T09:00:00+08:00", end: "2026-09-29T10:00:00+08:00", precipitationMm: 0, precipitationProbability: 5, weatherCode: 1 },
  { start: "2026-09-29T10:00:00+08:00", end: "2026-09-29T11:00:00+08:00", precipitationMm: 0, precipitationProbability: 5, weatherCode: 1 },
  { start: "2026-09-29T11:00:00+08:00", end: "2026-09-29T12:00:00+08:00", precipitationMm: 0, precipitationProbability: 5, weatherCode: 1 },
  { start: "2026-09-29T12:00:00+08:00", end: "2026-09-29T13:00:00+08:00", precipitationMm: 0, precipitationProbability: 5, weatherCode: 1 },
  { start: "2026-09-29T13:00:00+08:00", end: "2026-09-29T14:00:00+08:00", precipitationMm: 0, precipitationProbability: 8, weatherCode: 2 },
  { start: "2026-09-29T14:30:00+08:00", end: "2026-09-29T15:30:00+08:00", precipitationMm: 8.4, precipitationProbability: 96, weatherCode: 65 },
  { start: "2026-09-29T15:30:00+08:00", end: "2026-09-29T16:30:00+08:00", precipitationMm: 7.1, precipitationProbability: 94, weatherCode: 65 },
];

function weather(overrides: Partial<WeatherSnapshot> = {}): WeatherSnapshot {
  return {
    source: "Demo forecast",
    sourceType: "demo",
    fetchedAt: "2026-09-29T08:00:00.000Z",
    location: "Shanghai · demo scenario",
    hours,
    ...overrides,
  };
}

describe("weather and event reasoning", () => {
  it("uses half-open intervals so adjacent events do not overlap", () => {
    expect(overlaps("2026-09-29T15:00:00+08:00", "2026-09-29T16:00:00+08:00", "2026-09-29T16:00:00+08:00", "2026-09-29T17:00:00+08:00")).toBe(false);
    expect(overlaps("2026-09-29T15:00:00+08:00", "2026-09-29T16:00:00+08:00", "2026-09-29T15:30:00+08:00", "2026-09-29T16:30:00+08:00")).toBe(true);
  });

  it("detects heavy rain overlapping an outdoor tennis event", () => {
    expect(detectImpact(event, hours)).toMatchObject({
      eventId: "tennis-1",
      severity: "heavy rain",
      weatherStart: "2026-09-29T14:30:00+08:00",
      weatherEnd: "2026-09-29T16:30:00+08:00",
    });
  });

  it("recognizes Chinese outdoor activity names", () => {
    expect(detectImpact({ ...event, title: "户外网球" }, hours)?.severity).toBe("heavy rain");
  });

  it("does not call an indoor meeting weather affected", () => {
    expect(detectImpact({ ...event, title: "Indoor Planning Meeting" }, hours)).toBeUndefined();
  });

  it("applies deterministic rain and heavy rain thresholds", () => {
    expect(weatherSeverity({ ...hours[0], precipitationProbability: 50 })).toBe("rain");
    expect(weatherSeverity({ ...hours[0], precipitationMm: 7 })).toBe("heavy rain");
    expect(weatherSeverity({ ...hours[0], weatherCode: 65 })).toBe("heavy rain");
    expect(weatherSeverity(hours[0])).toBeUndefined();
  });

  it.each([95, 96, 97, 99])("recognizes thunderstorm code %s even with low rainfall estimates", (weatherCode) => {
    const storm = { ...hours[0], start: event.start, end: event.end, weatherCode };
    expect(weatherSeverity(storm)).toBe("thunderstorm");
    expect(detectImpact(event, [storm])?.severity).toBe("thunderstorm");
  });

  it("never recommends a thunderstorm window as a dry alternative", () => {
    const stormy = weather({ hours: hours.map((hour) => ({ ...hour, weatherCode: 95, precipitationMm: 0, precipitationProbability: 5 })) });
    expect(findAlternative(event, [event], stormy, Date.parse("2026-09-29T09:00:00+08:00"))).toBeUndefined();
  });

  it("finds the latest dry half-hour slot and preserves event duration", () => {
    const alternative = findAlternative(event, [event], weather(), Date.parse("2026-09-29T09:00:00+08:00"));
    expect(alternative?.start).toBe("2026-09-29T04:30:00.000Z");
    expect(Date.parse(alternative!.end) - Date.parse(alternative!.start)).toBe(60 * 60_000);
  });

  it("expires a proposal when weather materially changes, but not when only fetched_at changes", () => {
    const base = makeSourceBundle([event], weather());
    const proposal = createProposal(base, event, Date.parse("2026-09-29T09:00:00+08:00"));
    expect(proposal).toBeDefined();
    expect(proposalExpired(proposal!, makeSourceBundle([event], weather({ fetchedAt: "2026-09-29T09:00:00Z" })))).toBe(false);
    const changed = hours.map((hour) => hour.weatherCode === 65 ? { ...hour, weatherCode: 1, precipitationMm: 0, precipitationProbability: 8 } : hour);
    expect(proposalExpired(proposal!, makeSourceBundle([event], weather({ hours: changed })))).toBe(true);
  });

  it("verifies both expected event boundaries after the calendar re-read", () => {
    const expected = { start: "2026-09-29T12:30:00+08:00", end: "2026-09-29T13:30:00+08:00" };
    expect(verifyEvent({ ...event, ...expected }, expected)).toBe(true);
    expect(verifyEvent({ ...event, start: expected.start }, expected)).toBe(false);
    expect(verifyEvent(undefined, expected)).toBe(false);
  });

  it("changes the combined source version when a calendar event moves", () => {
    expect(sourceFingerprint([event], weather())).not.toBe(sourceFingerprint([{ ...event, start: "2026-09-29T15:30:00+08:00" }], weather()));
  });

  it("does not round away a material threshold crossing or a revision change", () => {
    const low = weather({ hours: hours.map((hour) => ({ ...hour, weatherCode: 1, precipitationMm: 0.99, precipitationProbability: 49.6 })) });
    const high = weather({ hours: low.hours.map((hour) => ({ ...hour, precipitationMm: 1, precipitationProbability: 50 })) });
    expect(sourceFingerprint([event], low)).not.toBe(sourceFingerprint([event], high));
    expect(sourceFingerprint([event], low)).not.toBe(sourceFingerprint([{ ...event, revision: "new" }], low));
  });
});

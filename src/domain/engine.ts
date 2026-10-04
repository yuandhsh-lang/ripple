import type {
  CalendarEvent,
  EventState,
  Impact,
  ObservedSources,
  Proposal,
  SourceState,
  WeatherHour,
  WeatherSnapshot,
} from "./model";

const OUTDOOR_TERMS = /\b(tennis|run(?:ning)?|soccer|football|golf|picnic|hike|hiking|walk|cycling|bike|baseball|basketball|outdoor|garden|beach|trail)\b|网球|跑步|足球|高尔夫|野餐|徒步|散步|骑行|户外|花园|海滩|步道/i;
const RAIN_CODES = new Set([51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]);
const HEAVY_RAIN_CODES = new Set([65, 67, 82]);
const THUNDERSTORM_CODES = new Set([95, 96, 97, 99]);

export function overlaps(startA: string, endA: string, startB: string, endB: string): boolean {
  const a0 = Date.parse(startA);
  const a1 = Date.parse(endA);
  const b0 = Date.parse(startB);
  const b1 = Date.parse(endB);
  return Number.isFinite(a0 + a1 + b0 + b1) && a0 < b1 && b0 < a1;
}

export function isOutdoorActivity(event: CalendarEvent): boolean {
  return OUTDOOR_TERMS.test(`${event.title} ${event.location ?? ""}`);
}

export function weatherSeverity(hour: WeatherHour): Impact["severity"] | undefined {
  if (THUNDERSTORM_CODES.has(hour.weatherCode)) return "thunderstorm";
  if (HEAVY_RAIN_CODES.has(hour.weatherCode) || hour.precipitationMm >= 7) return "heavy rain";
  if (RAIN_CODES.has(hour.weatherCode) || hour.precipitationMm >= 1 || hour.precipitationProbability >= 50) return "rain";
  return undefined;
}

export function detectImpact(event: CalendarEvent, hours: WeatherHour[]): Impact | undefined {
  if (event.allDay || !isOutdoorActivity(event)) return undefined;
  const relevant = hours
    .filter((hour) => weatherSeverity(hour) && overlaps(event.start, event.end, hour.start, hour.end))
    .sort((left, right) => Date.parse(left.start) - Date.parse(right.start));
  if (!relevant.length) return undefined;

  const first = relevant[0];
  const last = relevant[relevant.length - 1];
  return {
    eventId: event.id,
    eventTitle: event.title,
    weatherStart: first.start,
    weatherEnd: last.end,
    severity: relevant.some((hour) => weatherSeverity(hour) === "thunderstorm") ? "thunderstorm"
      : relevant.some((hour) => weatherSeverity(hour) === "heavy rain") ? "heavy rain" : "rain",
    peakPrecipitationProbability: Math.max(...relevant.map((hour) => hour.precipitationProbability)),
  };
}

function stableHash(value: string): string {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, "0");
}

function relevantHours(events: CalendarEvent[], weather: WeatherSnapshot): WeatherHour[] {
  const timed = events
    .filter((event) => !event.allDay)
    .map((event) => ({ start: Date.parse(event.start), end: Date.parse(event.end) }))
    .filter((event) => Number.isFinite(event.start) && Number.isFinite(event.end));
  if (!timed.length) return [];
  const from = Math.min(...timed.map((event) => event.start)) - 8 * 60 * 60_000;
  const to = Math.max(...timed.map((event) => event.end));
  return weather.hours.filter((hour) => Date.parse(hour.start) < to && Date.parse(hour.end) > from);
}

function eventDay(value: number, timeZone: string): string {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(value);
  return `${parts.find((part) => part.type === "year")?.value}-${parts.find((part) => part.type === "month")?.value}-${parts.find((part) => part.type === "day")?.value}`;
}

export function sourceFingerprint(events: CalendarEvent[], weather: WeatherSnapshot): string {
  const calendar = [...events]
    .map(({ id, title, start, end, location, timeZone, allDay, source, revision }) => ({ id, title, start, end, location, timeZone, allDay: Boolean(allDay), source, revision }))
    .sort((a, b) => a.id.localeCompare(b.id));
  const forecast = relevantHours(events, weather)
    .map(({ start, end, precipitationMm, precipitationProbability, weatherCode }) => ({
      start,
      end,
      precipitationMm,
      precipitationProbability,
      weatherCode,
    }))
    .sort((a, b) => a.start.localeCompare(b.start));
  // Equality uses the canonical payload rather than a collision-prone 32-bit hash.
  return `s2-${JSON.stringify({ location: weather.location, source: weather.source, calendar, forecast })}`;
}

export function getSourceState(events: CalendarEvent[], weather: WeatherSnapshot): SourceState {
  const calendarPayload = [...events]
    .map(({ id, title, start, end, location, timeZone, allDay }) => ({ id, title, start, end, location, timeZone, allDay: Boolean(allDay) }))
    .sort((a, b) => a.id.localeCompare(b.id));
  const weatherPayload = relevantHours(events, weather)
    .map(({ start, end, precipitationMm, precipitationProbability, weatherCode }) => ({
      start,
      end,
      precipitationMm: Math.round(precipitationMm * 10) / 10,
      precipitationProbability: Math.round(precipitationProbability),
      weatherCode,
    }))
    .sort((a, b) => a.start.localeCompare(b.start));
  return {
    calendarSource: weather.sourceType === "real" ? "Google Calendar" : "Demo calendar",
    calendarFetchedAt: new Date().toISOString(),
    calendarVersion: `c1-${stableHash(JSON.stringify(calendarPayload))}`,
    weatherSource: weather.source,
    weatherFetchedAt: weather.fetchedAt,
    weatherVersion: `w1-${stableHash(JSON.stringify(weatherPayload))}`,
    version: sourceFingerprint(events, weather),
  };
}

function slotIsDry(start: number, end: number, hours: WeatherHour[]): boolean {
  const relevant = hours
    .filter((hour) => Date.parse(hour.start) < end && start < Date.parse(hour.end))
    .sort((left, right) => Date.parse(left.start) - Date.parse(right.start));
  let coveredUntil = start;
  for (const hour of relevant) {
    const hourStart = Date.parse(hour.start);
    const hourEnd = Date.parse(hour.end);
    if (hourStart > coveredUntil || weatherSeverity(hour)) return false;
    coveredUntil = Math.max(coveredUntil, hourEnd);
    if (coveredUntil >= end) return true;
  }
  return false;
}

function slotIsFree(start: number, end: number, events: CalendarEvent[], eventId: string): boolean {
  return events.every((other) => {
    if (other.id === eventId) return true;
    if (other.allDay) {
      const firstDay = eventDay(Date.parse(other.start), other.timeZone);
      const afterLastDay = eventDay(Date.parse(other.end), other.timeZone);
      const candidateDay = eventDay(start, other.timeZone);
      return candidateDay < firstDay || candidateDay >= afterLastDay;
    }
    return !overlaps(new Date(start).toISOString(), new Date(end).toISOString(), other.start, other.end);
  });
}

export function findAlternative(
  event: CalendarEvent,
  events: CalendarEvent[],
  weather: WeatherSnapshot,
  now = Date.now(),
): EventState | undefined {
  const start = Date.parse(event.start);
  const end = Date.parse(event.end);
  if (!Number.isFinite(start + end) || end <= start) return undefined;
  const duration = end - start;

  // Search the same afternoon from the latest earlier half-hour slot backward.
  for (let candidate = start - 150 * 60_000; candidate >= start - 8 * 60 * 60_000; candidate -= 30 * 60_000) {
    if (eventDay(candidate, event.timeZone) !== eventDay(start, event.timeZone)) continue;
    const candidateEnd = candidate + duration;
    if (eventDay(candidateEnd - 1, event.timeZone) !== eventDay(candidate, event.timeZone)) continue;
    if (candidate <= now || !slotIsFree(candidate, candidateEnd, events, event.id)) continue;
    if (slotIsDry(candidate, candidateEnd, weather.hours)) {
      return { start: new Date(candidate).toISOString(), end: new Date(candidateEnd).toISOString() };
    }
  }
  return undefined;
}

export function createProposal(sources: ObservedSources, event: CalendarEvent, now = Date.now()): Proposal | undefined {
  const impact = detectImpact(event, sources.weather.hours);
  if (!impact) return undefined;
  const proposedState = findAlternative(event, sources.events, sources.weather, now);
  if (!proposedState) return undefined;
  const window = `${formatTime(impact.weatherStart, event.timeZone)}–${formatTime(impact.weatherEnd, event.timeZone)}`;
  return {
    proposalId: crypto.randomUUID(),
    createdAt: new Date(now).toISOString(),
    sourceStateVersion: sources.sourceState.version,
    calendarEventId: event.id,
    currentState: { start: event.start, end: event.end },
    proposedState,
    reason: `${impact.severity === "thunderstorm" ? "预计有雷暴" : impact.severity === "heavy rain" ? "预计有大雨" : "预计有雨"}，${window} 与这项户外安排重叠。`,
    impact,
    status: "PROPOSED",
  };
}

export function proposalExpired(proposal: Proposal, sources: ObservedSources): boolean {
  return proposal.sourceStateVersion !== sources.sourceState.version;
}

export function verifyEvent(actual: CalendarEvent | undefined, expected: EventState): boolean {
  return Boolean(actual)
    && Date.parse(actual!.start) === Date.parse(expected.start)
    && Date.parse(actual!.end) === Date.parse(expected.end);
}

export function formatTime(value: string, timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone): string {
  return new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZone }).format(new Date(value));
}

export function formatSourceTime(value: string, timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone): string {
  return new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZone }).format(new Date(value));
}

export function makeSourceBundle(events: CalendarEvent[], weather: WeatherSnapshot): ObservedSources {
  return { events, weather, sourceState: getSourceState(events, weather) };
}

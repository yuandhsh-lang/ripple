import type { WeatherHour, WeatherSnapshot } from "../domain/model";
import { WorkflowError } from "../domain/errors";

interface GeocodingResponse {
  results?: Array<{ name: string; country?: string; latitude: number; longitude: number; timezone?: string }>;
}

interface ForecastResponse {
  hourly?: {
    time?: string[];
    precipitation?: number[];
    precipitation_probability?: number[];
    weather_code?: number[];
  };
}

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new WorkflowError("DEPENDENCY_UNAVAILABLE", `天气服务暂时不可用（HTTP ${response.status}）。`, response.status === 429 || response.status >= 500);
  return response.json() as Promise<T>;
}

export async function fetchOpenMeteo(city: string): Promise<WeatherSnapshot> {
  if (!city.trim()) throw new WorkflowError("INVALID_INPUT", "请输入天气预报城市。");
  const search = new URL("https://geocoding-api.open-meteo.com/v1/search");
  search.search = new URLSearchParams({ name: city, count: "1", language: "zh", format: "json" }).toString();
  const geocoding = await getJson<GeocodingResponse>(search.toString());
  const place = geocoding.results?.[0];
  if (!place) throw new WorkflowError("INVALID_INPUT", `Open-Meteo 未找到“${city}”，请检查城市名称。`);

  const forecastUrl = new URL("https://api.open-meteo.com/v1/forecast");
  forecastUrl.search = new URLSearchParams({
    latitude: String(place.latitude),
    longitude: String(place.longitude),
    hourly: "precipitation,precipitation_probability,weather_code",
    forecast_days: "7",
    timezone: "UTC",
  }).toString();
  const forecast = await getJson<ForecastResponse>(forecastUrl.toString());
  const hourly = forecast.hourly;
  if (!hourly?.time || !hourly.weather_code || !hourly.precipitation || !hourly.precipitation_probability) {
    throw new WorkflowError("DEPENDENCY_UNAVAILABLE", "Open-Meteo 返回的逐小时预报数据不完整。", true);
  }

  const utcInstant = (time: string): number => Date.parse(/T.*(?:Z|[+-]\d{2}:?\d{2})$/.test(time) ? time : `${time}Z`);
  const hours: WeatherHour[] = hourly.time.flatMap((time, index) => {
    const instant = utcInstant(time);
    const nextTime = hourly.time?.[index + 1];
    if (!nextTime) return [];
    const endInstant = utcInstant(nextTime);
    const code = hourly.weather_code?.[index];
    // Open-Meteo's precipitation fields describe the preceding hour; the code is instantaneous.
    // Use the code at the interval's start and precipitation at its end.
    const mm = hourly.precipitation?.[index + 1];
    const probability = hourly.precipitation_probability?.[index + 1];
    // Gaps and missing observations must not become invented dry hours.
    if (!Number.isFinite(instant) || endInstant - instant !== 60 * 60_000
      || ![code, mm, probability].every((value) => typeof value === "number" && Number.isFinite(value))) return [];
    const start = new Date(instant).toISOString();
    const end = new Date(endInstant).toISOString();
    return [{
      start,
      end,
      precipitationMm: mm!,
      precipitationProbability: probability!,
      weatherCode: code!,
    }];
  });

  return {
    source: "Open-Meteo",
    sourceType: "real",
    fetchedAt: new Date().toISOString(),
    location: `${place.name}${place.country ? `, ${place.country}` : ""}`,
    hours,
  };
}

import type { WeatherHour, WeatherSnapshot } from "../domain/model";
import { demoScenarioDay } from "./demoDay";

function localSlot(day: Date, hour: number, minute = 0): string {
  return new Date(day.getFullYear(), day.getMonth(), day.getDate(), hour, minute).toISOString();
}

export function demoWeatherSnapshot(now = new Date()): WeatherSnapshot {
  const day = demoScenarioDay(now);
  const hours: WeatherHour[] = [];
  for (let hour = 9; hour < 14; hour += 1) {
    hours.push({
      start: localSlot(day, hour),
      end: localSlot(day, hour + 1),
      precipitationMm: 0,
      precipitationProbability: 5,
      weatherCode: 1,
    });
  }
  hours.push(
    { start: localSlot(day, 14, 30), end: localSlot(day, 15, 30), precipitationMm: 8.4, precipitationProbability: 96, weatherCode: 65 },
    { start: localSlot(day, 15, 30), end: localSlot(day, 16, 30), precipitationMm: 7.1, precipitationProbability: 94, weatherCode: 65 },
    { start: localSlot(day, 16, 30), end: localSlot(day, 17, 30), precipitationMm: 0.6, precipitationProbability: 30, weatherCode: 3 },
  );
  return {
    source: "Demo forecast",
    sourceType: "demo",
    fetchedAt: now.toISOString(),
    location: "上海 · 演示场景",
    hours,
  };
}

export function changeDemoWeather(snapshot: WeatherSnapshot): WeatherSnapshot {
  return {
    ...snapshot,
    fetchedAt: new Date().toISOString(),
    hours: snapshot.hours.map((hour) => ({
      ...hour,
      precipitationMm: hour.weatherCode === 65 ? 0 : hour.precipitationMm,
      precipitationProbability: hour.weatherCode === 65 ? 8 : hour.precipitationProbability,
      weatherCode: hour.weatherCode === 65 ? 1 : hour.weatherCode,
    })),
  };
}

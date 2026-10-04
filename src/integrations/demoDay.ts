export function demoScenarioDay(now = new Date()): Date {
  const day = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const finalSameDayReview = new Date(day.getFullYear(), day.getMonth(), day.getDate(), 11, 45);
  if (now.getTime() >= finalSameDayReview.getTime()) day.setDate(day.getDate() + 1);
  return day;
}

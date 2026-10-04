import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { formatTime, weatherSeverity } from "./domain/engine";
import type { AgentStatus, DataMode, DemoFault } from "./domain/model";
import { CalendarWorkflow, type WorkflowSnapshot } from "./domain/workflow";
import { workflowError } from "./domain/errors";
import { CalendarWorkflowCapability } from "./integrations/calendarCapability";
import { changeDemoWeather, demoWeatherSnapshot } from "./integrations/demoWeather";
import { DemoCalendarAdapter, resetDemoCalendar } from "./integrations/demoCalendar";
import { connectGoogleCalendar, GoogleCalendarAdapter, hasGoogleClientId } from "./integrations/googleCalendar";
import { fetchOpenMeteo } from "./integrations/openMeteo";
import "./App.css";

function sourceClock(value?: string): string {
  if (!value) return "尚未读取";
  return new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(value));
}

function statusCopy(status: AgentStatus, message?: string): string {
  if (message) return message;
  const copy: Record<AgentStatus, string> = {
    DETECTED: "正在读取已有安排。", UNDERSTOOD: "已核对天气与日历。",
    PROPOSED: "已生成调整建议。", AWAITING_APPROVAL: "请查看并确认建议。",
    EXECUTING: "正在更新日历…", VERIFYING: "正在从日历重新读取活动…",
    COMPLETED: "已更新并验证。", FAILED: "操作失败，未记录为成功。",
    DECLINED: "已拒绝更改。", STALE: "情况已有变化，请重新计算。",
    PARTIAL: "更改结果未完全验证，请检查日历。", CANCELLED: "已取消更改。",
  };
  return copy[status];
}

function statusLabel(status: AgentStatus): string {
  const labels: Record<AgentStatus, string> = {
    DETECTED: "读取中", UNDERSTOOD: "已理解", PROPOSED: "已建议", AWAITING_APPROVAL: "待确认",
    EXECUTING: "执行中", VERIFYING: "验证中", COMPLETED: "已完成", FAILED: "失败",
    DECLINED: "已拒绝", STALE: "已过期", PARTIAL: "结果未确认", CANCELLED: "已取消",
  };
  return labels[status];
}

function severityLabel(severity?: string): string {
  if (severity === "thunderstorm") return "雷暴";
  if (severity === "heavy rain") return "大雨";
  if (severity === "rain") return "降雨";
  return severity ?? "";
}

function sourceLabel(source?: string): string {
  if (!source) return "";
  if (source === "Demo forecast") return "演示天气预报";
  if (source === "Demo calendar") return "演示日历";
  return source;
}

function locationLabel(location?: string): string {
  return location?.replaceAll("Shanghai", "上海").replaceAll(", China", "，中国") ?? "";
}

function hourLabel(value: string, zone: string): string {
  return formatTime(value, zone);
}

function dateParts(value: Date, timeZone: string): [number, number, number] {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(value);
  return [
    Number(parts.find((part) => part.type === "year")?.value),
    Number(parts.find((part) => part.type === "month")?.value),
    Number(parts.find((part) => part.type === "day")?.value),
  ];
}

function relativeDay(value: string, timeZone: string): string {
  const target = dateParts(new Date(value), timeZone);
  const today = dateParts(new Date(), timeZone);
  const dayDelta = (Date.UTC(target[0], target[1] - 1, target[2]) - Date.UTC(today[0], today[1] - 1, today[2])) / 86_400_000;
  if (dayDelta === 0) return "今天";
  if (dayDelta === 1) return "明天";
  return new Intl.DateTimeFormat("zh-CN", { weekday: "short", month: "long", day: "numeric", timeZone }).format(new Date(value));
}

function LogoMark() {
  return (
    <svg className="logo-mark" viewBox="0 0 40 40" role="img" aria-label="Ripple">
      <circle cx="20" cy="20" r="16.2" fill="none" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="20" cy="20" r="10.4" fill="none" stroke="currentColor" strokeWidth="1.4" />
      <path d="M8 22.5c4.7-3.7 9.8-3.7 14.1 0 3.6 3.1 7.1 3 10.5.3" fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="1.8" />
    </svg>
  );
}

const FLOW = ["观察", "分析", "建议", "确认", "执行", "验证"] as const;

function App() {
  const [mode, setMode] = useState<DataMode>("demo");
  const [snapshot, setSnapshot] = useState<WorkflowSnapshot>();
  const [nowMs, setNowMs] = useState(() => Date.now());
  const [reviewOpen, setReviewOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [dark, setDark] = useState(false);
  const [connected, setConnected] = useState(false);
  const [location, setLocation] = useState("上海");
  const [locationDraft, setLocationDraft] = useState("上海");
  const [demoFault, setDemoFault] = useState<DemoFault>("none");
  const [notice, setNotice] = useState<string>();
  const workflowRef = useRef<CalendarWorkflow | undefined>(undefined);
  const busyRef = useRef(false);
  const initializedRef = useRef(false);
  const faultRef = useRef<DemoFault>("none");
  const sourceChangeArmed = useRef(false);
  const status = snapshot?.status ?? "DETECTED";
  const sources = snapshot?.sources;
  const events = sources?.events ?? [];
  const weather = sources?.weather;
  const proposal = snapshot?.proposal;
  const action = snapshot?.action;
  const verification = snapshot?.verification;
  const run = snapshot;
  const statusMessage = snapshot?.message;
  const activeEvent = useMemo(() => {
    const events = snapshot?.sources?.events ?? [];
    return events.find((event) => event.id === snapshot?.eventId)
      ?? events.find((event) => event.id === "demo-outdoor-tennis") ?? events[0];
  }, [snapshot]);

  const lock = (): boolean => {
    if (busyRef.current) return false;
    busyRef.current = true;
    setBusy(true);
    return true;
  };
  const unlock = () => { busyRef.current = false; setBusy(false); };
  const reportError = (error: unknown) => setNotice(workflowError(error, "DEPENDENCY_UNAVAILABLE").message);

  const startWorkflow = useCallback(async (selectedMode: DataMode, city: string) => {
    const realCalendar = selectedMode === "real" ? new GoogleCalendarAdapter() : undefined;
    const capability = new CalendarWorkflowCapability(
      () => selectedMode === "demo" ? new DemoCalendarAdapter(faultRef.current) : realCalendar!,
      async () => {
        if (selectedMode === "real") return fetchOpenMeteo(city);
        const forecast = demoWeatherSnapshot();
        // Keep changed demo facts stable across preflight and verification reads.
        return sourceChangeArmed.current || faultRef.current === "source-changed" ? changeDemoWeather(forecast) : forecast;
      },
      selectedMode === "demo" ? "WRITE_REVERSIBLE" : "WRITE_SENSITIVE",
    );
    const workflow = new CalendarWorkflow(capability, (next) => { setSnapshot(next); setNowMs(Date.now()); });
    workflowRef.current = workflow;
    setReviewOpen(false);
    await workflow.detect();
  }, []);

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;
    busyRef.current = true;
    void Promise.resolve().then(async () => {
      setBusy(true);
      try { await startWorkflow("demo", "上海"); }
      finally { busyRef.current = false; setBusy(false); }
    });
  }, [startWorkflow]);

  const checkFreshness = async () => {
    if (!lock()) return;
    setNotice(undefined);
    try {
      if (snapshot?.status === "AWAITING_APPROVAL") await workflowRef.current?.refresh();
      else await startWorkflow(mode, location);
    }
    catch (error) { reportError(error); }
    finally { unlock(); }
  };

  const recalculate = async (nextLocation = location) => {
    if (!lock()) return;
    setNotice(undefined);
    try { await startWorkflow(mode, nextLocation); }
    catch (error) { reportError(error); }
    finally { unlock(); }
  };

  const selectRealMode = async () => {
    if (!lock()) return;
    setNotice(undefined);
    try {
      await connectGoogleCalendar();
      const city = locationDraft.trim() || "上海";
      setConnected(true);
      setMode("real");
      setLocation(city);
      await startWorkflow("real", city);
    } catch (error) { reportError(error); }
    finally { unlock(); }
  };

  const switchToDemoMode = async () => {
    if (!lock()) return;
    setMode("demo");
    setConnected(false);
    setNotice(undefined);
    try { await startWorkflow("demo", location); }
    finally { unlock(); }
  };

  const denyProposal = () => { workflowRef.current?.decline(); setReviewOpen(false); };
  const cancelProposal = () => { workflowRef.current?.cancel(); setReviewOpen(false); };
  const execute = async () => {
    if (!lock()) return;
    setReviewOpen(false);
    setNotice(undefined);
    try { await workflowRef.current?.approve({ confirmed: true, explicit: true }); }
    catch (error) { reportError(error); }
    finally { unlock(); }
  };

  const retrySafely = async () => {
    if (!lock()) return;
    try { await workflowRef.current?.recheck(); }
    catch (error) { reportError(error); }
    finally { unlock(); }
  };

  const resetDemo = async () => {
    if (!lock()) return;
    try {
      resetDemoCalendar();
      setDemoFault("none");
      faultRef.current = "none";
      sourceChangeArmed.current = false;
      setMode("demo");
      setConnected(false);
      setNotice(undefined);
      await startWorkflow("demo", location);
    } catch (error) { reportError(error); }
    finally { unlock(); }
  };

  const triggerExpiry = async () => {
    if (mode !== "demo" || busyRef.current) return;
    sourceChangeArmed.current = true;
    await checkFreshness();
  };

  const setFault = (fault: DemoFault) => {
    if (busyRef.current) return;
    faultRef.current = fault;
    setDemoFault(fault);
    setNotice("演示故障场景已选择；执行前仍会核对数据并要求确认。");
  };

  const displayEvent = activeEvent;
  const impact = status === "STALE" ? undefined : proposal?.impact ?? snapshot?.impact;
  const sampleFallback = mode === "demo";
  const eventTitle = displayEvent?.title ?? (sampleFallback ? "户外网球" : "未选择活动");
  const planDay = displayEvent ? relativeDay(displayEvent.start, displayEvent.timeZone) : "今天";
  const eventStart = displayEvent ? formatTime(displayEvent.start, displayEvent.timeZone) : sampleFallback ? "15:00" : "—";
  const proposedStart = proposal ? formatTime(proposal.proposedState.start, displayEvent?.timeZone) : "—";
  const weatherHour = impact
    ? weather?.hours.find((hour) => hour.start === impact.weatherStart)
    : weather?.hours.find((hour) => weatherSeverity(hour));
  const trackStart = impact ? Date.parse(impact.weatherStart) - 30 * 60_000 : weatherHour ? Date.parse(weatherHour.start) - 30 * 60_000 : 0;
  const trackEnd = impact ? Date.parse(impact.weatherEnd) + 60 * 60_000 : weatherHour ? Date.parse(weatherHour.end) + 60 * 60_000 : 0;
  const trackSpan = Math.max(1, trackEnd - trackStart);
  const rainLeft = impact ? Math.max(0, (Date.parse(impact.weatherStart) - trackStart) / trackSpan * 100) : 40;
  const rainWidth = impact ? Math.min(100 - rainLeft, (Date.parse(impact.weatherEnd) - Date.parse(impact.weatherStart)) / trackSpan * 100) : 25;
  const eventForTrack = displayEvent?.start ?? "";
  const eventLeft = eventForTrack ? Math.max(2, Math.min(98, (Date.parse(eventForTrack) - trackStart) / trackSpan * 100)) : 62;
  const nowLeft = trackSpan > 1 ? Math.max(0, Math.min(100, (nowMs - trackStart) / trackSpan * 100)) : 83;

  const flowStages: AgentStatus[] = ["DETECTED", "UNDERSTOOD", "PROPOSED", "AWAITING_APPROVAL", "EXECUTING", "VERIFYING"];
  const flowIndex = Math.max(0, ...flowStages.map((step, index) => snapshot?.history.includes(step) ? index : 0));

  return (
    <div className={`app-shell${dark ? " theme-dark" : ""}`}>
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Ripple 首页"><LogoMark /><span>ripple</span></a>
        <div className="topbar-right">
          <span className={`mode-badge ${mode === "demo" ? "mode-demo" : "mode-real"}`}>
            <span className="badge-dot" />{mode === "demo" ? "演示数据" : "实时数据"}
          </span>
          <button className="icon-button settings-trigger" onClick={() => { setLocationDraft(location); setSettingsOpen(true); }} aria-label="打开设置" title="设置">⚙</button>
        </div>
      </header>

      <main id="top" className="page-wrap">
        <section className="intro-row" aria-labelledby="page-title">
          <div className="intro-copy">
            <p className="kicker"><span className="kicker-line" /> 让每一天，都有准备</p>
            <h1 id="page-title">让计划<br className="desktop-break" /> 从容应变。</h1>
            <p className="intro-subtitle">刷新数据，核对天气与计划的变化。<br />情况有变时，决定权仍在你手中。</p>
          </div>
          <div className="intro-art" aria-hidden="true">
            <div className="ripple-orbit orbit-one" />
            <div className="ripple-orbit orbit-two" />
            <div className="ripple-orbit orbit-three" />
            <div className="orbit-core"><span>15:00</span><small>计划</small></div>
            <div className="orbit-weather"><span className="rain-glyph">∿</span><small>降雨</small></div>
            <div className="orbit-proposed"><span>12:30</span><small>空档</small></div>
          </div>
        </section>

        <section className="day-heading">
          <div>
            <p className="kicker">{planDay.toUpperCase()} <span className="today-dot" /></p>
            <h2>{status === "PROPOSED" ? "天气影响了这项安排。" : status === "COMPLETED" ? `${planDay}计划已重新安排。` : `${planDay}安排一览。`}</h2>
          </div>
          <div className="day-actions">
            <button className="text-button" onClick={() => void checkFreshness()} disabled={busy}>
              <span className={busy ? "refresh-icon spinning" : "refresh-icon"}>↻</span> 刷新数据源
            </button>
            {mode === "demo" && <button className="text-button reset-link" onClick={() => void resetDemo()} disabled={busy}>重置演示</button>}
          </div>
        </section>

        {notice && <div className="notice-line" role="status">{notice}</div>}

        <section className="workspace-grid">
          <div className="plan-column">
            <div className="impact-banner">
            <div className="impact-banner-top"><span className="impact-label">{impact ? "发现计划冲突" : "数据已同步"}</span><span className="impact-now">{weather ? `更新于 ${sourceClock(weather.fetchedAt)}` : "正在读取数据"}</span></div>
              <div className="impact-message-row">
                <span className="weather-stamp" aria-hidden="true"><span>{impact ? "降雨" : "天气"}</span><b>{impact ? "〰" : "∿"}</b></span>
                <div><h3>{status === "COMPLETED" ? `${eventTitle}已调整至天气影响前。` : status === "STALE" ? "天气条件已变化，请重新评估。" : impact ? `${severityLabel(impact.severity)}可能影响这项安排。` : "当前没有可执行的调整建议。"}</h3><p>{impact ? `${hourLabel(impact.weatherStart, displayEvent?.timeZone ?? "Asia/Shanghai")} – ${hourLabel(impact.weatherEnd, displayEvent?.timeZone ?? "Asia/Shanghai")} · 可能影响户外安排` : sources ? "显示最近读取的数据，调整建议需以当前状态重新计算。" : "正在等待可验证的数据。"}</p></div>
              </div>
              <div className="rain-track" aria-label={impact ? `${severityLabel(impact.severity)}预报：${hourLabel(impact.weatherStart, displayEvent?.timeZone ?? "Asia/Shanghai")} 至 ${hourLabel(impact.weatherEnd, displayEvent?.timeZone ?? "Asia/Shanghai")}` : "逐小时天气预报与日历活动时间"}>
                <div className="rain-track-label"><span>{weatherHour ? hourLabel(new Date(trackStart).toISOString(), displayEvent?.timeZone ?? "Asia/Shanghai") : "今天"}</span><span>{impact ? hourLabel(impact.weatherEnd, displayEvent?.timeZone ?? "Asia/Shanghai") : "天气预报"}</span><span>{weatherHour ? hourLabel(new Date(trackEnd).toISOString(), displayEvent?.timeZone ?? "Asia/Shanghai") : ""}</span></div>
                <div className="rain-track-line"><span className="rain-window" style={{ left: `${rainLeft}%`, width: `${rainWidth}%` }} /><span className="event-marker" style={{ left: `${status === "COMPLETED" && proposal ? Math.max(2, (Date.parse(proposal.proposedState.start) - trackStart) / trackSpan * 100) : eventLeft}%` }}><i />{status === "COMPLETED" ? proposedStart : eventStart}</span>{weatherHour && <span className="now-marker" style={{ left: `${nowLeft}%`, right: "auto" }} />}</div>
                <div className="track-caption"><span>{impact ? "预报时段" : "逐小时预报"}</span><span className="track-rain">{impact ? `${severityLabel(impact.severity)} · ${impact.peakPrecipitationProbability}%` : weatherHour ? "预计有雨" : weather?.hours.length ? "当前预报未见降雨" : "预报不足"}</span><span>{displayEvent ? "活动" : "无活动"}</span></div>
              </div>
              <span className="banner-corner" aria-hidden="true">↗</span>
            </div>

            <div className="causal-section">
              <div className="section-title-row"><span className="section-number">01</span><div><p className="kicker">变化关联</p><h3>{impact ? "一处天气变化，影响一项计划。" : "天气预报与日历已核对。"}</h3></div></div>
              <div className="causal-flow">
                <div className="causal-node cause-node"><span className="node-symbol rain-symbol">≈</span><div><small>天气</small><strong>{severityLabel(impact?.severity) || (weatherHour ? "预计有雨" : weather?.hours.length ? "当前预报未见降雨" : "预报不足")}</strong><em>{impact ? `${hourLabel(impact.weatherStart, displayEvent?.timeZone)}–${hourLabel(impact.weatherEnd, displayEvent?.timeZone)}` : weatherHour ? `${hourLabel(weatherHour.start, displayEvent?.timeZone)}–${hourLabel(weatherHour.end, displayEvent?.timeZone)}` : locationLabel(weather?.location) || "等待天气预报"}</em></div></div>
                <div className="causal-connector"><span>时间重叠</span><i /></div>
                <div className="causal-node event-node"><span className="node-symbol court-symbol">T</span><div><small>日历</small><strong>{eventTitle}</strong><em>{status === "COMPLETED" ? proposedStart : eventStart} · {displayEvent?.location ?? (sampleFallback ? "滨江球场" : "今天没有定时活动")}</em></div></div>
              </div>
              <div className="causal-note"><span className="note-dash" />{status === "COMPLETED" ? "调整后的活动已避开天气预报中的影响时段。" : impact ? proposal ? "Ripple 已将天气影响时段与现有活动时间进行比对。" : statusMessage : sources ? "目前没有检测到户外活动与天气影响时段重叠。" : "正在等待天气与日历数据。"}</div>
            </div>

            <div className="timeline-section">
              <div className="section-title-row"><span className="section-number">02</span><div><p className="kicker">{planDay}日程</p><h3>{status === "COMPLETED" ? "午后安排已调整" : "当前午后安排"}</h3></div></div>
              <div className="timeline-list">
                {displayEvent ? <>
                  {proposal && <div className="timeline-item"><time>{status === "COMPLETED" ? proposedStart : formatTime(proposal.proposedState.start, displayEvent.timeZone)}</time><span className={`timeline-pin ${status === "COMPLETED" ? "pin-active" : "pin-open"}`} /><div className={`timeline-content ${status === "COMPLETED" ? "timeline-confirmed" : "timeline-suggestion"}`}><small>{status === "COMPLETED" ? "日历 · 已验证" : "建议时段"}</small><strong>{eventTitle}</strong><p>{status === "COMPLETED" ? `原定时间：${formatTime(proposal.currentState.start, displayEvent.timeZone)}` : "趁降雨前安排，避开雨天"}</p></div>{status === "COMPLETED" && <span className="verified-check">✓</span>}</div>}
                  {weatherHour && <div className="timeline-item rain-item"><time>{formatTime(weatherHour.start, displayEvent.timeZone)}</time><span className="timeline-pin pin-rain" /><div className="timeline-content"><small>{sourceLabel(weather?.source) || "天气预报"}</small><strong>{severityLabel(impact?.severity) || "预计有雨"} {impact ? "开始" : "时段"}</strong><p>{impact ? `预计持续至 ${formatTime(impact.weatherEnd, displayEvent.timeZone)}` : `预计这一小时内有降水`}</p></div><span className="timeline-weather">{impact?.peakPrecipitationProbability ?? weatherHour.precipitationProbability}%</span></div>}
                  <div className="timeline-item"><time>{status === "COMPLETED" && proposal ? formatTime(proposal.currentState.start, displayEvent.timeZone) : eventStart}</time><span className={`timeline-pin ${status === "COMPLETED" ? "pin-muted" : "pin-event"}`} /><div className={`timeline-content ${status === "COMPLETED" ? "timeline-muted" : "timeline-original"}`}><small>{status === "COMPLETED" ? "原定时间 · 已释放" : "当前日历活动"}</small><strong>{eventTitle}</strong><p>{status === "COMPLETED" ? `原定时间为 ${formatTime(proposal?.currentState.start ?? displayEvent.start, displayEvent.timeZone)}` : `${displayEvent.location ?? "日历活动"} · ${Math.round((Date.parse(displayEvent.end) - Date.parse(displayEvent.start)) / 60_000)} 分钟`}</p></div></div>
                </> : <div className="timeline-empty"><span>—</span><p>今天没有找到定时活动。</p></div>}
              </div>
            </div>
          </div>

          <aside className="decision-column" aria-label="计划审核与状态">
            <div className={`proposal-panel status-${status.toLowerCase()}`}>
              <div className="proposal-topline"><span className="proposal-index">R / 01</span><span className={`state-chip state-${status.toLowerCase()}`}><span className="state-pulse" />{statusLabel(status)}</span></div>
              <p className="kicker proposal-kicker">调整建议</p>
              <h3>{status === "COMPLETED" ? "计划已回到正轨。" : status === "PARTIAL" ? "更改结果尚未确认。" : status === "CANCELLED" ? "本次更改已取消。" : status === "FAILED" ? "更改未能验证。" : status === "DECLINED" ? "已保留原计划。" : status === "STALE" ? "计划需要重新评估。" : status === "UNDERSTOOD" && !proposal ? impact ? "发现冲突，暂无可用时段。" : "当前没有调整建议。" : "将活动调整到天气影响前。"}</h3>
              {status === "COMPLETED" ? (
                <div className="time-change completed-change"><div><small>调整后时间</small><strong>{proposedStart}</strong></div><span className="change-arrow">✓</span><div><small>验证结果</small><strong className="verified-copy">已确认</strong></div></div>
              ) : status === "FAILED" || status === "PARTIAL" || status === "DECLINED" || status === "STALE" || status === "CANCELLED" ? (
                <div className="terminal-state-copy"><span className="terminal-symbol">{status === "FAILED" ? "!" : status === "DECLINED" ? "—" : "↻"}</span><p>{statusCopy(status, statusMessage)}</p></div>
              ) : proposal ? (
                <div className="time-change"><div><small>原定时间</small><strong>{eventStart}</strong></div><span className="change-arrow">→</span><div><small>建议时间</small><strong>{proposal ? proposedStart : "12:30"}</strong></div></div>
              ) : <div className="terminal-state-copy"><span className="terminal-symbol">—</span><p>{statusCopy(status, statusMessage)}</p></div>}
              {snapshot?.error && <p role="alert" className="proposal-reason">{snapshot.error.code} · {snapshot.error.retryable ? "可重试读取" : "需要重新评估"}</p>}
              {proposal && <p className="proposal-reason">{proposal.reason}</p>}
              {status === "AWAITING_APPROVAL" && (
                <div className="proposal-actions"><button className="button-secondary" onClick={denyProposal} disabled={busy}>保留原时间</button><button className="button-primary" onClick={() => setReviewOpen(true)} disabled={busy || !proposal}>查看更改 <span>↗</span></button></div>
              )}
              {status === "COMPLETED" && <div className="completion-seal"><span>✓</span><strong>已更新并验证</strong><small>日历回读时间： {sourceClock(verification?.checkedAt)}</small></div>}
              {(status === "FAILED" || status === "PARTIAL") && <div className="proposal-actions failure-actions"><button className="button-secondary" onClick={() => void recalculate()} disabled={busy}>重新计算</button><button className="button-primary" onClick={() => void retrySafely()} disabled={busy || !snapshot?.canRecheck}>检查结果 <span>↻</span></button></div>}
              {status === "DECLINED" && <div className="proposal-actions"><button className="button-secondary" onClick={() => void recalculate()} disabled={busy}>重新计算</button><button className="button-primary" onClick={() => setSettingsOpen(true)}>检查访问权限</button></div>}
              {(status === "STALE" || status === "CANCELLED") && <div className="proposal-actions"><button className="button-primary full-button" onClick={() => void recalculate()} disabled={busy}>重新计算计划 <span>↻</span></button></div>}
              {status === "DETECTED" && <div className="analyzing-line"><span className="mini-loader" />正在读取天气与日历</div>}
              {status === "EXECUTING" && <div className="progress-state"><span className="progress-line" /><span>正在更新日历</span></div>}
              {status === "VERIFYING" && <div className="progress-state verifying-state"><span className="progress-line" /><span>正在重新读取活动</span></div>}

              <div className="panel-rule" />
              <div className="source-list">
                <div className="source-row"><span className="source-glyph calendar-glyph">▦</span><div><strong>{mode === "demo" ? "演示日历" : "Google Calendar"}</strong><small>{sources ? `${events.length} 项活动 · 读取于 ${sourceClock(sources.sourceState.calendarFetchedAt)}` : "正在读取日历"}</small></div><span className="source-live">{mode === "demo" ? "演示数据" : connected ? "已连接" : "未连接"}</span></div>
                <div className="source-row"><span className="source-glyph weather-glyph">≈</span><div><strong>{sourceLabel(weather?.source ?? (mode === "demo" ? "Demo forecast" : "Open-Meteo"))}</strong><small>{locationLabel(weather?.location ?? location)} · 读取于 {sourceClock(weather?.fetchedAt)}</small></div><span className="source-live">{weather ? mode === "demo" ? "演示数据" : "实时读取" : "等待读取"}</span></div>
              </div>
              <div className="freshness-note"><span className="freshness-dot" />建议基于当前数据状态生成。</div>
            </div>

            <div className="agent-flow-panel">
              <div className="flow-header"><span className="kicker">智能体运行</span><span className="run-label">运行 / {run?.runId.slice(-4).toUpperCase() ?? "01"}</span></div>
              <div className="flow-steps">
                {FLOW.map((step, index) => {
                  const completed = snapshot?.history.includes(flowStages[index + 1]) || status === "COMPLETED";
                  const current = index === flowIndex && status !== "COMPLETED" && !["DECLINED", "STALE", "CANCELLED", "FAILED", "PARTIAL"].includes(status);
                  const failed = (status === "FAILED" || status === "PARTIAL") && index === flowIndex;
                  const denied = (status === "DECLINED" || status === "CANCELLED") && index === 3;
                  const expired = status === "STALE" && index === 2;
                  return <div className={`flow-step${completed ? " is-complete" : ""}${current ? " is-current" : ""}${failed ? " is-error" : ""}${denied ? " is-denied" : ""}${expired ? " is-expired" : ""}`} key={step}><span className="flow-marker">{completed ? "✓" : failed ? "!" : denied ? "—" : expired ? "↻" : String(index + 1).padStart(2, "0")}</span><span>{step}</span>{index < FLOW.length - 1 && <i />}</div>;
                })}
              </div>
              {action && <div className="action-evidence"><span className={action.result === "success" ? "evidence-check" : action.result === "pending" ? "evidence-pending" : "evidence-failed"}>{action.result === "success" ? "✓" : action.result === "pending" ? "·" : "!"}</span><span>{action.result === "success" ? "日历更新已验证" : action.result === "pending" ? "正在执行日历操作" : action.message ?? "日历操作失败"}</span></div>}
              {verification && <div className={`verify-evidence${verification.verified ? "" : " evidence-error"}`}><small>回读验证 · {sourceClock(verification.checkedAt)}</small><span>{verification.verified ? `预期 ${formatTime(verification.expected.start, displayEvent?.timeZone)} · 实际 ${formatTime(verification.actual?.start ?? "", displayEvent?.timeZone)}` : verification.message}</span></div>}
            </div>
          </aside>
        </section>

        <footer className="page-footer"><span>RIPPLE <i /> 日历 × 天气</span><span>数据来源清晰可见，决定权始终在你。</span><span>本地优先 · {mode === "demo" ? "演示数据" : "实时数据"}</span></footer>
      </main>

      {reviewOpen && proposal && (
        <div className="sheet-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setReviewOpen(false); }}>
          <section className="review-sheet" role="dialog" aria-modal="true" aria-labelledby="review-title">
            <div className="sheet-grabber" />
            <div className="sheet-header"><span className="kicker">应用前请确认</span><button className="icon-button close-button" onClick={() => setReviewOpen(false)} aria-label="关闭审核窗口">×</button></div>
            <h2 id="review-title">要更改这项日历活动吗？</h2>
            <p className="sheet-lede">只有在你确认后，Ripple 才会更新这项活动。</p>
            <div className="review-event-heading"><span className="review-event-mark">T</span><div><strong>{displayEvent?.title ?? proposal.impact.eventTitle}</strong><small>日历活动 · {displayEvent?.location ?? "滨江球场"}</small></div></div>
            <div className="review-time-grid"><div className="review-time-cell"><small>原定时间</small><strong>{formatTime(proposal.currentState.start, displayEvent?.timeZone)}</strong><span>{planDay} · 1 小时</span></div><div className="review-arrow">→</div><div className="review-time-cell proposed-cell"><small>建议时间</small><strong>{formatTime(proposal.proposedState.start, displayEvent?.timeZone)}</strong><span>{planDay} · 时长不变</span></div></div>
            <div className="why-block"><span className="why-rule" /><div><small>调整原因</small><p>{proposal.reason}</p></div></div>
            <div className="review-source-line"><span>已检查的数据源</span><strong>{mode === "demo" ? "演示日历" : "Google Calendar"} <i /> {sourceLabel(weather?.source ?? "Open-Meteo")}</strong></div>
            <div className="review-warning"><span>i</span><p>确认后仅会调整这项活动的时间。Ripple 会重新读取活动，验证成功后才会显示完成。</p></div>
            <div className="sheet-actions"><button className="button-secondary" onClick={cancelProposal}>取消</button><button className="button-primary approve-button" onClick={() => void execute()} disabled={busy}>确认更改 <span>→</span></button></div>
          </section>
        </div>
      )}

      {settingsOpen && (
        <div className="sheet-backdrop settings-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) setSettingsOpen(false); }}>
          <section className="settings-sheet" role="dialog" aria-modal="true" aria-labelledby="settings-title">
            <div className="sheet-grabber" />
            <div className="sheet-header"><span className="kicker">偏好设置与数据源</span><button className="icon-button close-button" onClick={() => setSettingsOpen(false)} aria-label="关闭设置">×</button></div>
            <h2 id="settings-title">连接设置</h2>
            <p className="sheet-lede">选择 Ripple 获取日程和天气预报的来源。</p>
            <div className="connection-card"><div className="connection-head"><span className="connection-symbol">▦</span><div><strong>日历</strong><small>{mode === "demo" ? "演示数据 · 仅保存在本地" : "Google Calendar · 主日历"}</small></div><span className={`connection-status ${mode === "demo" ? "" : "connected-status"}`}>{mode === "demo" ? "演示模式" : connected ? "已连接" : "就绪"}</span></div>
              {mode === "real" ? <button className="button-secondary connection-button" onClick={() => void switchToDemoMode()} disabled={busy}>切换到演示模式</button> : <button className="button-primary connection-button" onClick={() => void selectRealMode()} disabled={busy || !hasGoogleClientId()}>{hasGoogleClientId() ? "连接 Google Calendar" : "需要配置 Google"}</button>}
              {!hasGoogleClientId() && <small className="setup-hint">请在 .env 中设置 VITE_GOOGLE_CLIENT_ID。应用不会保存客户端密钥。</small>}
            </div>
            <div className="connection-card weather-connection"><div className="connection-head"><span className="connection-symbol weather-connection-symbol">≈</span><div><strong>天气</strong><small>{mode === "demo" ? "演示预报 · 可重复的场景" : "Open-Meteo · 逐小时预报"}</small></div><span className="connection-status">{mode === "demo" ? "演示" : "实时"}</span></div><label className="field-label" htmlFor="location-field">天气预报地点</label><div className="location-field-row"><input id="location-field" value={locationDraft} onChange={(event) => setLocationDraft(event.target.value)} placeholder="输入城市名称" /><button className="button-secondary" onClick={() => { const nextLocation = locationDraft.trim(); if (nextLocation) setLocation(nextLocation); setSettingsOpen(false); if (mode === "real" && nextLocation) void recalculate(nextLocation); }} disabled={busy}>保存</button></div></div>
            {mode === "demo" && <div className="demo-controls"><div className="demo-controls-head"><div><p className="kicker">演示场景</p><strong>体验边界情况</strong></div><span>仅限演示数据</span></div><div className="fault-select-wrap"><label className="field-label" htmlFor="fault-select">日历与数据源行为</label><select id="fault-select" value={demoFault} onChange={(event) => setFault(event.target.value as DemoFault)}><option value="none">标准流程 · 更新并验证</option><option value="denied">权限拒绝 · 不写入</option><option value="write-failed">日历接口失败</option><option value="verify-mismatch">更新成功返回 · 回读结果不一致</option><option value="source-changed">天气变化 · 建议过期</option></select></div><div className="demo-control-actions"><button className="text-button" onClick={() => { setSettingsOpen(false); void resetDemo(); }} disabled={busy}>重置示例活动</button><button className="text-button" onClick={() => { setSettingsOpen(false); void triggerExpiry(); }} disabled={busy}>立即改变天气</button></div></div>}
            <div className="settings-bottom-row"><button className="theme-toggle" onClick={() => setDark((value) => !value)}><span>{dark ? "☼" : "◐"}</span> {dark ? "浅色外观" : "深色外观"}</button><button className="button-secondary" onClick={() => setSettingsOpen(false)}>完成</button></div>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;

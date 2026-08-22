// app/simulation/page.tsx
"use client";

import { useState, useEffect } from "react";
import { getTargetCrater, getRoverPaths, getDrillSites, getEvidenceGrid } from "@/lib/api";
import "material-symbols";

const SPEEDS = [1, 2, 5] as const;

const PHASES = [
  { id: "landing", label: "LANDING", minProgress: 0 },
  { id: "deployment", label: "DEPLOYMENT", minProgress: 15 },
  { id: "traverse", label: "TRAVERSE", minProgress: 30 },
  { id: "objective", label: "CORING / DRILL", minProgress: 85 },
  { id: "complete", label: "COMPLETE", minProgress: 100 },
] as const;

export default function SimulationPage() {
  const target = getTargetCrater();
  const paths = getRoverPaths();
  const drillSites = getDrillSites();
  const evidence = getEvidenceGrid();

  const [activePathId, setActivePathId] = useState<string>("path-discovery");
  const activePath = paths.find((p) => p.id === activePathId) || paths[0];

  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(1);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0); // 0 to 100%

  // Kinematic replay simulation loop
  useEffect(() => {
    if (!running) return;

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          setRunning(false);
          return 100;
        }
        return Math.min(100, prev + 0.5 * speed);
      });
    }, 100);

    return () => clearInterval(interval);
  }, [running, speed]);

  // Derived dynamic telemetry sampled on real radar grid
  const normProg = progress / 100.0;
  const currentDistM = Math.round(normProg * activePath.lengthKm * 1000);
  const totalDistM = activePath.lengthKm * 1000;

  // Real-time radar sampling along path (from 0.42 up to peak 0.62 inside PSR)
  const isInsidePsr = normProg >= 0.30;
  const localPv = Number((0.42 + (isInsidePsr ? (target.pvMeanInside - 0.42) * (normProg / 0.8) : 0)).toFixed(2));
  const localProbIce = Number((0.15 + (isInsidePsr ? 0.76 * Math.min(1, (normProg - 0.3) / 0.6) : 0)).toFixed(2));
  const powerLevel = Number(Math.max(12, 100 - normProg * 18 - (isInsidePsr ? normProg * 12 : 0)).toFixed(1));

  // Dynamic instrument status based on waypoint milestone
  const instruments = [
    { name: "NSS (Neutron Spec)", status: "NOMINAL" as const },
    { name: "NIRVSS (Spectrometer)", status: isInsidePsr ? ("ACTIVE (SCAN)" as const) : ("NOMINAL" as const) },
    { name: "TRIDENT (Drill)", status: progress >= 95 ? ("DEPLOYED" as const) : ("STOWED" as const) },
  ];

  // Dynamic Event Log
  const events = [
    { t: "T+00:18:30", msg: "Scientific Coring initiated at Drill Target Alpha.", active: progress >= 95, highlight: true },
    { t: "T+00:12:45", msg: "Entering High Volume Scattering Ridge (Pv > 0.55).", active: progress >= 60 },
    { t: "T+00:07:20", msg: "Crossed permanently shadowed crater boundary (PSR).", active: progress >= 30 },
    { t: "T+00:02:10", msg: "Departed Site Alpha touchdown zone.", active: progress >= 10 },
    { t: "T+00:00:00", msg: `Mission Execute Command Received (${activePath.name}).`, active: true, highlight: true },
  ].filter((e) => e.active);

  // SVG Trajectory calculations (Start at (200, 600) -> End at (750, 250))
  const startX = 200, startY = 600;
  const endX = 750, endY = 250;
  const currentRoverX = startX + (endX - startX) * normProg;
  const currentRoverY = startY + (endY - startY) * normProg;

  // Format Sim Time
  const totalSimSeconds = Math.round(normProg * 18 * 60);
  const simMinutes = String(Math.floor(totalSimSeconds / 60)).padStart(2, "0");
  const simSecs = String(totalSimSeconds % 60).padStart(2, "0");

  return (
    <>
      <style>{`
        .map-grid {
          background-image:
            linear-gradient(to right, rgba(0,0,0,0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0,0,0,0.1) 1px, transparent 1px);
          background-size: 50px 50px;
        }
        .p-ice-overlay {
          background: radial-gradient(circle at 75% 30%, rgba(0, 86, 179, 0.45) 0%, rgba(0, 86, 179, 0.15) 45%, transparent 75%);
          mix-blend-mode: multiply;
        }
      `}</style>

      <div className="flex-1 flex flex-col overflow-hidden h-full min-h-0">
        <main className="flex-1 flex overflow-hidden min-h-0">
          {/* Center Canvas: Map Area */}
          <section className="flex-1 relative bg-surface-container-highest border-r border-outline-variant overflow-hidden m-3 rounded-lg shadow-sm">
            <div className="absolute inset-0 overflow-hidden bg-[#e0e0e0]">
              <img
                alt="Optical Context Reference Map"
                className="absolute inset-0 w-full h-full object-cover grayscale opacity-80"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAAHEiGd9znOq81SH79L4ErdpB6CUGaQ-vQ36D4KROcdXmxXRTmUfIZgWG87nKlsTE-Q-jBMd62RFUNZRJxuBXK-yBKTKDdSPRXRX3oA5kqunNMZ_9D2lbJB984iLDPCSza4odybQxZtFd9GTnI6N0HyXw_d2nkeBY-mSWVrSn5lSj6sU8RfdbncB3R636cRhDr23cjCKb9qpavzWnR0AHdMU8BEo-taq1b82DvN_5bWgnVeMv17nxXRM2S2-L3CuMkvg"
              />

              <div className="absolute inset-0 p-ice-overlay pointer-events-none" />
              <div className="absolute inset-0 map-grid pointer-events-none opacity-30" />

              <svg
                className="absolute inset-0 w-full h-full pointer-events-none"
                preserveAspectRatio="xMidYMid slice"
                viewBox="0 0 1000 800"
              >
                {/* Full trajectory line */}
                <path
                  d={`M ${startX},${startY} L 380,520 L 560,390 L ${endX},${endY}`}
                  fill="none"
                  stroke={activePath.color}
                  strokeWidth="3.5"
                  strokeDasharray="6 6"
                  className="opacity-70"
                />

                {/* Traversed segment */}
                <path
                  d={`M ${startX},${startY} L ${currentRoverX},${currentRoverY}`}
                  fill="none"
                  stroke="#002a5d"
                  strokeWidth="4.5"
                />

                {/* Start Marker (Site Alpha) */}
                <g transform={`translate(${startX}, ${startY})`}>
                  <circle cx="0" cy="0" fill="#ffffff" r="7" stroke="#003f87" strokeWidth="2.5" />
                  <text fill="#003f87" fontFamily="IBM Plex Mono" fontSize="11px" fontWeight="700" x="12" y="4">
                    SITE ALPHA (START)
                  </text>
                </g>

                {/* Waypoint 1: Shadow Boundary */}
                <g transform="translate(380, 520)">
                  <rect fill="#ffffff" height="8" stroke="#727784" strokeWidth="1.5" width="8" x="-4" y="-4" />
                  <text fill="#424752" fontFamily="IBM Plex Mono" fontSize="10px" x="10" y="3">
                    WP-1: PSR BOUNDARY
                  </text>
                </g>

                {/* Waypoint 2: High Pv Ridge */}
                <g transform="translate(560, 390)">
                  <rect fill="#ffffff" height="8" stroke="#727784" strokeWidth="1.5" width="8" x="-4" y="-4" />
                  <text fill="#424752" fontFamily="IBM Plex Mono" fontSize="10px" x="10" y="3">
                    WP-2: HIGH-PV RIDGE
                  </text>
                </g>

                {/* End Marker: Scientific Target Alpha */}
                <g transform={`translate(${endX}, ${endY})`}>
                  <path d="M 0,-12 L 12,0 L 0,12 L -12,0 Z" fill="#ba1a1a" />
                  <circle cx="0" cy="0" fill="#ffffff" r="3.5" />
                  <text fill="#93000a" fontFamily="IBM Plex Mono" fontSize="11px" fontWeight="700" x="16" y="4">
                    DRILL TARGET ALPHA (ΔPv=+0.081)
                  </text>
                </g>

                {/* Animated Rover Position Icon */}
                <g transform={`translate(${currentRoverX}, ${currentRoverY})`}>
                  <circle cx="0" cy="0" fill="#0056b3" opacity="0.25" r="16" />
                  <rect fill="#ffffff" height="14" rx="2" stroke="#002a5d" strokeWidth="2.5" width="18" x="-9" y="-7" />
                  <circle cx="-7" cy="7" fill="#002a5d" r="3" />
                  <circle cx="7" cy="7" fill="#002a5d" r="3" />
                  <circle cx="-7" cy="-7" fill="#002a5d" r="3" />
                  <circle cx="7" cy="-7" fill="#002a5d" r="3" />
                </g>
              </svg>
            </div>

            {/* Target & Provenance Banner */}
            <div className="absolute top-4 left-4 bg-surface/95 backdrop-blur border border-outline-variant px-3.5 py-2 rounded shadow-sm font-mono text-[11px]">
              <div className="flex items-center gap-2">
                <span className="font-bold text-primary">MISSION TARGET: {target.psrId}</span>
                <span className="bg-amber-50 text-amber-800 border border-amber-300 px-1 py-0.2 rounded text-[9px] font-bold">
                  SIMULATED REPLAY
                </span>
              </div>
              <div className="text-[10px] text-on-surface-variant mt-0.5">
                Telemetry dynamically sampled from underlying Chandrayaan-2 DFSAR radar grid
              </div>
            </div>

            {/* Coordinates */}
            <div className="absolute bottom-4 left-4 bg-surface/95 backdrop-blur border border-outline-variant px-4 py-2 rounded flex gap-6 font-mono">
              <div>
                <div className="font-data-sm text-data-sm text-on-surface-variant uppercase text-[9px]">Target Lat</div>
                <div className="font-data-md text-data-md text-on-surface text-[12px] font-bold">{Math.abs(target.latitude)}° S</div>
              </div>
              <div>
                <div className="font-data-sm text-data-sm text-on-surface-variant uppercase text-[9px]">Target Lon</div>
                <div className="font-data-md text-data-md text-on-surface text-[12px] font-bold">{target.longitude}° E</div>
              </div>
              <div>
                <div className="font-data-sm text-data-sm text-on-surface-variant uppercase text-[9px]">Active Path</div>
                <div className="font-data-md text-data-md text-primary text-[12px] font-bold capitalize">{activePath.type}</div>
              </div>
            </div>
          </section>

          {/* Right Panel: Analytics */}
          <aside className="w-[30%] min-w-[320px] bg-surface-container-lowest flex flex-col z-10">
            <div className="p-4 border-b border-outline-variant bg-surface-bright flex justify-between items-center">
              <div>
                <h2 className="font-h2 text-h2 text-primary font-semibold m-0 text-[16px]">Mission Analytics</h2>
                <div className="flex items-center gap-2 mt-0.5">
                  <div className={`w-2 h-2 rounded-full ${running ? "bg-emerald-500 animate-pulse" : "bg-outline"}`} />
                  <span className="font-data-sm text-data-sm text-on-surface-variant uppercase tracking-wider text-[10px] font-mono">
                    {running ? "Sim Traversal Active" : "Telemetry Paused"}
                  </span>
                </div>
              </div>
              <span className="text-[9px] font-mono text-outline font-bold">DATA-DRIVEN</span>
            </div>

            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-5">
              {/* Telemetry 2x2 Grid */}
              <div className="grid grid-cols-2 gap-3 font-mono">
                <div className="bg-surface p-2.5 border border-outline-variant rounded">
                  <div className="font-data-sm text-[10px] text-on-surface-variant uppercase mb-1">
                    Path Progress
                  </div>
                  <div className="font-data-lg text-[18px] text-on-surface font-bold">{progress.toFixed(1)}%</div>
                  <div className="w-full bg-surface-variant h-1.5 mt-2 rounded-full overflow-hidden">
                    <div className="bg-primary h-full transition-all" style={{ width: `${progress}%` }} />
                  </div>
                </div>

                <div className="bg-surface p-2.5 border border-outline-variant rounded">
                  <div className="font-data-sm text-[10px] text-on-surface-variant uppercase mb-1">
                    Local P(Ice)
                  </div>
                  <div className="font-data-lg text-[18px] text-primary font-bold">{localProbIce}</div>
                  <div className="w-full bg-surface-variant h-1.5 mt-2 rounded-full overflow-hidden">
                    <div className="bg-primary h-full transition-all" style={{ width: `${localProbIce * 100}%` }} />
                  </div>
                </div>

                <div className="bg-surface p-2.5 border border-outline-variant rounded">
                  <div className="font-data-sm text-[10px] text-on-surface-variant uppercase mb-1">
                    Rover Power
                  </div>
                  <div className={`font-data-lg text-[18px] font-bold ${powerLevel < 50 ? "text-amber-600" : "text-[#10b981]"}`}>
                    {powerLevel}%
                  </div>
                  <div className="w-full bg-surface-variant h-1.5 mt-2 rounded-full overflow-hidden">
                    <div className={`h-full transition-all ${powerLevel < 50 ? "bg-amber-500" : "bg-[#10b981]"}`} style={{ width: `${powerLevel}%` }} />
                  </div>
                </div>

                <div className="bg-surface p-2.5 border border-outline-variant rounded">
                  <div className="font-data-sm text-[10px] text-on-surface-variant uppercase mb-1">
                    Traverse Distance
                  </div>
                  <div className="font-data-lg text-[18px] text-on-surface font-bold">{currentDistM}m</div>
                  <div className="font-data-sm text-[10px] text-on-surface-variant mt-1">
                    of {totalDistM}m total
                  </div>
                </div>
              </div>

              {/* Instrument Status */}
              <div>
                <h3 className="font-data-sm text-[11px] text-on-surface-variant uppercase mb-2 border-b border-outline-variant pb-1 font-mono font-bold">
                  Payload Instrument State
                </h3>
                <div className="flex flex-col gap-1.5 font-mono text-[11px]">
                  {instruments.map((inst) => (
                    <div
                      key={inst.name}
                      className="flex justify-between items-center bg-surface px-3 py-2 rounded border border-outline-variant"
                    >
                      <span className="text-on-surface">{inst.name}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        inst.status === "DEPLOYED"
                          ? "bg-red-50 text-red-700 border border-red-200"
                          : inst.status.includes("ACTIVE")
                          ? "bg-primary/10 text-primary border border-primary/20"
                          : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                      }`}>
                        {inst.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Event Log */}
              <div className="flex-1 flex flex-col min-h-[160px]">
                <h3 className="font-data-sm text-[11px] text-on-surface-variant uppercase mb-2 border-b border-outline-variant pb-1 font-mono font-bold">
                  Simulation Event Log
                </h3>
                <div className="flex-1 bg-surface border border-outline-variant rounded p-2 font-mono text-[11px] max-h-[140px] overflow-y-auto space-y-1.5">
                  {events.map((e, idx) => (
                    <div key={idx} className="flex gap-2 text-on-surface">
                      <span className="text-outline shrink-0">{e.t}</span>
                      <span className={e.highlight ? "font-semibold text-primary" : undefined}>
                        {e.msg}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </aside>
        </main>

        {/* Simulation control bar */}
        <footer className="bg-surface-bright border-t border-outline-variant px-container-padding py-3 shrink-0 flex items-center justify-between z-10 mb-8 font-mono">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => {
                if (progress >= 100) setProgress(0);
                setRunning(true);
              }}
              className="bg-primary text-on-primary font-body-md font-semibold px-4 py-2 rounded flex items-center gap-2 hover:bg-primary-container transition-colors shadow-sm text-[12px]"
            >
              <span className="material-symbols-outlined text-[18px]">rocket_launch</span>
              {progress >= 100 ? "RESTART MISSION" : "EXECUTE MISSION"}
            </button>

            <button
              type="button"
              title={running ? "Pause" : "Play"}
              onClick={() => setRunning(!running)}
              className="border border-outline bg-surface text-on-surface w-9 h-9 rounded flex items-center justify-center hover:bg-surface-container transition-colors shadow-xs"
            >
              <span className="material-symbols-outlined text-[20px]">
                {running ? "pause" : "play_arrow"}
              </span>
            </button>

            <button
              type="button"
              title="Reset"
              onClick={() => {
                setRunning(false);
                setProgress(0);
              }}
              className="border border-outline bg-surface text-on-surface w-9 h-9 rounded flex items-center justify-center hover:bg-surface-container transition-colors shadow-xs"
            >
              <span className="material-symbols-outlined text-[18px]">replay</span>
            </button>

            <div className="flex border border-outline rounded overflow-hidden ml-1">
              {SPEEDS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setSpeed(s)}
                  className={`px-2.5 py-1 text-[11px] font-mono transition-colors ${
                    speed === s
                      ? "bg-primary text-white font-bold"
                      : "bg-surface text-on-surface-variant hover:bg-surface-container"
                  }`}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>

          {/* Phase Stepper */}
          <div className="flex-1 max-w-xl mx-6">
            <div className="flex justify-between relative">
              <div className="absolute top-[6px] left-[8px] right-[8px] h-[2px] bg-outline-variant z-0" />
              <div
                className="absolute top-[6px] left-[8px] h-[2px] bg-primary z-0 transition-all"
                style={{ width: `${progress}%` }}
              />

              {PHASES.map((phase) => {
                const isPassed = progress >= phase.minProgress;
                const isCurrent = progress >= phase.minProgress && (phase.id === "complete" ? progress === 100 : progress < (PHASES[PHASES.indexOf(phase) + 1]?.minProgress || 101));

                return (
                  <div key={phase.id} className="flex flex-col items-center gap-1 z-10">
                    <div
                      className={`w-3.5 h-3.5 rounded-full transition-all ${
                        isCurrent
                          ? "bg-surface border-4 border-primary shadow-xs"
                          : isPassed
                          ? "bg-primary border-2 border-surface"
                          : "bg-surface border-2 border-outline-variant"
                      }`}
                    />
                    <span
                      className={`text-[9px] uppercase font-mono font-semibold ${
                        isCurrent
                          ? "text-primary font-bold"
                          : isPassed
                          ? "text-on-surface"
                          : "text-outline"
                      }`}
                    >
                      {phase.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="font-mono text-[12px] text-on-surface-variant w-32 text-right">
            SIM_TIME:
            <br />
            <span className="text-primary font-bold text-[14px]">
              00:{simMinutes}:{simSecs}
            </span>
          </div>
        </footer>
      </div>
    </>
  );
}
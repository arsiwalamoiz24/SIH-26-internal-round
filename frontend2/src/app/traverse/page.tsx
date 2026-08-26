"use client";

import { useState, useEffect } from "react";
import { PRIMARY } from "@/data/prism";

export default function TraversePage() {
  const [activeWaypoint, setActiveWaypoint] = useState<number | null>(null);
  const [animProgress, setAnimProgress] = useState(0);

  // Animate path drawing on mount
  useEffect(() => {
    let frame = 0;
    const animate = () => {
      frame++;
      setAnimProgress(Math.min(frame / 120, 1)); // 2 second animation
      if (frame < 120) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, []);

  return (
    <main style={{ minHeight: "100dvh", paddingTop: "var(--nav-h)", background: "var(--void)", display: "flex", flexDirection: "column" }}>
      
      {/* Header */}
      <div style={{ padding: "40px", borderBottom: "1px solid var(--border)", background: "var(--surface)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "20px" }}>
          <div>
            <div className="label-caps" style={{ marginBottom: "8px" }}>Rover Operations</div>
            <h1 style={{ fontFamily: "var(--font-display)", fontSize: "32px", color: "var(--text-primary)", margin: 0, letterSpacing: "-0.01em" }}>
              Path Planning & Traverse
            </h1>
          </div>
          <div style={{ display: "flex", gap: "32px" }}>
            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "4px" }}>Total Distance</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "20px", color: "var(--text-primary)" }}>{PRIMARY.traverse.distance}</div>
            </div>
            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "4px" }}>Est. Time</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "20px", color: "var(--text-primary)" }}>{PRIMARY.traverse.estTime}</div>
            </div>
            <div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "4px" }}>Max Slope</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "20px", color: "var(--signal-warn)" }}>{PRIMARY.traverse.maxSlope}</div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 400px" }}>
        
        {/* Left: Map Area */}
        <section style={{ position: "relative", borderRight: "1px solid var(--border)", background: "#000", overflow: "hidden", display: "flex", alignItems: "center", justifyItems: "center" }}>
          
          <div style={{ position: "relative", width: "100%", height: "100%", minHeight: "600px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            
            {/* The Path Image serves as the base terrain */}
            <div style={{ position: "relative", width: "80%", maxWidth: "800px", aspectRatio: "1/1", border: "1px solid rgba(255,255,255,0.1)" }}>
              <img 
                src={PRIMARY.images.path} 
                alt="Traverse Map" 
                style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.8 }} 
              />
              
              {/* SVG Overlay for Waypoints & Animated Path */}
              {/* Based on the waypoints in PRIMARY data */}
              <svg 
                viewBox="0 0 1000 1000" 
                style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}
              >
                {/* Generate path string from waypoints */}
                <path
                  d={`M ${PRIMARY.traverse.waypoints.map(w => `${w.x * 10},${w.y * 10}`).join(" L ")}`}
                  fill="none"
                  stroke="var(--amber)"
                  strokeWidth="4"
                  strokeDasharray="10 5"
                  strokeDashoffset={1000 * (1 - animProgress)} // animate draw
                  style={{ transition: "stroke-dashoffset 0.1s linear" }}
                />

                {/* Waypoint dots */}
                {PRIMARY.traverse.waypoints.map((wp, i) => (
                  <g 
                    key={wp.id} 
                    style={{ pointerEvents: "auto", cursor: "pointer" }}
                    onMouseEnter={() => setActiveWaypoint(i)}
                    onMouseLeave={() => setActiveWaypoint(null)}
                  >
                    <circle 
                      cx={wp.x * 10} 
                      cy={wp.y * 10} 
                      r={activeWaypoint === i ? 12 : 8} 
                      fill={activeWaypoint === i ? "var(--amber)" : "var(--void)"}
                      stroke="var(--amber)"
                      strokeWidth="2"
                      style={{ transition: "all 0.2s ease" }}
                    />
                    <text
                      x={wp.x * 10 + 16}
                      y={wp.y * 10 + 4}
                      fill={activeWaypoint === i ? "var(--amber)" : "rgba(255,255,255,0.7)"}
                      fontSize="14"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      {wp.id}
                    </text>
                  </g>
                ))}
              </svg>

            </div>
          </div>

        </section>

        {/* Right: Waypoint Details */}
        <section style={{ background: "var(--surface)", display: "flex", flexDirection: "column" }}>
          
          <div style={{ padding: "32px 40px", borderBottom: "1px solid var(--border)" }}>
            <div className="label-caps" style={{ marginBottom: "20px" }}>Waypoint Telemetry</div>
            <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
              Hover over waypoints on the map to inspect local terrain data, hazards, and optical boulder counts at that specific navigation node.
            </p>
          </div>

          <div style={{ flex: 1, padding: "40px" }}>
            {activeWaypoint !== null ? (
              <div style={{ animation: "fade-in 0.3s ease" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "24px" }}>
                  <h2 style={{ fontFamily: "var(--font-mono)", fontSize: "24px", color: "var(--amber)", margin: 0 }}>
                    {PRIMARY.traverse.waypoints[activeWaypoint].id}
                  </h2>
                  <span className="status-pill">{PRIMARY.traverse.waypoints[activeWaypoint].type}</span>
                </div>
                
                <div style={{ display: "grid", gap: "16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", paddingBottom: "12px", borderBottom: "1px solid var(--border)" }}>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)" }}>Local Slope</span>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "14px", color: "var(--text-primary)" }}>{PRIMARY.traverse.waypoints[activeWaypoint].slope}</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", paddingBottom: "12px", borderBottom: "1px solid var(--border)" }}>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)" }}>Hazard Level</span>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "14px", color: "var(--signal-high)" }}>{PRIMARY.traverse.waypoints[activeWaypoint].hazard}</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", paddingBottom: "12px", borderBottom: "1px solid var(--border)" }}>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)" }}>Boulder Count</span>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "14px", color: "var(--text-primary)" }}>{PRIMARY.traverse.waypoints[activeWaypoint].boulders}</span>
                  </div>
                </div>

                {PRIMARY.traverse.waypoints[activeWaypoint].type === "Ice Target" && (
                  <div style={{ marginTop: "24px", padding: "16px", background: "rgba(196,162,104,0.1)", border: "1px solid rgba(196,162,104,0.3)", borderRadius: "4px" }}>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--amber)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "8px" }}>
                      Target Acquired
                    </div>
                    <div style={{ fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--text-primary)", lineHeight: 1.5 }}>
                      Primary anomalous radar signature detected at this location. Core sampling recommended.
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", opacity: 0.5 }}>
                <div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "24px", marginBottom: "12px" }}>⌖</div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--text-secondary)" }}>
                    Select Waypoint
                  </div>
                </div>
              </div>
            )}
          </div>

        </section>
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(5px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 1024px) {
          main > div:last-child {
            grid-template-columns: 1fr !important;
            grid-template-rows: 600px auto;
          }
          section:nth-child(2) {
            border-left: none !important;
          }
        }
      `}</style>
    </main>
  );
}

"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { PRIMARY, CANDIDATES, MISSION_STEPS } from "@/data/prism";
import { useIsLightTheme } from "@/hooks/useIsLightTheme";

// ── Star field canvas ────────────────────────────────────────────
function StarField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const stars = Array.from({ length: 220 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.1 + 0.2,
      opacity: Math.random() * 0.5 + 0.1,
      twinkleSpeed: Math.random() * 0.008 + 0.002,
      twinkleOffset: Math.random() * Math.PI * 2,
    }));

    let frame = 0;
    let animId: number;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const now = frame * 0.01;
      stars.forEach((s) => {
        const alpha = s.opacity * (0.6 + 0.4 * Math.sin(now * s.twinkleSpeed * 100 + s.twinkleOffset));
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(220, 215, 205, ${alpha})`;
        ctx.fill();
      });
      frame++;
      animId = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
      }}
    />
  );
}

// ── Animated coordinate reveal ───────────────────────────────────
function CoordReveal({ value, delay = 0 }: { value: string; delay?: number }) {
  const [displayed, setDisplayed] = useState("");
  const chars = "0123456789.°SEN·-";

  useEffect(() => {
    const timer = setTimeout(() => {
      let i = 0;
      const interval = setInterval(() => {
        if (i >= value.length) {
          clearInterval(interval);
          setDisplayed(value);
          return;
        }
        setDisplayed(
          value.slice(0, i) +
          chars[Math.floor(Math.random() * chars.length)] +
          value.slice(i + 1)
        );
        i++;
      }, 35);
      return () => clearInterval(interval);
    }, delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return <>{displayed || "\u00a0".repeat(value.length)}</>;
}

// ── Animated number counter ──────────────────────────────────────
function CountUp({ to, decimals = 0, duration = 1500, delay = 0 }: {
  to: number;
  decimals?: number;
  duration?: number;
  delay?: number;
}) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          const startTime = performance.now() + delay;
          const tick = (now: number) => {
            if (now < startTime) return requestAnimationFrame(tick);
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setVal(eased * to);
            if (progress < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [to, duration, delay]);

  return <span ref={ref}>{val.toFixed(decimals)}</span>;
}

// ── Polar dot map (SVG) ──────────────────────────────────────────
function PolarMiniMap() {
  // Convert lat/lon to simple polar projection for overview
  const toXY = (lat: number, lon: number, size: number) => {
    const r = ((90 + lat) / 14) * (size * 0.44); // scale to map extent
    const theta = (lon * Math.PI) / 180;
    return {
      x: size / 2 + r * Math.sin(theta),
      y: size / 2 - r * Math.cos(theta),
    };
  };

  const size = 280;
  const cx = size / 2;
  const mapRadius = size * 0.44;
  const isLight = useIsLightTheme();

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Background Image of South Pole */}
      <image
        href="/south_pole_image.jpg"
        x={cx - mapRadius * 1.1}
        y={cx - mapRadius * 1.1}
        width={mapRadius * 2.2}
        height={mapRadius * 2.2}
        opacity={isLight ? 0.55 : 0.4}
        style={{ mixBlendMode: isLight ? "multiply" : "lighten", objectFit: "cover" }}
        preserveAspectRatio="xMidYMid slice"
      />
      {/* Grid rings */}
      {[1, 2, 3, 4].map((i) => (
        <circle
          key={i}
          cx={cx}
          cy={cx}
          r={(i / 4.5) * (size * 0.44)}
          fill="none"
          stroke="var(--border)"
          strokeWidth="1"
        />
      ))}
      {/* Grid spokes */}
      {Array.from({ length: 8 }, (_, i) => {
        const angle = (i / 8) * Math.PI * 2;
        return (
          <line
            key={i}
            x1={cx}
            y1={cx}
            x2={cx + Math.sin(angle) * size * 0.44}
            y2={cx - Math.cos(angle) * size * 0.44}
            stroke="var(--border)"
            strokeWidth="1"
          />
        );
      })}
      {/* South Pole label */}
      <text x={cx} y={cx + 4} textAnchor="middle" fontSize="7" fill="var(--text-muted)" fontFamily="monospace">90°S</text>

      {/* Candidate dots */}
      {CANDIDATES.map((c) => {
        const pos = toXY(c.lat, c.lon, size);
        const isPrimary = c.isPrimary;
        return (
          <g key={c.id}>
            {isPrimary && (
              <circle cx={pos.x} cy={pos.y} r={10} fill="rgba(196,162,104,0.1)" stroke="rgba(196,162,104,0.4)" strokeWidth="1" />
            )}
            <circle
              cx={pos.x}
              cy={pos.y}
              r={isPrimary ? 4 : 2.5}
              fill={isPrimary ? "#C4A268" : "rgba(62,107,154,0.8)"}
              stroke={isPrimary ? "#E4D89A" : "rgba(90,140,190,0.5)"}
              strokeWidth={isPrimary ? 1.5 : 1}
            />
          </g>
        );
      })}

      {/* Primary label */}
      {(() => {
        const p = toXY(PRIMARY.lat, PRIMARY.lon, size);
        return (
          <text
            x={p.x + 8}
            y={p.y - 6}
            fontSize="7"
            fill="var(--amber, #C4A268)"
            fontFamily="monospace"
            fontWeight="700"
          >
            SP-840980
          </text>
        );
      })()}
    </svg>
  );
}

// ── Radar metric bar ─────────────────────────────────────────────
function RadarBar({ label, value, percentile, isAnomaly }: {
  label: string;
  value: number;
  percentile: number;
  isAnomaly?: boolean;
}) {
  const barColor = isAnomaly
    ? "var(--signal-flag)"
    : percentile > 80
      ? "var(--signal-high)"
      : "var(--blue)";

  const fill = isAnomaly ? (100 - percentile) : percentile;

  return (
    <div style={{ padding: "12px 0", borderBottom: "1px solid var(--border-subtle)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
        <span style={{ fontFamily: "var(--font-mono, monospace)", fontSize: "10px", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--text-secondary)" }}>
          {label}
        </span>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <span style={{ fontFamily: "var(--font-mono, monospace)", fontSize: "14px", color: "var(--text-primary)", fontWeight: 500 }}>
            {value.toFixed(3)}
          </span>
          <span style={{
            fontFamily: "var(--font-mono, monospace)",
            fontSize: "10px",
            color: isAnomaly ? "var(--signal-flag)" : "var(--signal-high)",
            minWidth: "70px",
            textAlign: "right",
          }}>
            {isAnomaly ? `${percentile.toFixed(1)}th pct ⚑` : `${percentile.toFixed(1)}th pct`}
          </span>
        </div>
      </div>
      <div style={{ height: "2px", background: "var(--border)", borderRadius: "1px", overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${Math.max(fill, 2)}%`,
          background: barColor,
          borderRadius: "1px",
          transition: "width 1.2s cubic-bezier(0.23, 1, 0.32, 1)",
        }} />
      </div>
    </div>
  );
}

// ── Main page ────────────────────────────────────────────────────
export default function HomePage() {
  const [heroVisible, setHeroVisible] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const sectionsRef = useRef<(HTMLElement | null)[]>([]);
  const [visibleSections, setVisibleSections] = useState<Set<number>>(new Set());

  useEffect(() => {
    const timer = setTimeout(() => setHeroVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // Lightweight scroll-Y for parallax
  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => setHeroVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const idx = parseInt(entry.target.getAttribute("data-idx") || "0");
          if (entry.isIntersecting) {
            setVisibleSections((prev) => new Set([...prev, idx]));
          }
        });
      },
      { threshold: 0.10 }  // slightly earlier trigger for more cinematic feel
    );
    sectionsRef.current.forEach((el) => {
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  const setSectionRef = (idx: number) => (el: HTMLElement | null) => {
    sectionsRef.current[idx] = el;
  };

  return (
    <main style={{ background: "var(--void)" }}>

      {/* ══════════════════════════════════════════
          HERO
          ══════════════════════════════════════════ */}
      <section
        style={{
          position: "relative",
          height: "100dvh",
          display: "flex",
          alignItems: "center",
          overflow: "hidden",
          background: "radial-gradient(ellipse 80% 60% at 50% 120%, rgba(62,107,154,0.12) 0%, transparent 70%)",
        }}
      >
        <StarField />

        {/* Subtle polar grid decorative overlay */}
        <div style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            radial-gradient(circle at 50% 50%, transparent 30%, rgba(62,107,154,0.03) 70%),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.015) 0px, transparent 1px, transparent 120px, rgba(255,255,255,0.015) 121px),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.015) 0px, transparent 1px, transparent 120px, rgba(255,255,255,0.015) 121px)
          `,
          pointerEvents: "none",
        }} />

        <div
          className="container-page"
          style={{
            position: "relative",
            zIndex: 2,
            paddingTop: "80px",
          }}
        >
          {/* PRISM wordmark — the hero centrepiece */}
          <div
            style={{
              opacity: heroVisible ? 1 : 0,
              transform: heroVisible ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 1s ease 0.3s, transform 1s ease 0.3s",
              marginBottom: "6px",
            }}
          >
            <h1 className="prism-wordmark-hero">
              PRISM
            </h1>
          </div>

          {/* Subtitle */}
          <div
            style={{
              opacity: heroVisible ? 1 : 0,
              transform: heroVisible ? "translateY(0)" : "translateY(16px)",
              transition: "opacity 0.9s ease 0.6s, transform 0.9s ease 0.6s",
              marginBottom: "40px",
            }}
          >
            <p style={{
              fontFamily: "var(--font-mono)",
              fontSize: "clamp(11px, 1.4vw, 13px)",
              letterSpacing: "0.20em",
              textTransform: "uppercase",
              color: "var(--text-muted)",
              maxWidth: "480px",
              lineHeight: 2.0,
            }}>
              Lunar South Pole · Ice Investigation
            </p>
          </div>

          {/* CTAs */}
          <div
            style={{
              opacity: heroVisible ? 1 : 0,
              transform: heroVisible ? "translateY(0)" : "translateY(12px)",
              transition: "opacity 0.8s ease 1.1s, transform 0.8s ease 1.1s",
              display: "flex",
              gap: "14px",
              flexWrap: "wrap",
            }}
          >
            <Link href="/candidates">
              <button className="btn-ghost" style={{ fontSize: "11px" }}>
                Explore Candidates →
              </button>
            </Link>
            <Link href="/evidence">
              <button className="btn-blue" style={{ fontSize: "11px" }}>
                View Ice Evidence
              </button>
            </Link>
          </div>
        </div>

        {/* Mini polar map — right side with parallax */}
        <div style={{
          position: "absolute",
          right: "clamp(24px, 6vw, 80px)",
          top: "50%",
          transform: `translateY(calc(-50% + ${scrollY * 0.12}px))`,
          opacity: heroVisible ? 0.85 : 0,
          transition: heroVisible ? "opacity 1.4s ease 1.4s" : "none",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "10px",
        }}>
          <PolarMiniMap />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "9px", letterSpacing: "0.14em", color: "var(--text-muted)", textTransform: "uppercase" }}>
            South Polar Region · 7 Candidates
          </span>
        </div>

        {/* Scroll indicator */}
        <div style={{
          position: "absolute",
          bottom: "40px",
          left: "50%",
          transform: "translateX(-50%)",
          opacity: heroVisible ? 0.8 : 0,
          transition: "opacity 1s ease 2s",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "12px",
          animation: "scroll-bounce 2s infinite ease-in-out",
        }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.2em", color: "var(--text-primary)", textTransform: "uppercase" }}>Scroll</span>
          <div style={{
            width: "2px",
            height: "24px",
            background: "var(--text-primary)",
            borderRadius: "2px",
          }} />
        </div>
      </section>

      {/* ══════════════════════════════════════════
          STORY BAR — key numbers
          ══════════════════════════════════════════ */}
      <section
        ref={setSectionRef(0)}
        data-idx="0"
        style={{
          borderTop: "1px solid var(--border)",
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
        }}
      >
        <div
          className="container-page"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "0",
          }}
        >
          {[
            { n: 336, dec: 0, label: "PSRs Screened", unit: "" },
            { n: 7, dec: 0, label: "Shortlisted Candidates", unit: "" },
            { n: 14.234, dec: 1, label: "Candidate Area", unit: " km²" },
            { n: 1742.1, dec: 0, label: "Terrain Relief", unit: " m" },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                padding: "32px 24px",
                borderRight: i < 3 ? "1px solid var(--border)" : "none",
                opacity: visibleSections.has(0) ? 1 : 0,
                transform: visibleSections.has(0) ? "translateY(0)" : "translateY(16px)",
                transition: `opacity 0.8s ease ${i * 0.12}s, transform 0.8s ease ${i * 0.12}s`,
              }}
            >
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "clamp(28px,3vw,40px)", fontWeight: 400, color: "var(--text-primary)", letterSpacing: "-0.02em", lineHeight: 1 }}>
                <CountUp to={item.n} decimals={item.dec} delay={i * 120} />
                <span style={{ fontSize: "0.55em", color: "var(--text-secondary)" }}>{item.unit}</span>
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--text-muted)", marginTop: "6px" }}>
                {item.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════
          MISSION NARRATIVE — 5 steps
          ══════════════════════════════════════════ */}
      <section
        ref={setSectionRef(1)}
        data-idx="1"
        style={{ padding: "120px 0" }}
      >
        <div className="container-page">
          <div style={{ marginBottom: "60px" }}>
            <div className="ruler" style={{ marginBottom: "24px" }}>
              <span>Mission Pipeline</span>
            </div>
            <h2 style={{
              fontFamily: "var(--font-display)",
              fontSize: "clamp(28px, 3.5vw, 44px)",
              fontWeight: 600,
              color: "var(--text-primary)",
              letterSpacing: "-0.02em",
              lineHeight: 1.15,
              maxWidth: "480px",
            }}>
              Discover. Analyze.<br />Map. Detect. Traverse.
            </h2>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "0" }}>
            {MISSION_STEPS.map((step, i) => (
              <div
                key={step.id}
                style={{
                  padding: "28px 24px",
                  borderLeft: i > 0 ? "1px solid var(--border)" : "none",
                  opacity: visibleSections.has(1) ? 1 : 0,
                  transform: visibleSections.has(1) ? "translateY(0)" : "translateY(40px)",
                  transition: `opacity 0.9s ease ${i * 0.1}s, transform 0.9s ease ${i * 0.1}s`,
                }}
              >
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.14em", color: "var(--amber)", textTransform: "uppercase", marginBottom: "16px" }}>
                  {step.label}
                </div>
                <div style={{ fontFamily: "var(--font-display)", fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "10px", lineHeight: 1.3 }}>
                  {step.headline}
                </div>
                <div style={{ fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                  {step.sub}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          PRIMARY CANDIDATE — full bleed section
          ══════════════════════════════════════════ */}
      <section
        ref={setSectionRef(2)}
        data-idx="2"
        style={{
          background: "var(--surface)",
          borderTop: "1px solid var(--border)",
        }}
      >
        <div className="container-page" style={{ padding: "80px 40px" }}>
          {/* Header */}
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: "48px",
            flexWrap: "wrap",
            gap: "20px",
          }}>
            <div
              style={{
                opacity: visibleSections.has(2) ? 1 : 0,
                transform: visibleSections.has(2) ? "translateY(0)" : "translateY(16px)",
                transition: "opacity 0.7s ease, transform 0.7s ease",
              }}
            >
              <div className="label-caps" style={{ marginBottom: "10px" }}>Primary Target</div>
              <h2 style={{
                fontFamily: "var(--font-mono)",
                fontSize: "clamp(20px, 2.5vw, 30px)",
                fontWeight: 400,
                color: "var(--text-primary)",
                letterSpacing: "0.04em",
                lineHeight: 1.1,
              }}>
                {PRIMARY.id}
              </h2>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)", marginTop: "6px" }}>
                {PRIMARY.latStr} · {PRIMARY.lonStr} · {PRIMARY.areaKm2} km²
              </div>
            </div>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <span className="status-pill">Rank 1 / 7</span>
              <span style={{
                fontFamily: "var(--font-mono)",
                fontSize: "10px",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "var(--text-secondary)",
                border: "1px solid var(--border)",
                padding: "4px 10px",
                borderRadius: "99px",
              }}>
                Score 1.00
              </span>
            </div>
          </div>

          {/* 2-column: image + metrics */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: "32px", alignItems: "start" }}>
            {/* Radar composite image */}
            <div
              style={{
                opacity: visibleSections.has(2) ? 1 : 0,
                transform: visibleSections.has(2) ? "translateX(0)" : "translateX(-32px)",
                transition: "opacity 0.9s ease, transform 0.9s ease",
              }}
            >
              <img
                src={PRIMARY.images.radar}
                alt="Chandrayaan-2 DFSAR Radar Composite — SP_840980_0797630"
                className="scientific-image"
                style={{ width: "100%", aspectRatio: "16/10", objectFit: "cover" }}
              />
              <div style={{ marginTop: "10px", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "8px" }}>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.1em" }}>
                  DFSAR L-band · {PRIMARY.acquisition.date} · {PRIMARY.acquisition.station}
                </span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.08em" }}>
                  {PRIMARY.acquisition.id.slice(0, 40)}…
                </span>
              </div>
            </div>

            {/* Physics metrics panel */}
            <div
              style={{
                opacity: visibleSections.has(2) ? 1 : 0,
                transform: visibleSections.has(2) ? "translateX(0)" : "translateX(32px)",
                transition: "opacity 0.9s ease 0.2s, transform 0.9s ease 0.2s",
              }}
            >
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.14em", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "16px" }}>
                Radar Physics Evidence
              </div>

              <RadarBar label="Pv — Volume Scatter" value={PRIMARY.radar.pv.mean} percentile={PRIMARY.radar.pv.percentile} />
              <RadarBar label="CPR — Circular Polarization" value={PRIMARY.radar.cpr.mean} percentile={PRIMARY.radar.cpr.percentile} />
              <RadarBar label="SERD — Entropy Ratio" value={PRIMARY.radar.serd.mean} percentile={PRIMARY.radar.serd.percentile} isAnomaly />
              <RadarBar label="T-Ratio — Coherence" value={PRIMARY.radar.tRatio.mean} percentile={PRIMARY.radar.tRatio.percentile} />

              <div style={{ marginTop: "20px", padding: "14px 16px", border: "1px solid var(--border)", borderRadius: "4px", background: "rgba(255,255,255,0.02)" }}>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-muted)", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "4px" }}>
                  ML Anomaly · Isolation Forest
                </div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "14px", color: "var(--text-primary)" }}>
                  Rank {PRIMARY.ml.rank} / {PRIMARY.ml.nPSRs} PSRs
                </div>
              </div>

              <div style={{ marginTop: "16px" }}>
                <Link href="/evidence">
                  <button className="btn-ghost" style={{ width: "100%", justifyContent: "center" }}>
                    Full Evidence Analysis →
                  </button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          TERRAIN & HAZARD — split section
          ══════════════════════════════════════════ */}
      <section
        ref={setSectionRef(3)}
        data-idx="3"
        style={{ padding: "0", overflow: "hidden" }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
          {/* Terrain */}
          <div style={{ position: "relative", minHeight: "480px", overflow: "hidden" }}>
            <img
              src={PRIMARY.images.terrain}
              alt="LOLA DEM Terrain Analysis — Slope, Roughness, Illumination"
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                position: "absolute",
                inset: 0,
                filter: "brightness(0.7)",
              }}
            />
            <div style={{
              position: "absolute",
              inset: 0,
              background: "linear-gradient(to right, rgba(6,8,13,0) 0%, rgba(6,8,13,0.1) 100%)",
            }} />
            <div
              style={{
                position: "relative",
                padding: "40px",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "flex-end",
                opacity: visibleSections.has(3) ? 1 : 0,
                transform: visibleSections.has(3) ? "translateY(0)" : "translateY(40px)",
                transition: "opacity 0.8s ease, transform 0.8s ease",
              }}
            >
              <div className="label-caps" style={{ marginBottom: "10px" }}>03 — Terrain</div>
              <h3 style={{ fontFamily: "var(--font-display)", fontSize: "24px", fontWeight: 600, color: "#fff", marginBottom: "12px", lineHeight: 1.2 }}>
                20 m/px LOLA DEM
              </h3>
              <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
                {[
                  { v: "22.1°", l: "PSR Mean Slope" },
                  { v: "6.29 m", l: "TRI Roughness" },
                  { v: "1742 m", l: "Relief" },
                ].map((d) => (
                  <div key={d.l}>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "18px", color: "#fff", fontWeight: 400 }}>{d.v}</div>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", letterSpacing: "0.12em", color: "rgba(255,255,255,0.5)", textTransform: "uppercase" }}>{d.l}</div>
                  </div>
                ))}
              </div>
              <Link href="/terrain" style={{ marginTop: "20px" }}>
                <button className="btn-ghost" style={{ background: "rgba(0,0,0,0.4)" }}>
                  Explore Terrain →
                </button>
              </Link>
            </div>
          </div>

          {/* Hazard map */}
          <div style={{ position: "relative", minHeight: "480px", overflow: "hidden" }}>
            <img
              src={PRIMARY.images.hazard}
              alt="Hazard Classification Map — SP_840980_0797630"
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                position: "absolute",
                inset: 0,
                filter: "brightness(0.75) saturate(0.9)",
              }}
            />
            <div style={{
              position: "absolute",
              inset: 0,
              background: "linear-gradient(to left, rgba(6,8,13,0) 0%, rgba(6,8,13,0.1) 100%)",
            }} />
            <div
              style={{
                position: "relative",
                padding: "40px",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                justifyContent: "flex-end",
                opacity: visibleSections.has(3) ? 1 : 0,
                transform: visibleSections.has(3) ? "translateY(0)" : "translateY(40px)",
                transition: "opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s",
              }}
            >
              <div className="label-caps" style={{ marginBottom: "10px" }}>04 — Hazard Intelligence</div>
              <h3 style={{ fontFamily: "var(--font-display)", fontSize: "24px", fontWeight: 600, color: "#fff", marginBottom: "12px", lineHeight: 1.2 }}>
                Hazard Classification
              </h3>
              <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
                {[
                  { v: "78.6%", l: "PSR Hazard &gt;20°", color: "var(--signal-flag)" },
                  { v: "10.5%", l: "Approach Hazard", color: "var(--signal-high)" },
                  { v: "4.3%", l: "Critical Zone", color: "var(--signal-warn)" },
                ].map((d) => (
                  <div key={d.l}>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "18px", color: d.color, fontWeight: 400 }} dangerouslySetInnerHTML={{ __html: d.v }} />
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", letterSpacing: "0.12em", color: "rgba(255,255,255,0.5)", textTransform: "uppercase" }} dangerouslySetInnerHTML={{ __html: d.l }} />
                  </div>
                ))}
              </div>
              <Link href="/terrain" style={{ marginTop: "20px" }}>
                <button className="btn-ghost" style={{ background: "rgba(0,0,0,0.4)" }}>
                  View Hazard Map →
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          BOULDER DETECTION
          ══════════════════════════════════════════ */}
      <section
        ref={setSectionRef(4)}
        data-idx="4"
        style={{
          padding: "80px 0",
          background: "var(--void)",
          borderTop: "1px solid var(--border)",
        }}
      >
        <div className="container-page">
          <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: "60px", alignItems: "center" }}>
            <div
              style={{
                opacity: visibleSections.has(4) ? 1 : 0,
                transform: visibleSections.has(4) ? "translateX(0)" : "translateX(-40px)",
                transition: "opacity 0.9s ease, transform 0.9s ease",
              }}
            >
              <div className="label-caps" style={{ marginBottom: "14px" }}>04 — Optical Analysis</div>
              <h2 style={{
                fontFamily: "var(--font-display)",
                fontSize: "clamp(24px, 2.8vw, 36px)",
                fontWeight: 600,
                color: "var(--text-primary)",
                letterSpacing: "-0.02em",
                lineHeight: 1.2,
                marginBottom: "20px",
              }}>
                YOLOv8 Boulder Detection
              </h2>
              <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.7, marginBottom: "24px" }}>
                NASA ShadowCam imagery processed with Zero-DCE low-light enhancement,
                then analyzed by a YOLOv8n segmentation model trained on BoulderNet data
                to identify surface hazards for rover path planning.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "28px" }}>
                {[
                  "ShadowCam imagery — permanently shadowed crater interior",
                  "Zero-DCE enhancement for low-light feature extraction",
                  "YOLOv8n segmentation — boulder boundary detection",
                ].map((item, i) => (
                  <div key={i} style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
                    <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--amber)", marginTop: "3px" }}>→</span>
                    <span style={{ fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5 }}>{item}</span>
                  </div>
                ))}
              </div>
              <Link href="/traverse">
                <button className="btn-ghost">View Traverse Plan →</button>
              </Link>
            </div>

            {/* Image comparison */}
            <div
              style={{
                opacity: visibleSections.has(4) ? 1 : 0,
                transform: visibleSections.has(4) ? "translateX(0)" : "translateX(40px)",
                transition: "opacity 0.9s ease 0.15s, transform 0.9s ease 0.15s",
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "12px",
              }}
            >
              {[
                { src: PRIMARY.images.shadowcam, label: "ShadowCam Raw" },
                { src: PRIMARY.images.boulderDetection, label: "YOLOv8 Detection" },
              ].map((img) => (
                <div key={img.label}>
                  <img
                    src={img.src}
                    alt={img.label}
                    className="scientific-image"
                    style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover" }}
                  />
                  <div style={{ marginTop: "8px", fontFamily: "var(--font-mono)", fontSize: "9px", letterSpacing: "0.1em", color: "var(--text-muted)", textTransform: "uppercase" }}>
                    {img.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          FOOTER CTA
          ══════════════════════════════════════════ */}
      <section
        ref={setSectionRef(5)}
        data-idx="5"
        style={{
          padding: "80px 0",
          borderTop: "1px solid var(--border)",
          background: "var(--surface)",
        }}
      >
        <div className="container-page" style={{ textAlign: "center" }}>
          <div
            style={{
              opacity: visibleSections.has(5) ? 1 : 0,
              transform: visibleSections.has(5) ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.8s ease, transform 0.8s ease",
            }}
          >
            <div className="label-caps" style={{ marginBottom: "20px", display: "flex", justifyContent: "center" }}>
              <span>Begin Investigation</span>
            </div>
            <h2 style={{
              fontFamily: "var(--font-display)",
              fontSize: "clamp(32px, 4vw, 56px)",
              fontWeight: 600,
              letterSpacing: "-0.03em",
              color: "var(--text-primary)",
              marginBottom: "40px",
              lineHeight: 1.1,
            }}>
              Seven candidates.<br />One mission.
            </h2>
            <div style={{ display: "flex", gap: "14px", justifyContent: "center", flexWrap: "wrap" }}>
              <Link href="/candidates">
                <button className="btn-ghost">Explore All Candidates →</button>
              </Link>
              <Link href="/terrain">
                <button className="btn-blue">Terrain & Hazards</button>
              </Link>
              <Link href="/traverse">
                <button className="btn-ghost">Rover Traverse</button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid var(--border)",
        padding: "24px 40px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "12px",
        background: "var(--void)",
      }}>
        <span className="prism-wordmark" style={{ fontSize: "16px" }}>PRISM</span>
        <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.08em" }}>
            Chandrayaan-2 DFSAR · LOLA 20m DEM · NASA ShadowCam
          </span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.08em" }}>
            {PRIMARY.acquisition.date}
          </span>
        </div>
      </footer>

      <style>{`
        @keyframes pulse-down {
          0%, 100% { opacity: 0.4; transform: scaleY(1); }
          50% { opacity: 0.8; transform: scaleY(1.1); }
        }

        @keyframes scroll-bounce {
          0%, 100% { transform: translate(-50%, 0); }
          50% { transform: translate(-50%, 10px); }
        }

        @media (max-width: 900px) {
          section > div[style*="grid-template-columns: 1fr 380px"] {
            grid-template-columns: 1fr !important;
          }
          section > div[style*="grid-template-columns: repeat(4"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          section > div[style*="grid-template-columns: repeat(5"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }
          section > div[style*="grid-template-columns: 360px 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }

        @media (max-width: 600px) {
          section > div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
          .prism-wordmark-hero { font-size: 64px !important; }
        }
      `}</style>
    </main>
  );
}

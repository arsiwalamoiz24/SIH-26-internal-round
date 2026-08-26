"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

const NAV_LINKS = [
  { href: "/",           label: "Overview" },
  { href: "/candidates", label: "Candidates" },
  { href: "/evidence",   label: "Evidence" },
  { href: "/terrain",    label: "Terrain" },
  { href: "/traverse",   label: "Traverse" },
];

export default function Nav() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [hoveredLink, setHoveredLink] = useState<string | null>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    
    // Check initial theme from data-theme if present
    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    if (isLight) setTheme("light");
    
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next === "light" ? "light" : "");
  };

  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        height: "var(--nav-h, 60px)",
        display: "flex",
        alignItems: "center",
        padding: "0 32px",
        transition: "background 0.3s ease, border-color 0.3s ease",
        background: scrolled
          ? "var(--surface)"
          : "transparent",
        backdropFilter: scrolled ? "blur(12px)" : "none",
        borderBottom: scrolled
          ? "1px solid var(--border)"
          : "1px solid transparent",
      }}
    >
      {/* Wordmark */}
      <Link href="/" style={{ textDecoration: "none", marginRight: "auto" }}>
        <span className="prism-wordmark-nav">PRISM</span>
      </Link>

      {/* Desktop nav links - Spotlight Animated Tabs */}
      <nav
        style={{
          display: "flex",
          gap: "8px",
          alignItems: "center",
          position: "relative",
        }}
        className="hidden-mobile"
        onMouseLeave={() => setHoveredLink(null)}
      >
        {NAV_LINKS.map((link) => {
          const isActive = pathname === link.href;
          const isHovered = hoveredLink === link.href;
          
          return (
            <Link
              key={link.href}
              href={link.href}
              onMouseEnter={() => setHoveredLink(link.href)}
              style={{
                position: "relative",
                padding: "6px 16px",
                borderRadius: "99px",
                fontFamily: "var(--font-mono, monospace)",
                fontSize: "11px",
                fontWeight: 600,
                letterSpacing: "0.10em",
                textTransform: "uppercase",
                color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                textDecoration: "none",
                transition: "color 0.2s ease",
                zIndex: 1,
              }}
            >
              {isHovered && !isActive && (
                <motion.div
                  layoutId="nav-hover-pill"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2, ease: "easeOut" }}
                  style={{
                    position: "absolute",
                    inset: 0,
                    background: "rgba(120, 120, 120, 0.1)",
                    borderRadius: "99px",
                    zIndex: -1,
                  }}
                />
              )}
              {isActive && (
                <motion.div
                  layoutId="nav-active-pill"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  style={{
                    position: "absolute",
                    inset: 0,
                    background: "var(--text-primary)",
                    borderRadius: "99px",
                    zIndex: -1,
                  }}
                />
              )}
              <span style={{ position: "relative", zIndex: 2, color: isActive ? "var(--void)" : (isHovered ? "var(--text-primary)" : "var(--text-secondary)") }}>
                {link.label}
              </span>
            </Link>
          );
        })}

        <div style={{ width: "1px", height: "16px", background: "var(--border)", margin: "0 8px" }} />

        {/* Theme toggle — subtle */}
        <button
          onClick={toggleTheme}
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          style={{
            background: "none",
            border: "1px solid transparent",
            borderRadius: "4px",
            padding: "5px 8px",
            cursor: "pointer",
            color: "var(--text-muted)",
            fontSize: "12px",
            lineHeight: 1,
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget).style.color = "var(--text-primary)";
            (e.currentTarget).style.background = "var(--border-subtle)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget).style.color = "var(--text-muted)";
            (e.currentTarget).style.background = "transparent";
          }}
        >
          {theme === "dark" ? "◑" : "○"}
        </button>
      </nav>

      {/* Mobile hamburger */}
      <button
        className="show-mobile"
        onClick={() => setMobileOpen(!mobileOpen)}
        style={{
          background: "none",
          border: "1px solid var(--border)",
          borderRadius: "4px",
          padding: "6px 10px",
          cursor: "pointer",
          color: "var(--text-secondary)",
          fontSize: "16px",
          display: "none",
        }}
      >
        {mobileOpen ? "✕" : "≡"}
      </button>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            style={{
              position: "absolute",
              top: "var(--nav-h, 60px)",
              left: 0,
              right: 0,
              background: "var(--surface)",
              borderBottom: "1px solid var(--border)",
              padding: "20px 32px",
              display: "flex",
              flexDirection: "column",
              gap: "16px",
              zIndex: 99,
            }}
          >
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                style={{
                  fontFamily: "var(--font-mono, monospace)",
                  fontSize: "13px",
                  fontWeight: 700,
                  letterSpacing: "0.10em",
                  textTransform: "uppercase",
                  color: pathname === link.href ? "var(--amber)" : "var(--text-secondary)",
                }}
              >
                {link.label}
              </Link>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @media (max-width: 768px) {
          .hidden-mobile { display: none !important; }
          .show-mobile { display: block !important; }
        }
      `}</style>
    </header>
  );
}

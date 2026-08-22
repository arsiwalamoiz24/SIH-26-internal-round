"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Settings, HelpCircle, UserCircle } from "lucide-react";
import clsx from "clsx";

const navLinks = [
  { href: "/", label: "Overview" },
  { href: "/candidate/SP_840980_0797630", label: "Candidate Report" },
  { href: "/ice-detection", label: "Ice Detection" },
  { href: "/surface-hazards", label: "Surface Map" },
  { href: "/simulation", label: "Simulation" },
  { href: "/landing-site", label: "Landing Site" },
  { href: "/rover-traverse", label: "Hazard & Traverse" },
];

export function TopNav() {
  const pathname = usePathname();

  return (
    <nav className="w-full z-50 flex justify-between items-center px-container-padding h-12 bg-surface tech-border-b shrink-0">
      <div className="flex items-center gap-6">
        <div className="text-[16px] font-h2 font-black tracking-tight text-primary">
          PRISM MISSION CONTROL
        </div>
        <div className="hidden md:flex gap-1 h-12">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={clsx(
                  "px-3 font-body-sm text-body-sm cursor-pointer hover:bg-surface-container-high transition-colors h-full flex items-center border-b-2",
                  isActive
                    ? "text-primary border-primary font-bold pb-1"
                    : "text-on-surface-variant border-transparent"
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
      <div className="flex items-center gap-4">
        <Settings className="text-outline cursor-pointer hover:text-on-surface w-5 h-5" />
        <HelpCircle className="text-outline cursor-pointer hover:text-on-surface w-5 h-5" />
        <UserCircle className="text-outline cursor-pointer hover:text-on-surface w-5 h-5" />
      </div>
    </nav>
  );
}

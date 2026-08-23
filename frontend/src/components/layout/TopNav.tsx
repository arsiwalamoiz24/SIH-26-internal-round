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
    <nav className="w-full z-50 flex justify-between items-center px-6 h-[52px] bg-[#FAF8F5] border-b border-[#CCC8C1] shrink-0">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          {/* Lunar crescent icon */}
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="text-[#2E6499]">
            <path d="M10 2a8 8 0 0 0 0 16 6 6 0 0 1 0-16z" fill="currentColor" opacity="0.85"/>
          </svg>
          <span className="text-[15px] font-semibold tracking-tight text-[#18150F]">
            PRISM
          </span>
          <span className="text-[13px] font-normal text-[#8A8680] ml-0.5 tracking-normal">
            Mission Dashboard
          </span>
        </div>

        <div className="hidden md:flex gap-0.5 h-[52px] items-stretch">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={clsx(
                  "px-3.5 text-[13px] cursor-pointer transition-colors h-full flex items-center border-b-2 rounded-none",
                  isActive
                    ? "text-[#2E6499] border-[#2E6499] font-semibold"
                    : "text-[#5E5A54] border-transparent hover:text-[#18150F] hover:bg-[#F0EDE7]"
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>

      <div className="flex items-center gap-3.5">
        <Settings className="text-[#8A8680] cursor-pointer hover:text-[#18150F] w-[18px] h-[18px] transition-colors" />
        <HelpCircle className="text-[#8A8680] cursor-pointer hover:text-[#18150F] w-[18px] h-[18px] transition-colors" />
        <UserCircle className="text-[#8A8680] cursor-pointer hover:text-[#18150F] w-[18px] h-[18px] transition-colors" />
      </div>
    </nav>
  );
}

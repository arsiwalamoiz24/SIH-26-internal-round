export function Footer() {
  return (
    <footer className="fixed bottom-0 left-0 w-full z-50 flex justify-between bg-[#d3e4fe] items-center px-container-padding h-8 border-t border-outline-variant shrink-0">
      <div className="font-data-sm text-on-surface-variant">
        © 2026 PRISM MISSION CONTROL | BUILD: 08.22.4-BETA
      </div>
      <div className="flex gap-6">
        <span className="text-on-surface-variant font-data-sm cursor-default">
          System Health: Nominal
        </span>
        <span className="text-on-surface-variant font-data-sm cursor-default">
          Network: 42ms
        </span>
        <span className="text-on-surface-variant font-data-sm cursor-default">
          Uptime: 99.98%
        </span>
      </div>
    </footer>
  );
}

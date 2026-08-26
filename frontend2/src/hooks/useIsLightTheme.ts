"use client";

import { useEffect, useState } from "react";

// Tracks document.documentElement's data-theme attribute (set by Nav.tsx's
// toggle) so components can react live to a light/dark switch.
export function useIsLightTheme() {
  const [isLight, setIsLight] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    const update = () => setIsLight(root.getAttribute("data-theme") === "light");
    update();

    const observer = new MutationObserver(update);
    observer.observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);

  return isLight;
}

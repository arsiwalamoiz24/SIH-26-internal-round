"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { getEvidenceGrid, getRoverPaths, getWideTerrainGrid } from "@/lib/api";

function bilinearSample(grid: number[][], row: number, col: number): number {
  const n = grid.length;
  const r0 = Math.max(0, Math.min(n - 1, Math.floor(row)));
  const r1 = Math.max(0, Math.min(n - 1, r0 + 1));
  const c0 = Math.max(0, Math.min(n - 1, Math.floor(col)));
  const c1 = Math.max(0, Math.min(n - 1, c0 + 1));
  const fr = row - r0;
  const fc = col - c0;
  const v00 = grid[r0][c0];
  const v01 = grid[r0][c1];
  const v10 = grid[r1][c0];
  const v11 = grid[r1][c1];
  return v00 * (1 - fr) * (1 - fc) + v01 * (1 - fr) * fc + v10 * fr * (1 - fc) + v11 * fr * fc;
}

interface TerrainVisualizerProps {
  activePathId?: string;
  showBayesian?: boolean;
}

export function TerrainVisualizer({ activePathId = "path-discovery", showBayesian = true }: TerrainVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 2000);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xfff4e0, 1.15);
    dirLight.position.set(20, 30, 12);
    scene.add(dirLight);
    const fillLight = new THREE.DirectionalLight(0xcfe0ff, 0.5);
    fillLight.position.set(-15, 10, -10);
    scene.add(fillLight);

    // Real LOLA DEM elevation -- wide-context window (18km, real geography well
    // beyond the radar/ML coverage) drives the terrain mesh height everywhere.
    // Real per-pixel Pv/CPR/ice-likelihood evidence (6.6km, narrower real window)
    // is blended in as color ONLY within its own true covered footprint below --
    // it is not stretched to cover ground it was never measured over.
    const wide = getWideTerrainGrid();
    const evidence = getEvidenceGrid();
    const N = wide.gridSize; // 120
    const segs = N - 1;

    // Same real-meters-to-scene-units scale as the original narrow window used,
    // so existing rover path coordinates (already hand-tuned to that scale)
    // remain valid without modification.
    const NARROW_WINDOW_M = evidence.windowHalfM * 2; // 6600
    const NARROW_PLANE_SIZE = 28;
    const METERS_TO_UNITS = NARROW_PLANE_SIZE / NARROW_WINDOW_M;
    const WIDE_WINDOW_M = wide.windowHalfM * 2; // 18000
    const PLANE_SIZE = WIDE_WINDOW_M * METERS_TO_UNITS;

    const geo = new THREE.PlaneGeometry(PLANE_SIZE, PLANE_SIZE, segs, segs);
    geo.rotateX(-Math.PI / 2);

    const positions = geo.attributes.position.array;
    const colors: number[] = [];

    // Real elevation range across the wide window drives a hypsometric-style
    // terrain palette (deep shadowed floor -> lit rim), instead of a flat
    // data-viz color. This is the DEFAULT color everywhere on the mesh.
    const wideFlat = wide.elevationGridRelativeM.flat();
    const elevMin = Math.min(...wideFlat);
    const elevMax = Math.max(...wideFlat);
    const elevRange = Math.max(1, elevMax - elevMin);

    const terrainLow = new THREE.Color(0x53565f);   // deep crater floor, shadowed regolith
    const terrainMid = new THREE.Color(0xa8a08c);   // mid-slope regolith
    const terrainHigh = new THREE.Color(0xe8dcbe);  // sunlit rim / ejecta

    const iceColor = new THREE.Color(0x5eb6ff); // real ice-likelihood tint

    const halfNarrowM = evidence.windowHalfM; // 3300

    for (let r = 0; r < N; r++) {
      for (let c = 0; c < N; c++) {
        const vertIndex = r * N + c;
        const elevM = wide.elevationGridRelativeM[r]?.[c] ?? 0;
        const h = elevM * METERS_TO_UNITS;
        positions[vertIndex * 3 + 1] = h;

        // Real-world offset (meters) of this vertex from the candidate center --
        // both grids share the exact same real center, computed independently.
        const dx = ((c / segs) - 0.5) * WIDE_WINDOW_M;
        const dy = ((r / segs) - 0.5) * WIDE_WINDOW_M;

        // Base color: real elevation-based hypsometric shading
        const t = (elevM - elevMin) / elevRange;
        const base = t < 0.5
          ? terrainLow.clone().lerp(terrainMid, t / 0.5)
          : terrainMid.clone().lerp(terrainHigh, (t - 0.5) / 0.5);

        let col = base;
        if (Math.abs(dx) <= halfNarrowM && Math.abs(dy) <= halfNarrowM && showBayesian) {
          // Within the real per-pixel evidence window: blend in the real
          // ice-likelihood value (higher probability = more blue tint).
          const narrowN = evidence.probIceGrid.length;
          const fc = ((dx / halfNarrowM + 1) / 2) * (narrowN - 1);
          const fr = ((dy / halfNarrowM + 1) / 2) * (narrowN - 1);
          const probVal = bilinearSample(evidence.probIceGrid, fr, fc);
          col = base.clone().lerp(iceColor, Math.min(0.9, probVal * 0.85));
        } else if (Math.abs(dx) <= halfNarrowM && Math.abs(dy) <= halfNarrowM && !showBayesian) {
          const narrowN = evidence.cprGrid.length;
          const fc = ((dx / halfNarrowM + 1) / 2) * (narrowN - 1);
          const fr = ((dy / halfNarrowM + 1) / 2) * (narrowN - 1);
          const cprVal = bilinearSample(evidence.cprGrid, fr, fc);
          if (cprVal > 1.0) col = base.clone().lerp(iceColor, 0.85);
        }
        colors.push(col.r, col.g, col.b);
      }
    }

    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geo.computeVertexNormals();

    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      flatShading: false,
      roughness: 0.92,
      metalness: 0.02,
    });
    const terrain = new THREE.Mesh(geo, mat);
    scene.add(terrain);

    // Thin outline marking the true real-evidence footprint, so it reads as
    // "this is where the real per-pixel data actually is" rather than an
    // unexplained soft-edged blend.
    const evidenceOutlinePts: THREE.Vector3[] = [];
    const halfNarrowUnits = halfNarrowM * METERS_TO_UNITS;
    [[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]].forEach(([sx, sz]) => {
      evidenceOutlinePts.push(new THREE.Vector3(sx * halfNarrowUnits, 0.02, sz * halfNarrowUnits));
    });
    const outlineGeo = new THREE.BufferGeometry().setFromPoints(evidenceOutlinePts);
    const outlineMat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.35 });
    const outlineLine = new THREE.Line(outlineGeo, outlineMat);
    scene.add(outlineLine);

    // Camera: pulled back to frame the full wide-context terrain
    const camDist = PLANE_SIZE * 0.85;
    camera.position.set(0, camDist * 0.62, camDist * 0.72);
    camera.lookAt(0, -camDist * 0.05, 0);

    // Sample real elevation (wide grid) to anchor rover paths to the actual
    // terrain surface instead of a fixed/arbitrary height.
    const sampleElevationUnits = (sx: number, sz: number): number => {
      const dxM = sx / METERS_TO_UNITS;
      const dyM = sz / METERS_TO_UNITS;
      const fc = ((dxM / (WIDE_WINDOW_M / 2) + 1) / 2) * segs;
      const fr = ((dyM / (WIDE_WINDOW_M / 2) + 1) / 2) * segs;
      return bilinearSample(wide.elevationGridRelativeM, fr, fc) * METERS_TO_UNITS;
    };

    // Render Pareto Rover Trajectories, hugging the real terrain surface
    const pathsData = getRoverPaths();
    const pathMeshes: THREE.Line[] = [];

    pathsData.forEach(pData => {
      const isSelected = activePathId === pData.id;
      const points = pData.points.map(p => {
        const terrainY = sampleElevationUnits(p[0], p[2]);
        return new THREE.Vector3(p[0], terrainY + 0.18, p[2]);
      });
      const curve = new THREE.CatmullRomCurve3(points);
      const pathGeo = new THREE.BufferGeometry().setFromPoints(curve.getPoints(60));
      const pathMat = new THREE.LineBasicMaterial({
        color: new THREE.Color(pData.color),
        linewidth: isSelected ? 3 : 1.5,
        transparent: !isSelected,
        opacity: isSelected ? 1 : 0.55,
      });
      const pathLine = new THREE.Line(pathGeo, pathMat);
      scene.add(pathLine);
      pathMeshes.push(pathLine);
    });

    let animationFrameId: number;
    const ROT_SPEED = 0.0004;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      terrain.rotation.y += ROT_SPEED;
      outlineLine.rotation.y += ROT_SPEED;
      pathMeshes.forEach(pm => pm.rotation.y += ROT_SPEED);
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      renderer.dispose();
      geo.dispose();
      mat.dispose();
      outlineGeo.dispose();
      outlineMat.dispose();
    };
  }, [activePathId, showBayesian]);

  return <div ref={containerRef} className="absolute inset-0 z-0 bg-[#e5e7eb]" />;
}

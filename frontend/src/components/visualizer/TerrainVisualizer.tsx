"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { getEvidenceGrid, getRoverPaths } from "@/lib/api";

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
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 16, 26);
    camera.lookAt(0, -1, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(8, 15, 10);
    scene.add(dirLight);

    // Load real radar evidence grid (48x48)
    const evidence = getEvidenceGrid();
    const [rows, cols] = evidence.dimensions;
    const segsX = cols - 1;
    const segsZ = rows - 1;

    const geo = new THREE.PlaneGeometry(28, 28, segsX, segsZ);
    geo.rotateX(-Math.PI / 2);

    const positions = geo.attributes.position.array;
    const colors: number[] = [];
    
    // Stepped single-hue color palette for Probabilistic Ice Likelihood
    const colorScale = [
      new THREE.Color(0xd1d5db), // 0.0 - 0.2: Regolith background
      new THREE.Color(0x93c5fd), // 0.2 - 0.4: Low probability
      new THREE.Color(0x60a5fa), // 0.4 - 0.6: Moderate likelihood
      new THREE.Color(0x3b82f6), // 0.6 - 0.8: High likelihood
      new THREE.Color(0x2563eb), // 0.8 - 0.9: Strong signature
      new THREE.Color(0x1d4ed8)  // 0.9 - 1.0: Peak anomaly
    ];

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const vertIndex = r * cols + c;
        const pvVal = evidence.pvGrid[r]?.[c] ?? 0.25;
        const cprVal = evidence.cprGrid[r]?.[c] ?? 0.23;
        const probVal = evidence.probIceGrid[r]?.[c] ?? 0.10;
        const isInsidePsr = evidence.psrMaskGrid[r]?.[c] ?? false;

        // Radar Evidence Surface height: base PSR depression + volume scattering anomaly ridge
        let h = isInsidePsr ? -2.2 + (pvVal - 0.4) * 3.5 : 0.4 + (pvVal - 0.4) * 1.5;
        positions[vertIndex * 3 + 1] = h;

        if (showBayesian) {
          // Continuous stepped Probabilistic Ice Likelihood
          const step = Math.min(5, Math.max(0, Math.floor(probVal * 6)));
          const col = colorScale[step] || colorScale[0];
          colors.push(col.r, col.g, col.b);
        } else {
          // Binary CPR mode (CPR > 1.0 literature threshold)
          const isHighCpr = cprVal > 1.0;
          const col = isHighCpr ? new THREE.Color(0x1d4ed8) : new THREE.Color(0xd1d5db);
          colors.push(col.r, col.g, col.b);
        }
      }
    }
    
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geo.computeVertexNormals();
    
    const mat = new THREE.MeshPhongMaterial({ 
      vertexColors: true, 
      flatShading: true,
      shininess: 15
    });
    const terrain = new THREE.Mesh(geo, mat);
    scene.add(terrain);

    // Render Pareto Rover Trajectories
    const pathsData = getRoverPaths();
    const pathMeshes: THREE.Line[] = [];

    pathsData.forEach(pData => {
      const isSelected = activePathId === pData.id;
      const points = pData.points.map(p => new THREE.Vector3(p[0], p[1], p[2]));
      const curve = new THREE.CatmullRomCurve3(points);
      const pathGeo = new THREE.BufferGeometry().setFromPoints(curve.getPoints(60));
      const pathMat = new THREE.LineBasicMaterial({ 
        color: new THREE.Color(pData.color), 
        linewidth: isSelected ? 3 : 1.5,
      });
      const pathLine = new THREE.Line(pathGeo, pathMat);
      
      if (isSelected) {
        pathLine.position.y += 0.15;
      }
      
      scene.add(pathLine);
      pathMeshes.push(pathLine);
    });

    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      terrain.rotation.y += 0.0008;
      pathMeshes.forEach(pm => pm.rotation.y += 0.0008);
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
    };
  }, [activePathId, showBayesian]);

  return <div ref={containerRef} className="absolute inset-0 z-0 bg-[#e5e7eb]" />;
}

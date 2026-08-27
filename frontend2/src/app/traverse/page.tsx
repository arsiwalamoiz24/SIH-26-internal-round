"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Instance, Instances, OrbitControls, useTexture } from "@react-three/drei";
import { CANDIDATES, FAUSTINI, CABEUS, spIdLabel } from "@/data/prism";
import * as THREE from "three";
import {
  buildFineGrid,
  astar,
  buildTelemetry,
  selectLandingSite,
  MAX_MISSION_SECONDS,
  type PathfindingGridData,
  type BoulderData,
  type TraversePlan,
} from "@/lib/traversePlanner";

/* =========================================================
   TYPES
========================================================= */

type BoundaryJSON = {
  boundary_xy_m: [number, number][];
};

type ElevationGridJSON = {
  elevationGridRelativeM: number[][];
  window_half_m: number;
  grid_size: number;
};

type RimLookup = {
  rimByAngle: Float32Array;
  scale: number;
};

type TerrainData = {
  grid: ElevationGridJSON | null;
  scale: number;
  rimByAngle: Float32Array;
  depthScale: number;
  elevRange: number;
};

type RoutePoint = {
  x: number;
  y: number;
  z: number;
  slope: number;
  slopeDeg: number;
  nd: number;
  heading: number;
  // Real telemetry from the A* plan's battery/speed model (src/lib/
  // traversePlanner.ts), carried through for the live rover HUD -- not
  // re-derived from the mesh, so it stays exactly what the planner computed.
  batterySoc?: number;
  speedMs?: number;
  illumination?: number;
};

type RouteMetrics = {
  cumulative: number[];
  total: number;
};

/* =========================================================
   CONSTANTS
========================================================= */

const ANGLE_BUCKETS = 360;
const AVG_RIM_UNITS = 8.2;

const MESH_SIZE = 20;
const MESH_HALF = MESH_SIZE / 2;

const DEPTH_SCALE = 3.2;

const MAX_SLOPE_DEG = 10;
const HARD_SLOPE_DEG = 15;

/*
 * Wheels sit at y=0.07 with radius 0.09, so this small
 * clearance places the bottom of the wheels on the terrain.
 */
const ROVER_CLEARANCE = 0.025;
const PATH_CLEARANCE = 0.075;

// Matches the site's shared --amber accent (used for the primary/featured
// highlight color elsewhere). A fixed hex, not var(--amber) -- this value is
// also used directly in a Three.js material, which can't resolve CSS custom
// properties, so it can't switch with the light/dark theme toggle the way
// the rest of the page's 2D chrome does.
const PATH_COLOR = "#C4A268";

/*
 * Complete traversal duration: exactly 10 seconds.
 */
const SIM_DURATION_MS = 10_000;

/* =========================================================
   RIM HELPERS
========================================================= */

function buildRimLookup(
  boundaryPoints: [number, number][]
): RimLookup {
  let maxR = 0;

  for (const [x, y] of boundaryPoints) {
    maxR = Math.max(maxR, Math.hypot(x, y));
  }

  const scale =
    maxR > 0 ? AVG_RIM_UNITS / maxR : 1;

  const scaled = boundaryPoints.map(
    ([x, y]) => [x * scale, y * scale] as [number, number]
  );

  const rimByAngle = new Float32Array(
    ANGLE_BUCKETS
  ).fill(AVG_RIM_UNITS);

  for (let i = 0; i < ANGLE_BUCKETS; i++) {
    const theta =
      (i / ANGLE_BUCKETS) * Math.PI * 2;

    const dx = Math.cos(theta);
    const dz = Math.sin(theta);

    let best = Infinity;

    for (let j = 0; j < scaled.length; j++) {
      const [ax, az] = scaled[j];
      const [bx, bz] =
        scaled[(j + 1) % scaled.length];

      const ex = bx - ax;
      const ez = bz - az;

      const det = ex * dz - ez * dx;

      if (Math.abs(det) < 1e-9) {
        continue;
      }

      const t = (-ax * ez + ex * az) / det;
      const s = (dx * az - dz * ax) / det;

      if (
        t > 0.01 &&
        s >= 0 &&
        s <= 1 &&
        t < best
      ) {
        best = t;
      }
    }

    if (Number.isFinite(best)) {
      rimByAngle[i] = best;
    }
  }

  return {
    rimByAngle,
    scale,
  };
}

function getRimRadius(
  x: number,
  z: number,
  lookup: RimLookup
) {
  let theta = Math.atan2(z, x);

  if (theta < 0) {
    theta += Math.PI * 2;
  }

  const bucket =
    Math.floor(
      (theta / (Math.PI * 2)) * ANGLE_BUCKETS
    ) % ANGLE_BUCKETS;

  return (
    lookup.rimByAngle[bucket] ||
    AVG_RIM_UNITS
  );
}

/* =========================================================
   ELEVATION SAMPLING
========================================================= */

function sampleElevationGrid(
  grid: number[][],
  gridSize: number,
  u: number,
  v: number
) {
  const cu = THREE.MathUtils.clamp(
    u,
    0,
    gridSize - 1.001
  );

  const cv = THREE.MathUtils.clamp(
    v,
    0,
    gridSize - 1.001
  );

  const u0 = Math.floor(cu);
  const v0 = Math.floor(cv);

  const u1 = Math.min(u0 + 1, gridSize - 1);
  const v1 = Math.min(v0 + 1, gridSize - 1);

  const fu = cu - u0;
  const fv = cv - v0;

  const g00 = grid[v0]?.[u0] ?? 0;
  const g10 = grid[v0]?.[u1] ?? g00;
  const g01 = grid[v1]?.[u0] ?? g00;
  const g11 = grid[v1]?.[u1] ?? g00;

  const top = g00 + (g10 - g00) * fu;
  const bottom = g01 + (g11 - g01) * fu;

  return top + (bottom - top) * fv;
}

/* =========================================================
   FALLBACK CRATER
========================================================= */

function getFallbackCraterY(
  x: number,
  z: number,
  rimByAngle: Float32Array,
  depthScale: number
) {
  const distance = Math.hypot(x, z);

  let theta = Math.atan2(z, x);

  if (theta < 0) {
    theta += Math.PI * 2;
  }

  const bucket =
    Math.floor(
      (theta / (Math.PI * 2)) * ANGLE_BUCKETS
    ) % ANGLE_BUCKETS;

  const rim =
    rimByAngle[bucket] || AVG_RIM_UNITS;

  const normalizedDistance =
    rim > 0 ? distance / rim : 1;

  if (normalizedDistance < 1) {
    const parabola =
      1 - normalizedDistance * normalizedDistance;

    const gaussian = Math.exp(
      -normalizedDistance *
        normalizedDistance *
        3
    );

    return (
      -depthScale *
      (parabola * 0.6 + gaussian * 0.4)
    );
  }

  const drop = Math.min(
    (normalizedDistance - 1) * 0.8,
    0.6
  );

  return -depthScale * drop * 0.4;
}

/* =========================================================
   SHARED TERRAIN SAMPLING
========================================================= */

function sampleTerrainY(
  x: number,
  z: number,
  terrain: TerrainData
) {
  const {
    grid,
    scale,
    rimByAngle,
    depthScale,
    elevRange,
  } = terrain;

  if (
    grid &&
    Number.isFinite(scale) &&
    scale > 0
  ) {
    const halfM = grid.window_half_m;
    const gridSize = grid.grid_size;

    const realX = x / scale;
    const realZ = z / scale;

    const u =
      ((realX + halfM) / (2 * halfM)) *
      (gridSize - 1);

    const v =
      ((realZ + halfM) / (2 * halfM)) *
      (gridSize - 1);

    if (
      u >= 0 &&
      u <= gridSize - 1 &&
      v >= 0 &&
      v <= gridSize - 1
    ) {
      const elevation = sampleElevationGrid(
        grid.elevationGridRelativeM,
        gridSize,
        u,
        v
      );

      const metersToMeshY =
        depthScale /
        Math.max(elevRange / 2, 1);

      if (Number.isFinite(elevation)) {
        return elevation * metersToMeshY;
      }
    }
  }

  return getFallbackCraterY(
    x,
    z,
    rimByAngle,
    depthScale
  );
}

function sampleTerrainNormal(
  x: number,
  z: number,
  terrain: TerrainData
) {
  const epsilon = 0.08;

  const left = sampleTerrainY(
    x - epsilon,
    z,
    terrain
  );

  const right = sampleTerrainY(
    x + epsilon,
    z,
    terrain
  );

  const down = sampleTerrainY(
    x,
    z - epsilon,
    terrain
  );

  const up = sampleTerrainY(
    x,
    z + epsilon,
    terrain
  );

  return new THREE.Vector3(
    left - right,
    epsilon * 2,
    down - up
  ).normalize();
}

function sampleSlopeDeg(
  x: number,
  z: number,
  terrain: TerrainData
) {
  const normal = sampleTerrainNormal(
    x,
    z,
    terrain
  );

  const radians = Math.acos(
    THREE.MathUtils.clamp(normal.y, -1, 1)
  );

  return THREE.MathUtils.radToDeg(radians);
}

/* =========================================================
   ROUTE POINT CREATION
========================================================= */

function createRoutePoint(
  x: number,
  z: number,
  heading: number,
  terrain: TerrainData,
  rimLookup: RimLookup,
  telemetry?: { batterySoc: number; speedMs: number; illumination: number; slopeDeg: number }
): RoutePoint {
  const groundY = sampleTerrainY(
    x,
    z,
    terrain
  );

  // Real slope from the A* plan (src/lib/traversePlanner.ts -- a real Sobel
  // gradient on real LOLA elevation meters) when available. The local
  // fallback below instead differentiates the *visual* mesh in mesh-space
  // units, mixing the mesh's own vertical exaggeration with its per-candidate
  // horizontal scale factor -- not a real angle, only a rough shading cue,
  // and one that can read wildly higher than the real slope the rover
  // actually planned against. Only used before the real plan has loaded.
  const slopeDeg = telemetry?.slopeDeg ?? sampleSlopeDeg(
    x,
    z,
    terrain
  );

  const rim = getRimRadius(
    x,
    z,
    rimLookup
  );

  return {
    x,
    y: groundY + PATH_CLEARANCE,
    z,
    slope: Math.tan(
      THREE.MathUtils.degToRad(slopeDeg)
    ),
    slopeDeg,
    nd:
      rim > 0
        ? Math.hypot(x, z) / rim
        : 0,
    heading,
    batterySoc: telemetry?.batterySoc,
    speedMs: telemetry?.speedMs,
    illumination: telemetry?.illumination,
  };
}

/* =========================================================
   REAL A*-PLANNED ROUTE

   Waypoints come from a real weighted-A* search over real slope/
   illumination/boulder cost grids (src/lib/traversePlanner.ts),
   not a parametric spiral -- the rover goes wherever the real
   terrain lets it, avoiding real detected boulders and steep
   slopes, from a selected landing site to the ice-evidence target.
========================================================= */

/*
 * Converts the real A*-planned waypoints (real meters, relative
 * to the candidate's own center) from PRISM/src/export_pathfinding_grids.py +
 * export_real_boulder_positions.py + src/lib/traversePlanner.ts into mesh-
 * space RoutePoints for rendering. Height/slope/rim-fraction are resampled
 * directly against this page's own terrain field for visual consistency with
 * CraterMesh/Rover, which already read the same real elevation data.
 */
function buildRouteFromRealPlan(
  plan: TraversePlan,
  terrain: TerrainData,
  rimLookup: RimLookup
): RoutePoint[] {
  const scale = rimLookup.scale;
  const route: RoutePoint[] = [];

  for (let i = 0; i < plan.waypoints.length; i++) {
    const wp = plan.waypoints[i];
    const x = wp.x * scale;
    const z = wp.y * scale;
    const prev = route[route.length - 1];
    const heading = prev
      ? Math.atan2(z - prev.z, x - prev.x)
      : (wp.heading * Math.PI) / 180;

    route.push(createRoutePoint(x, z, heading, terrain, rimLookup, {
      batterySoc: wp.batterySoc, speedMs: wp.speedMs, illumination: wp.illumination, slopeDeg: wp.slopeDeg,
    }));
  }

  return route;
}

/* =========================================================
   ROUTE DISTANCE METRICS
========================================================= */

function calculateRouteMetrics(
  route: RoutePoint[]
): RouteMetrics {
  if (route.length === 0) {
    return {
      cumulative: [],
      total: 0,
    };
  }

  const cumulative = new Array<number>(
    route.length
  );

  cumulative[0] = 0;

  let total = 0;

  for (let i = 1; i < route.length; i++) {
    const previous = route[i - 1];
    const current = route[i];

    total += Math.hypot(
      current.x - previous.x,
      current.z - previous.z
    );

    cumulative[i] = total;
  }

  return {
    cumulative,
    total,
  };
}

/*
 * Finds and interpolates the rover position by route distance.
 * This creates a more consistent physical speed than moving
 * by array index.
 */
function sampleRouteAtProgress(
  route: RoutePoint[],
  metrics: RouteMetrics,
  progress: number
): RoutePoint | null {
  if (route.length === 0) {
    return null;
  }

  if (
    route.length === 1 ||
    metrics.total <= 0
  ) {
    return route[0];
  }

  const clampedProgress =
    THREE.MathUtils.clamp(progress, 0, 1);

  const targetDistance =
    metrics.total * clampedProgress;

  let low = 0;
  let high = metrics.cumulative.length - 1;

  while (low < high) {
    const middle = Math.floor(
      (low + high) / 2
    );

    if (
      metrics.cumulative[middle] <
      targetDistance
    ) {
      low = middle + 1;
    } else {
      high = middle;
    }
  }

  const nextIndex = Math.max(1, low);
  const previousIndex = nextIndex - 1;

  const previous = route[previousIndex];
  const next = route[nextIndex];

  const previousDistance =
    metrics.cumulative[previousIndex];

  const nextDistance =
    metrics.cumulative[nextIndex];

  const segmentLength =
    nextDistance - previousDistance;

  const localT =
    segmentLength > 0
      ? THREE.MathUtils.clamp(
          (targetDistance - previousDistance) /
            segmentLength,
          0,
          1
        )
      : 0;

  const x = THREE.MathUtils.lerp(
    previous.x,
    next.x,
    localT
  );

  const z = THREE.MathUtils.lerp(
    previous.z,
    next.z,
    localT
  );

  const y = THREE.MathUtils.lerp(
    previous.y,
    next.y,
    localT
  );

  const slope = THREE.MathUtils.lerp(
    previous.slope,
    next.slope,
    localT
  );

  const slopeDeg = THREE.MathUtils.lerp(
    previous.slopeDeg,
    next.slopeDeg,
    localT
  );

  const nd = THREE.MathUtils.lerp(
    previous.nd,
    next.nd,
    localT
  );

  /*
   * Use actual segment direction so the rover faces along
   * the circular path.
   */
  const heading = Math.atan2(
    next.z - previous.z,
    next.x - previous.x
  );

  const lerpOptional = (a?: number, b?: number) =>
    a !== undefined && b !== undefined
      ? THREE.MathUtils.lerp(a, b, localT)
      : (b ?? a);

  return {
    x,
    y,
    z,
    slope,
    slopeDeg,
    nd,
    heading,
    batterySoc: lerpOptional(previous.batterySoc, next.batterySoc),
    speedMs: lerpOptional(previous.speedMs, next.speedMs),
    illumination: lerpOptional(previous.illumination, next.illumination),
  };
}

function findRouteIndexAtProgress(
  metrics: RouteMetrics,
  progress: number
) {
  if (
    metrics.cumulative.length === 0 ||
    metrics.total <= 0
  ) {
    return 0;
  }

  const target =
    metrics.total *
    THREE.MathUtils.clamp(progress, 0, 1);

  let low = 0;
  let high = metrics.cumulative.length - 1;

  while (low < high) {
    const middle = Math.floor(
      (low + high) / 2
    );

    if (
      metrics.cumulative[middle] <
      target
    ) {
      low = middle + 1;
    } else {
      high = middle;
    }
  }

  return low;
}

/* =========================================================
   CRATER MESH
========================================================= */

function CraterMesh({
  candidateId,
  terrain,
}: {
  candidateId: string;
  terrain: TerrainData;
}) {
  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(
      MESH_SIZE,
      MESH_SIZE,
      220,
      220
    );

    geo.rotateX(-Math.PI / 2);

    const positions = geo.attributes.position;

    for (
      let i = 0;
      i < positions.count;
      i++
    ) {
      const x = positions.getX(i);
      const z = positions.getZ(i);

      const y = sampleTerrainY(
        x,
        z,
        terrain
      );

      positions.setY(
        i,
        Number.isFinite(y) ? y : 0
      );
    }

    positions.needsUpdate = true;

    geo.computeVertexNormals();

    /*
     * Subtle slope-based terrain coloring.
     */
    const colors = new Float32Array(
      positions.count * 3
    );

    for (
      let i = 0;
      i < positions.count;
      i++
    ) {
      const x = positions.getX(i);
      const z = positions.getZ(i);

      const radius = Math.hypot(x, z);

      const slope = sampleSlopeDeg(
        x,
        z,
        terrain
      );

      let r = 0.7;
      let g = 0.69;
      let b = 0.67;

      if (radius < 3.2) {
        r = 0.42;
        g = 0.45;
        b = 0.5;
      }

      if (slope > MAX_SLOPE_DEG) {
        const hazard =
          THREE.MathUtils.clamp(
            (slope - MAX_SLOPE_DEG) / 20,
            0,
            1
          );

        r = THREE.MathUtils.lerp(
          r,
          0.62,
          hazard * 0.48
        );

        g = THREE.MathUtils.lerp(
          g,
          0.22,
          hazard * 0.48
        );

        b = THREE.MathUtils.lerp(
          b,
          0.2,
          hazard * 0.48
        );
      }

      colors[i * 3] = r;
      colors[i * 3 + 1] = g;
      colors[i * 3 + 2] = b;
    }

    geo.setAttribute(
      "color",
      new THREE.BufferAttribute(colors, 3)
    );

    return geo;
  }, [terrain]);

  useEffect(() => {
    return () => {
      geometry.dispose();
    };
  }, [geometry]);

  const textureUrl =
    `/assets/prism/hazard_only/${candidateId}.png`;

  const texture = useTexture(textureUrl);

  useEffect(() => {
    texture.wrapS = THREE.ClampToEdgeWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;
    texture.colorSpace = THREE.SRGBColorSpace;

    const textureHalfM = 5000;

    const meshHalfExtentM =
      MESH_HALF /
      Math.max(terrain.scale, 0.0001);

    const repeatFraction = Math.min(
      meshHalfExtentM / textureHalfM,
      1
    );

    texture.offset.set(
      (1 - repeatFraction) / 2,
      (1 - repeatFraction) / 2
    );

    texture.repeat.set(
      repeatFraction,
      repeatFraction
    );

    texture.needsUpdate = true;
  }, [texture, terrain.scale]);

  return (
    <mesh
      geometry={geometry}
      receiveShadow
      castShadow
    >
      <meshStandardMaterial
        map={texture}
        vertexColors
        roughness={0.97}
        metalness={0}
      />
    </mesh>
  );
}

/* =========================================================
   COMPLETE RED PATH
========================================================= */

function PathLine({
  points,
}: {
  points: RoutePoint[];
}) {
  const pathObject = useMemo(() => {
    if (points.length < 2) {
      return null;
    }

    const stride = Math.max(
      1,
      Math.floor(points.length / 900)
    );

    const vectors: THREE.Vector3[] = [];

    for (
      let i = 0;
      i < points.length;
      i += stride
    ) {
      const point = points[i];

      vectors.push(
        new THREE.Vector3(
          point.x,
          point.y,
          point.z
        )
      );
    }

    const destination =
      points[points.length - 1];

    const lastVector =
      vectors[vectors.length - 1];

    if (
      !lastVector ||
      lastVector.distanceTo(
        new THREE.Vector3(
          destination.x,
          destination.y,
          destination.z
        )
      ) > 0.001
    ) {
      vectors.push(
        new THREE.Vector3(
          destination.x,
          destination.y,
          destination.z
        )
      );
    }

    const curve = new THREE.CatmullRomCurve3(
      vectors,
      false,
      "centripetal",
      0.2
    );

    const segments = Math.min(
      1800,
      Math.max(300, vectors.length * 2)
    );

    const geometry = new THREE.TubeGeometry(
      curve,
      segments,
      0.045,
      8,
      false
    );

    const material = new THREE.MeshBasicMaterial({
      color: PATH_COLOR,
      depthTest: true,
      depthWrite: false,
      toneMapped: false,
    });

    const mesh = new THREE.Mesh(
      geometry,
      material
    );

    mesh.renderOrder = 20;

    return mesh;
  }, [points]);

  useEffect(() => {
    return () => {
      if (!pathObject) {
        return;
      }

      pathObject.geometry.dispose();

      (
        pathObject.material as THREE.Material
      ).dispose();
    };
  }, [pathObject]);

  if (!pathObject) {
    return null;
  }

  return <primitive object={pathObject} />;
}

/* =========================================================
   ICE SURFACE LAYER
========================================================= */

function IceLayer({
  terrain,
}: {
  terrain: TerrainData;
}) {
  const geometry = useMemo(() => {
    const geo = new THREE.CircleGeometry(
      0.95,
      72
    );

    geo.rotateX(-Math.PI / 2);

    const positions = geo.attributes.position;

    for (
      let i = 0;
      i < positions.count;
      i++
    ) {
      let x = positions.getX(i);
      let z = positions.getZ(i);

      const radius = Math.hypot(x, z);

      if (radius > 0.001) {
        const angle = Math.atan2(z, x);

        const irregularity =
          0.92 +
          Math.sin(angle * 5) * 0.045 +
          Math.sin(angle * 9 + 0.7) * 0.025 +
          Math.sin(angle * 13) * 0.015;

        x *= irregularity;
        z *= irregularity;
      }

      const y = sampleTerrainY(
        x,
        z,
        terrain
      );

      positions.setXYZ(
        i,
        x,
        y + 0.028,
        z
      );
    }

    positions.needsUpdate = true;
    geo.computeVertexNormals();

    return geo;
  }, [terrain]);

  useEffect(() => {
    return () => {
      geometry.dispose();
    };
  }, [geometry]);

  return (
    <mesh
      geometry={geometry}
      receiveShadow
      renderOrder={5}
    >
      <meshPhysicalMaterial
        color="#79d5ff"
        roughness={0.2}
        metalness={0}
        transmission={0.3}
        thickness={0.02}
        transparent
        opacity={0.66}
        clearcoat={0.85}
        clearcoatRoughness={0.16}
        side={THREE.DoubleSide}
        depthWrite={false}
      />
    </mesh>
  );
}

/* =========================================================
   BOULDER MARKERS

   Real YOLOv8n-seg detections on local ShadowCam imagery
   (PRISM/src/export_real_boulder_positions.py) -- these are the
   actual obstacles the A* planner routed around, not decoration.
========================================================= */

function BoulderMarkers({
  boulders,
  terrain,
  scale,
}: {
  boulders: BoulderData["boulders"];
  terrain: TerrainData;
  scale: number;
}) {
  const placed = useMemo(() => {
    // Cap render count for perf on dense candidates (some have 500+ real
    // detections); keep the highest-confidence ones, biased toward larger
    // rocks since those are the ones that actually matter for routing.
    const sorted = [...boulders].sort(
      (a, b) => b.confidence * b.radius_m - a.confidence * a.radius_m
    );

    return sorted.slice(0, 180).map((b) => {
      const x = b.x * scale;
      const z = b.y * scale;
      const y = sampleTerrainY(x, z, terrain);
      const size = Math.max(0.03, Math.min(0.22, (b.radius_m * scale) / 1.5));
      return { x, y: y + size * 0.5, z, size };
    });
  }, [boulders, terrain, scale]);

  if (placed.length === 0) return null;

  return (
    <Instances limit={placed.length} range={placed.length}>
      <sphereGeometry args={[1, 8, 8]} />
      <meshStandardMaterial
        color="#9a7a5a"
        roughness={0.95}
        metalness={0}
      />
      {placed.map((p, i) => (
        <Instance
          key={i}
          position={[p.x, p.y, p.z]}
          scale={p.size}
        />
      ))}
    </Instances>
  );
}

/* =========================================================
   LANDING SITE MARKER
========================================================= */

function LandingSiteMarker({
  point,
}: {
  point: RoutePoint | undefined;
}) {
  if (!point) return null;

  return (
    <group position={[point.x, point.y + 0.02, point.z]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.22, 0.3, 32]} />
        <meshBasicMaterial
          color="#ffd23f"
          transparent
          opacity={0.9}
          side={THREE.DoubleSide}
        />
      </mesh>
      <mesh position={[0, 0.24, 0]}>
        <coneGeometry args={[0.05, 0.4, 8]} />
        <meshStandardMaterial
          color="#ffd23f"
          emissive="#ffd23f"
          emissiveIntensity={0.4}
        />
      </mesh>
    </group>
  );
}

/* =========================================================
   ROVER
========================================================= */

function Rover({
  point,
  isMoving,
  terrain,
}: {
  point: RoutePoint;
  isMoving: boolean;
  terrain: TerrainData;
}) {
  const roverRef = useRef<THREE.Group>(null);
  const wheelRefs = useRef<THREE.Mesh[]>([]);
  const initializedRef = useRef(false);

  useFrame((_, delta) => {
    const rover = roverRef.current;

    if (!rover) {
      return;
    }

    const groundY = sampleTerrainY(
      point.x,
      point.z,
      terrain
    );

    const targetPosition = new THREE.Vector3(
      point.x,
      groundY + ROVER_CLEARANCE,
      point.z
    );

    /*
     * Snap on initial load and replay. This prevents the
     * rover from flying from the ice back to the start.
     */
    const distanceToTarget =
      rover.position.distanceTo(targetPosition);

    if (
      !initializedRef.current ||
      distanceToTarget > 1
    ) {
      rover.position.copy(targetPosition);
      initializedRef.current = true;
    } else {
      rover.position.lerp(
        targetPosition,
        1 - Math.exp(-delta * 24)
      );
    }

    const normal = sampleTerrainNormal(
      point.x,
      point.z,
      terrain
    );

    /*
     * Route heading in the horizontal X/Z plane.
     */
    const forward = new THREE.Vector3(
      Math.cos(point.heading),
      0,
      Math.sin(point.heading)
    );

    /*
     * Project forward onto the terrain surface.
     */
    forward
      .sub(
        normal
          .clone()
          .multiplyScalar(
            forward.dot(normal)
          )
      )
      .normalize();

    const right = new THREE.Vector3()
      .crossVectors(normal, forward)
      .normalize();

    const correctedForward =
      new THREE.Vector3()
        .crossVectors(right, normal)
        .normalize();

    const orientationMatrix =
      new THREE.Matrix4().makeBasis(
        right,
        normal,
        correctedForward
      );

    const targetQuaternion =
      new THREE.Quaternion()
        .setFromRotationMatrix(
          orientationMatrix
        );

    if (distanceToTarget > 1) {
      rover.quaternion.copy(targetQuaternion);
    } else {
      rover.quaternion.slerp(
        targetQuaternion,
        1 - Math.exp(-delta * 14)
      );
    }

    if (isMoving) {
      for (const wheel of wheelRefs.current) {
        if (wheel) {
          wheel.rotation.x += delta * 10;
        }
      }
    }
  });

  return (
    <group ref={roverRef}>
      {/* Main chassis */}
      <mesh
        position={[0, 0.17, 0]}
        castShadow
      >
        <boxGeometry args={[0.42, 0.16, 0.58]} />

        <meshStandardMaterial
          color="#c7c0b4"
          roughness={0.62}
          metalness={0.26}
        />
      </mesh>

      {/* Upper deck */}
      <mesh
        position={[0, 0.3, 0]}
        castShadow
      >
        <boxGeometry args={[0.48, 0.04, 0.65]} />

        <meshStandardMaterial
          color="#242d3a"
          roughness={0.32}
          metalness={0.58}
        />
      </mesh>

      {/* Solar panel */}
      <mesh
        position={[0, 0.335, -0.04]}
        castShadow
      >
        <boxGeometry args={[0.4, 0.015, 0.35]} />

        <meshStandardMaterial
          color="#152c56"
          roughness={0.25}
          metalness={0.55}
        />
      </mesh>

      {/* Solar panel lines */}
      {[-0.12, -0.04, 0.04, 0.12].map(
        (x) => (
          <mesh
            key={x}
            position={[x, 0.345, -0.04]}
          >
            <boxGeometry
              args={[0.006, 0.005, 0.34]}
            />

            <meshBasicMaterial color="#6686ad" />
          </mesh>
        )
      )}

      {/* Mast */}
      <mesh
        position={[0.11, 0.43, -0.06]}
        castShadow
      >
        <cylinderGeometry
          args={[0.012, 0.012, 0.22, 10]}
        />

        <meshStandardMaterial
          color="#8d887f"
          metalness={0.6}
          roughness={0.45}
        />
      </mesh>

      {/* Mast camera */}
      <mesh
        position={[0.11, 0.56, -0.06]}
        castShadow
      >
        <boxGeometry args={[0.09, 0.065, 0.09]} />

        <meshStandardMaterial
          color="#2b333b"
          roughness={0.3}
          metalness={0.65}
        />
      </mesh>

      {/* Front camera/sensor */}
      <mesh position={[0, 0.23, 0.3]}>
        <sphereGeometry args={[0.025, 12, 12]} />

        <meshStandardMaterial
          color="#ff452e"
          emissive="#ff1800"
          emissiveIntensity={2}
        />
      </mesh>

      {/* Wheels */}
      {[
        [-0.235, 0.07, 0.22],
        [-0.235, 0.07, -0.22],
        [0.235, 0.07, 0.22],
        [0.235, 0.07, -0.22],
      ].map((position, index) => (
        <group
          key={index}
          position={
            position as [number, number, number]
          }
        >
          <mesh
            ref={(element) => {
              if (element) {
                wheelRefs.current[index] = element;
              }
            }}
            rotation={[0, 0, Math.PI / 2]}
            castShadow
          >
            <cylinderGeometry
              args={[0.09, 0.09, 0.065, 18]}
            />

            <meshStandardMaterial
              color="#151310"
              roughness={0.98}
              metalness={0.02}
            />
          </mesh>

          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry
              args={[0.03, 0.03, 0.07, 10]}
            />

            <meshStandardMaterial
              color="#8b857b"
              roughness={0.48}
              metalness={0.72}
            />
          </mesh>
        </group>
      ))}
    </group>
  );
}

/* =========================================================
   LIGHTING
========================================================= */

function LightingRig() {
  return (
    <>
      <ambientLight
        intensity={0.18}
        color="#b9c5d8"
      />

      <hemisphereLight
        args={[
          "#8da4c5",
          "#151719",
          0.28,
        ]}
      />

      <directionalLight
        position={[9, 15, 5]}
        intensity={3.2}
        color="#fff0db"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-left={-14}
        shadow-camera-right={14}
        shadow-camera-top={14}
        shadow-camera-bottom={-14}
        shadow-camera-near={1}
        shadow-camera-far={45}
        shadow-bias={-0.0004}
      />

      <directionalLight
        position={[-7, 7, -10]}
        intensity={0.42}
        color="#7290b5"
      />
    </>
  );
}

/* =========================================================
   UI HELPERS
========================================================= */

function TelemetryValue({
  label,
  value,
  color = "var(--text-primary)",
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "10px",
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "16px",
          color,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function TelemetryRow({
  label,
  value,
  color = "var(--text-primary)",
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "10px 0",
        borderBottom:
          "1px solid var(--border)",
      }}
    >
      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "12px",
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          color: "var(--text-secondary)",
        }}
      >
        {label}
      </span>

      <span
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: "14px",
          color,
        }}
      >
        {value}
      </span>
    </div>
  );
}

function SmallLabel({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div
      style={{
        fontFamily: "var(--font-mono)",
        fontSize: "9px",
        color: "var(--text-muted)",
        textTransform: "uppercase",
        letterSpacing: "0.08em",
        marginBottom: "3px",
      }}
    >
      {children}
    </div>
  );
}

/* =========================================================
   PAGE
========================================================= */

// Faustini/Cabeus first, like every other page's site list -- real
// externally-validated reference sites, not a separate subsection.
const ALL_TRAVERSE_SITES = [FAUSTINI, CABEUS, ...CANDIDATES];

/** Real point-in-polygon test against the candidate's own PSR boundary (meters, relative to center). */
function pointInBoundary(x: number, y: number, boundaryPts: [number, number][]): boolean {
  let inside = false;
  for (let i = 0, j = boundaryPts.length - 1; i < boundaryPts.length; j = i++) {
    const [xi, yi] = boundaryPts[i];
    const [xj, yj] = boundaryPts[j];
    const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

export default function TraversePage() {
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>(CANDIDATES[0].id);
  const selectedCandidate =
    ALL_TRAVERSE_SITES.find((c) => c.id === selectedCandidateId) || CANDIDATES[0];
  const candidateId = selectedCandidate.id;
  const elevRange =
    selectedCandidate.terrain.elevRange;

  const [mounted, setMounted] = useState(false);

  const [boundary, setBoundary] =
    useState<BoundaryJSON | null>(null);

  const [wideGrid, setWideGrid] =
    useState<ElevationGridJSON | null>(null);

  const [pathfindingGrid, setPathfindingGrid] =
    useState<PathfindingGridData | null>(null);

  const [boulderData, setBoulderData] =
    useState<BoulderData | null>(null);

  const [dataReady, setDataReady] =
    useState(false);

  const [simRunning, setSimRunning] =
    useState(false);

  const [simComplete, setSimComplete] =
    useState(false);

  /*
   * Simulation progress follows physical route distance,
   * not point index.
   */
  const [simProgress, setSimProgress] =
    useState(0);

  const [
    activeWaypoint,
    setActiveWaypoint,
  ] = useState<number | null>(null);

  const animationFrameRef =
    useRef<number | null>(null);

  /* =========================================================
     MOUNT
  ========================================================= */

  useEffect(() => {
    setMounted(true);
  }, []);

  /* =========================================================
     LOAD TERRAIN DATA
  ========================================================= */

  useEffect(() => {
    let cancelled = false;

    setDataReady(false);

    Promise.all([
      fetch(
        `/assets/prism/psr_boundary/${candidateId}.json`
      )
        .then((response) =>
          response.ok ? response.json() : null
        )
        .catch(() => null),

      fetch(
        `/assets/prism/elevation/${candidateId}_real_elevation_grid_wide.json`
      )
        .then((response) =>
          response.ok ? response.json() : null
        )
        .catch(() => null),

      fetch(
        `/assets/prism/pathfinding/${candidateId}_pathfinding_grid.json`
      )
        .then((response) =>
          response.ok ? response.json() : null
        )
        .catch(() => null),

      fetch(
        `/assets/prism/pathfinding/${candidateId}_boulders.json`
      )
        .then((response) =>
          response.ok ? response.json() : null
        )
        .catch(() => null),
    ]).then(
      ([boundaryData, elevationData, pathfindingData, boulders]) => {
        if (cancelled) {
          return;
        }

        setBoundary(boundaryData);
        setWideGrid(elevationData);
        setPathfindingGrid(pathfindingData);
        setBoulderData(boulders);
        setDataReady(true);
      }
    );

    return () => {
      cancelled = true;
    };
  }, [candidateId]);

  /* =========================================================
     TERRAIN DATA
  ========================================================= */

  const rimLookup = useMemo<RimLookup>(() => {
    if (
      boundary?.boundary_xy_m &&
      boundary.boundary_xy_m.length > 2
    ) {
      return buildRimLookup(
        boundary.boundary_xy_m
      );
    }

    return {
      rimByAngle: new Float32Array(
        ANGLE_BUCKETS
      ).fill(AVG_RIM_UNITS),
      scale: 1,
    };
  }, [boundary]);

  const terrain = useMemo<TerrainData>(
    () => ({
      grid: wideGrid,
      scale: rimLookup.scale,
      rimByAngle: rimLookup.rimByAngle,
      depthScale:
        (elevRange / 1742) * DEPTH_SCALE,
      elevRange,
    }),
    [wideGrid, rimLookup, elevRange]
  );

  /* =========================================================
     REAL A* ROUTE — landing site to the ice-evidence target,
     over a real slope/illumination/boulder cost grid (see
     src/lib/traversePlanner.ts). Replaces the old hardcoded
     spiral entirely.
  ========================================================= */

  const realPlan = useMemo<TraversePlan | null>(() => {
    if (!pathfindingGrid || !boundary?.boundary_xy_m) {
      return null;
    }
    // Same real elevation grid CraterMesh/terrain use, once mesh/terrain
    // data has loaded -- lets the router evaluate the actual along-heading
    // slope (see directionalSlopeDeg in traversePlanner.ts) instead of only
    // the isotropic steepest-direction magnitude, so a path can cross a
    // locally steep area at an angle (switchback-style) instead of being
    // flatly blocked by it or forced to power straight up it.
    const elevationSource = wideGrid
      ? { grid: wideGrid.elevationGridRelativeM, halfM: wideGrid.window_half_m, size: wideGrid.grid_size }
      : undefined;

    // Size the fine pathfinding window off the real PSR polygon's own
    // extent, not a flat constant -- a fixed 4000m half-window works for
    // most candidates but sits entirely *inside* very large real floors
    // (Cabeus's true polygon reaches ~15.9km from its centroid), leaving no
    // real cell outside the crater for the lander to sit on.
    const boundaryPts = boundary.boundary_xy_m;
    let maxBoundaryR = 0;
    for (const [x, y] of boundaryPts) {
      maxBoundaryR = Math.max(maxBoundaryR, Math.hypot(x, y));
    }
    const fineHalfM = Math.min(
      pathfindingGrid.window_half_m,
      Math.max(4000, maxBoundaryR * 1.3)
    );
    const fg = buildFineGrid(pathfindingGrid, fineHalfM, 160, elevationSource);
    const isInsideCrater = (x: number, y: number) => pointInBoundary(x, y, boundaryPts);

    // The ice-evidence target: the candidate's own reference point, which is
    // exactly where every real Pv/CPR/SERD/T-Ratio measurement on this site
    // was centered (see src/data/prism.ts).
    const target: [number, number] = [0, 0];
    const landing = selectLandingSite(fg, isInsideCrater, target);
    const boulders = boulderData?.boulders ?? [];

    const result = astar(fg, boulders, [landing.x, landing.y], target);
    if (!result) return null;

    return buildTelemetry(fg, result.cells);
  }, [pathfindingGrid, boundary, boulderData, wideGrid]);

  const plannedRoute = useMemo(() => {
    if (!dataReady || !realPlan) {
      return [];
    }

    return buildRouteFromRealPlan(
      realPlan,
      terrain,
      rimLookup
    );
  }, [dataReady, realPlan, terrain, rimLookup]);

  const routeMetrics = useMemo(
    () => calculateRouteMetrics(plannedRoute),
    [plannedRoute]
  );

  useEffect(() => {
    setSimProgress(0);
    setSimRunning(false);
    setSimComplete(false);
  }, [plannedRoute]);

  const currentPoint = useMemo(
    () =>
      sampleRouteAtProgress(
        plannedRoute,
        routeMetrics,
        simProgress
      ),
    [plannedRoute, routeMetrics, simProgress]
  );

  const currentRouteIndex = useMemo(
    () =>
      findRouteIndexAtProgress(
        routeMetrics,
        simProgress
      ),
    [routeMetrics, simProgress]
  );

  /* =========================================================
     EXACT 10-SECOND SIMULATION
  ========================================================= */

  useEffect(() => {
    if (
      !simRunning ||
      plannedRoute.length < 2
    ) {
      return;
    }

    const startingProgress = simProgress;
    const startTime = performance.now();

    /*
     * Resume correctly after pause.
     */
    const remainingDuration = Math.max(
      100,
      SIM_DURATION_MS *
        (1 - startingProgress)
    );

    const animate = (now: number) => {
      const localProgress =
        THREE.MathUtils.clamp(
          (now - startTime) /
            remainingDuration,
          0,
          1
        );

      const nextProgress =
        THREE.MathUtils.lerp(
          startingProgress,
          1,
          localProgress
        );

      setSimProgress(nextProgress);

      if (localProgress >= 1) {
        setSimProgress(1);
        setSimRunning(false);
        setSimComplete(true);
        animationFrameRef.current = null;
        return;
      }

      animationFrameRef.current =
        requestAnimationFrame(animate);
    };

    animationFrameRef.current =
      requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(
          animationFrameRef.current
        );

        animationFrameRef.current = null;
      }
    };
  }, [simRunning, plannedRoute]);

  /* =========================================================
     CONTROLS
  ========================================================= */

  const toggleSimulation = useCallback(() => {
    if (plannedRoute.length < 2) {
      return;
    }

    if (simComplete) {
      setSimProgress(0);
      setSimComplete(false);

      /*
       * Start on the next browser frame so the rover first
       * snaps back to the landing position.
       */
      requestAnimationFrame(() => {
        setSimRunning(true);
      });

      return;
    }

    setSimRunning((running) => !running);
  }, [plannedRoute, simComplete]);

  /* =========================================================
     TELEMETRY
  ========================================================= */

  const slopeDeg =
    currentPoint?.slopeDeg ?? 0;

  const currentSlope =
    `${slopeDeg.toFixed(1)}°`;

  const currentHazard =
    slopeDeg > HARD_SLOPE_DEG
      ? "High"
      : slopeDeg > MAX_SLOPE_DEG
        ? "Medium"
        : "Low";

  // Live telemetry at the rover's current simulated position, straight from
  // the real A* plan's battery/speed model (src/lib/traversePlanner.ts) --
  // not re-derived, so it's exactly what the planner computed for this point.
  const currentBatteryPct = currentPoint?.batterySoc;
  const currentSpeedMs = currentPoint?.speedMs;
  const currentIllumFrac = currentPoint?.illumination;

  // Real total path distance from the A* plan (meters -> km), not a
  // hardcoded constant -- this now always matches the actual rendered route.
  const totalDistanceKm = (realPlan?.totalDistanceM ?? 0) / 1000;
  const elapsedKm = simProgress * totalDistanceKm;

  // Playback is a fixed SIM_DURATION_MS-long animation of the whole route,
  // independent of the rover's real mission time (below) -- this is a UI
  // scrub position, not a data value.
  const elapsedSeconds =
    simProgress * (SIM_DURATION_MS / 1000);

  const maxRouteSlope = useMemo(() => {
    let maximum = 0;

    for (const point of plannedRoute) {
      maximum = Math.max(
        maximum,
        point.slopeDeg
      );
    }

    return maximum;
  }, [plannedRoute]);

  // Real mission-duration estimate from the battery/speed model, expressed
  // in days against the hard 14-day rover-life budget.
  const missionDays = (realPlan?.totalTimeS ?? 0) / 86400;
  const maxMissionDays = MAX_MISSION_SECONDS / 86400;
  const withinMissionBudget = realPlan?.withinMissionBudget ?? true;
  const finalBatterySoc = realPlan?.finalBatterySoc ?? 0;
  const minBatterySoc = realPlan?.minBatterySoc ?? 0;

  /* =========================================================
     WAYPOINTS
  ========================================================= */

  const keyWaypoints = useMemo(() => {
    if (plannedRoute.length < 2) {
      return [];
    }

    const definitions = [
      {
        progress: 0,
        label: "Landing Site",
        type: "landing",
      },
      {
        progress: 0.15,
        label: "Departure Corridor",
        type: "waypoint",
      },
      {
        progress: 0.3,
        label: "Slope Transit",
        type: "waypoint",
      },
      {
        progress: 0.46,
        label: "Boulder-Field Skirt",
        type: "waypoint",
      },
      {
        progress: 0.62,
        label: "PSR Interior Approach",
        type: "waypoint",
      },
      {
        progress: 0.78,
        label: "Shadowed Descent",
        type: "waypoint",
      },
      {
        progress: 0.93,
        label: "Final Ice Approach",
        type: "waypoint",
      },
      {
        progress: 1,
        label: "Ice Target",
        type: "destination",
      },
    ];

    return definitions.map((definition) => {
      const index = findRouteIndexAtProgress(
        routeMetrics,
        definition.progress
      );

      return {
        ...plannedRoute[index],
        index,
        progress: definition.progress,
        label: definition.label,
        type: definition.type,
      };
    });
  }, [plannedRoute, routeMetrics]);

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <main
      style={{
        height: "100dvh",
        paddingTop: "var(--nav-h)",
        background: "var(--void)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* HEADER */}
      <div
        style={{
          padding: "10px 24px",
          borderBottom:
            "1px solid var(--border)",
          background: "var(--surface)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          rowGap: "8px",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "20px",
          }}
        >
          <div className="label-caps">
            Live Rover Telemetry
          </div>

          <TelemetryValue
            label="Slope"
            value={currentSlope}
            color={
              slopeDeg > MAX_SLOPE_DEG
                ? "var(--signal-warn)"
                : "var(--signal-high)"
            }
          />

          <TelemetryValue
            label="Battery"
            value={currentBatteryPct !== undefined ? `${currentBatteryPct.toFixed(0)}%` : "—"}
            color={
              currentBatteryPct === undefined
                ? "var(--text-primary)"
                : currentBatteryPct < 15
                  ? "var(--signal-flag)"
                  : currentBatteryPct < 40
                    ? "var(--signal-warn)"
                    : "var(--signal-high)"
            }
          />

          <TelemetryValue
            label="Speed"
            value={currentSpeedMs !== undefined ? `${currentSpeedMs.toFixed(3)} m/s` : "—"}
          />

          <TelemetryValue
            label="Illumination"
            value={currentIllumFrac !== undefined ? `${(currentIllumFrac * 100).toFixed(1)}%` : "—"}
          />
        </div>

        <div
          style={{
            display: "flex",
            gap: "20px",
            alignItems: "center",
          }}
        >
          <TelemetryValue
            label="Playback"
            value={`${elapsedSeconds.toFixed(1)} / ${(SIM_DURATION_MS / 1000).toFixed(1)} s`}
          />

          <TelemetryValue
            label="Distance"
            value={`${elapsedKm.toFixed(2)} / ${totalDistanceKm.toFixed(2)} km`}
          />

          <TelemetryValue
            label="Hazard"
            value={currentHazard}
            color={
              currentHazard === "High"
                ? "var(--signal-flag)"
                : currentHazard === "Medium"
                  ? "var(--signal-warn)"
                  : "var(--signal-high)"
            }
          />

          <button
            onClick={toggleSimulation}
            disabled={plannedRoute.length < 2}
            style={{
              padding: "10px 22px",
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              fontWeight: 700,
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              background: simComplete
                ? "var(--signal-high)"
                : simRunning
                  ? "var(--signal-flag)"
                  : PATH_COLOR,
              color: "#fff",
              border: "none",
              borderRadius: "var(--radius-sm)",
              cursor:
                plannedRoute.length > 1
                  ? "pointer"
                  : "default",
              opacity:
                plannedRoute.length > 1
                  ? 1
                  : 0.5,
            }}
          >
            {simComplete
              ? "Replay"
              : simRunning
                ? "Pause"
                : simProgress > 0
                  ? "Resume"
                  : "Start Traverse"}
          </button>
        </div>
      </div>


      {/* MAIN CONTENT */}
      <div
        className="traverse-layout"
        style={{
          flex: 1,
          display: "grid",
          gridTemplateColumns: "1fr 280px",
          overflow: "hidden",
        }}
      >
        {/* 3D VIEW */}
        <section
          style={{
            position: "relative",
            background: "var(--surface)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              zIndex: 10,
              padding: "12px 20px",
              display: "flex",
              justifyContent: "space-between",
              pointerEvents: "none",
            }}
          >
            <div>
              <div className="label-caps">3D Topography · LOLA DEM</div>

              <h1
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "18px",
                  color: "var(--text-primary)",
                  margin: "4px 0 0",
                  letterSpacing: "-0.01em",
                }}
              >
                {selectedCandidate.label}
              </h1>
            </div>

            <div style={{ textAlign: "right" }}>
              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "16px",
                  color: PATH_COLOR,
                }}
              >
                {Math.round(simProgress * 100)}%
              </div>

              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  color: "var(--text-muted)",
                  marginTop: "4px",
                  letterSpacing: "0.06em",
                }}
              >
                {totalDistanceKm.toFixed(2)} KM A* PATH · MAX SLOPE{" "}
                {maxRouteSlope.toFixed(1)}°
              </div>
            </div>
          </div>

          {simComplete && (
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform:
                  "translate(-50%, -50%)",
                zIndex: 30,
                padding: "18px 28px",
                background:
                  "color-mix(in srgb, var(--surface) 85%, transparent)",
                border: "1px solid var(--signal-high)",
                borderRadius: "var(--radius-lg)",
                textAlign: "center",
                backdropFilter: "blur(8px)",
              }}
            >
              <div
                className="label-caps"
                style={{ color: "var(--signal-high)" }}
              >
                Mission Complete
              </div>

              <div
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "22px",
                  color: "var(--text-primary)",
                  marginTop: "6px",
                }}
              >
                Ice Target Reached
              </div>

              <div
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "11px",
                  color: "var(--text-secondary)",
                  marginTop: "8px",
                }}
              >
                A* traverse playback completed in {(SIM_DURATION_MS / 1000).toFixed(0)} seconds
              </div>
            </div>
          )}

          <div
            style={{
              width: "100%",
              height: "100%",
            }}
          >
            {mounted &&
            dataReady &&
            plannedRoute.length > 0 &&
            currentPoint ? (
              <Canvas
                shadows
                dpr={[1, 2]}
                camera={{
                  position: [19, 23, 19],
                  fov: 38,
                  near: 0.1,
                  far: 100,
                }}
                gl={{
                  antialias: true,
                  toneMapping:
                    THREE.ACESFilmicToneMapping,
                  toneMappingExposure: 1,
                }}
              >
                <LightingRig />

                <CraterMesh
                  candidateId={candidateId}
                  terrain={terrain}
                />

                {/*
                  The full red route is always shown,
                  including the final path to the ice.
                */}
                <PathLine points={plannedRoute} />

                <IceLayer terrain={terrain} />

                {boulderData && (
                  <BoulderMarkers
                    boulders={boulderData.boulders}
                    terrain={terrain}
                    scale={rimLookup.scale}
                  />
                )}

                <LandingSiteMarker point={plannedRoute[0]} />

                <Rover
                  point={currentPoint}
                  isMoving={simRunning}
                  terrain={terrain}
                />

                <OrbitControls
                  makeDefault
                  enablePan
                  screenSpacePanning
                  minPolarAngle={0.12}
                  maxPolarAngle={
                    Math.PI / 2 - 0.06
                  }
                  minDistance={7}
                  maxDistance={55}
                  enableDamping
                  dampingFactor={0.06}
                  target={[0, -1.3, 0]}
                />
              </Canvas>
            ) : (
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--text-muted)",
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                }}
              >
                Loading terrain and computing A* route…
              </div>
            )}
          </div>
        </section>

        {/* RIGHT PANEL */}
        <section
          style={{
            background: "var(--surface)",
            borderLeft:
              "1px solid var(--border)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "12px 16px",
              borderBottom:
                "1px solid var(--border)",
            }}
          >
            <div
              className="label-caps"
              style={{ marginBottom: "8px" }}
            >
              Traverse Planning
            </div>

            <p
              style={{
                margin: 0,
                fontFamily: "var(--font-body)",
                fontSize: "12px",
                color: "var(--text-secondary)",
                lineHeight: 1.55,
              }}
            >
              Weighted A* search over real slope, illumination, and
              detected-boulder cost grids, from a selected landing
              site to the ice-evidence target — real obstacles cost
              real detours, not a straight line down the slope.
            </p>

            <select
              value={selectedCandidateId}
              onChange={(e) => {
                setSelectedCandidateId(e.target.value);
                setSimProgress(0);
                setSimRunning(false);
                setSimComplete(false);
              }}
              style={{
                marginTop: "10px",
                width: "100%",
                fontFamily: "var(--font-mono)",
                fontSize: "12px",
                padding: "6px 10px",
                background: "transparent",
                color: "var(--text-primary)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)",
                cursor: "pointer",
              }}
            >
              {ALL_TRAVERSE_SITES.map((site) => (
                <option key={site.id} value={site.id}>
                  {site.id === FAUSTINI.id || site.id === CABEUS.id
                    ? `${spIdLabel(site.id)} ${site.label}`
                    : "isPrimary" in site && site.isPrimary
                      ? `${site.label} (Primary)`
                      : site.label}
                </option>
              ))}
            </select>
          </div>

          {/* LEGEND */}
          <div
            style={{
              padding: "10px 16px",
              borderBottom:
                "1px solid var(--border)",
            }}
          >
            {[
              {
                color: PATH_COLOR,
                label: "A*-Planned Rover Path",
              },
              {
                color: "#7ec8e8",
                label: "Surface Ice Layer",
              },
              {
                color: "#a83a3a",
                label: "Steep Terrain",
              },
            ].map(({ color, label }) => (
              <div
                key={label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  margin: "5px 0",
                }}
              >
                <div
                  style={{
                    width: "13px",
                    height: "4px",
                    background: color,
                    borderRadius: "var(--radius-sm)",
                  }}
                />

                <span
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    color: "var(--text-secondary)",
                  }}
                >
                  {label}
                </span>
              </div>
            ))}
          </div>

          {/* CURRENT STATE */}
          <div
            style={{
              padding: "10px 16px",
              borderBottom:
                "1px solid var(--border)",
            }}
          >
            <TelemetryRow
              label="Progress"
              value={`${Math.round(
                simProgress * 100
              )}%`}
            />

            <TelemetryRow
              label="Simulation Time"
              value={`${elapsedSeconds.toFixed(1)} s`}
            />

            <TelemetryRow
              label="Terrain Slope"
              value={currentSlope}
              color={
                slopeDeg > MAX_SLOPE_DEG
                  ? "var(--signal-warn)"
                  : "var(--signal-high)"
              }
            />

            <TelemetryRow
              label="Hazard"
              value={currentHazard}
            />

            <TelemetryRow
              label="Route Point"
              value={`${currentRouteIndex + 1} / ${
                plannedRoute.length
              }`}
            />
          </div>

          {/* WAYPOINT LIST */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "4px 0",
            }}
          >
            {keyWaypoints.map((waypoint) => {
              const visited =
                simProgress >= waypoint.progress;

              const current =
                Math.abs(
                  simProgress - waypoint.progress
                ) < 0.035;

              return (
                <div
                  key={`${waypoint.type}-${waypoint.index}`}
                  onMouseEnter={() =>
                    setActiveWaypoint(waypoint.index)
                  }
                  onMouseLeave={() =>
                    setActiveWaypoint(null)
                  }
                  style={{
                    padding: "7px 16px",
                    display: "flex",
                    alignItems: "center",
                    gap: "9px",
                    cursor: "pointer",
                    borderLeft: current
                      ? `2px solid ${PATH_COLOR}`
                      : "2px solid transparent",
                    background: current
                      ? "rgba(196,162,104,0.1)"
                      : "transparent",
                  }}
                >
                  <div
                    style={{
                      width: "7px",
                      height: "7px",
                      borderRadius: "50%",
                      flexShrink: 0,
                      background: visited
                        ? PATH_COLOR
                        : "var(--border)",
                      boxShadow: current
                        ? `0 0 8px ${PATH_COLOR}`
                        : "none",
                    }}
                  />

                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "11px",
                        color: visited
                          ? "var(--text-primary)"
                          : "var(--text-secondary)",
                      }}
                    >
                      {waypoint.label}
                    </div>

                    <div
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "9px",
                        color: "var(--text-muted)",
                        marginTop: "3px",
                        letterSpacing: "0.04em",
                      }}
                    >
                      SLOPE{" "}
                      {waypoint.slopeDeg.toFixed(1)}°
                    </div>
                  </div>

                  {waypoint.type === "landing" && (
                    <span
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "9px",
                        letterSpacing: "0.06em",
                        color: "var(--signal-high)",
                      }}
                    >
                      START
                    </span>
                  )}

                  {waypoint.type === "destination" && (
                    <span
                      style={{
                        fontFamily: "var(--font-mono)",
                        fontSize: "9px",
                        letterSpacing: "0.06em",
                        color: "#7ec8e8",
                      }}
                    >
                      ICE
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          {/* ACTIVE WAYPOINT */}
          {activeWaypoint !== null && (
            <div
              style={{
                padding: "9px 16px",
                borderTop:
                  "1px solid var(--border)",
                background:
                  "rgba(196,162,104,0.05)",
              }}
            >
              {(() => {
                const waypoint =
                  keyWaypoints.find(
                    (item) =>
                      item.index === activeWaypoint
                  );

                if (!waypoint) {
                  return null;
                }

                return (
                  <>
                    <TelemetryRow
                      label="Selected"
                      value={waypoint.label}
                      color={PATH_COLOR}
                    />

                    <TelemetryRow
                      label="Slope"
                      value={`${waypoint.slopeDeg.toFixed(
                        1
                      )}°`}
                    />

                    <TelemetryRow
                      label="Radius"
                      value={`${Math.hypot(
                        waypoint.x,
                        waypoint.z
                      ).toFixed(2)} u`}
                    />
                  </>
                );
              })()}
            </div>
          )}

          {/* BOTTOM STATS */}
          <div
            style={{
              padding: "10px 16px",
              borderTop:
                "1px solid var(--border)",
              background: "var(--surface)",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "10px",
              }}
            >
              <div>
                <SmallLabel>
                  Mission Duration
                </SmallLabel>

                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    color: withinMissionBudget
                      ? "var(--text-primary)"
                      : "var(--signal-warn)",
                  }}
                >
                  {missionDays.toFixed(2)} / {maxMissionDays.toFixed(0)}.0 days
                </div>
              </div>

              <div>
                <SmallLabel>
                  Battery Reserve
                </SmallLabel>

                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    color:
                      minBatterySoc < 15
                        ? "var(--signal-warn)"
                        : "var(--signal-high)",
                  }}
                >
                  {finalBatterySoc.toFixed(0)}% final ·{" "}
                  {minBatterySoc.toFixed(0)}% min
                </div>
              </div>

              <div>
                <SmallLabel>
                  Path Distance
                </SmallLabel>

                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    color: "var(--text-primary)",
                  }}
                >
                  {totalDistanceKm.toFixed(2)} km
                </div>
              </div>

              <div>
                <SmallLabel>
                  Max Route Slope
                </SmallLabel>

                <div
                  style={{
                    fontFamily: "var(--font-mono)",
                    fontSize: "11px",
                    color:
                      maxRouteSlope > MAX_SLOPE_DEG
                        ? "var(--signal-warn)"
                        : "var(--signal-high)",
                  }}
                >
                  {maxRouteSlope.toFixed(1)}°
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <style>{`
        @media (max-width: 1100px) {
          .traverse-layout {
            grid-template-columns: 1fr !important;
            grid-template-rows: 540px auto;
            overflow-y: auto !important;
          }

          .traverse-layout > section:nth-child(2) {
            border-left: none !important;
            border-top: 1px solid var(--border) !important;
            min-height: 420px;
          }
        }
      `}</style>
    </main>
  );
}
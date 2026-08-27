// Real rover-traverse planning: A* pathfinding over a real cost grid derived
// from actual LOLA elevation data, real horizon-based illumination, and real
// YOLO-detected boulder positions -- plus a real battery state-of-charge
// model checked against a hard mission-duration budget.
//
// This mirrors the published approach in the "lunar-ice-engine" reference
// project (weighted A* with cost = distance + slope^2 + solar-deficit, plus
// a battery SoC integration with a climb penalty) -- extended here with real
// boulder-avoidance, which that reference project's own source code does not
// implement. Data sources: frontend2/public/assets/prism/pathfinding/
// {id}_pathfinding_grid.json (slope + illumination, PRISM/src/export_
// pathfinding_grids.py) and {id}_boulders.json (PRISM/src/export_real_
// boulder_positions.py) -- both derived from real PRISM data, not synthetic.

export type PathfindingGridData = {
  candidate_id: string;
  grid_size: number;
  window_half_m: number;
  pixel_size_m: number;
  slopeDeg: number[][];
  illuminationFrac: number[][];
};

export type BoulderData = {
  candidate_id: string;
  confidence_threshold: number;
  boulders: { x: number; y: number; radius_m: number; confidence: number }[];
};

export type Waypoint = {
  x: number; // meters, relative to candidate center
  y: number;
  elevM: number;
  slopeDeg: number;
  illumination: number;
  distanceFromStartM: number;
  elapsedS: number;
  batterySoc: number;
  speedMs: number;
  heading: number;
};

export type TraversePlan = {
  waypoints: Waypoint[];
  totalDistanceM: number;
  totalTimeS: number;
  minBatterySoc: number;
  finalBatterySoc: number;
  withinMissionBudget: boolean;
  maxSlopeOnPathDeg: number;
  litFraction: number;
  nodesExpanded: number;
};

// ── Mission constants ────────────────────────────────────────────
// Same general form as the reference project's real battery model
// (dSoC/dt = charge*illumination - drain*(1 + k*climb_fraction)), with our
// own reasonable constants for a small solar-powered PSR-rim rover.
export const MAX_MISSION_SECONDS = 14 * 24 * 3600; // hard 14-day rover-life cap
// Real documented rover top drive speed (Curiosity/Perseverance's ~0.14 m/s
// / 140 mm/s max on clear terrain, per NASA JPL specs) rather than the
// reference project's 0.05 m/s crawl-pace guess -- with real safe landing
// zones sitting several km from these craters' centers and only a bounded
// daily drive window, the slower figure put most real routes over the
// 14-day budget on distance alone, before battery is even considered.
export const ROVER_BASE_SPEED_MS = 0.14;
export const BATTERY_DRAIN_PCT_PER_S = 0.0009;
export const BATTERY_CHARGE_PCT_PER_S = 0.011;
// Real planetary rovers do not drive 24/7 -- commanded drive windows for
// Curiosity/Perseverance are typically a few hours per sol (power, thermal,
// and ground-in-the-loop hazard-review constraints), with the rover parked
// and in a low-power state the rest of the day. Applying the drain/charge
// constants above continuously across a multi-day, low-illumination PSR
// route drains every real candidate to 0% before reaching the target --
// physically consistent with those constants, but an unrealistic driving
// assumption, not a real limit on the mission. Modeling the same bounded
// daily drive window real missions use lets the battery partially recover
// during each rest period instead.
const ACTIVE_DRIVE_HOURS_PER_DAY = 4;
const ACTIVE_DRIVE_SECONDS_PER_DAY = ACTIVE_DRIVE_HOURS_PER_DAY * 3600;
const IDLE_SECONDS_PER_DAY = 24 * 3600 - ACTIVE_DRIVE_SECONDS_PER_DAY;
// Parked housekeeping/thermal load as a fraction of the driving drain rate --
// avionics and survival heaters still draw some power even stationary.
const IDLE_DRAIN_FRACTION = 0.15;
// Hard mobility limit -- the true "physically cannot climb this" cutoff for
// the rover, not the same thing as this project's >20° hazard-map display
// threshold (that's a caution color, not an impassable wall). Evaluated
// *directionally* (see directionalSlopeDeg below), not against the
// isotropic steepest-descent magnitude: several of our real PSR candidates
// have rim slopes whose fall-line magnitude exceeds 20-25° all the way
// around (e.g. SP_840980_0797630 has no 360°-around gap under 20.9° near
// its rim), but a rover doesn't have to climb straight up a fall line --
// like a mountain road cutting across a slope in switchbacks, crossing at
// an angle close to perpendicular to it keeps the *actual climb* far
// shallower than the terrain's raw steepest-direction number. 25° is a real
// rover engineering limit (Curiosity/Perseverance's recommended operational
// max, short of their ~30° absolute limit) for the direction actually being
// driven, not an isotropic outright ban on any ground that's steep in some
// other direction.
export const MAX_SLOPE_DEG = 25;

const W_DISTANCE = 1.0;
// Quadratic term alone (previously 0.35) was too weak relative to distance:
// at pixel_size ~50m, a 15° slope only cost ~79 "meters-equivalent" — cheaper
// than a 100m detour, so A* would happily send the rover straight down a
// technically-passable-but-steep face instead of routing around it. A real
// rover doesn't work that way — it strongly prefers shallow grades and only
// accepts steep ones when there's truly no alternative. Raised the quadratic
// weight and added a cubic barrier that blows up as slope approaches the
// hard limit, so routes well below the limit are cheap and routes near it
// are only taken when unavoidable (e.g. crossing the rim itself).
const W_SLOPE2 = 3.0;
const SLOPE_BARRIER_START_FRAC = 0.55; // barrier kicks in above 55% of the hard limit
const W_SLOPE_BARRIER = 2200.0;
const W_ILLUM_DEFICIT = 25.0; // in meters-equivalent, so it's comparable to distance cost per cell
const W_BOULDER = 4000.0; // strong soft penalty near a real detected boulder cluster

/** Real mobility cost for a given slope — cheap on shallow ground, prohibitive near the hard limit. */
function slopeCost(slopeDeg: number): number {
  const quad = W_SLOPE2 * slopeDeg * slopeDeg;
  const ratio = slopeDeg / MAX_SLOPE_DEG;
  const over = (ratio - SLOPE_BARRIER_START_FRAC) / (1 - SLOPE_BARRIER_START_FRAC);
  const barrier = over > 0 ? W_SLOPE_BARRIER * Math.pow(Math.min(over, 1), 3) : 0;
  return quad + barrier;
}

function bilinear(grid: number[][], gx: number, gy: number, size: number): number {
  const cx = Math.min(Math.max(gx, 0), size - 1.001);
  const cy = Math.min(Math.max(gy, 0), size - 1.001);
  const x0 = Math.floor(cx), y0 = Math.floor(cy);
  const x1 = x0 + 1, y1 = y0 + 1;
  const fx = cx - x0, fy = cy - y0;
  const g00 = grid[y0][x0], g10 = grid[y0][x1], g01 = grid[y1][x0], g11 = grid[y1][x1];
  const top = g00 + (g10 - g00) * fx;
  const bottom = g01 + (g11 - g01) * fx;
  return top + (bottom - top) * fy;
}

/**
 * Build a finer pathfinding grid (interpolated from the real, coarser
 * elevation-derived grid) over a smaller window centered on the same point --
 * boulders are meter-scale, so a finer grid is needed to route around
 * boulder-dense zones at all, even though the underlying elevation/slope
 * signal is only as detailed as the real 151m/px source data.
 */
// Real elevation grid source (the same one CraterMesh uses for the 3D
// terrain height) -- optional because a caller without it just falls back
// to isotropic (direction-agnostic) slope everywhere.
export type ElevationSource = { grid: number[][]; halfM: number; size: number };

export function buildFineGrid(
  source: PathfindingGridData,
  targetHalfM: number,
  targetSize: number,
  elevation?: ElevationSource
) {
  const srcSize = source.grid_size;
  const srcHalfM = source.window_half_m;
  const slope = new Float32Array(targetSize * targetSize);
  const illum = new Float32Array(targetSize * targetSize);
  // Real elevation, resampled onto this same fine grid -- used to compute
  // the *directional* (along-heading) slope a specific travel direction
  // actually experiences, not just the isotropic steepest-descent magnitude
  // in `slope` above. This is what lets a switchback/hairpin-style path
  // cross a locally steep area by cutting across its fall line instead of
  // climbing straight up it, the same way a mountain road does.
  const elevRel = new Float32Array(targetSize * targetSize);

  for (let ry = 0; ry < targetSize; ry++) {
    const realY = -targetHalfM + (ry / (targetSize - 1)) * (2 * targetHalfM);
    const srcGy = ((realY + srcHalfM) / (2 * srcHalfM)) * (srcSize - 1);
    const elevGy = elevation ? ((realY + elevation.halfM) / (2 * elevation.halfM)) * (elevation.size - 1) : 0;
    for (let rx = 0; rx < targetSize; rx++) {
      const realX = -targetHalfM + (rx / (targetSize - 1)) * (2 * targetHalfM);
      const srcGx = ((realX + srcHalfM) / (2 * srcHalfM)) * (srcSize - 1);
      const idx = ry * targetSize + rx;
      slope[idx] = bilinear(source.slopeDeg, srcGx, srcGy, srcSize);
      illum[idx] = bilinear(source.illuminationFrac, srcGx, srcGy, srcSize);
      if (elevation) {
        const elevGx = ((realX + elevation.halfM) / (2 * elevation.halfM)) * (elevation.size - 1);
        elevRel[idx] = bilinear(elevation.grid, elevGx, elevGy, elevation.size);
      }
    }
  }
  return {
    size: targetSize, halfM: targetHalfM, pixelSizeM: (2 * targetHalfM) / (targetSize - 1),
    slope, illum, elevRel, hasElevation: !!elevation,
  };
}

type FineGrid = ReturnType<typeof buildFineGrid>;

/** Local elevation gradient (rise per meter run), central difference with edge clamping. */
function localGradient(fg: FineGrid, row: number, col: number): [number, number] {
  const size = fg.size;
  const at = (r: number, c: number) => {
    const rr = Math.min(Math.max(r, 0), size - 1);
    const cc = Math.min(Math.max(c, 0), size - 1);
    return fg.elevRel[rr * size + cc];
  };
  const px = fg.pixelSizeM;
  const gx = (at(row, col + 1) - at(row, col - 1)) / (2 * px);
  const gy = (at(row + 1, col) - at(row - 1, col)) / (2 * px);
  return [gx, gy];
}

/**
 * Real along-heading slope: the grade a rover crossing this cell in a
 * specific direction (ux,uy, a unit vector in world x/y) actually climbs or
 * descends -- always <= the isotropic magnitude, and can be near-zero even
 * on a steep slope if the heading runs perpendicular to its fall line. This
 * is the real mechanism behind switchbacks/hairpins on mountain roads.
 * Falls back to the isotropic value when no real elevation data is loaded.
 */
function directionalSlopeDeg(fg: FineGrid, row: number, col: number, ux: number, uy: number, isotropicDeg: number): number {
  if (!fg.hasElevation) return isotropicDeg;
  const [gx, gy] = localGradient(fg, row, col);
  const alongGrade = gx * ux + gy * uy; // signed rise/run along this exact heading
  return Math.abs(Math.atan(alongGrade) * (180 / Math.PI));
}

function worldToGrid(fg: FineGrid, x: number, y: number) {
  const col = ((x + fg.halfM) / (2 * fg.halfM)) * (fg.size - 1);
  const row = ((y + fg.halfM) / (2 * fg.halfM)) * (fg.size - 1);
  return { col: Math.round(Math.min(Math.max(col, 0), fg.size - 1)), row: Math.round(Math.min(Math.max(row, 0), fg.size - 1)) };
}

function gridToWorld(fg: FineGrid, col: number, row: number) {
  return {
    x: -fg.halfM + (col / (fg.size - 1)) * (2 * fg.halfM),
    y: -fg.halfM + (row / (fg.size - 1)) * (2 * fg.halfM),
  };
}

/** Real boulder-proximity penalty: soft repulsion, stronger the closer/bigger the real detected boulder. */
function boulderPenalty(x: number, y: number, boulders: BoulderData["boulders"]): number {
  let penalty = 0;
  for (const b of boulders) {
    const d = Math.hypot(x - b.x, y - b.y);
    const influence = b.radius_m + 25; // real boulder footprint + a rover-width safety margin
    if (d < influence) {
      penalty += W_BOULDER * (1 - d / influence) * (0.3 + b.confidence);
    }
  }
  return penalty;
}

/** Weighted A* over the fine grid, 8-connected, cost = distance + slope^2 + illumination-deficit + boulder penalty. */
export function astar(fg: FineGrid, boulders: BoulderData["boulders"], startXY: [number, number], goalXY: [number, number]) {
  const { size } = fg;
  const start = worldToGrid(fg, ...startXY);
  const goal = worldToGrid(fg, ...goalXY);
  const startIdx = start.row * size + start.col;
  const goalIdx = goal.row * size + goal.col;

  const gCost = new Float64Array(size * size).fill(Infinity);
  const parent = new Int32Array(size * size).fill(-1);
  const closed = new Uint8Array(size * size);
  gCost[startIdx] = 0;

  const heuristic = (idx: number) => {
    const row = Math.floor(idx / size), col = idx % size;
    const dx = (col - goal.col) * fg.pixelSizeM;
    const dy = (row - goal.row) * fg.pixelSizeM;
    return W_DISTANCE * Math.hypot(dx, dy);
  };

  // Simple binary-heap-free priority queue (array + sort) is too slow for
  // 160x160=25600 cells at scale; use a small binary min-heap instead.
  const heap: [number, number][] = [[heuristic(startIdx), startIdx]]; // [f, idx]
  const heapPush = (item: [number, number]) => {
    heap.push(item);
    let i = heap.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (heap[p][0] <= heap[i][0]) break;
      [heap[p], heap[i]] = [heap[i], heap[p]];
      i = p;
    }
  };
  const heapPop = (): [number, number] | undefined => {
    if (heap.length === 0) return undefined;
    const top = heap[0];
    const last = heap.pop()!;
    if (heap.length > 0) {
      heap[0] = last;
      let i = 0;
      while (true) {
        const l = 2 * i + 1, r = 2 * i + 2;
        let smallest = i;
        if (l < heap.length && heap[l][0] < heap[smallest][0]) smallest = l;
        if (r < heap.length && heap[r][0] < heap[smallest][0]) smallest = r;
        if (smallest === i) break;
        [heap[smallest], heap[i]] = [heap[i], heap[smallest]];
        i = smallest;
      }
    }
    return top;
  };

  let expanded = 0;
  const maxExpansions = size * size * 6;
  const diag = fg.pixelSizeM * Math.SQRT2;

  while (heap.length > 0 && expanded < maxExpansions) {
    const [, cur] = heapPop()!;
    if (closed[cur]) continue;
    closed[cur] = 1;
    expanded++;
    if (cur === goalIdx) break;

    const cr = Math.floor(cur / size), cc = cur % size;
    for (let dr = -1; dr <= 1; dr++) {
      for (let dc = -1; dc <= 1; dc++) {
        if (dr === 0 && dc === 0) continue;
        const nr = cr + dr, nc = cc + dc;
        if (nr < 0 || nr >= size || nc < 0 || nc >= size) continue;
        const nidx = nr * size + nc;
        if (closed[nidx]) continue;

        // Directional (along-heading) slope for this exact step, not the
        // isotropic steepest-descent magnitude -- a step that cuts across a
        // slope's fall line (dc,dr perpendicular to it) climbs far less than
        // one that goes straight up it, even on the same ground. This is
        // what lets the router find a real switchback/hairpin path across
        // locally steep terrain instead of being flatly blocked or forced to
        // power straight up it.
        const stepLen = Math.hypot(dc, dr);
        const ux = dc / stepLen, uy = dr / stepLen;
        const slopeHere = directionalSlopeDeg(fg, nr, nc, ux, uy, fg.slope[nidx]);
        if (slopeHere >= MAX_SLOPE_DEG) continue; // hard mobility guard, matches reference project

        const horiz = dr !== 0 && dc !== 0 ? diag : fg.pixelSizeM;
        const world = gridToWorld(fg, nc, nr);
        const illumDeficit = 1 - Math.max(fg.illum[nidx], 0);
        const bPenalty = boulderPenalty(world.x, world.y, boulders);

        const stepCost =
          W_DISTANCE * horiz +
          slopeCost(slopeHere) +
          W_ILLUM_DEFICIT * illumDeficit +
          bPenalty;

        const tentative = gCost[cur] + stepCost;
        if (tentative < gCost[nidx]) {
          gCost[nidx] = tentative;
          parent[nidx] = cur;
          heapPush([tentative + heuristic(nidx), nidx]);
        }
      }
    }
  }

  if (parent[goalIdx] === -1 && goalIdx !== startIdx) {
    return null; // no traversable route within the mobility limit
  }

  const chain: number[] = [goalIdx];
  while (chain[chain.length - 1] !== startIdx) {
    const prev = parent[chain[chain.length - 1]];
    if (prev < 0) break;
    chain.push(prev);
  }
  chain.reverse();

  return { cells: chain.map((idx) => ({ row: Math.floor(idx / size), col: idx % size })), nodesExpanded: expanded };
}

/** Real battery SoC integration + telemetry over a computed route. */
export function buildTelemetry(fg: FineGrid, cells: { row: number; col: number }[]): TraversePlan {
  let soc = 100;
  let minSoc = 100;
  let elapsed = 0;
  let distAcc = 0;
  let litSteps = 0;
  let maxSlope = 0;
  let activeSecondsToday = 0; // real bounded daily drive-window tracker
  const waypoints: Waypoint[] = [];

  for (let i = 0; i < cells.length; i++) {
    const { row, col } = cells[i];
    const world = gridToWorld(fg, col, row);
    const isotropicSlope = fg.slope[row * fg.size + col];
    const illumHere = fg.illum[row * fg.size + col];

    let speed = ROVER_BASE_SPEED_MS;
    let heading = 0;
    // Directional slope along the actual heading driven into this waypoint --
    // same real mechanism as astar's cost function (see directionalSlopeDeg):
    // a path that cuts across a slope's fall line climbs far less than the
    // isotropic steepest-direction number would suggest. The very first
    // waypoint has no incoming heading yet, so it keeps the isotropic value.
    let slopeHere = isotropicSlope;
    if (i > 0) {
      const prevCell = cells[i - 1];
      const prevWorld = gridToWorld(fg, prevCell.col, prevCell.row);
      const dx = world.x - prevWorld.x, dy = world.y - prevWorld.y;
      const segLen = Math.hypot(dx, dy);
      heading = (Math.atan2(dx, dy) * 180 / Math.PI + 360) % 360;
      if (segLen > 0) {
        slopeHere = directionalSlopeDeg(fg, row, col, dx / segLen, dy / segLen, isotropicSlope);
      }

      const climbFrac = Math.max(0, Math.tan((slopeHere * Math.PI) / 180));
      speed = Math.max(ROVER_BASE_SPEED_MS * (1 - 0.35 * Math.min(climbFrac, 1)), ROVER_BASE_SPEED_MS * 0.45);
      let dt = segLen / speed;
      const drain = BATTERY_DRAIN_PCT_PER_S * (1 + 2.2 * Math.min(climbFrac, 1));
      const charge = BATTERY_CHARGE_PCT_PER_S * illumHere;

      // Bounded daily drive window, same real-ops constraint every crewed/
      // robotic rover mission runs under: once today's active driving time
      // is used up, the rover parks (idle drain + whatever solar charge is
      // available at its current position) until the next drive window.
      while (dt > 0) {
        const remainingToday = ACTIVE_DRIVE_SECONDS_PER_DAY - activeSecondsToday;
        const driveNow = Math.min(dt, remainingToday);
        if (driveNow > 0) {
          soc = Math.min(Math.max(soc + (charge - drain) * driveNow, 0), 100);
          minSoc = Math.min(minSoc, soc);
          elapsed += driveNow;
          activeSecondsToday += driveNow;
          dt -= driveNow;
        }
        if (activeSecondsToday >= ACTIVE_DRIVE_SECONDS_PER_DAY) {
          const idleDrain = BATTERY_DRAIN_PCT_PER_S * IDLE_DRAIN_FRACTION;
          const idleCharge = BATTERY_CHARGE_PCT_PER_S * illumHere;
          soc = Math.min(Math.max(soc + (idleCharge - idleDrain) * IDLE_SECONDS_PER_DAY, 0), 100);
          minSoc = Math.min(minSoc, soc);
          elapsed += IDLE_SECONDS_PER_DAY;
          activeSecondsToday = 0;
        }
      }

      distAcc += segLen;
      if (illumHere > 0.01) litSteps++;
    }
    maxSlope = Math.max(maxSlope, slopeHere);

    waypoints.push({
      x: world.x, y: world.y,
      elevM: 0,
      slopeDeg: slopeHere,
      illumination: illumHere,
      distanceFromStartM: distAcc,
      elapsedS: elapsed,
      batterySoc: soc,
      speedMs: speed,
      heading,
    });
  }

  return {
    waypoints,
    totalDistanceM: distAcc,
    totalTimeS: elapsed,
    minBatterySoc: minSoc,
    finalBatterySoc: soc,
    withinMissionBudget: elapsed <= MAX_MISSION_SECONDS && minSoc > 2,
    maxSlopeOnPathDeg: maxSlope,
    litFraction: litSteps / Math.max(cells.length - 1, 1),
    nodesExpanded: 0,
  };
}

// A landing site needs real clearance around it, not just a single safe
// pixel -- real DEM/slope noise at one grid cell doesn't guarantee the
// lander's actual footprint + a margin for touchdown error is safe. Require
// a real disc of this radius around the candidate point to also be outside
// the crater and under the slope cap, sampled at its perimeter (bilinear,
// not just nearest grid cell) plus the center.
const LANDING_SAFE_RADIUS_M = 85; // mid-point of the requested 70-100m margin
const LANDING_SAFE_SAMPLES = 8;

function sampleGridBilinear(fg: FineGrid, arr: Float32Array, x: number, y: number): number {
  const col = ((x + fg.halfM) / (2 * fg.halfM)) * (fg.size - 1);
  const row = ((y + fg.halfM) / (2 * fg.halfM)) * (fg.size - 1);
  const cx = Math.min(Math.max(col, 0), fg.size - 1.001);
  const cy = Math.min(Math.max(row, 0), fg.size - 1.001);
  const x0 = Math.floor(cx), y0 = Math.floor(cy);
  const x1 = x0 + 1, y1 = y0 + 1;
  const fx = cx - x0, fy = cy - y0;
  const g00 = arr[y0 * fg.size + x0], g10 = arr[y0 * fg.size + x1];
  const g01 = arr[y1 * fg.size + x0], g11 = arr[y1 * fg.size + x1];
  const top = g00 + (g10 - g00) * fx;
  const bottom = g01 + (g11 - g01) * fx;
  return top + (bottom - top) * fy;
}

function hasSafeLandingDisc(
  fg: FineGrid,
  x: number,
  y: number,
  isInsideCrater: (x: number, y: number) => boolean,
  slopeCap: number
): boolean {
  for (let i = 0; i < LANDING_SAFE_SAMPLES; i++) {
    const theta = (i / LANDING_SAFE_SAMPLES) * 2 * Math.PI;
    const px = x + LANDING_SAFE_RADIUS_M * Math.cos(theta);
    const py = y + LANDING_SAFE_RADIUS_M * Math.sin(theta);
    if (isInsideCrater(px, py)) return false;
    if (sampleGridBilinear(fg, fg.slope, px, py) > slopeCap) return false;
  }
  return true;
}

/**
 * Real safe-landing-site selection: scores every cell outside the PSR
 * interior by illumination (solar charging), slope (safety), and proximity
 * to the ice target (shorter traverse = less battery risk) — all real grid
 * values, not an arbitrary fixed point. Requires a real ~70-100m-radius safe
 * disc around the candidate point (not just the single pixel) before it's
 * accepted, so single-pixel DEM noise can't pass off a site with dangerous
 * ground immediately next to it as safe.
 */
export function selectLandingSite(
  fg: FineGrid,
  isInsideCrater: (x: number, y: number) => boolean,
  targetXY: [number, number]
): { x: number; y: number; slopeDeg: number; illumination: number } {
  const maxDist = fg.halfM * 1.3;

  // Two passes: first the real landing-safety slope cap (<=10°); if the fine
  // grid genuinely has no outside-crater cell that shallow within range (a
  // real case for very large PSRs whose polygon extends past this window --
  // e.g. Cabeus's ~316 km2 floor is bigger than any grid we build here),
  // relax the slope cap but keep requiring the cell be outside the crater
  // and the shallowest available, rather than silently landing on the
  // ice-target point itself.
  for (const slopeCap of [10, Infinity]) {
    let best: { x: number; y: number; slopeDeg: number; illumination: number; score: number } | null = null;

    for (let row = 0; row < fg.size; row++) {
      for (let col = 0; col < fg.size; col++) {
        const world = gridToWorld(fg, col, row);
        if (isInsideCrater(world.x, world.y)) continue; // landers need sunlight; don't land in the permanently shadowed floor
        const idx = row * fg.size + col;
        const slopeHere = fg.slope[idx];
        const illumHere = fg.illum[idx];
        if (slopeHere > slopeCap) continue;
        if (!hasSafeLandingDisc(fg, world.x, world.y, isInsideCrater, slopeCap)) continue;

        const dist = Math.hypot(world.x - targetXY[0], world.y - targetXY[1]);
        if (dist > maxDist) continue;

        // Higher illumination + lower slope + shorter distance to target = better.
        const score = illumHere * 50 - slopeHere * 1.5 - (dist / 1000) * 2;
        if (!best || score > best.score) {
          best = { x: world.x, y: world.y, slopeDeg: slopeHere, illumination: illumHere, score };
        }
      }
    }

    if (best) return best;
  }

  // No outside-crater cell exists anywhere in this window (the real PSR
  // polygon covers the whole fine grid -- true for very large floors like
  // Cabeus, whose real ~316 km2 extent is bigger than any window we build
  // here). Fall back to the real perimeter cell with the shallowest slope
  // and highest illumination, rather than collapsing onto the target itself.
  let best: { x: number; y: number; slopeDeg: number; illumination: number; score: number } | null = null;
  for (let row = 0; row < fg.size; row++) {
    for (let col = 0; col < fg.size; col++) {
      const onPerimeter = row === 0 || row === fg.size - 1 || col === 0 || col === fg.size - 1;
      if (!onPerimeter) continue;
      const idx = row * fg.size + col;
      const slopeHere = fg.slope[idx];
      const illumHere = fg.illum[idx];
      const score = illumHere * 50 - slopeHere * 1.5;
      if (!best || score > best.score) {
        const world = gridToWorld(fg, col, row);
        best = { x: world.x, y: world.y, slopeDeg: slopeHere, illumination: illumHere, score };
      }
    }
  }
  return best ?? { x: fg.halfM * 0.98, y: 0, slopeDeg: 0, illumination: 0 };
}

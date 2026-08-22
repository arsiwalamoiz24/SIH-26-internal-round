# PRISM, explained simply

**What this project actually did, in plain language, from the beginning to the most recent results.**

---

## The one-paragraph version

We're looking for water ice hidden in permanently dark craters at the Moon's south pole, using satellite radar and other space-agency data instead of a shovel. We picked one specific dark crater as our best guess, gathered every kind of evidence we could reach for it — radar "texture" readings, a ground-steepness check, and a harder-won radar "purity" measurement — and it looked genuinely promising on paper. Then, as a final honesty check, we compared our method against real, previously-published, independently-confirmed ice sites and clearly-checked "no ice here" sites. Our scoring did **not** reliably tell the two groups apart, and the one site with rock-solid proof (a NASA probe that literally sampled the ground) scored the *worst* of all of them. That's an important, humbling result, and we're reporting it honestly instead of hiding it.

---

## 1. Why any of this matters

There's no water on the Moon's surface in most places — sunlight boils it away. But right at the poles, some crater floors never see sunlight at all (they're called **permanently shadowed regions**, or PSRs). Those spots are so cold that if water ice ever landed there, it could survive for billions of years, buried under the dust. Finding it matters because future astronauts could drink it, breathe it (split into oxygen), or turn it into rocket fuel — without hauling it up from Earth.

The problem: you can't see into a permanently dark crater with an ordinary camera. You need instruments that don't need sunlight — radar, which bounces its own signal off the ground and reads the echo.

## 2. Meet the candidate: `SP_840980_0797630`

This project didn't invent a candidate — one was already identified, in earlier work, by scanning radar data across the whole south polar region and flagging craters whose radar echo "looked icy." The one this whole investigation focuses on:

- **Where:** latitude −84.098°, longitude 79.764° — about 179 km from the actual pole.
- **What it is:** the floor of a permanently shadowed crater, roughly 14 km² — a little smaller than a small town.
- **Why it stood out:** its radar echo pattern resembled what you'd expect from a rough, jumbled, "fluffy" surface — the kind of texture ice deposits tend to produce — rather than smooth dust.

Everything from here is this project checking that candidate as rigorously as possible, with real satellite data, not guesswork.

## 3. Reading the radar

Radar doesn't take a picture — it sends a signal down and listens to what bounces back. *How* the signal changes on the way back tells you about the surface. Four of these "how it changed" measurements are the backbone of this project:

- **Pv (volume scattering fraction)** — roughly: "did the signal bounce off just the surface, or did it get scrambled by structure just underneath it?" Ice buried in fluffy regolith scrambles it more. Higher = more of that scrambled, structure-heavy signature.
- **CPR (circular polarization ratio)** — a measure of how much the radar's polarization ("spin") got flipped by the bounce. Icy, jumbled surfaces tend to flip it more than smooth dust.
- **T-Ratio** — a related polarization measurement, another angle on the same "rough vs. smooth" question.
- **SERD** — another scattering-based measurement; in this project it turned out to behave in a way that doesn't fit the simple "high = icy" story (more on that below).

**What we found for our candidate**, using the real ISRO Chandrayaan-2 radar mosaic (not a mockup):

| Measurement | This spot's reading | How that compares to the rest of the south pole |
|---|---|---|
| Pv | 0.454 | Higher than **94%** of the entire mapped south pole |
| CPR | 0.565 | Higher than **97%** of it |
| T-Ratio | 0.571 | Higher than **96%** of it |
| SERD | 0.673 | Higher than only **4%** of it (unusually *low*, not high) |

Three out of four readings put this crater near the very top of the whole south pole's radar "icy signature" ranking. That's a genuinely strong, real result. The fourth (SERD) doesn't fit the story, and rather than quietly drop it or explain it away, we ran a full separate investigation into *why* — see §6.

## 4. Is it actually a good landing spot?

Finding ice is one question. Landing a rover on it is another. We pulled real NASA elevation data (the same instrument that maps the whole Moon, LOLA) for this crater and its surroundings and measured the actual slope of the ground.

**The honest answer: probably not an easy landing.** The permanently shadowed floor itself averages a **22° slope** — steep — and about **79%** of that floor is steeper than the rough "too steep to be safe" line often used in mission planning (20°). The gentler approach terrain around it averages **9°**. So: promising radar signature, difficult terrain. Both facts are reported side by side, not one hidden to protect the other.

## 5. The hardest measurement: DOP, and the mistake we caught

There's a fifth radar measurement — **degree of polarization (DOP)** — which needed something the other four didn't: data from one *specific* satellite pass over that *exact* spot, not a big combined map. That turned this into a real search-and-download problem, and it's worth telling honestly, mistake included.

**The setup:** Chandrayaan-2 has made 602 separate radar passes that fed into the big combined maps we used for Pv/CPR/SERD/T-Ratio. None of those 602 had been checked individually for whether they actually flew directly over our one small crater — that takes a much finer-grained check than "is it in the same general area."

**First attempt — a real mistake, caught before it caused harm:** We built an automated check using each pass's rough, boxy "coverage area" as stated in its file label. It flagged a match, and we downloaded that file — 4.88 gigabytes. Only *after* downloading it did a stricter, pixel-by-pixel check reveal that the actual imaged strip was a long, narrow, *tilted* ribbon — and our target sat about 75 km outside it. The boxy "coverage area" from the label had been drawn loosely around that tilted ribbon, like a rectangle drawn around a diagonal line, and our first check trusted the rectangle instead of the actual line. We deleted the wrong file, fixed the check to use the *true* tilted-shape boundary instead of the loose rectangle, and re-ran it against all 602 passes properly.

**The fix found the real thing:** Six of the 602 passes genuinely do fly over the crater. We picked the one with the most comfortable safety margin, downloaded it (1.92 GB, the actual pass, not a stand-in), and — for extra certainty — checked it against the pass's own built-in per-pixel location table. The nearest recorded point to our exact target coordinate was **91 meters** away. That's about the length of a football pitch, on a satellite pass — about as close to "exact" as this kind of data gets.

**The actual DOP reading, from real data, for the real spot:**

| DOP formula used | Reading |
|---|---|
| Standard formula (most trusted for this instrument) | **0.680** |
| Alternate formula #1 | 0.594 |
| Alternate formula #2 | 0.909 |

We separately researched a 2026 published paper that proposes "DOP below 0.13" as a strong sign of buried ice. Our number (0.680) doesn't come close to meeting that. But — and this matters — that paper's DOP is built from a *different* radar combination and a *different* calibration process than ours. We checked what we could find of their method and concluded that comparing our number straight to their 0.13 line isn't actually a fair, apples-to-apples test yet. So: doesn't meet their exact bar, but the comparison itself needs more work before that "doesn't meet" means much.

## 6. The SERD mystery, chased down properly

SERD (from §3) was the one reading that didn't fit the "higher = icier" pattern. Rather than shrug, we investigated the entire south-pole SERD map, all ~600 million pixels of it, not just our one crater.

**What we found:** about 43% of the big SERD map is marked "no data" — but almost all of that (99.99%) is simply the edges of the map where no radar pass ever actually flew (an expected, boring gap, not a mystery). A tiny leftover sliver of "no data" pixels (0.01%) sits *inside* the actually-imaged area, and those specific pixels are strongly linked to unusually high CPR readings nearby — suggesting SERD's calculation runs into some kind of mathematical limit exactly where CPR gets extreme. Good news for our candidate specifically: it has **zero** missing SERD pixels — this whole mystery doesn't affect our one crater's own reading, only explains why SERD behaves oddly *elsewhere* on the map.

## 7. Ranking our candidate against six others

An earlier stage of this project had already shortlisted seven promising craters (ours plus six others) using the same kind of radar screening. We built a transparent scoring method — no invented weights, just each crater's Pv/CPR/T-Ratio ranked against the other six and averaged — and our candidate came out **#1 of 7**. We're careful to call this a "physics evidence score," not a "probability of ice," because it isn't calibrated against any real confirmed-ice site (see §8) to know what a good score actually corresponds to in reality.

We also ran an unsupervised anomaly-detection method (no ice labels involved, just "does this crater look statistically unusual compared to 336 others with radar coverage") — our candidate came out **40th of 336**, a real but far more modest result, and one we're upfront uses features that aren't fully independent of how the candidate was chosen in the first place.

## 8. The reality check — and the honest, uncomfortable result

Everything above describes how *interesting* our one candidate looks by our own methods. It says nothing about whether our methods actually *work*. So we built an independent check.

**What "independent" means here:** we did not use anything PRISM itself produced. Instead we found two kinds of real, previously-published, outside evidence:

1. **LCROSS** — in 2009, NASA deliberately crashed a rocket stage into a crater called Cabeus and flew a spacecraft through the resulting dust plume with instruments that directly detected water. This is about as close to "confirmed" as lunar ice evidence gets — it's a physical sample, not radar guesswork.
2. **A 2018 published study** using a different instrument (a mineral-mapping camera on an earlier Indian mission, Chandrayaan-1) that had specifically searched named craters for a water-ice light signature, and reported, crater by crater, where it *was* found and — just as usefully — where it was specifically checked and **not** found.

We took 7 craters with real, published ice evidence and 5 craters explicitly checked and reported as ice-free, ran our exact same radar-reading process on all of them, and compared the results.

**The result: our readings could not tell the two groups apart.** The "ice confirmed" craters and the "checked, no ice" craters came back statistically indistinguishable on Pv, CPR, SERD, and T-Ratio. Worse, when we ranked all of them by our evidence score, the single most trustworthy site on the entire list — Cabeus, the one NASA *physically sampled* — came out **dead last**, scoring lower than every "no ice found" control crater.

We're not softening that. It's a real finding from real data, and it means our current scoring method, on its own, is not yet a reliable way to tell an icy crater from an ordinary one. It doesn't mean our original candidate has *no* ice — the check itself has real limits (small sample, and we could only use each crater's rough center point rather than its exact icy pixel, since that finer data isn't published anywhere we could find) — but it does mean nobody should treat a high PRISM score as proof.

## 9. Everything else that got built along the way

A few supporting pieces exist and work, even though they weren't the headline result:

- **A full georeferencing check** — proof that when we say "this pixel is at −84.098°, 79.764°," the math connecting the satellite image's grid to real Moon coordinates is correct to a vanishingly small error.
- **A comparison against someone else's public ice-detection project on GitHub** — cataloguing what they did that we should consider adopting (like never training a model on the same data used to find the label), what's a different formula that we shouldn't just borrow numbers from, and what's simply unfinished on both sides.
- **A planned-but-not-built slot for image-recognition tools** (the kind that would spot individual boulders or ice-textured patches in an up-close photo) — deliberately left as "not trained yet," because no labeled photo data of confirmed ice exists to train on, and faking that would be worse than leaving it blank.

## 10. Where things actually stand today

**Solid, real, and reproducible:**
- The candidate's location math is verified correct.
- Three of four radar readings (Pv, CPR, T-Ratio) are strongly elevated for this candidate compared to the rest of the south pole — a genuine, real pattern in real data.
- The terrain is real NASA elevation data, honestly showing a difficult, steep interior.
- A real, specific, individually-confirmed satellite pass over this exact crater was found (after fixing a real mistake along the way) and its DOP was genuinely computed from real data — not estimated, not borrowed from an unrelated file.
- The SERD anomaly has a data-backed explanation, and it doesn't taint our candidate's own reading.

**Genuinely uncertain, on the record:**
- We don't yet know if "high Pv/CPR/T-Ratio" as we've measured it actually predicts ice — our one independent check found it doesn't cleanly separate confirmed-ice sites from confirmed-empty ones.
- Our DOP number can't yet be honestly compared to the one published scientific threshold we found for it, because the formulas aren't calibrated the same way.
- The steep terrain is a real obstacle to any future landing attempt at this exact spot.

That combination — real infrastructure, real numbers, and an honest "we checked, and it's not proven yet" — is the actual, accurate state of this project.

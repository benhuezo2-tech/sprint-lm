# ALTIS Coaching the Short Sprints: the learned layer (Nov 21, 2026)

This file holds only what is new to the coaching mind. Rules already in SKILL.md, identity.md and persona.md (observation/interpretation/decision, keep-if/revise-if, one cue, evidence grading, measurement noise, safety scope) are not repeated here.

## Source ledger (read first)
- **The paid course itself was not read.** It is behind the athlete's login, and the browser tab he had open is on his computer, which the cloud session can't reach. Module titles are verified from the ALTIS product page: 12 modules, about 24 h, more than 160 videos, Dan Pfaff as primary author with Stuart McMillan, PJ Vazel, Andreas Behm, Kevin Tyler and others.
- **Read in full:** the free ALTIS e-book *200m Female Sprinter Training Program* (43 pp, 2019 season, an athlete with PRs of 11.18 and 22.44), written by McMillan, who calls it "the WHAT" behind this course. Tag **[ALTIS-primary]**.
- **ALTIS public pages:** *From Gun to Tape* (100 m pocket guide), *Stop Dragging Your Toes* (start/acceleration pocket guide), *Fluid and Ferocious* (Sep 2026), the Rich Roll podcast summary (May 2025), *Developing Team Speed* (Sep 2026), and the Foundation Course index. Tag **[ALTIS-public]**.
- **Secondary:** Sportsmith (C. Josse) for the intensity zones, a kinogram vendor guide for frame definitions, and search snippets. Tag **[secondary]**.
- **Blocked:** SimpliFaster (403), the ALTIS *Kinogram Method* e-book (no direct link) and the S-MAS paper (403). Nothing is cited from them. Where a module's paid content is unseen, the entry says so.
- **Literature** was verified on PubMed and is tagged with its design. Côté & Gilbert 2009 (doi:10.1260/174795409789623892) and Abraham & Collins 2011 (Quest 63:366, doi:10.1080/00336297.2011.10483687) were verified bibliographically on the web only. **[Synth]** marks my own synthesis.

## Module by module: content, evidence, and the decision it changes

**M2: Dynamics and mechanics of sprinting**
- Top speed rises with **greater support force, not faster limb repositioning.** Across 33 runners from 6.2 to 11.1 m/s, mean vertical force was 1.26× higher at 11.1 m/s and swing time did not differ (Weyand 2000, doi:10.1152/jappl.2000.89.5.1991; cross-sectional plus incline/decline manipulation).
- Sprinters front-load force. Faster sprinters (10.4 vs 8.7 m/s) applied more vertical force in the **first half of stance** (2.65 vs 2.21 body weights) but not the second (Clark & Weyand 2014, doi:10.1152/japplphysiol.00174.2014; n = 7 + 7).
- **Thigh angular velocity** tracks speed and limb vertical velocity at touchdown (R² > 0.70; Clark 2020, doi:10.1242/bio.053546; n = 40, cross-sectional). "Whip from the hip" is the mechanism for the front-loaded impulse.
- In acceleration, **force orientation beats force amount.** The slope of the ratio of horizontal to total force against speed correlated with 100 m (r > 0.73), and total force did not (Morin 2011, doi:10.1249/MSS.0b013e318216ea37; n = 12). Elite sprinters (9.95–10.29) show linear force-velocity and force-ratio-velocity relationships (Rabita 2015, doi:10.1111/sms.12389). Across one sprint, propulsive impulse drives acceleration from 55–95% of vmax, suppressing braking matters from 75–95%, and mean vertical force drives top speed (Nagahara 2018, doi:10.1123/jab.2016-0356; n = 18).
- McMillan splits a sprint into **quantity** (force, rate, direction) and **quality** (efficiency, absence of unnecessary tension). The elite stride is "fluid *and* ferocious", and under pressure the two rarely survive together [ALTIS-public, coach opinion].
- Performance has three levers: **Structure** (fixed or slow-changing: limb length, fiber type), **Function** (force, range of motion, endurance) and **Coordination** (organizing the movement). "Most athletes have structure and function. What they're missing is coordination." [ALTIS-public, coach opinion]
- **Decision it changes:** judge max-velocity work by fly output and by the touchdown-to-full-support region, where front-loaded force shows, not by cues that speed up the swing. Judge acceleration by projection and force direction.

**M3: Trainability, strategy, technical models, KPIs**
- At the elite level, annual within-athlete change is smaller than typical variation and the smallest worthwhile change. The determinants are still trainable: power, technique and sprint-specific endurance. Research mostly tests short maximal sprints with short recoveries, while practice uses a broad range of distances, intensities and recoveries tied to purpose (Haugen 2019, doi:10.1186/s40798-019-0221-0; integrative review). An athlete far from elite level has more trainable headroom than those elite figures suggest [Synth, likely].
- **Model versus bandwidth.** Pfaff: "You've got to coach to something" [secondary]. McMillan: coach to **technical bandwidths**, not a single model, and phase labels (drive, transition, max velocity) are "potentially misleading" because every step differs from the one before and after [ALTIS-public]. My reconciliation [Synth]: the model sets direction, the bandwidth sets tolerance, and only a deviation outside the bandwidth that is linked to an output is worth coaching.
- **Athlete types:** muscular sprinters tend to accelerate better; elastic sprinters hold speed better and tolerate more volume on longer reps (Pfaff [secondary]). ALTIS also sorts sprinters into "pushers" and "pullers" (e-book title only; the definitions were not reached).
- **Event model (new tool):** `scripts/sprintstats.py race`. It treats the 100 m as one velocity curve: mono-exponential rise v = vmax(1 − e^(−t/τ)), the field basis validated by Samozino 2016 (doi:10.1111/sms.12490; <5% bias against force plates), followed by a linear speed loss. In 100 m finals, vmax and mean power strongly determine performance (r > −0.80; Slawinski 2017, doi:10.1111/sms.12627). Example outputs [simulation; τ 1.3 s, RT 0.15 s and 3% loss from 60 m are placeholders]:
  - 11.90 corresponds to vmax ≈ 9.64 m/s; 10.22 corresponds to ≈ 11.49 m/s (+19%).
  - At 11.90: +1% vmax ≈ 0.10 s; τ −5% ≈ 0.07 s; one point less speed loss ≈ 0.02 s; RT −0.01 s = 0.01 s.
  - **Fly currency:** a 9.14 m fly of 0.95 s (9.62 m/s) models to 11.92; 0.94 s models to 11.81. **One hundredth on the 9.14 m fly ≈ one tenth in the 100.** 10.22 corresponds to a fly of about 0.80 s. The ±16.7 ms per gate of 60 fps video is therefore worth about ±0.17 s of modeled 100 m time, which is why fly decisions need 240 fps.
  - Limits: τ and the speed loss interact with vmax in reality, and a 9.14 m fly slightly underestimates true vmax. The model ranks levers; it does not predict races.

**M4: Starting ability** (the paid content is unseen; this comes from the *From Gun to Tape* outline [ALTIS-public])
- Teaching order: pedal set-up and foot placement → shoulders relative to the hands → weight on hands versus feet → head, spine and shoulder alignment → what the athlete thinks about before "set" → the rise into "set" → block clearance. "The race starts before the gun."
- **Decision:** the set position is a low-variance, repeatable skill. Fix it once, film it from the same angle, and then leave it alone unless block-clearance or 10 m times say otherwise.

**M5: Acceleration ability**
- Toe drag does not improve starting efficiency. It began as an error correction for exaggerated cyclical heel recovery, and ALTIS doesn't "obsess over low heel recovery" in the first steps. ALTIS claims maximum step frequency is reached by step 3–4 (not verified here). Footwear and surface are the two most significant environmental constraints. Changes are judged as part of the whole: "you can't rob Peter to pay Paul" [ALTIS-public].
- The acceleration problem changes considerably across the first 5–20 m, with longer contacts and lower body angles. ALTIS runs 30–40 minute acceleration blocks [ALTIS-public].
- Acceleration lasts roughly the first 3–6 s and depends relatively more on maximal strength, so ALTIS pairs it with zone 3 lifting [ALTIS-primary, coach opinion].
- **Sleds:** light loads (<10% body mass) give a small decrement in acceleration and a moderate gain in vmax in sprint-trained athletes. Moderate to very heavy loads give trivial to extremely large acceleration gains in team-sport and strength-trained athletes. Superiority over unresisted sprinting remains **equivocal** (Petrakos 2016, doi:10.1007/s40279-015-0422-8; systematic review of 11 studies). ALTIS uses 1080 Sprint 4-step bursts and band-resisted drills as tools, not as requirements.
- **Decision:** add a technical acceleration intervention only when τ or the 0–10 m split is the largest lever in race-time currency.

**M6: Maximum velocity and the ALTIS kinogram**
- Five frames. Stance: **touch-down, full support, toe-off.** Flight: **maximal vertical projection (MVP) and strike.** Strike is the point where the swing-leg hamstring is under maximal stretch [ALTIS via snippet].
- Practical frame picks [secondary]:
  - MVP: both feet parallel to the ground.
  - Strike: the opposite thigh perpendicular to the ground.
  - Full support: foot under the pelvis, toe plumb below the ASIS.
  - Toe-off: the last frame before the foot leaves the ground, with the front shin roughly parallel to the rear thigh.
  - Touch-down: the first contact frame. Landing well in front of the centre of mass means braking.
- ALTIS positions are "a starting point"; each coach sets the positions for their own group. One vendor guide puts it as "no pass mark … a way of seeing rather than a test to fail."
- **Validated alternative:** the S-MAS, a 12-item dichotomous score from 240 fps max-velocity video. In 126 elite footballers, each +1 point raised the rate of new sprint-related hamstring strain (incidence rate ratio 1.33, 95% CI 1.01–1.76, adjusted for age and previous injury; Bramah 2026, doi:10.1136/bjsports-2024-108600; prospective cohort). Transfer to track sprinters is unverified, and the 12 items were not retrieved.
- Progression: drills → wickets → flys [ALTIS-public]. "You don't get better at running by doing drills. You get better at running by running well." [ALTIS-public]
- **Decision:** use the kinogram for frame-locked comparisons over time (same frames, same camera). A position changes only when it sits outside the bandwidth and fly output agrees.

**M7: Speed endurance and the sprint finish**
- Efficiency means holding a higher percentage of vmax for longer, and some cues work against it [ALTIS-public].
- **Speed reserve:** when top speed rises, every lower speed becomes cheaper, so vmax is the root lever for short-sprint speed endurance [ALTIS-public, coach opinion; consistent with the race model].
- **Cue sequence:** force and aggression early, ease late. "Relax" works only after the quantity is established: "the right words, in the right order" [ALTIS-public]. Against the one-cue rule [Synth]: keep one cue per rep or race, and choose it for the largest lever. A sequence is a race plan, not a bundle of corrections.
- Pfaff's zones are blocks, acceleration, speed, special speed endurance and alactic runs, described as 120–150 m efforts [secondary]. The e-book's speed-endurance sessions use segment runs, 150 m reps at set times, and 80 m turnarounds cut off at a **5% drop-off**. The skill's 3% stop rule applies to maximal-quality reps. The two thresholds differ because the reps serve different purposes, not because one of them is wrong [Synth].

**M8–9: Teaching inventories** (the paid videos are unseen; this is the visible inventory from the e-book [ALTIS-primary])
- Drops-ins (a 1–3 step skip or hop into acceleration) and bursts (3–5 hard steps).
- Stick (on the shoulders) accelerations, stick wickets, and wickets over 15–21 banana hurdles at 190–230 cm spacings.
- Dribbles (ankle, calf or knee height) and dribble-bleed into stride.
- Sprint drills with a dowel or band resistance.
- Skips for distance and height, speed bounds, alternate-leg bounds.
- Hurdle hops, including "freeze" landings, and rudiment hops.
- Medicine-ball overhead-back and underhand-forward heaves.
- Fly 30 from 30, bend runs (full, half, off), segment runs, turnaround runs, curve-treadmill tempo.
- **Decision** [Synth]: an inventory item is a constraint that changes one variable of the movement problem. Pick it by which frame or which output is off, never for variety.

**M10: Sport injuries in sprinting**
- "Availability is the foundation of performance." "Probability, not prevention." Health is read as **Trait** (what the athlete brings over time), **State** (how they present today) and **Workload** (volume, intensity, density). Injury pathways are structural, functional and technical [ALTIS-public].
- Programs that include the Nordic hamstring exercise roughly halve hamstring injuries: risk ratio 0.49 (95% CI 0.32–0.74), 0.52 across RCTs only (van Dyk 2019, doi:10.1136/bjsports-2018-100045; meta-analysis of 15 studies, 8,459 athletes). The ALTIS program carries Nordics, glute-ham raises, single-leg hamstring isometrics and 6 s eccentrics all year.
- Exposure to ≥95% vmax in training was associated with lower injury odds than exposure capped at 85% (OR 0.12). Both under- and over-exposure raised risk, a U-shaped relationship (Malone 2017, doi:10.1016/j.jsams.2016.08.005; Gaelic football cohort, n = 37, observational).
- **Don't run load rules off the acute:chronic workload ratio.** There is no evidence supporting it for injury management (Impellizzeri 2020, doi:10.1123/ijspp.2019-0864).

**M11: Programming concepts for the short sprints** (the visible core, from the ALTIS-primary e-book)
- **Cycle unit:** 2- or 3-week cycles. The first ~10 weeks undulate: 2 weeks of intensification (loading through intensity) alternate with 2 weeks of extensification (loading through volume). Through the year the two converge into a 2:1 load:unload pattern.
- **Three-week roles:**
  - W1 Introduce: about 75% of W2's load, heavy teaching, high cognitive demand.
  - W2 Stabilize: about 25% more physical load, less cueing.
  - W3 Unload ("realization"): about 50% of W2, almost no teaching; the athlete expresses what was learned.
  - The tables label the weeks Introduction, Exploration and Stabilization.
- **Week:** Tuesday and Saturday are the protected main days, with Thursday secondary. Wednesday, Friday and Sunday are recovery. Monday is **Potentiation & Preparation** after a passive day off, because elite power athletes "perform better the day after doing something." What P&P contains is individual: lifts, hurdle hops, short accelerations, or for this athlete extensive tempo, which also became her pre-meet session. Developmental athletes likely need no P&P.
- **Upright days** mean volumes over 50 m at more than ~85% intensity. A third upright day is tolerable when intensity is below ~85%. Elites may need **7–10 days** after very high-intensity sessions. Younger athletes rarely need more than **48 h** and can handle three intense sessions a week.
- **Sequencing:** early in the year, one ability per day (acceleration *or* max speed *or* speed endurance). Later, several per session: acceleration before special endurance, wickets before speed endurance. Extensive skips or bounds of 40–60 m follow speed sessions.
- **Weight room** runs on the main track days, plus an optional light lift on P&P day, matched to the track work:
  - acceleration ↔ zone 3 (maximum strength)
  - max speed ↔ zone 1 (speed-strength, "dynamic effort")
  - speed endurance ↔ zone 2 (work capacity or hypertrophy)
  - Both protecting the main days and individualization override this pairing. Complexes (for example back squat + jump squat) come only after separate training hits diminishing returns.
- **Pfaff's imprint:** very few exercises, consistent loading from cycle to cycle, technical mastery. "There is wisdom in this consistency of load." Consistent structure is what makes adaptation understandable and predictable.
- **Decision it changes** [Synth]: a stable menu and a stable week are also a *measurement design*. Keeping the structure constant is what makes the athlete's response readable, which fixes the open-loop failure at its source. Judge learning in the realization week, not on teaching days.
- **Intensity zones** (Need for Speed, team-sport version, as % of max sprint speed [secondary, ~2021]): <65% maximal aerobic speed; 65–78% low; 78–88% moderate; 88–95% high; ≥95% maximal.

**M1 / M12: Introduction and elite coach-athlete perspectives** (the content is unseen). The course outcomes list error detection and correction, building competency through cues and teaching activities, competition preparation, and athlete self-management.

## What a coach is made of (Foundation Course plus coaching science)
- **The Foundation Course has 12 modules:** biomechanics; applied physiology (including fatigue, travel and the female athlete); functional anatomy; training methodology (adaptation, periodization, loading, exercise classification, specificity, variation, individualization); planning; progressions and long-term athlete development; athlete management (environment, relationships, goal setting, resilience, well-being); cueing and motor learning; strength fundamentals and inventory; speed fundamentals and inventory. Each section ends in a learning check with an 80% pass mark.
- **Three knowledge types serving athlete outcomes in a context** (Côté & Gilbert 2009):
  - professional knowledge (the sport and its science)
  - interpersonal knowledge (the relationship)
  - intrapersonal knowledge (reflection, which drives the growth of the other two)
  - These serve the athlete outcomes of competence, confidence, connection and character. Critique: those outcomes come mostly from youth sport.
- **Coaching is professional judgment and decision-making:** nested decisions before, during and after sessions (Abraham & Collins 2011; the wording is from citing works).
- **Motivating behavior** (Mageau & Vallerand 2003, doi:10.1080/0264041031000140374; model and review): autonomy support plus **structure** plus involvement meet the needs for autonomy, competence and relatedness. Structure is part of autonomy support, not its opposite.
- **Learning is not performance:** delayed retention and transfer reveal learning better than end-of-practice performance does (Kantak & Winstein 2012, doi:10.1016/j.bbr.2011.11.028). ALTIS's no-teaching realization week is this principle built into a program [Synth].
- **McMillan:** the first question is "What makes this athlete unique?" "Coaching is curiosity." Use as little technology as possible; the coaching eye decides. Integrated systems share one language: "If the athlete doesn't feel supported by the whole system, the system isn't working."

## Where ALTIS parts ways with other schools, and the variable that explains it
| Question | ALTIS | Rival view | Explaining variable |
|---|---|---|---|
| Phases or continuum | Phases are "potentially misleading"; every step differs | Phase models, % of vmax bins (research) | Purpose: phases suit analysis and programming; the continuum suits coaching the athlete |
| Drills | "Run well" beats drills; drills are teaching constraints | Drill-volume and Mach-drill traditions | Whether the drill keeps the task's information, which decides transfer |
| Intensity spacing | Graded zones; ~85% threshold for upright days | Francis high/low, avoiding the middle zone [coach opinion, not verified here] | Recovery cost by level: ALTIS itself says developmental athletes recover in ≤48 h |
| Early heel recovery | Low heel and toe drag not pursued | Low-heel teaching | Toe drag was a correction for exaggerated cyclical recovery, not a model |
| Sleds | Used as a tool | Promoted as essential | Load versus purpose; overall equivocal against unresisted sprinting (Petrakos 2016) |
| "Relax" | Only after force is established | Bud Winter "relax and win" | Race position: quantity first, quality late |

## The event modality: Price → Lever → Calendar → Proof
A new way of thinking that runs under every sprint decision. It extends the existing rules and does not replace them.
1. **Price it.** Convert any observation or proposed change into modeled 100 m time (`race`, a simulation with labeled inputs), then rank options by time gained ÷ (cost + risk). One hundredth on the 9.14 m fly is worth about a tenth in the 100, so top speed is priced first at this level.
2. **Find the lever.** Name the limiter on three axes:
   - structure, function or coordination
   - quantity (force, rate, direction) or quality (tension, efficiency)
   - on the curve: vmax, τ, speed loss or reaction time
   Kinogram frames locate it on the body. Two explanations that point to the same lever need no tiebreak.
3. **Place it on the calendar.** Every session either *is* a protected quality day or prepares for or recovers from one. Changes are introduced in an introduce week, loaded in the stabilize week, and judged in the realization week.
4. **Prove it with retention, not practice.** The proof is a stable-condition fly or race in the realization week or competition, measured with the existing noise rules. Practice-day improvements count as performance, not learning.
- **The self-coached case:** when the athlete trains alone, the coaching eye and in-session adjustment have to be executable by the athlete. Each protected session carries one pre-set decision number: the single measured value that changes the rest of the session.

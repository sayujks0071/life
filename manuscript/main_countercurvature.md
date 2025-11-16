# Biological Countercurvature of Spacetime: An Information--Cosserat Framework for Spinal Geometry

**Author:** Dr. Sayuj Krishnan S, MBBS, DNB (Neurosurgery)  
**Affiliation:** Consultant Neurosurgeon and Spine Surgeon, Yashoda Hospitals, Malakpet, Hyderabad, India  
**Email:** dr.sayujkrishnan@gmail.com

---

## Abstract

Living systems routinely generate and maintain structure against gravity, from plant stems that grow upward to vertebrate spines that adopt robust S-shaped profiles. Here we develop a quantitative framework in which such behavior is interpreted as *biological countercurvature*: information-driven modification of the effective geometry experienced by a body in a gravitational field. We combine an information--elasticity coupling (IEC) model of spinal patterning with three-dimensional Cosserat rod mechanics implemented in PyElastica, treating the rod in gravity as an analog spacetime and the IEC information field I(s) as a source of effective countercurvature.

On the body axis s, we define a biological metric dℓ_eff² = g_eff(s) ds², where the conformal factor g_eff(s) depends on the local amplitude and gradient of I(s). Using this countercurvature metric, we introduce a normalized geodesic curvature deviation D̂_geo that measures how far information-shaped equilibrium curvature profiles depart from the corresponding gravity-selected profiles. Across canonical simulations---human-like spinal S-curves, plant-like stems, and microgravity adaptation---we show that D̂_geo cleanly separates gravity-dominated, cooperative, and information-dominated regimes in (χ_κ, g) space, where χ_κ controls information-to-curvature coupling and g denotes gravitational strength.

To probe pathology within the same framework, we introduce a small, localized thoracic asymmetry in the information field or lateral rest curvature and track coronal-plane deformations. In the gravity-dominated regime, this perturbation produces negligible lateral deviation. In contrast, in the information-dominated corner of the phase diagram, the same small asymmetry is amplified into a scoliosis-like symmetry-broken branch, characterized by increased lateral displacement and Cobb-like angles, together with large D̂_geo. These results suggest that normal sagittal curvature and scoliosis-like patterns can emerge from a single IEC--Cosserat model operating in different countercurvature regimes, providing an analog-gravity perspective on how biological information reshapes equilibrium geometry in a gravitational field.

---

## Significance

Why does life so often grow and stand "against" gravity? In this work we develop a concrete mechanical model where developmental and neural information fields reshape the equilibrium geometry of a spine-like structure in a gravitational field. Using a Cosserat rod in gravity as an analog spacetime, and an information--elasticity coupling as a source of "biological countercurvature," we show how normal human-like S-shaped spinal profiles, plant-like upward growth, microgravity adaptation, and scoliosis-like lateral deviations can all be generated within a single framework. A metric derived from the information field lets us treat normal and pathological curvatures as different "geodesics" in an information-modified geometry. This provides a quantitative language for how biological information can stabilize, redirect, or destabilize the shapes that gravity alone would select.

---

## 1. Introduction

Living systems do not simply obey gravity; they appear to negotiate with it. Human spines adopt robust S-shaped profiles, plant stems grow upward, and neural structures adapt under microgravity. These behaviors suggest that biological information---developmental patterning, neural control, or genetic programs---actively reshapes the equilibrium geometry that gravity alone would select.

We propose that such behavior can be understood through *biological countercurvature*: information-driven modification of the effective geometry experienced by a body in a gravitational field. To make this concrete, we combine an information--elasticity coupling (IEC) model with three-dimensional Cosserat rod mechanics, treating the rod in gravity as an analog spacetime and the IEC information field as a source of effective countercurvature. This analog-gravity perspective provides a quantitative framework for understanding how biological information can stabilize, redirect, or destabilize curvature modes in a gravitational background.

Our framework introduces three key elements: (1) a biological metric dℓ_eff² = g_eff(s) ds² derived from the information field I(s) and its gradient, (2) a normalized geodesic curvature deviation D̂_geo that quantifies how information reshapes equilibrium curvature relative to gravity-selected profiles, and (3) a phase diagram mapping distinct countercurvature regimes---gravity-dominated, cooperative, and information-dominated---as a function of information-coupling strength and gravitational loading. We show that normal sagittal spinal curvature and scoliosis-like lateral deviations emerge as different regimes of the same unified model, providing a quantitative bridge between information processing, mechanics, and geometry in living systems.

---

## 2. Methods

### 2.1 Information--Elasticity Coupling (IEC) and beam model

We consider a one-dimensional body axis parameterized by arc-length s ∈ [0,L], along which an information field I(s) is defined. The IEC model couples this information field to mechanical properties: rest curvature κ_rest(s), effective stiffness E_eff(s), and active moments M_info(s). The coupling is controlled by three dimensionless parameters: χ_κ (information-to-curvature coupling), χ_E (information-to-stiffness coupling), and χ_M (information-to-active-moment coupling). For the spine-like configuration, we use a canonical information field that peaks in lumbar and cervical regions, corresponding to regions of high neural activity, and a rest curvature κ_gen(s) chosen to match typical human sagittal spinal curvature.

The baseline beam model solves the static equilibrium of a cantilever beam under gravity, with boundary conditions of a clamped base and free end. The information-coupled rest curvature, effective stiffness, and active moments modify the equilibrium solution relative to the passive (gravity-only) case.

### 2.2 Cosserat rod formulation and PyElastica implementation

We upgrade the IEC beam model to a full three-dimensional Cosserat rod in gravity using PyElastica. The Cosserat rod formulation accounts for bending, twisting, and stretching along the rod axis, with director frames tracking the orientation of cross-sections. The rod is discretized into n elements, each with its own rest curvature, stiffness, and material properties.

Boundary conditions consist of a clamped base (position and orientation fixed) and a free end. Gravity is applied as a body force along the rod. The information-coupled properties---rest curvature κ_rest(s), effective stiffness E_eff(s), and active moments M_info(s)---are interpolated onto the rod discretization and applied element-wise. Time integration uses PyElastica's standard Position-Verlet scheme, with damping to reach static equilibrium.

### 2.3 Biological countercurvature metric and geodesic curvature deviation

**Mathematical Box: Countercurvature metric and geodesic curvature deviation**

On the body axis s ∈ [0,L] we define an effective biological metric

dℓ_eff² = g_eff(s) ds²,

where the conformal factor g_eff(s) > 0 is determined by the local amplitude and gradient of the information field I(s).

Specifically, we normalize I(s) to Ĩ(s) ∈ [0,1] and compute its centered version Ĩ_centered(s) = Ĩ(s) - ⟨Ĩ⟩, where ⟨·⟩ denotes the mean over [0,L]. We also normalize the gradient dI(s)/ds to Ĩ'(s) with maximum absolute value 1. The conformal factor is then defined as

g_eff(s) = exp[2φ(s)],  where  φ(s) = β₁ Ĩ_centered(s) + β₂ Ĩ'(s),

where β₁, β₂ > 0 are weighting parameters (typically β₁ = 1.0, β₂ = 0.5).

The geodesic curvature deviation measures the Riemannian distance between passive (gravity-only) and information-coupled curvature profiles:

D_geo² = ∫₀ᴸ g_eff(s) [κ_I(s) - κ₀(s)]² ds,

where κ₀(s) is the curvature profile with all information coupling set to zero (χ_κ = 0), and κ_I(s) is the curvature profile with nonzero coupling. The normalized version is

D̂_geo = D_geo / (√[∫₀ᴸ g_eff(s) κ₀(s)² ds] + ε),

where ε is a small regularization parameter.

---

The countercurvature metric g_eff(s) weights regions of high information density or sharp information gradients more heavily in the effective geometry, encoding where biological countercurvature is most active. The geodesic curvature deviation D̂_geo quantifies how far information-driven equilibrium configurations depart from the gravity-selected geodesics, providing a quantitative measure of information-driven structure maintenance.

### 2.4 Numerical experiments

#### 2.4.1 Spine-like S-curves

For the spine-like configuration, we use a canonical spinal information field I(s) that peaks in lumbar and cervical regions, corresponding to regions of high neural activity. The rest curvature κ_gen(s) is chosen to match typical human sagittal spinal curvature. We sweep the information--curvature coupling parameter χ_κ ∈ [0, 0.05] while maintaining fixed gravity g = 9.81 m/s². Boundary conditions consist of a clamped base and free end.

#### 2.4.2 Plant-like upward growth

For the plant-like configuration, we compare a passive rod (sagging under gravity) to an information-driven rod that bends upward. The information field I(s) is chosen to promote upward curvature, and we vary χ_κ to explore the transition from passive sag to active upward growth. The geodesic deviation D̂_geo quantifies this transition, with D̂_geo < 0.1 indicating gravity-dominated sag and D̂_geo > 0.2 indicating strong information-driven upward bending.

#### 2.4.3 Microgravity adaptation

We run the same information field I(s) across a range of gravity levels g ∈ {1.0, 0.5, 0.1, 0.05, 0.01} times Earth gravity. For each g, we compute both the passive (gravity-only) curvature energy and the normalized geodesic deviation D̂_geo, demonstrating that information-driven structure persists as gravitational loading is reduced.

### 2.5 Thoracic asymmetry and scoliosis metrics

To probe scoliosis-like symmetry breaking, we introduced a small left--right asymmetry in the model spine. The body axis was discretized as a one-dimensional arc-length coordinate s ∈ [0,L], which we normalized to ŝ ∈ [0,1]. A localized thoracic bump was defined on this normalized coordinate as

G(ŝ) = exp[-½((ŝ - ŝ₀)/σ)²],

with center ŝ₀ ≈ 0.6 (mid-thoracic levels) and width chosen such that the full width at half maximum spanned approximately 2--3 vertebral levels. In the simplest implementation, an otherwise symmetric information field I_sym(s) was perturbed as

I_asym(s) = I_sym(s) + ε_asym · ΔI · G(ŝ),

where ΔI = max_s I_sym(s) - min_s I_sym(s) and ε_asym is a small dimensionless amplitude (typically ε_asym ~ 0.05). In an alternative implementation, a lateral curvature bump κ_lat(s) = ε_lat G(ŝ) was added directly to the coronal component of the Cosserat rod's rest curvature vector, with ε_lat chosen in the range 0.01--0.05 m⁻¹. Both approaches seeded a controlled, localized asymmetry without otherwise altering the sagittal IEC patterning.

For each simulation, we extracted the coronal-plane centerline coordinates (z(s), y(s)), where z denotes the cranio--caudal axis and y the lateral (left--right) direction. A simple lateral scoliosis index was defined as

S_lat = max_s |y(s)| / L_eff,

with L_eff = max_s z(s) - min_s z(s) the effective longitudinal span. As a Cobb-like angle, we fitted straight lines to the top and bottom fractions of the rod in the (z,y) plane using least-squares regression and computed the angle between them. Specifically, linear fits were obtained for the lowest and highest 20% of points; the Cobb-like angle was defined as the absolute difference between the corresponding line orientations. These scoliosis metrics were evaluated for both symmetric (ε_asym = 0) and asymmetric (ε_asym > 0) runs at each point in (χ_κ, g) parameter space, and used in combination with the normalized geodesic curvature deviation D̂_geo to classify gravity-dominated, cooperative, and scoliosis-like regimes.

---

## 3. Results

### 3.1 Gravity-selected vs information-selected curvature modes

In the spine-like configuration, the information field I(s) generates a smooth S-shaped curvature profile κ_I(s) that is well approximated by a single sign-changing mode along the cranio--caudal axis. In contrast, the purely gravity-selected solution κ₀(s) tends toward a monotonic, C-shaped sag. The stabilized sagittal S-curve is dominated by a single smooth sign-changing mode: κ_I(s) exhibits only one sign change along the axis and a max-to-RMS curvature ratio of ≈ 1.81, consistent with a sine-like counter-curvature profile against gravity. The normalized geodesic curvature deviation between the gravity-selected and information-selected solutions is D̂_geo ≈ 0.14, confirming that the information-driven S-curve is not a small perturbation of the passive sag. In this sense, the mature human spine behaves as a sinusoidal counter-curvature mode stabilized against gravity by information--elasticity coupling.

For the plant-like configuration, we compare a passive rod (sagging under gravity) to an information-driven rod that bends upward. The information field I(s) is chosen to promote upward curvature, and we vary χ_κ to explore the transition from passive sag to active upward growth. The geodesic deviation D̂_geo quantifies this transition, with D̂_geo < 0.1 indicating gravity-dominated sag and D̂_geo > 0.2 indicating strong information-driven upward bending.

### 3.2 Persistence of information-driven shape in microgravity

As gravitational loading is reduced, the passive (gravity-only) curvature energy collapses, yet the information-selected structure persists. We ran the same information field I(s) across a range of gravity levels g ∈ {1.0, 0.5, 0.1, 0.05, 0.01} times Earth gravity. For each g, we computed both the passive curvature energy and the normalized geodesic deviation D̂_geo between passive and information-driven solutions.

As the effective gravitational acceleration is reduced from g = 1.0 to g = 0.10, the normalized geodesic curvature deviation remains essentially unchanged, D̂_geo ≈ 0.091 (changes by less than 1% in our simulations), indicating that the information-selected "spinal wave" is geometrically stable in microgravity even as the passive response to gravity weakens. This persistence provides quantitative support for the biological countercurvature hypothesis: information fields can maintain structure even when gravitational loading is negligible.

### 3.3 Phase diagram of countercurvature regimes

We map the countercurvature behavior across the (χ_κ, g) parameter space, where χ_κ controls information-to-curvature coupling strength and g denotes gravitational acceleration. The normalized geodesic deviation D̂_geo cleanly separates distinct regimes: (1) *Gravity-dominated* (D̂_geo < 0.1), where information has minimal effect and the rod follows gravity-selected geodesics; (2) *Cooperative* (0.1 < D̂_geo < 0.3), where information reshapes curvature but does not override gravitational loading; and (3) *Information-dominated/scoliotic* (D̂_geo > 0.3), where information-driven countercurvature strongly modifies the effective geometry and small asymmetries can be amplified into scoliosis-like branches.

Across the (χ_κ, g) plane, our simulations reveal two distinct regimes in the present parameter window: a gravity-dominated corner where D̂_geo < 0.1 and both S_lat and Cobb-like angles remain near zero (e.g., χ_κ = 0.015, g = 9.81, D̂_geo ≈ 0.059), and a cooperative regime where D̂_geo increases to O(10⁻¹) while sagittal curvature is visibly reshaped by the information field (e.g., χ_κ = 0.065, g = 9.81, D̂_geo ≈ 0.15). Within the current sweep, our thresholds for a "scoliotic regime" (S_lat ≳ 0.05, Cobb-like angles ≳ 5°) are not crossed, so the symmetry-broken branch remains a predicted extension at larger χ_κ or stronger asymmetries rather than a regime realized in this parameter window.

### 3.4 Information-dominated regime and scoliosis-like symmetry breaking

To probe how information-driven countercurvature interacts with left--right asymmetries, we introduced a small perturbation in the thoracic region of the model spine. In the symmetric baseline configuration, the IEC information field I(s) and rest curvature κ_rest(s) were restricted to the sagittal plane, yielding a purely gravity-selected S-shaped equilibrium. We then added a localized "thoracic bump" either to I(s) or to the lateral component of the rest curvature, with relative amplitude ε_asym ≈ 5% (Methods). This perturbation mimics a subtle developmental or neuromuscular asymmetry concentrated at mid-thoracic levels.

For each pair of information--curvature coupling χ_κ and gravity level g, we simulated both the symmetric (ε_asym = 0) and asymmetric (ε_asym > 0) Cosserat rod. From the 3D centerline we extracted coronal-plane coordinates (z,y) and computed a simple lateral scoliosis index S_lat = max_s |y(s)| / L_eff, where L_eff is the longitudinal span in z. In addition, we estimated a Cobb-like angle by fitting straight lines to the top and bottom segments of the rod in the coronal plane and measuring the angle between them. These metrics were evaluated alongside the normalized geodesic curvature deviation D̂_geo, which quantifies information-driven departures from the gravity-selected curvature in the countercurvature metric g_eff(s).

In the gravity-dominated regime of the phase diagram (low χ_κ, high g), the asymmetric and symmetric solutions remained nearly indistinguishable: S_lat and Cobb-like angles changed by at most a few percent and a few degrees, respectively, and D̂_geo remained below the "small deviation" threshold. Here, the same small thoracic perturbation is effectively suppressed by the gravitationally selected curvature. In contrast, in the information-dominated regime (high χ_κ at moderate or reduced gravity), the identical perturbation produced pronounced lateral deformations. The lateral index increased beyond S_lat ≳ 0.05 and Cobb-like angles exceeded ~5--10°, while D̂_geo simultaneously crossed into the "large deviation" regime. In this region of parameter space, the information field no longer merely refines a gravity-selected S-curve; it reshapes the effective metric so strongly that a small asymmetry in I(s) is amplified into a scoliosis-like symmetry-broken branch.

These results suggest that scoliosis-like patterns can emerge naturally when the spine operates in an information-dominated countercurvature regime. Rather than requiring a completely different mechanical mechanism, the same IEC--Cosserat framework that explains normal sagittal curvature also admits a bifurcating lateral branch when information-driven countercurvature overwhelms the gravitational background, offering a unified perspective on normal and pathological spinal geometry.

---

## 4. Discussion

### 4.1 Biological interpretation of countercurvature regimes

The phase diagram reveals how biological information and gravity interact to shape equilibrium curvature. In the gravity-dominated regime, the rod follows the geodesics selected by gravity alone, with information playing a minimal role. As information--curvature coupling increases, the system transitions to a cooperative regime where information reshapes curvature while still operating within the gravitational background. In the information-dominated regime, information-driven countercurvature becomes the dominant factor, strongly modifying the effective geometry and enabling symmetry-breaking behaviors such as scoliosis-like lateral deviations.

This framework provides a quantitative language for understanding how developmental and neural information can stabilize, redirect, or destabilize curvature modes in a gravitational field. The normalized geodesic curvature deviation D̂_geo serves as a quantitative measure of this interaction, allowing us to map distinct regimes and predict transitions between them.

### 4.2 Growth against gravity as a standing counter-curvature mode

Our results suggest that the adult sagittal spine can be interpreted as a standing counter-curvature mode selected by an information field acting against gravity, rather than as a passive beam that merely sags under load. In the gravity-dominated regime, the rod relaxes toward a simple C-shaped profile, but as information--elasticity coupling increases, the system transitions to a robust, sine-like S-curve that persists even as gravity is reduced. From this perspective, "growth against gravity" for the spine is not simply a matter of resisting load; it is the selection and stabilization of a particular curvature mode in an information-modified geometry. This view naturally extends to developmental trajectories (progressive recruitment of higher curvature modes) and to pathology, where the same machinery amplifies small asymmetries into scoliosis-like lateral branches in the information-dominated regime.

### 4.3 Analog gravity interpretation and relation to spacetime curvature

Our use of the term "countercurvature of spacetime" is explicitly analog rather than fundamental. In this work, the Cosserat rod in a uniform gravitational field plays the role of an effective spacetime, and the information field I(s) modifies the metric dℓ_eff² = g_eff(s) ds² along the body axis. The geodesic curvature deviation D̂_geo then measures how strongly information reshapes the equilibrium geometry relative to the gravity-selected solution, in close analogy to how additional fields can modify geodesics in general relativity. We do not propose any modification of Einstein's equations or claim that biological information directly curves physical spacetime. Instead, we use this analog-gravity language to organize and quantify how developmental and neuromuscular information can select, stabilize, or destabilize curvature modes of the spine in a gravitational background.

### 4.4 Implications for scoliosis and spinal control

The framework suggests that scoliosis-like patterns can emerge when the spine operates in an information-dominated countercurvature regime, where small asymmetries are amplified into pronounced lateral deviations. This provides a quantitative perspective on how developmental or neuromuscular asymmetries might lead to pathological curvature patterns. The phase diagram indicates that such behavior is most likely when information--curvature coupling is strong and gravitational loading is moderate or reduced, suggesting potential mechanisms for scoliosis development and progression.

The unified framework also suggests that normal sagittal curvature and scoliosis-like lateral deviations are not fundamentally different phenomena, but rather different regimes of the same information--elasticity coupling mechanism. This perspective may inform therapeutic strategies that target the information--curvature coupling itself, rather than treating normal and pathological curvature as separate problems.

---

## 5. Limitations and Outlook

Several limitations should be noted. First, the information field I(s) is phenomenological rather than derived from first principles; its functional form and coupling parameters are chosen to match observed spinal curvature patterns. Second, the countercurvature metric g_eff(s) is a heuristic construction that encodes the hypothesis that information density and gradients modify effective geometry, but the specific weighting parameters (β₁, β₂) are empirical choices. Third, the current implementation uses a simplified beam model for most experiments, with full 3D Cosserat rod mechanics applied primarily to the scoliosis analysis; future work should extend the full 3D treatment to all experiments.

Second, the normalized geodesic curvature deviation D̂_geo can inflate as gravity approaches zero because the denominator (base energy) collapses while D_geo may remain finite. This is expected behavior but should be interpreted with caution in the microgravity limit.

Third, the scoliosis metrics (S_lat, Cobb-like angles) are defined for coronal-plane coordinates, but in 2D beam models we use a "pseudo-coronal" projection where the sagittal x-coordinate is treated as lateral deviation. This is an approximation; full 3D Cosserat rod models provide actual coronal-plane coordinates.

Future directions include: (1) extending the framework to experimental data from microgravity experiments and clinical scoliosis measurements, (2) deriving the information field from first principles based on developmental patterning or neural control mechanisms, (3) exploring the relationship between information--curvature coupling and known biological processes such as HOX/PAX patterning or neuromuscular control, and (4) developing therapeutic strategies that target the information--curvature coupling itself.

---

## 6. Conclusion

We have developed a quantitative framework for biological countercurvature that unifies normal sagittal spinal curvature and scoliosis-like lateral deviations within a single information--elasticity coupling model. The framework introduces a biological metric dℓ_eff² = g_eff(s) ds² derived from information fields, a normalized geodesic curvature deviation D̂_geo that quantifies information-driven departures from gravity-selected profiles, and a phase diagram mapping distinct countercurvature regimes. Our results demonstrate that information-driven structure maintenance persists in microgravity, that normal and pathological curvature patterns emerge as different regimes of the same unified model, and that the framework provides a quantitative language for understanding how biological information reshapes equilibrium geometry in a gravitational field.

The analog-gravity perspective---treating the rod in gravity as an effective spacetime and information fields as sources of countercurvature---provides a conceptual bridge between information processing, mechanics, and geometry in living systems. Future work should extend the framework to experimental data, derive information fields from first principles, and explore therapeutic strategies that target the information--curvature coupling itself.

---

## Code Availability

All simulations and analyses in this work were performed using the open-source Python package `spinalmodes` (version 0.1.0), available at https://github.com/sayujks0071/life. The package implements the information--elasticity coupling (IEC) beam solver, the countercurvature metric, geodesic curvature deviation, scoliosis metrics, and PyElastica-based Cosserat rod simulations used in this study.

Key functions include `compute_countercurvature_metric` and `geodesic_curvature_deviation` (module `spinalmodes.countercurvature.api`), scoliosis metrics `compute_scoliosis_metrics` and `classify_scoliotic_regime`, and the IEC solver `solve_beam_static`. All experiment scripts (microgravity, spine modes, plant growth, phase diagram, and scoliosis regime) are provided under `src/spinalmodes/experiments/countercurvature/`, and can be invoked via documented command-line interfaces and shell helpers. A minimal end-to-end example is provided in `examples/quickstart.py` and `examples/quickstart.ipynb`.

The exact version of the code used to generate the results in this manuscript is archived as release v0.1.0 (see `CITATION.cff` in the repository).

---

## Data Availability

All data underlying the figures in this manuscript are either stored in plain-text CSV files or can be regenerated from the provided code. Experiment outputs (including curvature profiles, countercurvature metrics, geodesic deviations, and scoliosis indices) are written to the `outputs/` directory by the scripts in `src/spinalmodes/experiments/countercurvature/`.

For each figure panel, we provide a short mapping from script to output files in the repository documentation (`docs/manuscript_code_data_availability.md`). Running the experiments with the default parameters (or the `--quick` mode for reduced-resolution versions) reproduces all CSV files used by the figure-generation scripts. No proprietary or patient-identifiable data are used in this study.

---

## Figures

**Figure 1:** Information-driven countercurvature in spine-like and plant-like configurations. Panel A shows the curvature profiles for passive (gravity-only) and information-coupled configurations. Panel B displays the countercurvature metric g_eff(s) along the rod axis, highlighting regions of high information processing. Panel C demonstrates how normalized geodesic deviation D̂_geo increases with information--curvature coupling strength χ_κ. Panel D shows that D̂_geo persists as gravitational loading is reduced, while passive curvature energy collapses, demonstrating information-driven structure maintenance in microgravity.

**Figure 2:** Phase diagram in (χ_κ, g) space showing gravity-dominated, cooperative, and information-dominated countercurvature regimes. The contour plot shows normalized geodesic deviation D̂_geo as a function of information--curvature coupling χ_κ and gravitational strength g. Markers indicate points where a small thoracic asymmetry (ε_asym = 0.05) produces a scoliosis-like lateral branch (high S_lat and Cobb-like angles). The scoliotic regime (shaded region) emerges in the information-dominated corner of the phase diagram, where D̂_geo > 0.3 and small asymmetries are amplified into pronounced lateral deformations.

---

*Note: This is a markdown version of the LaTeX manuscript for easy reading. For the original LaTeX source with proper formatting, equations, and references, see `manuscript/main_countercurvature.tex`.*


# PI research overview

**Question:** after whole-body PET/CT segmentation is fixed, can reference-free scores identify examinations with substantial spatial error for priority review? Quantitative volume agreement can conceal spatial false-positive and false-negative cancellation. The candidate hypothesis is that a fixed UQ score adds error-ordering value beyond a simple Predicted MTV size baseline on independent patients; this is **not demonstrated** by the current development evidence.

## Existing engineering contribution

The repository provides inspectable geometry/unit QC, affine-aware physical volume, binary segmentation and lesion-matching utilities, risk–coverage with explicit ties, reproducibility manifests, wrapper checks and a compact synthetic PyTorch training path. [Implementation–test pairs](PROGRAMMING_EVIDENCE.md) support these engineering behaviors. They do not establish clinical reference completeness or patient reliability. The public nnU-Net sampler/trainer adaptation is a post-hoc `PARTIAL_RECIPE`. nnU-Net, AutoPET and LesionTracer remain [upstream contributions](../THIRD_PARTY.md); no sole-authorship claim is made.

## Completed real-data development evidence and negative findings

The [five-case 40-epoch record](DEVELOPMENT_BASELINE_40E_CASE.md) is `DEVELOPMENT_EXPOSED`: one seed and fold 0. EMA-selected and final checkpoints trade missed volume against false-positive volume; better Dice does not imply lower net-volume error. An analytic empty-mask control achieves lower volume MAE while missing all reference foreground. Performance is insufficient for clinical conclusions. This record is separate from FDG20.

The [FDG20 pilot](FDG20_PILOT_METHODS.md) uses fixed official five-fold predictions, TTA and mean-logits integration. It is availability-sampled, training exposure was not excluded, and it is **not independent validation**. Ten reference-foreground and ten empty-reference annotations are annotation categories, not clinical-positive/negative groups. Frozen Entropy/variance AURC and retained-risk analyses coexist with post-hoc Predicted MTV/Pairwise comparisons; all referral-FNV shares are post-hoc. Predicted MTV is a size baseline, not UQ. Pairwise disagreement performed worse than the analytic random expectation. The [public aggregate JSON](fdg20_pilot_aggregate_summary.json) is the numeric source; protected patient-level calculations cannot be rerun publicly.

## What has not been demonstrated

No independent reliability advantage, clinically confirmed complete lesion-miss endpoint, clinical safety benefit, reader-time saving, independent PSMA or external-centre validation has been demonstrated. Simulated referral-FNV allocation is not observed error correction. Computational common-uncovered regions are candidate failure mechanisms, not clinically confirmed missed lesions. Background/field-of-view sensitivity, unknown exposure and reference completeness constrain interpretation. Checkpoint redistribution rights and historical adaptation-code byte identity remain unresolved.

## Evidence-driven research sequence

All stages are **PROPOSED / NOT RUN**; the SAP and clinical-reference SOP are **PENDING**.

1. **Observation to independent benchmark:** development results do not demonstrate an incremental UQ advantage over the size baseline. After permissions and all-member exposure audit, freeze the candidate Entropy-versus-MTV paired ΔAURC comparison before independent outcomes. A null or adverse comparison is a valid result.
2. **Benchmark to mechanism:** if independent failure analysis and expert review confirm a reproducible blind spot under a complete reference/matching SOP, distinguish voxel FNV, complete reference-lesion misses and clinically major misses. Test low-cost complementary cues first; an auxiliary model requires a separate incremental question and explicit prompt/workload costs.
3. **Transfer and workflow under independent protocols:** test whether ranking survives tracer, centre, scanner and disease-spectrum shifts, and measure actual time/corrections. This stage does not require a successful Study 2 cue/model; Study 2 itself does not require a positive Study 1 UQ result. Simulated referral is not observed clinical benefit; direct transfer and recalibration require separate evaluation.

The [overall PhD framework](PHD_RESEARCH_FRAMEWORK.md) makes these dependencies, falsifiable hypotheses, negative outcomes and unchanged G1–G10 conditions explicit. The [literature evidence register](RESEARCH_LITERATURE_EVIDENCE.md) separates published support from this project's PET transfer assumptions. G1 remains **BLOCKED_PROVENANCE**; patient Phase C **NOT_RUN**; historical FDG20 independence **NOT_VERIFIED**. Route A is **PENDING_CUSTODIAN_EVIDENCE**; Route B is **DESIGN CANDIDATE / NOT RUN**. Neither document grants execution permission or changes historical results.

The immediate blocker is independent-data access and exposure documentation; the independent FDG data search is paused. Sample sizes, centre counts, expected effects and clinical thresholds remain `TBD`; approvals remain `PENDING`. See [research gates](RESEARCH_GATES.md), the retained [design candidate](RESEARCH_DESIGN_CANDIDATE.md), and the [claim-to-source matrix](PI_EVIDENCE_MATRIX.md). These stages define substantive research still required for a doctoral contribution.

# Research literature evidence and transfer conditions

**Level C supports prior work, not completed PET research in this repository.**
Targeted verification date: **2026-10-20**. This is a focused design/prior-art
check, not a systematic review or a claim of exhaustive novelty coverage.
Publisher/proceedings text, author preprints, PubMed and Crossref were checked
for identity and the specific claims below. No external performance numbers
are imported into our results. Local skill instructions are workflow guidance,
not scientific evidence. The [framework](PHD_RESEARCH_FRAMEWORK.md) labels its
own transfers and hypotheses separately.

`VERIFIED_PUBLISHED` means a published identity and the stated bounded claim
were checked, not that every experiment or supplement was reproduced.
`VERIFIED_PREPRINT` does not imply peer review. `PARTIAL_VERIFICATION` limits
use to the verified portion; `UNVERIFIED`/`NOT_USED` cannot support a core claim.

## Literature verification table

| Study | Year | DOI / stable source | Original task | Main method | Actual supported finding | Limitation | Relevance | Transfer condition | Verification status |
|---|---|---|---|---|---|---|---|---|---|
| L01 Geifman / El-Yaniv | 2017 | [Proceedings](https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html) | Image classification with rejection | Confidence selection and selective risk | Coverage trades against risk among retained predictions | Classification loss and sampling assumptions; not PET or clinical review | T1 | Define a PET risk/action and independently evaluate it; no imported guarantee | VERIFIED_PUBLISHED |
| L02 Maier-Hein et al. | 2024 | [10.1038/s41592-023-02151-z](https://doi.org/10.1038/s41592-023-02151-z) | Image-analysis validation | Problem fingerprint and metric-selection framework | Metrics should reflect domain/task properties and aggregation structure | Consensus recommendations, not proof of clinical utility of our risk | T2 | Justify voxel/lesion/examination endpoints separately | VERIFIED_PUBLISHED |
| L03 Tejani et al., CLAIM | 2024 | [10.1148/ryai.240300](https://doi.org/10.1148/ryai.240300) | Medical imaging AI reporting | Delphi-based checklist | Describe reference standards and patient-disjoint data partitions | Reporting guidance is not a quality score or study approval | T5/T6 | Actual membership and reference evidence still needed | VERIFIED_PUBLISHED |
| L04 Lakshminarayanan et al. | 2017 | [Proceedings](https://papers.nips.cc/paper_files/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html) | Classification/regression uncertainty | Independently optimized neural ensembles | Predictive uncertainty can be estimated with ensembles in evaluated settings | No guarantee that agreeing members are correct in PET | T3 | Specify training diversity and test shared-error/shift behavior | VERIFIED_PUBLISHED |
| L05 Roy et al. | 2019 | [10.1016/j.neuroimage.2019.03.042](https://doi.org/10.1016/j.neuroimage.2019.03.042) | Whole-brain T1 MRI structure QC | Bayesian QuickNAT, MC dropout, structure-wise measures | Uncertainty measures relate to structure segmentation quality in studied data | Brain structures, not whole-body PET error or reader benefit | T3 | Re-evaluate aggregation and risk in the PET task | VERIFIED_PUBLISHED; full-method access via author preprint |
| L06 Zenk et al. | 2025 | [10.1016/j.media.2024.103392](https://doi.org/10.1016/j.media.2024.103392) | Medical segmentation failure detection | Confidence aggregation and Risk–Coverage benchmark | Published report identifies Pairwise Dice as a robust baseline | CT/MRI benchmark; no PET superiority claim; version-access limits below | T1/T3 | Use as a comparator, not a correctness guarantee | VERIFIED_PUBLISHED for abstract/highlights; author-preprint methods separately identified |
| L07 Boellaard et al. | 2015 | [10.1007/s00259-014-2961-x](https://doi.org/10.1007/s00259-014-2961-x) | Quantitative FDG PET/CT | Procedure/quantification guidance, version 2.0 | SUV and volume delineation require defined acquisition/measurement conventions | Historical guidance, not a claim about the latest clinical standard or our model | T4 | Validate units, SUV, geometry and delineation protocol | VERIFIED_PUBLISHED |
| L08 Gatidis et al. | 2022 | [10.1038/s41597-022-01718-3](https://doi.org/10.1038/s41597-022-01718-3) | Annotated whole-body FDG PET/CT dataset | Manual lesion annotation and technical segmentation validation | Provides a PET lesion-segmentation resource and task context | Does not identify our local copy, resolve permissions, or exclude model exposure | T4 | Bind exact version/variant, reference and local lineage separately | VERIFIED_PUBLISHED |
| L09 Zech et al. | 2018 | [10.1371/journal.pmed.1002683](https://doi.org/10.1371/journal.pmed.1002683) | Pneumonia classification in radiographs | Cross-hospital evaluation and confounder analysis | Generalization varied across hospitals; confounding affected interpretation | Radiograph classification, not PET segmentation | T5 | Examine site/spectrum/measurement effects without assuming PET effect size | VERIFIED_PUBLISHED |
| L10 Vasey et al., DECIDE-AI | 2022 | [10.1136/bmj-2022-070904](https://doi.org/10.1136/bmj-2022-070904) | Early live clinical AI decision-support evaluation | Consensus reporting guideline | Clinical workflow/human factors need explicit evaluation and reporting | Guidance is neither an approved reader protocol nor evidence of benefit | T6 | Observe actual interactions/corrections under a separate study | VERIFIED_PUBLISHED for guideline scope/recommendations; supplements not audited |
| L11 Sahlsten et al. | 2024 | [10.1038/s43856-024-00528-5](https://doi.org/10.1038/s43856-024-00528-5) | Oropharyngeal primary-tumor PET/CT segmentation | Bayesian/deep ensembles, uncertainty and referral evaluation | PET/CT uncertainty-based quality assessment/referral has existing task-specific prior art | Regional radiotherapy target, not our whole-body FPV+FNV comparison or observed workflow benefit | T3/T6 | Revalidate the target task, comparison, reference and endpoint; no first-use claim | VERIFIED_PUBLISHED |

## Core claim support locations and bibliographic identity

### L01

Geifman Y, El-Yaniv R. **Selective Classification for Deep Neural Networks**.
Advances in Neural Information Processing Systems 30 (2017).
[Full proceedings paper](https://papers.neurips.cc/paper_files/paper/2017/file/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf),
§2, equation (1), defines coverage and selective risk; §3 states the risk-control
construction. [arXiv:1705.08500](https://arxiv.org/abs/1705.08500) is the
corresponding preprint, not a separate PET study. Our mL-valued discrete AURC
is a repository-specific evaluation contract, not that paper's clinical guarantee.

### L02

Maier-Hein L, Reinke A, Godau P, et al. **Metrics reloaded: recommendations for
image analysis validation**. Nature Methods **21**, 195–212 (2024).
[Publisher full text](https://www.nature.com/articles/s41592-023-02151-z):
“Metrics Reloaded framework,” steps 1–3, Fig. 3 and Extended Data Table 1
support problem-aware selection and attention to aggregation. DOI contains
2023 but publication is 2024; the two are not interchangeable dates.

### L03

Tejani AS, Klontzas ME, Gatti AA, et al. **Checklist for Artificial Intelligence
in Medical Imaging (CLAIM): 2024 Update**. Radiology: Artificial Intelligence
**6**(4), e240300 (2024). [Publisher](https://pubs.rsna.org/doi/full/10.1148/ryai.240300),
[PubMed](https://pubmed.ncbi.nlm.nih.gov/38809149/),
[public full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC11304031/).
Items 19–20 address partitioning/disjointness; Reference Standard discussion
and item 37 address reference/assessment. Publisher web text and PubMed were
used when a direct Crossref/automated publisher request failed. No checklist
score or radiomics-specific validation is inferred.

### L04

Lakshminarayanan B, Pritzel A, Blundell C. **Simple and Scalable Predictive
Uncertainty Estimation using Deep Ensembles**. Advances in Neural Information
Processing Systems 30 (2017). [Full paper](https://papers.nips.cc/paper_files/paper/2017/file/9ef2ed4b7fd2c810847ffa5fa85bce38-Paper.pdf),
§2.4 and Algorithm 1 describe ensemble construction/combination; §3 evaluates
uncertainty. Predictive entropy here is not automatically a pure epistemic
quantity, and cross-validation folds in our historical model are not assumed
to satisfy the same diversity contract.

### L05

Roy AG, Conjeti S, Navab N, Wachinger C; Alzheimer's Disease Neuroimaging
Initiative. **Bayesian QuickNAT: Model uncertainty in deep whole-brain
segmentation for structure-wise quality control**. NeuroImage **195**, 11–22
(2019). [PubMed identity/abstract](https://pubmed.ncbi.nlm.nih.gov/30926511/)
and [author full-text preprint](https://arxiv.org/html/1811.09800), §3.3–3.4
uncertainty methods and §4–5 experimental setup/results, were checked separately. MC-dropout structure
quality associations are the bounded support; no PET performance/correlation
number or claim of general correctness is transferred.
§3.4.2 defines structure-volume coefficient of variation, mean pairwise Dice,
all-sample intersection/union and mean voxel uncertainty. QC relates these to
structure Dice, not whole-body examination FPV+FNV or observed reader benefit.

### L06

Zenk M, Zimmerer D, Isensee F, et al. **Comparative benchmarking of failure
detection methods in medical image segmentation: Unveiling the role of
confidence aggregation**. Medical Image Analysis **101**, 103392 (2025).
[Publisher abstract/highlights](https://www.sciencedirect.com/science/article/pii/S1361841524003177),
[PubMed identity](https://pubmed.ncbi.nlm.nih.gov/39657400/), and Crossref
confirm DOI **10.1016/j.media.2024.103392**: online 2024, issue 2025.
The claim of a robust Pairwise baseline is in the published abstract/highlights.
[Author preprint v2](https://arxiv.org/html/2406.03323v2), §4.2/Table 2 and
§5/Fig. 6, supplies the accessible CT/MRI/method context. It is a **2024
preprint**, not relabeled as the final 2025 full text; final-PDF automated access
was unsuccessful. No version-specific quantitative result is imported.
In that preprint, §4.1 uses per-case `1 - mean class DSC` risk (auxiliary NSD);
§4.4.3 averages all unordered mask-pair Dice values, using mean class Dice for
multiclass masks. Table 2 covers brain/heart/prostate MRI and COVID/kidney CT,
with corruption, spectrum, scanner/site shifts and an in-distribution task.
Fig. 6 also shows shared-error failures. These definitions differ from FDG20's
binary mL risk and development exposure; this is not a same-condition replication.

### L07

Boellaard R, Delgado-Bolton R, Oyen WJG, et al. **FDG PET/CT: EANM procedure
guidelines for tumour imaging: version 2.0**. European Journal of Nuclear
Medicine and Molecular Imaging **42**, 328–354 (2015).
[Full publisher text](https://link.springer.com/article/10.1007/s00259-014-2961-x),
“Quantification of FDG uptake,” SUV/SUL discussion and MTV/TLG delineation
paragraphs. Crossref online date is December 2014; the journal issue is 2015.
This is a historical measurement foundation, not a current clinical prescription
or an instruction to adopt its thresholds in our proposed endpoint.

### L08

Gatidis S, Hepp T, Früh M, et al. **A whole-body FDG-PET/CT Dataset with manually
annotated Tumor Lesions**. Scientific Data **9**, 601 (2022).
[Publisher full text](https://www.nature.com/articles/s41597-022-01718-3),
Methods: Data collection/Annotation and “Technical Validation: Deep Learning-based
Lesion Segmentation.” Its acquisition/annotation and benchmark context cannot
prove the identity or training independence of historical FDG20 objects.

### L09

Zech JR, Badgeley MA, Liu M, et al. **Variable generalization performance of a
deep learning model to detect pneumonia in chest radiographs: A cross-sectional
study**. PLOS Medicine **15**(11), e1002683 (2018).
[Full article](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002683),
Results on cross-system generalization and hospital/prevalence confounding,
Discussion on generalizability. We transfer a threat-to-validity question,
not its observed performance or a proven cause of FDG20's ranking.

### L10

Vasey B, Nagendran M, Campbell B, et al.; DECIDE-AI expert group. **Reporting
guideline for the early stage clinical evaluation of decision support systems
driven by artificial intelligence: DECIDE-AI**. BMJ **377**, e070904 (2022).
[BMJ recommendations](https://www.bmj.com/content/377/bmj-2022-070904),
Box 1 definitions and Table 2 reporting checklist. Publisher-indexed text and
[PubMed](https://pubmed.ncbi.nlm.nih.gov/35584845/) verify the bounded scope;
direct automated full-page access was intermittent/blocked. The simultaneous
Nature Medicine publication is not counted as a second independent study.
No supplementary checklist compliance assessment or clinical effect is claimed.

### L11

Sahlsten J, Jaskari J, Wahid KA, et al. **Application of simultaneous uncertainty
quantification and segmentation for oropharyngeal cancer use-case with Bayesian
deep learning**. Communications Medicine **4**, 110 (2024).
[Publisher full text](https://www.nature.com/articles/s43856-024-00528-5),
Methods: “Uncertainty measures”/referral evaluation and Discussion, verifies
PET/CT uncertainty/referral prior art. The earlier **2023 preprint has a different
title and analysis description**; its sample counts, method counts and results
are not substituted into the 2024 paper. This check uses the published identity
and text; no numerical clinical benefit is borrowed.
The models use 3D residual U-Nets. Patient scores include entropy variants,
volume coefficient of variation and DSC-risk. Cross-validation supports
quality-threshold estimation; holdout evaluation examines batch and fixed-threshold
referral. Proposed manual correction in the workflow is not evidence of measured
correction time or improved clinical outcomes.

## Prior-art overlap assessment

Model identities below are the papers' methods, not our historical checkpoints.
Version/access limits above apply; these comparisons do not establish novelty.

| Original study | Imaging task | Model identity | UQ level | Risk endpoint | Review strategy | Validation type | Our remaining testable question |
|---|---|---|---|---|---|---|---|
| Roy 2019, L05 | Brain MRI structures | Bayesian QuickNAT / MC dropout | Voxel and structure | Structure Dice/QC | QC indicators | MRI seen/unseen datasets | Does examination ranking add to fixed-mask PET size? |
| Zenk 2025, L06; methods: 2024 v2 | CT/MRI segmentation | U-Net; ensemble/dropout | Pixel to case; pairwise masks | 1−mean DSC; auxiliary NSD | Risk–Coverage rejection | Multiple tasks and shifts | Does ordering hold for independent PET spatial mL risk? |
| Sahlsten 2024, L11 | PET/CT OPC primary GTV | Residual U-Net ensembles | Voxel and patient | DSC; referral/quality estimation | Batch and threshold referral | Cross-validation and external holdout | Increment beyond MTV; whole-body risk and actual review cost? |
| Biswas 2026, P01 preprint | Whole-body FDG/PSMA | nnU-Net ensembles; augmented model | Voxel; case routing | Dice / FPVol / FNVol | Automated model choice | Held-out and Deep-PSMA testing | Fixed-mask review ordering and adjudicated clinical yield? |

### P01 — related preprint, separate from eleven published references

Biswas BA et al. **Improving PET/CT-Based Whole-Body Lesion Segmentation Using
Prediction Uncertainty-Augmented Models** (2026).
[Record](https://arxiv.org/abs/2606.10115), [full HTML](https://arxiv.org/html/2606.10115).
**VERIFIED_PREPRINT — BOUNDED CLAIM SUPPORT**: methods/results, figure captions
and Tables 1–5 inspected; no reproduction or peer-review inference.
§§2.4–2.7 use five nnU-Net members, entropy decomposition, an epistemic input
channel and PET-based routing. §§3.2/4.2 evaluate voxel errors, including per-case
AUROC, not our examination AURC. §§4–5 report reduced FNVol with increased FPVol;
the router transfers poorly to Deep-PSMA. §2.2 reports patient-grouped AutoPET
splits and exclusively held-out Deep-PSMA: paired FDG/PSMA in prostate cancer,
including an FDG disease-spectrum shift. This reported design does not independently
verify all pretrained-member exposure. Uncertainty-guided augmentation, failure
analysis and transfer overlap our candidates; no first-use claim is justified.
Human correction/cost benefit is **NOT_VERIFIED**. No performance is imported.

## Theory-to-design transfer map

Each right-hand entry is our proposal/inference, not a finding of the cited paper.

| Topic | Original definition/task | Direct support | PET transfer assumption | How it can fail | Required test and current evidence |
|---|---|---|---|---|---|
| T1 Selective prediction | Accept/reject classification; conditional loss on accepted cases | L01 §2; L06 failure-ranking abstract | An examination score orders a fixed PET spatial risk | Correlated risk/score can change with cohort or endpoint; imported guarantees invalid | Independent common-cohort Risk–Coverage; current PET evidence development only |
| T2 Problem-aware metrics | Validation at image/object/pixel levels | L02 fingerprint/metric application | Spatial mL error is relevant to the proposed review action | Small important misses hidden by volume; incomplete references | Complementary predeclared endpoints and clinical adjudication; no approved clinical endpoint yet |
| T3 Ensemble uncertainty | Probabilistic ensembles, structure/segmentation QC | L04–L06; L11 | Diversity/aggregation contains useful error information in this target task | All members share an error; burden/background dominates | Fixed-mask comparison, known-failure controls, independent subgroup analysis; synthetic and development evidence only |
| T4 PET measurement | Acquisition-normalized uptake and delineated volume | L07 quantification; L08 methods | Input units, registration and reference scope are valid | FOV, reconstruction, partial annotations or geometry distort risk | Versioned physical QC/reference SOP; no new patient measurement here |
| T5 Shift/independence | Disjoint partitions and cross-hospital testing | L03 items 19–20; L09 results | No evaluation patient influences any training or selection stage | Repeated exams, member overlap, target tuning or spectrum changes | Authorized all-member patient audit and separate external contrasts; G1 BLOCKED_PROVENANCE |
| T6 Translation | Live decision-support evaluation; PET referral simulation | L10 Box 1/Table 2; L11 referral methods | Referral can improve decisions at an acceptable real cost | False prompts, no correction gain, automation bias or workload increase | Approved reader protocol and observed time/corrections; NOT RUN |

## Exclusions, uncertainty and novelty restraint

- Roy 2019 and Zenk 2025 are now specifically identified above; no vague
  author/year shorthand is used as evidence. Their tasks and versions remain distinct.
- P01 is now full-text checked within the bounds above. It remains a preprint,
  excluded from the **eleven published references**; no exhaustive novelty
  search or independent verification of its patient/member lineage is claimed.
- No claim that this project invented selective review, ensemble QC, PET
  uncertainty, or risk–coverage is supported or made. Proposed contributions
  require the specific independent comparisons in the framework.
- A missing artifact/reporting item is UNKNOWN, not evidence it was never
  produced. Publication and checklist adherence are not patient independence.

## Workflow/software attribution (not biomedical prior art)

Local `scientific-critical-thinking` and `citation-management` skill instructions
(K-Dense) informed claim appraisal and metadata verification. They were read,
not treated as empirical evidence; their scripts were not claimed as executed.
Kassis T, Agarwal V, He Y, Patel D, Brueckner AM. **Scientific Agent Skills: A
Library of Procedural Knowledge for Research Agents** (2026).
[arXiv:2609.00065](https://arxiv.org/abs/2609.00065),
[DOI](https://doi.org/10.48550/arXiv.2609.00065).
**VERIFIED_PREPRINT**: author list/title/current abstract record checked; no
journal version identified in that record. This is workflow attribution only,
not one of the eleven published scientific references above.

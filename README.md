# Adaptive Risk Gate

Code and aggregate results for **"Risk-controlled oversight for multimodal chest-radiograph AI: finite-sample guarantees for escalation and critical-finding risk, and the limited value of requesting more information"** (Abdur Rahman, 2026).

A gate routes each chest-radiograph case to Answer, Escalate or Ask. Escalation thresholds are calibrated with Learn-then-Test to bound severity-weighted missed-finding burden, with simultaneous bounds for four critical findings (edema, consolidation, pneumonia, pneumothorax).

## Contents

| Path | What |
|---|---|
| `notebooks/01_main_analysis.ipynb` | Full pipeline: embeddings, cross-fitted classifier, gate calibration, robustness, NegBio second labeler, external NIH ChestX-ray14 check, results tables |
| `notebooks/02_mimic_subgroup_audit.ipynb` | MIMIC subgroup audit (sex, age, race); reuses checkpoints written by notebook 01 |
| `notebooks/03_external_chexpert_plus.ipynb` | Second external cohort, CheXpert Plus (Stanford): frozen MIMIC models applied with clinical history and lateral views, risk targets, routing baselines, Ask actions, sex/age/race subgroups; reuses checkpoints written by notebook 01; aggregate results in `results/external_chexpert_plus/` |
| `results/main/` | Aggregate result tables (CSV), `results_v19.json`, `Results_Summary_V19.md` scorecard |
| `results/mimic_subgroups/` | Subgroup AUROC and risk tables |
| `figures/src/make_figures.py` | Regenerates all manuscript figures from `results/` |
| `figures/final/` | Final figures (PDF and PNG) |

`V19` in result file names is the internal run version that produced the reported results.

## Data access

No patient-level data, embeddings, images or report text are included. Everything in `results/` is aggregate.

- **MIMIC-CXR-JPG 2.1.0, MIMIC-CXR 2.1.0 and MIMIC-IV 3.1:** credentialed access through [PhysioNet](https://physionet.org). You must complete the credentialing process and sign the data use agreement; embeddings derived from these data cannot be redistributed.
- **NIH ChestX-ray14:** public.
- **CheXpert Plus:** Stanford AIMI via [Redivis](https://stanford.redivis.com/datasets/5yyj-1a9f6ap0x); requires approved data access under the Stanford research agreement.
- **Models:** BiomedCLIP and BiomedBERT are loaded from Hugging Face.

## Running

The notebooks were run on Google Colab with data mounted from Google Drive; paths such as `/content/drive/MyDrive/...` must be changed to your own storage. Run notebook 01 first, then 02 and 03 (03 asks for Redivis sign-in). Figures:

```
pip install -r requirements.txt
python figures/src/make_figures.py
```

`requirements.txt` is not version-pinned; pin versions from your environment for exact reproduction.

## Severity weights

Per-finding severity weights are author-assigned, informed by published literature on the urgency of chest radiographic findings, and were not rated by clinicians. They are defined as `SEVERITY` in the notebooks and listed in the manuscript Methods.

## Citation

Please cite the manuscript (reference to be added on publication). MIT licence; see `LICENSE`.

Author: Abdur Rahman, Independent Researcher. ORCID: https://orcid.org/0009-0005-5495-5405

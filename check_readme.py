"""Verify numerical claims in README.md against the aggregate outputs and analysis notebook."""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN, SUB, CXP = ROOT/'results'/'main', ROOT/'results'/'mimic_subgroups', ROOT/'results'/'external_chexpert_plus'
readme = (ROOT/'README.md').read_text(encoding='utf8').replace('−', '-').replace('–', '-')
SECTION = readme[:readme.index('## Citation')]   # the part with numeric claims
r = json.load(open(MAIN/'results_v19.json')); sg = json.load(open(SUB/'mimic_subgroups.json'))
x = json.load(open(CXP/'results_v20_chexpert_plus.json'))['external_chexpert_plus']

def rows(name, base=MAIN):
    return list(csv.DictReader(open(base/f'{name}.csv')))

def nb_source(name):
    nb = json.load(open(ROOT/'notebooks'/name, encoding='utf8'))
    return '\n'.join(''.join(c['source']) for c in nb['cells'])
CODE = nb_source('01_main_analysis.ipynb')
PLAN_SRC = CODE[CODE.index('PLAN = dict('):]; PLAN_SRC = PLAN_SRC[:PLAN_SRC.index('\n)\n')+3]
class _NP:
    @staticmethod
    def geomspace(*a, **k):
        return type('L', (), {'tolist': lambda self: []})()
_ns = {'np': _NP}; exec(PLAN_SRC, _ns); PLAN = _ns['PLAN']

checks = []
def must(label, text):
    checks.append(('must', label, text, text in SECTION))
def code(label, text, ok):
    checks.append(('code', label, text, bool(ok) and text in SECTION))
pc = lambda v, d=1: f'{100*v:.{d}f}%'

# MIMIC and external target attainment
g = r['guarantee_internal']
fc = r['fresh_confirmation']
partitions = rows('seed_stability')
tally = f"{g['realised_le_alpha']}/{g['configurations']}"
patient_count = r['label_agreement']['patients']
code('cross-fit', f"**{tally}** score-target combinations in each of three partitions of the same {patient_count:,} patients",
     len(partitions) == 3 and all(row['guarantee'] == tally for row in partitions))
must('additional MIMIC', f"**{fc['target_met']}/{fc['configs']}** targets in {fc['patients']:,} additional MIMIC patients")
e = r['external_nih']
code('NIH', f"On NIH ChestX-ray14 ({e['patients']:,} patients), the four-signal policy met "
     f"**{e['target_met_mimic_calibrated']}/{e['configs']}** exploratory targets with either calibration source",
     e['target_met_mimic_calibrated'] == e['target_met_nih_recalibrated'])
tn = x['targets_natural']
must('CheXpert Plus source', f"MIMIC thresholds met **{tn['met_mimic_calibrated']}/{tn['configs']}** targets")
must('CheXpert Plus local', f"After local calibration on {x['cal_patients']:,} patients, the policy met "
     f"**{tn['met_cxp_recalibrated']}/{tn['configs']}** targets on the same {x['test_patients']:,} evaluation patients")

# MIMIC referral rates and the primary paired contrast
gates = {row['gate']: pc(float(row['referral'])) for row in rows('gate_at_guaranteed_risk')
         if row['method'] == 'ltt' and row['harm'] == 'fn' and row['alpha'] == '0.03'}
must('referral rates', f"At a MIMIC burden target of 0.03, uncertainty alone referred **{gates['U']}** "
     f"and the four-signal policy referred **{gates['UDMS']}**")
must('comparators', f"Entropy referred {gates['entropy']}, conformal ambiguity {gates['ambiguity']}, and the "
     f"learning-to-defer surrogates {gates['L2D_U']} (uncertainty) and {gates['L2D_UDMS']} (four signals)")
rq = next(q for q in rows('rq1_referral_contrasts')
          if q['harm'] == 'fn' and q['alpha'] == '0.03' and q['contrast'] == 'Full gate vs binary baseline')
d, lo, hi = (1000 * float(rq[k]) for k in ('delta_referral', 'lo', 'hi'))
must('primary contrast', f"**{d:.1f} per 1,000 patients** (95% CI {lo:.1f} to {hi:.1f}, "
     f"Holm-adjusted p = {float(rq['p_holm']):.2f})")

# Value of history in the paired subset and in the budget simulation
labels = rows('classifier_per_label')
def macro_auroc(column):
    return sum(float(row[column]) for row in labels) / len(labels)
must('paired AUROC', f"macro-AUROC from **{macro_auroc('auroc_image_only_on_present'):.3f} to "
     f"{macro_auroc('auroc_image_plus_context'):.3f}**")
cost = next(q for q in rows('budget_contrasts') if q['budget'] == '0.3' and q['metric'] == 'cost'
            and q['policy_a'] == 'ask_ctx_UDMS' and q['policy_b'] == 'binary_UDMS')
must('workload budget', f"mean budget of {float(cost['budget']):.2f} review units per patient")
must('modeled cost', f"**{float(cost['delta']):.5f} per patient** (95% CI "
     f"{float(cost['lo']):.5f} to {float(cost['hi']):.5f})")
must('MIMIC subgroups', f"{sg['point_target_met']}/{sg['configs']} MIMIC")
must('CheXpert Plus subgroups', f"{x['subgroups']['point_target_met']}/{x['subgroups']['configs']} CheXpert Plus subgroup configurations")

# ---- Methods at a glance: design constants read live from the notebook
code('delta', 'δ = 0.10', PLAN['delta'] == 0.10)
code('boot', '5,000 replicates', PLAN['boot'] == 5000)
code('folds', 'six patient groups', PLAN['folds'] == 6)
code('seeds', 'Three partitions reused the same patients', len(PLAN['seeds']) == 3)
code('candidate cutoffs', '201 candidate cutoffs', 'ESC_RATES = np.linspace(1, 0, 201)' in CODE)
hk = PLAN['harm_kinds']
code('burden targets', f"{hk['fn'][0]:.2f}-{hk['fn'][-1]:.2f}", True)
code('critical targets', f"{hk['severe'][0]:.2f}-{hk['severe'][-1]:.2f}", True)
code('severity in notebooks', '`SEVERITY` in the notebooks', 'SEVERITY = np.array(' in CODE)
# NOTE: the encoder's token limit and embedding width are read from a runtime config manifest, not hardcoded in the
# notebook source, so they can't be verified as literals from this repo's content alone - not checked here.

bad = [c_ for c_ in checks if not c_[3]]
print(f"{len(checks)-len(bad)}/{len(checks)} README checks passed against results/ and notebooks/")
for kind, label, text, _ in bad:
    print('FAILED', kind, '|', label, '->', text)
sys.exit(1 if bad else 0)

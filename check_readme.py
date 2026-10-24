"""Verify every number in this repo's README.md Key-results and Methods sections against results/ and notebooks/.

Same idea as a manuscript number audit, applied to the repo's own public claims instead: every number in README.md
must be traced to either a value in results/*.json or results/*.csv, or a literal design constant read from the
analysis notebooks (the PLAN dict, SEVERITY, etc.). No manuscript text or numbers are used here or needed - this
file only reads what is already public in this repository.

Run: python check_readme.py   (repo root; needs no extra packages beyond the standard library)"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN, SUB, CXP = ROOT/'results'/'main', ROOT/'results'/'mimic_subgroups', ROOT/'results'/'external_chexpert_plus'
readme = (ROOT/'README.md').read_text(encoding='utf8').replace('−', '-').replace('–', '-')
SECTION = readme[readme.index('## Key results'):readme.index('## Citation')]   # the part with numeric claims
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

# ---- row 1: cross-fit and untouched guarantees
g = r['guarantee_internal']; fc = r['fresh_confirmation']
must('cross-fit', f"**{g['realised_le_alpha']}/{g['configurations']}** cross-fitted configurations")
must('untouched', f"**{fc['target_met']}/{fc['configs']}** targets on 2,000 untouched MIMIC patients")

# ---- row 2: NIH and CheXpert Plus guarantees
e = r['external_nih']
must('NIH', f"**{e['target_met_mimic_calibrated']}/{e['configs']}** with the MIMIC threshold unchanged")
tn = x['targets_natural']
must('CXP kept', f"only **{tn['met_mimic_calibrated']}/{tn['configs']}** with the MIMIC threshold")
must('CXP recal', f"**{tn['met_cxp_recalibrated']}/{tn['configs']}** after recalibrating the threshold on {x['cal_patients']:,} local patients")

# ---- row 3: escalation rates at burden target 0.03
gg = {(q['harm'], q['alpha'], q['gate']): q for q in rows('gate_at_guaranteed_risk') if q['method'] == 'ltt'}
ref = lambda gate: float(gg[('fn', '0.03', gate)]['referral'])
must('escalation', f"**{pc(ref('UDMS'))}** (calibrated uncertainty) vs {pc(ref('entropy'))} entropy, {pc(ref('ambiguity'))} conformal ambiguity, "
     f"{round(100*ref('L2D_U'))}-{round(100*ref('L2D_UDMS'))}% surrogate learning-to-defer")

# ---- row 4: primary endpoint (extra signals)
rq = [q for q in rows('rq1_referral_contrasts') if q['harm'] == 'fn' and q['alpha'] == '0.03' and q['contrast'] == 'Full gate vs binary baseline'][0]
d, lo, hi = float(rq['delta_referral']), float(rq['lo']), float(rq['hi'])
must('primary endpoint', f"primary endpoint {1000*d:.1f} escalations per 1,000; 95% CI {1000*lo:.1f} to +{1000*hi:.1f}; Holm p = {float(rq['p_holm']):.1f}")

# ---- row 5: value of information
c = r['classifier']
must('AUROC gain', f"macro-AUROC {c['macro_auroc_image_only']:.3f} → {c['macro_auroc_with_context']:.3f}")

# ---- row 6: subgroups
must('MIMIC subgroups', f"{sg['point_target_met']}/{sg['configs']} MIMIC")
must('CXP subgroups', f"{x['subgroups']['point_target_met']}/{x['subgroups']['configs']} CheXpert Plus subgroup configurations")

# ---- Methods at a glance: design constants read live from the notebook
code('delta', 'δ = 0.10', PLAN['delta'] == 0.10)
code('boot', '5,000 replicates', PLAN['boot'] == 5000)
code('folds', 'six patient groups', PLAN['folds'] == 6)
code('seeds', 'three independent fold assignments', len(PLAN['seeds']) == 3)
hk = PLAN['harm_kinds']
code('burden targets', f"{hk['fn'][0]:.2f}-{hk['fn'][-1]:.2f}", True)
code('critical targets', f"{hk['severe'][0]:.2f}-{hk['severe'][-1]:.2f}", True)
code('severity in notebooks', '`SEVERITY` in the notebooks', 'SEVERITY = np.array(' in CODE)
# NOTE: the encoder's token limit and embedding width are read from a runtime config manifest, not hardcoded in the
# notebook source, so they can't be verified as literals from this repo's content alone - not checked here.

bad = [c_ for c_ in checks if not c_[3]]
print(f"{len(checks)-len(bad)}/{len(checks)} README numbers verified against results/ and notebooks/")
for kind, label, text, _ in bad:
    print('FAILED', kind, '|', label, '->', text)
sys.exit(1 if bad else 0)

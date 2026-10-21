"""Publication figures for the manuscript. Reads only the share-safe result tables; writes vector PDF + 450-dpi PNG.
Run:  python make_figures.py        (needs numpy, pandas, matplotlib)
Colours: validated categorical palette (blue, orange, aqua, magenta, violet) with direct labels; sequential/diverging ramps for heatmaps."""
import re, json, ast
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[2]
R = ROOT/'results'/'main'; RB = ROOT/'results'/'mimic_subgroups'
OUT = ROOT/'figures'/'final'; OUT.mkdir(exist_ok=True)
res = json.load(open(R/'results_v19.json'))

C = dict(blue='#2a78d6', orange='#eb6834', aqua='#1baf7a', yellow='#eda100', magenta='#e87ba4', violet='#6250d6', red='#e34948', green='#008300')
INK, INK2, MUTED, GRID, AXIS, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#ffffff'
plt.rcParams.update({
    'font.family': 'Arial', 'font.size': 7.5, 'axes.titlesize': 8, 'axes.labelsize': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'axes.edgecolor': AXIS, 'axes.linewidth': 0.7, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.facecolor': SURF, 'figure.facecolor': SURF, 'savefig.facecolor': SURF,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.5, 'axes.axisbelow': True, 'legend.frameon': False, 'legend.fontsize': 7,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'lines.solid_capstyle': 'round'})
def rd(name, base=R):
    return pd.read_csv(base/f'{name}.csv')
def panel(ax, letter, x=-0.12, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=10, fontweight='bold', va='bottom', ha='left', color=INK)
def save(fig, name):
    fig.savefig(OUT/f'{name}.pdf', bbox_inches='tight'); fig.savefig(OUT/f'{name}.png', dpi=450, bbox_inches='tight'); plt.close(fig); print('saved', name)
def dotci(ax, y, m, lo, hi, color, size=22, marker='o', lw=1.4, zorder=3):
    ax.hlines(y, lo, hi, color=color, lw=lw, zorder=zorder); ax.scatter([m], [y], s=size, color=color, marker=marker, zorder=zorder+1, edgecolor=SURF, linewidth=0.6)
def num(s): return float(s)

# ============================================================== Figure 1: study design
def fig1():
    fig, ax = plt.subplots(figsize=(7.4, 5.3)); ax.set_xlim(0, 100); ax.set_ylim(0, 72); ax.axis('off'); ax.grid(False)
    def box(x, y, w, h, text, fc='#f3f6fb', ec=AXIS, fs=6.8, bold=False, color=INK):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.25,rounding_size=1.2', fc=fc, ec=ec, lw=0.9))
        ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', color=color, linespacing=1.3)
    def arrow(x1, y1, x2, y2, color=INK2, rad=0.0):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=9, lw=1.0, color=color, connectionstyle=f'arc3,rad={rad}'))
    ax.text(1, 70.5, 'Data (frozen embeddings; no encoder training)', fontsize=8, fontweight='bold', color=INK2)
    box(1, 56, 30, 12, 'MIMIC-CXR-JPG\n5,994 patients, 14 labels\nimage + clinical history\n+ lateral view', fc='#e8f0fb', ec=C['blue'])
    box(35, 56, 30, 12, 'Untouched MIMIC patients\n2,000 patients\n(no design choice used them)', fc='#e8f0fb', ec=C['blue'])
    box(69, 56, 30, 12, 'NIH ChestX-ray14 (external)\n6,000 patients, image only\n8 labels shared with CheXpert', fc='#fdeee8', ec=C['orange'])
    ax.text(1, 51.5, 'Cross-fitting: 6 patient groups, roles rotate, every patient evaluated once', fontsize=8, fontweight='bold', color=INK2)
    roles = [('Fit', C['blue']), ('Fit', C['blue']), ('Fit', C['blue']), ('Tune', C['aqua']), ('Calibrate', C['yellow']), ('Evaluate', C['violet'])]
    for i, (t, col) in enumerate(roles):
        ax.add_patch(Rectangle((1+i*8.6, 42.5), 8.0, 6, fc=col, ec=SURF, lw=1.2)); ax.text(1+i*8.6+4, 45.5, t, ha='center', va='center', color='white' if t != 'Calibrate' else INK, fontsize=6.8, fontweight='bold')
    ax.text(54, 45.5, 'repeated for 3 independent\ngroup assignments', fontsize=6.8, color=INK2, va='center', linespacing=1.3)
    ax.text(1, 40.3, 'classifier heads  |  temperature, conformal quantiles, gate models  |  escalation threshold  |  out-of-sample results', fontsize=6.0, color=INK2)
    ax.text(1, 35.8, 'Oversight layer', fontsize=8, fontweight='bold', color=INK2)
    box(1, 19.5, 21, 13.5, 'Signals\nuncertainty U\ndisagreement D\nmissing context M\nseverity S, ensemble E', fc='#f6f4fd', ec=C['violet'], fs=6.4)
    box(27, 22, 19, 9.5, 'Gate score:\npredicted loss\nof answering', fs=6.6)
    box(51, 21, 22, 11.5, 'Threshold t calibrated\n(Learn-then-Test):\nrisk among answered\ncases \u2264 target', fc='#fff6e0', ec=C['yellow'], fs=6.4)
    acts = [('Answer', C['green'], 30.5, True), ('Escalate', C['red'], 23.5, True), ('Ask history / lateral view\n(simulated request)', C['orange'], 15.0, False)]
    for t, col, yy, bd in acts:
        box(78, yy, 21, 5.5 if bd else 6.5, t, fc='white', ec=col, fs=6.4, bold=bd)
    arrow(22.4, 26.3, 26.6, 26.7); arrow(46.4, 26.7, 50.6, 26.7)
    arrow(73.4, 28.5, 77.6, 33.0, rad=-0.15); arrow(73.4, 26.7, 77.6, 26.3); arrow(73.4, 25.0, 77.6, 18.8, rad=0.15)
    ax.text(1, 13.0, 'Evaluation', fontsize=8, fontweight='bold', color=INK2)
    items = ['Observed risk vs target:\ncross-fit, untouched,\nNIH, second labeler', 'Escalations needed vs\nentropy, conformal-ambiguity\nand surrogate-loss deferral', 'Extra signals and Ask\nactions: paired intervals,\nHolm, 3 fold assignments', 'Per-finding bounds,\nsex / age / race\nsubgroups']
    for i, t in enumerate(items):
        box(1+i*24.7, 0.6, 23.2, 9.6, t, fc='#f4f4f1', fs=6.2)
    save(fig, 'Fig1_study_design')

# ============================================================== Figure 2: information value and calibration
def fig2():
    cl = rd('classifier_per_label').sort_values('gain_context'); cov = rd('conformal_coverage'); cov = cov[cov.group == 'all'].set_index('label').loc[cl.label]
    fig = plt.figure(figsize=(7.4, 3.9)); gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], height_ratios=[1.35, 1], wspace=0.55, hspace=0.62)
    ax = fig.add_subplot(gs[:, 0]); y = np.arange(len(cl))
    ax.axvline(0, color=INK2, lw=0.8)
    ax.hlines(y, 0, cl.gain_context, color=C['blue'], lw=1.0, alpha=0.35); ax.scatter(cl.gain_context, y+0.12, s=26, color=C['blue'], label='+ clinical history', zorder=3, edgecolor=SURF, lw=0.6)
    ax.scatter(cl.gain_lateral, y-0.12, s=26, color=C['orange'], marker='D', label='+ lateral view', zorder=3, edgecolor=SURF, lw=0.6)
    ax.set_yticks(y, cl.label); ax.set_xlabel('AUROC gain over image only'); ax.set_ylim(-0.7, len(cl)-0.3); ax.grid(axis='y', alpha=0)
    ax.legend(loc='lower right', handletextpad=0.2); panel(ax, 'A', -0.42)
    ax.set_title('What each information request adds (per label)', loc='left', fontsize=8, fontweight='bold', pad=6)
    mac = res['classifier']
    ax.text(0.98, 0.74, f"macro-AUROC {mac['macro_auroc_image_only']:.3f} \u2192 {mac['macro_auroc_with_context']:.3f} with history\nmacro gain from lateral view: +{mac['macro_gain_lateral']:.3f}", transform=ax.transAxes, fontsize=6.6, va='top', ha='right', color=INK2)
    # B: routing value in cost units
    ax2 = fig.add_subplot(gs[0, 1]); v = res['value_of_information']
    for i, (k, lab, col, mk) in enumerate([('context', 'history', C['blue'], 'o'), ('lateral', 'lateral view', C['orange'], 'D')]):
        dotci(ax2, 1-i, v[k]['mean']*1e3, v[k]['lo']*1e3, v[k]['hi']*1e3, col, marker=mk)
    ax2.axvline(0, color=INK2, lw=0.8); ax2.set_yticks([1, 0], ['clinical history', 'lateral view']); ax2.set_ylim(-0.6, 1.6); ax2.grid(axis='y', alpha=0)
    ax2.set_xlabel('Realised cost reduction per patient (x10$^{-3}$)'); panel(ax2, 'B', -0.4); ax2.set_title('Value for routing', loc='left', fontsize=8, fontweight='bold', pad=6)
    # C: conformal coverage
    ax3 = fig.add_subplot(gs[1, 1]); yy = np.arange(len(cov))
    ax3.axvline(0.9, color=INK2, lw=0.8, ls='--'); ax3.hlines(yy, cov.lo, cov.hi, color=C['aqua'], lw=1.2); ax3.scatter(cov.coverage, yy, s=14, color=C['aqua'], zorder=3, edgecolor=SURF, lw=0.4)
    ax3.set_yticks([]); ax3.set_ylabel('one line per label', fontsize=6.4); ax3.set_xlim(0.87, 0.93); ax3.set_xlabel('Conformal set coverage (nominal 90%)'); ax3.grid(axis='y', alpha=0)
    ax3.text(0.9, len(cov)-0.1, '14 labels', fontsize=6.4, color=MUTED, ha='center', va='bottom'); panel(ax3, 'C', -0.4)
    save(fig, 'Fig2_information_value')

# ============================================================== Figure 3: risk control holds
def fig3():
    g = rd('gate_at_guaranteed_risk'); g = g[g.method == 'ltt']; fr = rd('fresh_cohort_gate'); ex = rd('external_nih_gate'); cf = rd('critical_finding_guarantee')
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.2)); axs = axs.ravel()
    def setup(ax, title, letter):
        ax.axhline(1, color=C['red'], lw=1.0); ax.axhspan(1, 1.6, color=C['red'], alpha=0.06, lw=0); ax.set_ylim(0, 1.45); ax.set_ylabel('Observed risk / target')
        ax.set_title(title, loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax, letter, -0.14); ax.text(0.99, 0.985, 'above 1 = target exceeded', transform=ax.transAxes, ha='right', va='top', fontsize=6, color=C['red'])
    labels = None
    # A cross-fit
    ax = axs[0]; setup(ax, 'Cross-fitted, 5,994 patients', 'A')
    rows = [(h, a) for h in ['fn', 'severe'] for a in sorted(g[g.harm == h].alpha.unique())]; x = np.arange(len(rows)); labels = [('burden\n' if h == 'fn' else 'critical\n')+f'{a:g}' for h, a in rows]
    for gate, col, mk, dx in [('U', C['blue'], 'o', -0.12), ('UDMS', C['violet'], 's', 0.12)]:
        r = [num(g[(g.harm == h) & (g.alpha == a) & (g.gate == gate)].realised_risk.iloc[0])/a for h, a in rows]
        ax.scatter(x+dx, r, s=24, color=col, marker=mk, label={'U': 'uncertainty only', 'UDMS': 'full signal set'}[gate], zorder=3, edgecolor=SURF, lw=0.5)
    ax.set_xticks(x, labels, rotation=0); ax.legend(loc='upper left', ncol=2, handletextpad=0.2, columnspacing=0.8, bbox_to_anchor=(0, 0.93))
    # B untouched
    ax = axs[1]; setup(ax, 'Untouched MIMIC patients, n = 2,000', 'B')
    for gate, col, mk, dx in [('U', C['blue'], 'o', -0.12), ('UDMS', C['violet'], 's', 0.12)]:
        for i, (h, a) in enumerate(rows):
            q = fr[(fr.harm == h) & (fr.alpha == a) & (fr.gate == gate)].iloc[0]
            dotci(ax, 0, 0, 0, 0, col, size=0); ax.vlines(i+dx, q.risk_lo/a, q.risk_hi/a, color=col, lw=1.2); ax.scatter([i+dx], [q.risk/a], s=24, color=col, marker=mk, zorder=3, edgecolor=SURF, lw=0.5)
    ax.set_xticks(x, labels)
    # C external
    ax = axs[2]; setup(ax, f"External NIH ChestX-ray14, n = {res['external_nih']['patients']:,}", 'C')
    exu = ex[ex.gate == 'UDMS']; rowsx = [(h, a) for h in ['fn', 'severe'] for a in sorted(exu[exu.harm == h].alpha.unique())]; xx = np.arange(len(rowsx))
    for col_r, col_hi, color, mk, dx, lab in [('risk_mimic_calibrated', 'risk_hi_mimic', C['orange'], 'o', -0.12, 'MIMIC calibration unchanged'), ('risk_nih_recalibrated', 'risk_hi_nih', C['aqua'], 's', 0.12, 'threshold recalibrated on NIH')]:
        r = [exu[(exu.harm == h) & (exu.alpha == a)][col_r].iloc[0]/a for h, a in rowsx]; hi = [exu[(exu.harm == h) & (exu.alpha == a)][col_hi].iloc[0]/a for h, a in rowsx]
        ax.vlines(xx+dx, r, hi, color=color, lw=1.0); ax.scatter(xx+dx, r, s=24, color=color, marker=mk, label=lab, zorder=3, edgecolor=SURF, lw=0.5)
    ax.set_xticks(xx, [('burden\n' if h == 'fn' else 'critical\n')+f'{a:.3g}' for h, a in rowsx]); ax.legend(loc='upper left', handletextpad=0.2, bbox_to_anchor=(0, 0.93))
    ax.text(0.99, 0.80, 'whiskers: upper 95% bound', transform=ax.transAxes, ha='right', fontsize=6, color=MUTED)
    # D per-finding
    ax = axs[3]; setup(ax, 'Per-finding bounds, one shared threshold', 'D')
    labs = ['Edema', 'Consolidation', 'Pneumonia', 'Pneumothorax']; sh = cf[(cf.method == 'shared_score_single_threshold') & (cf.gate == 'UDMS')]
    for frac, col, mk, dx, name in [(0.75, C['blue'], 'o', -0.12, 'target = 75% of answer-everything rate'), (0.5, C['violet'], 's', 0.12, 'target = 50% of answer-everything rate')]:
        q = sh[sh.target_fraction == frac].iloc[0]; r = [q[f'risk_{l}']/q[f'target_{l}'] for l in labs]
        ax.scatter(np.arange(4)+dx, r, s=26, color=col, marker=mk, label=name, zorder=3, edgecolor=SURF, lw=0.5)
    ax.set_xticks(np.arange(4), labs, rotation=0, fontsize=6.6); ax.legend(loc='upper left', bbox_to_anchor=(0, 0.93), handletextpad=0.2)
    for a in axs[:3]:
        a.set_xlabel('Target (burden = severity-weighted missed findings; critical = critical-miss rate)', fontsize=6.6)
    fig.tight_layout(h_pad=1.6, w_pad=1.6)
    save(fig, 'Fig3_risk_control')

# ============================================================== Figure 4: efficiency vs baselines
def fig4():
    g = rd('gate_at_guaranteed_risk'); g = g[(g.method == 'ltt') & (g.harm == 'fn')]; p = rd('per_1000_patients')
    fig = plt.figure(figsize=(7.6, 3.5)); gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1], wspace=0.75)
    ax = fig.add_subplot(gs[0]); alphas = sorted(g.alpha.unique())
    styles = [('oracle', 'oracle ceiling', MUTED, '--', 'none'), ('L2D_U', 'surrogate-loss deferral', C['magenta'], '-', 'v'), ('ambiguity', 'conformal ambiguity', C['orange'], '-', '^'),
              ('entropy', 'entropy', C['aqua'], '-', 's'), ('U', 'uncertainty only', C['blue'], '-', 'o'), ('UDMS', 'full signal set', C['violet'], '-', 'D')]
    ends = {}
    for gate, lab, col, ls, mk in styles:
        y = [100*num(g[(g.alpha == a) & (g.gate == gate)].referral.iloc[0]) for a in alphas]
        ax.plot(alphas, y, color=col, ls=ls, lw=1.6 if gate not in ('U', 'UDMS') else 1.6, marker=mk if mk != 'none' else None, ms=3.8, zorder=3, mec=SURF, mew=0.4); ends[gate] = (y[-1], lab, col)
    # direct labels at the right end with simple de-overlap
    items = sorted(ends.items(), key=lambda kv: kv[1][0]); pos = []; last = -99
    for k, (yv, lab, col) in items:
        yy = max(yv, last+5.0); pos.append((yy, lab, col)); last = yy
    for yy, lab, col in pos:
        ax.text(alphas[-1]+0.0007, yy, lab, color=col, fontsize=6.6, va='center', fontweight='bold')
    ax.set_xlim(alphas[0]-0.0005, alphas[-1]+0.0165); ax.set_xticks(alphas); ax.set_ylim(0, 100)
    ax.set_xlabel('Target severity-weighted missed-finding burden (guaranteed)'); ax.set_ylabel('Patients escalated to a clinician (%)')
    ax.set_title('Escalations at equal guaranteed risk', loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax, 'A', -0.17)
    # B forest per 1000
    ax2 = fig.add_subplot(gs[1]); comps = [('Full gate vs binary baseline', 'uncertainty-only gate', C['blue']), ('Full gate vs entropy deferral', 'entropy deferral', C['aqua']),
                                           ('Full gate vs conformal-ambiguity deferral', 'conformal ambiguity', C['orange']), ('Full gate vs learning-to-defer surrogate baseline', 'surrogate-loss deferral', C['magenta'])]
    for i, (key, lab, col) in enumerate(comps):
        q = p[(p.harm == 'fn') & (p.alpha == 0.03) & (p.comparison == key)].iloc[0]
        dotci(ax2, len(comps)-1-i, q.escalations_avoided_per_1000, q.lo, q.hi, col, size=26)
        f = (lambda v: f"{v:.0f}" if abs(v) >= 20 else f"{v:.1f}"); ax2.text(1.03, len(comps)-1-i, f"{f(q.escalations_avoided_per_1000)}\n({f(q.lo)} to {f(q.hi)})", transform=ax2.get_yaxis_transform(), fontsize=6.2, va='center', color=INK2, linespacing=1.15)
    ax2.set_xscale('symlog', linthresh=20, linscale=0.8); ax2.axvline(0, color=INK2, lw=0.8); ax2.set_yticks(np.arange(len(comps))[::-1], [c[1] for c in comps]); ax2.grid(axis='y', alpha=0)
    ax2.set_xticks([-10, 0, 10, 100, 300]); ax2.set_xticklabels(['-10', '0', '10', '100', '300']); ax2.set_xlim(-25, 400)
    ax2.set_xlabel('Escalations avoided per 1,000 patients\n(full signal set vs comparator; burden target 0.03)'); ax2.set_title('Gain of the full gate', loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax2, 'B', -0.52)
    save(fig, 'Fig4_efficiency')

# ============================================================== Figure 5: extra signals and Ask actions
def parse_cost(s):
    m = re.match(r'([+-][\d.]+) \[([+-][\d.]+),([+-][\d.]+)\]', s); return tuple(float(x) for x in m.groups())
def fig5():
    rq = rd('rq1_referral_contrasts'); ens = rd('ensemble_signal_contrasts'); sd = rd('seed_stability'); sr = rd('scheme_robustness'); grid = rd('ask_break_even_grid')
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.4)); ax = axs[0, 0]
    # A primary endpoint
    q = rq[(rq.harm == 'fn') & (rq.alpha == 0.03) & (rq.contrast == 'Full gate vs binary baseline')].iloc[0]; fcon = rd('fresh_cohort_contrast'); f3 = fcon[(fcon.harm == 'fn') & (fcon.alpha == 0.03)].iloc[0]
    rows = [('Cross-fit pooled', q.delta_referral*100, q.lo*100, q.hi*100, C['violet']), ('Untouched MIMIC', f3.delta_referral_full_vs_U*100, f3.lo*100, f3.hi*100, C['violet'])]
    for i, (lab, m, lo, hi, col) in enumerate(rows): dotci(ax, 4-i, m, lo, hi, col, size=28)
    for j in range(3):
        ax.scatter([sd.full_vs_binary.iloc[j]*100], [2-j], s=28, color=C['blue'], marker='D', zorder=4, edgecolor=SURF, lw=0.6)
    ax.axvline(0, color=INK2, lw=0.8); ax.set_yticks([4, 3, 2, 1, 0], ['Cross-fit pooled\n(95% CI)', 'Untouched MIMIC\n(95% CI)', 'Fold assignment 1', 'Fold assignment 2', 'Fold assignment 3']); ax.grid(axis='y', alpha=0)
    ax.set_xlabel('Change in escalation rate, full vs uncertainty-only (percentage points)'); ax.set_xlim(-1.2, 1.0); ax.set_ylim(-0.6, 5.1)
    ax.set_title('Primary endpoint: no stable difference', loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax, 'A', -0.38); ax.text(0.02, 0.985, 'left of 0 = full gate escalates fewer', transform=ax.transAxes, fontsize=6, color=MUTED, va='top')
    # B signals
    ax = axs[0, 1]; items = [('D adds to U', 'cross-modal disagreement D'), ('M adds to U+D', 'missing context M'), ('S adds to U+D+M', 'severity S')]
    rows = [(lab, rq[(rq.harm == 'fn') & (rq.alpha == 0.03) & (rq.contrast == key)].iloc[0]) for key, lab in items]
    e1 = ens[(ens.harm == 'fn') & (ens.alpha == 0.03) & (ens.contrast == 'E adds to U')].iloc[0]; e2 = ens[(ens.harm == 'fn') & (ens.alpha == 0.03) & (ens.contrast == 'E adds to U+D+M+S')].iloc[0]
    rows += [('ensemble spread E (on U)', e1), ('ensemble spread E (on all)', e2)]
    for i, (lab, r) in enumerate(rows): dotci(ax, len(rows)-1-i, r.delta_referral*100, r.lo*100, r.hi*100, C['violet'] if i < 3 else C['aqua'], size=26)
    ax.axvline(0, color=INK2, lw=0.8); ax.set_yticks(np.arange(len(rows))[::-1], [r[0] for r in rows]); ax.grid(axis='y', alpha=0); ax.set_ylim(-0.6, len(rows)-0.4)
    ax.set_xlabel('Change in escalation rate when the signal is added\n(percentage points; burden target 0.03)'); ax.set_title('Signals added to uncertainty', loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax, 'B', -0.4)
    # C Ask by scenario
    ax = axs[1, 0]; names = {'natural': 'History available (natural)', 'mcar30': '30% withheld at random', 'mcar60': '60% withheld at random', 'struct40': '40% withheld, structured\n(scheme unseen in training)'}
    ys = []
    for i, sc in enumerate(['natural', 'mcar30', 'mcar60', 'struct40']):
        m, lo, hi = parse_cost(sr[sr.scheme == sc].ask_context_budget_cost.iloc[0]); y = 5-i; ys.append((y, names[sc]))
        if hi - lo > 0: dotci(ax, y, m*1e4, lo*1e4, hi*1e4, C['blue'], size=28)
        else: ax.scatter([0], [y], s=28, color=C['blue'], marker='o', zorder=4)
    fa = res['fresh_ask_context']; dotci(ax, 0.9, fa['delta_cost']*1e4, fa['lo']*1e4, fa['hi']*1e4, C['aqua'], size=28, marker='s'); ys.append((0.9, 'Untouched MIMIC patients'))
    ax.axvline(0, color=INK2, lw=0.8); ax.set_yticks([y for y, _ in ys], [n for _, n in ys]); ax.grid(axis='y', alpha=0); ax.set_ylim(0.2, 6.1)
    ax.set_xlabel('Change in routing cost when asking for history\n(x10$^{-4}$ cost units; budget 0.3, request cost 0.10)'); ax.set_title('Asking for clinical history', loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax, 'C', -0.45)
    ax.text(0.98, 0.985, 'left of 0 = asking lowers cost', transform=ax.transAxes, fontsize=6, color=MUTED, ha='right', va='top')
    # D heatmap
    ax = axs[1, 1]; gh = grid[(grid.request == 'context') & (grid.budget == 0.3)]; pv = gh.pivot_table(index='a', columns='f', values='delta_cost')*1e4; vt = gh.pivot_table(index='a', columns='f', values='verdict', aggfunc='first')
    cmap = LinearSegmentedColormap.from_list('div', [C['blue'], '#f0efec', C['red']]); lim = np.abs(pv.values).max()
    im = ax.imshow(pv.values, cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim), aspect='auto'); ax.grid(False)
    ax.set_xticks(range(pv.shape[1]), [f'{c:g}' for c in pv.columns]); ax.set_yticks(range(pv.shape[0]), [f'{c:g}' for c in pv.index])
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            v = vt.values[i, j]; mark = {'better': '↓', 'worse': '↑'}.get(v, '')
            ax.text(j, i, f'{pv.values[i, j]:.1f}{mark}', ha='center', va='center', fontsize=6.4, color=INK)
    ax.set_xlabel('Retrieval failure probability'); ax.set_ylabel('Request workload (fraction of a full review)'); ax.set_title('Cost change by request cost (x10$^{-4}$)', loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax, 'D', -0.38)
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.ax.tick_params(labelsize=6); cb.outline.set_visible(False)
    ax.text(0.5, -0.33, '↓ significantly lower cost with asking   ↑ significantly higher', transform=ax.transAxes, fontsize=6, color=MUTED, ha='center')
    fig.tight_layout(h_pad=2.0, w_pad=1.6)
    save(fig, 'Fig5_signals_and_ask')

# ============================================================== Figure 6: subgroups
def fig6():
    sg = rd('mimic_subgroup_risk', RB); au = rd('mimic_subgroup_auroc', RB).set_index('group')
    order = ['sex=F', 'sex=M', 'age<40', 'age 40-64', 'age>=65', 'race=WHITE', 'race=BLACK', 'race=HISPANIC', 'race=ASIAN', 'race=OTHER/UNKNOWN']
    nice = {'sex=F': 'Women', 'sex=M': 'Men', 'age<40': 'Age < 40', 'age 40-64': 'Age 40-64', 'age>=65': 'Age ≥ 65', 'race=WHITE': 'White', 'race=BLACK': 'Black', 'race=HISPANIC': 'Hispanic', 'race=ASIAN': 'Asian', 'race=OTHER/UNKNOWN': 'Other / unknown'}
    u = sg[sg.gate == 'UDMS']; y = np.arange(len(order))[::-1]
    fig, axs = plt.subplots(1, 4, figsize=(7.4, 3.8), sharey=True, gridspec_kw=dict(wspace=0.12))
    ax = axs[0]
    ax.scatter([au.loc[o, 'macro_auroc'] for o in order], y, s=24, color=C['blue'], zorder=3, edgecolor=SURF, lw=0.5)
    ax.set_yticks(y, [f'{nice[o]}  (n={int(u[u.group == o].n.iloc[0]):,})' for o in order]); ax.set_xlim(0.74, 0.9); ax.set_xlabel('Macro-AUROC'); ax.grid(axis='y', alpha=0); panel(ax, 'A', -1.0)
    ax.set_title('Classifier quality', loc='left', fontsize=8, fontweight='bold', pad=6)
    ax = axs[1]; q = u[(u.harm == 'fn') & (u.alpha == 0.03)].set_index('group')
    ax.barh(y, [100*q.loc[o, 'referral'] for o in order], color=C['orange'], height=0.6); ax.set_xlabel('Escalated (%)'); ax.grid(axis='y', alpha=0); panel(ax, 'B', -0.12)
    ax.set_title('Escalation share', loc='left', fontsize=8, fontweight='bold', pad=6)
    for ax, harm, alpha, letter, title in [(axs[2], 'fn', 0.03, 'C', 'Burden (target 0.03)'), (axs[3], 'severe', 0.10, 'D', 'Critical misses (target 0.10)')]:
        q = u[(u.harm == harm) & (u.alpha == alpha)].set_index('group')
        for yy, o in zip(y, order):
            r = q.loc[o]; col = C['red'] if r.risk/alpha > 1 else C['violet']
            ax.hlines(yy, r.lo/alpha, r.hi/alpha, color=col, lw=1.2); ax.scatter([r.risk/alpha], [yy], s=24, color=col, zorder=3, edgecolor=SURF, lw=0.5)
        ax.axvline(1, color=C['red'], lw=1.0); ax.set_xlim(0, 1.4); ax.set_xlabel('Observed risk / target'); ax.grid(axis='y', alpha=0); panel(ax, letter, -0.12)
        ax.set_title(title, loc='left', fontsize=7.6, fontweight='bold', pad=6)
    for ax in axs:
        for yy in [y[1]-0.5, y[4]-0.5]: ax.axhline(yy, color=AXIS, lw=0.6)
    fig.text(0.5, -0.03, 'Escalation share and risks are for the full signal set. Whiskers: 95% interval; red = point estimate above target. AUROC averages the labels with at least 20 positives and negatives (6-14 per group).\nThe guarantee is marginal (over all patients), not per subgroup.', ha='center', fontsize=6.4, color=MUTED)
    save(fig, 'Fig6_subgroups')

# ============================================================== Supplement
def figS1():
    d = rd('decision_curve'); fig, ax = plt.subplots(figsize=(3.6, 3.0))
    sty = [('random', 'random', MUTED, ':'), ('binary_entropy', 'entropy', C['aqua'], '-'), ('binary_L2D', 'surrogate-loss', C['magenta'], '-'), ('binary_U', 'uncertainty only', C['blue'], '-'), ('binary_UDMS', 'full signal set', C['violet'], '-'), ('oracle_binary', 'oracle', MUTED, '--')]
    for k, lab, col, ls in sty:
        r = d[d.policy == k]; ax.plot(r.price_of_workload, r.net_benefit, color=col, ls=ls, lw=1.5, label=lab)
    ax.set_xlabel('Price of one unit of clinician workload'); ax.set_ylabel('Net benefit (cost avoided - price x workload)'); ax.legend(loc='upper right', fontsize=6.4)
    save(fig, 'FigS1_decision_curve')
def figS2():
    tr = rd('external_nih_transfer_auroc'); ct = rd('external_nih_contrast'); ct = ct[ct.comparison == 'Full gate vs U']
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1, 1.1], wspace=0.7)); ax = axs[0]; tr = tr.sort_values('auroc_image_only'); y = np.arange(len(tr))
    ax.hlines(y, 0.5, tr.auroc_image_only, color=C['orange'], lw=1.0, alpha=0.4); ax.scatter(tr.auroc_image_only, y, s=26, color=C['orange'], zorder=3, edgecolor=SURF, lw=0.5)
    ax.set_yticks(y, [f"{l}  ({100*p:.1f}%)" for l, p in zip(tr.label, tr.prevalence)]); ax.set_xlim(0.5, 0.9); ax.set_xlabel('AUROC of the MIMIC-trained image head'); ax.grid(axis='y', alpha=0); panel(ax, 'A', -0.62)
    ax.set_title('Transfer to NIH (prevalence)', loc='left', fontsize=8, fontweight='bold', pad=6)
    ax = axs[1]; ct = ct.reset_index(drop=True)
    for i, r in ct.iterrows():
        col = {'better': C['green'], 'worse': C['red']}.get(r.verdict_holm, MUTED); dotci(ax, len(ct)-1-i, r.delta_referral*100, r.lo*100, r.hi*100, col, size=24)
    ax.axvline(0, color=INK2, lw=0.8); ax.set_yticks(np.arange(len(ct))[::-1], [('burden ' if h == 'fn' else 'critical ')+f'{a:.3g}' for h, a in zip(ct.harm, ct.alpha)]); ax.grid(axis='y', alpha=0)
    ax.set_xlabel('Change in escalation rate (pp)'); ax.set_title('Full vs uncertainty-only gate', loc='left', fontsize=8, fontweight='bold', pad=6); panel(ax, 'B', -0.4)
    ax.text(0.98, 0.36, 'green = fewer, red = more\nescalations (Holm-adjusted)', transform=ax.transAxes, fontsize=6, color=MUTED, ha='right')
    save(fig, 'FigS2_external_nih')

if __name__ == '__main__':
    for f in [fig1, fig2, fig3, fig4, fig5, fig6, figS1, figS2]:
        f()

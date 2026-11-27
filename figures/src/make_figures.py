"""Data figures (Figs. 4-8, S1-S4) of the manuscript, drawn only from the share-safe result tables; writes vector PDF + 450-dpi PNG.
Run:  python make_figures.py        (needs numpy, pandas, matplotlib)
Figures 1-3 are draw.io schematics (drawio/make_drawio.py, drawio/export_drawio.py) and share this palette.
Figures carry panel letters, axes and legends only; titles and explanations are in the manuscript captions.

Chart type follows the question:
  Fig. 4  dumbbells (level and gain per label), interval plots      Fig. 5  realized risk against target, identity line (log-log)
  Fig. 6  risk-coverage curves + slopegraph between cohorts          Fig. 7  forest plots + break-even heatmap
  Fig. 8  subgroup forest plots      S1 transfer scatter with identity line      S2 forest plots      S3 decision curves
Colour has one meaning throughout: image blue, history ochre, lateral teal; four-signal navy, uncertainty only blue,
entropy teal, conformal ambiguity ochre, surrogate learning-to-defer brick, oracle grey; source-calibrated threshold = open ochre,
recalibrated locally = filled teal; better teal, worse brick, inconclusive grey."""
import re, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
R = ROOT/'results'/'main'; RB = ROOT/'results'/'mimic_subgroups'; RX = ROOT/'results'/'external_chexpert_plus'
OUT = ROOT/'figures'/'final'; OUT.mkdir(exist_ok=True)
res = json.load(open(R/'results_v19.json'))
cxp = json.load(open(RX/'results_v20_chexpert_plus.json'))['external_chexpert_plus']

NAVY, BLUE, TEAL, OCHRE, BRICK, GREY = '#17344D', '#3A7FB5', '#00918A', '#C08232', '#B5534A', '#8A97A3'
INK, INK2, MUTED, GRID, AXIS, SURF = '#17344D', '#4A5B6A', '#7D8B97', '#E6EAEE', '#B9C3CC', '#FFFFFF'
GATE = {'UDMS': (NAVY, 'four-signal', 'D'), 'U': (BLUE, 'uncertainty only', 'o'), 'entropy': (TEAL, 'entropy', 's'),
        'ambiguity': (OCHRE, 'conformal ambiguity', '^'), 'L2D_U': (BRICK, 'surrogate learning-to-defer', 'v'), 'oracle': (GREY, 'oracle', None)}
VERDICT = {'better': TEAL, 'worse': BRICK}
plt.rcParams.update({
    'font.family': 'Arial', 'font.size': 7.5, 'axes.labelsize': 7.5, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'axes.edgecolor': AXIS, 'axes.linewidth': 0.7, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK,
    'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.facecolor': SURF,
    'figure.facecolor': SURF, 'savefig.facecolor': SURF, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
    'axes.axisbelow': True, 'legend.frameon': False, 'legend.fontsize': 6.8, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'lines.solid_capstyle': 'round'})


def rd(name, base=R):
    return pd.read_csv(base/f'{name}.csv')
def letter(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=10, fontweight='bold', va='bottom', ha='right', color=INK)
def save(fig, name):
    fig.savefig(OUT/f'{name}.pdf', bbox_inches='tight'); fig.savefig(OUT/f'{name}.png', dpi=450, bbox_inches='tight'); plt.close(fig); print('saved', name)
def dot(ax, y, m, lo=None, hi=None, color=NAVY, marker='o', size=26, filled=True, lw=1.4, z=3):
    if lo is not None:
        ax.hlines(y, lo, hi, color=color, lw=lw, zorder=z)
    ax.scatter([m], [y], s=size, marker=marker, zorder=z+1, color=color if filled else SURF, edgecolor=color if not filled else SURF, linewidth=1.1 if not filled else 0.6)
def zero(ax, at=0):
    ax.axvline(at, color=INK2, lw=0.8, zorder=1)
def ygrid_off(ax):
    ax.grid(axis='y', alpha=0)
def legend_handles(items):
    return [Line2D([], [], color=c, marker=m, mfc=(c if f else SURF), ls=ls, lw=lw, ms=4.6, label=l) for c, m, f, l, ls, lw in items]
pct = FuncFormatter(lambda v, _: f'{v:g}')


# ============================================================== Fig. 4: what history and a lateral view are worth
def fig4():
    cl = rd('classifier_per_label').sort_values('gain_context'); cov = rd('conformal_coverage'); cov = cov[cov.group == 'all'].set_index('label').reindex(cl.label)
    v = res['value_of_information']; y = np.arange(len(cl))
    fig = plt.figure(figsize=(7.4, 4.7)); gs = fig.add_gridspec(2, 3, width_ratios=[1.25, 1.25, 0.8], height_ratios=[3.4, 0.9], wspace=0.1, hspace=0.42)
    axa = fig.add_subplot(gs[0, 0]); axb = fig.add_subplot(gs[0, 1], sharey=axa); axc = fig.add_subplot(gs[0, 2], sharey=axa)
    for ax, base, new, col, mk in [(axa, cl.auroc_image_only_on_present, cl.auroc_image_plus_context, OCHRE, 'o'), (axb, cl.auroc_image_only_on_eligible, cl.auroc_image_plus_lateral, TEAL, 'D')]:
        ax.hlines(y, base, new, color=col, lw=2.4, alpha=0.35, zorder=1)
        ax.scatter(base, y, s=22, color=SURF, edgecolor=BLUE, linewidth=1.1, zorder=3)
        ax.scatter(new, y, s=26, color=col, marker=mk, edgecolor=SURF, linewidth=0.5, zorder=4)
        ax.set_xlim(0.48, 0.98); ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9]); ax.set_xlabel('AUROC'); ygrid_off(ax)
    axa.set_yticks(y, cl.label); axa.set_ylim(-0.7, len(cl)-0.3); axb.tick_params(labelleft=False); axc.tick_params(labelleft=False)
    fig.legend(handles=legend_handles([(BLUE, 'o', False, 'frontal image alone', '', 0), (OCHRE, 'o', True, '+ clinical history', '', 0), (TEAL, 'D', True, '+ lateral view', '', 0)]),
               loc='lower center', bbox_to_anchor=(0.5, -0.03), ncol=3, handletextpad=0.1, columnspacing=1.6)
    axc.axvline(0.9, color=INK2, lw=0.8, ls=(0, (3, 2))); axc.hlines(y, cov.lo, cov.hi, color=NAVY, lw=1.3); axc.scatter(cov.coverage, y, s=16, color=NAVY, zorder=3, edgecolor=SURF, lw=0.4)
    axc.set_xlim(0.875, 0.925); axc.set_xticks([0.88, 0.90, 0.92]); axc.set_xlabel('conformal coverage'); ygrid_off(axc)
    for ax, s in [(axa, 'A'), (axb, 'B'), (axc, 'C')]: letter(ax, s, -0.02 if s != 'A' else -0.5)
    axd = fig.add_subplot(gs[1, :]); zero(axd)
    for i, (k, lab, col, mk) in enumerate([('context', 'clinical history', OCHRE, 'o'), ('lateral', 'lateral view', TEAL, 'D')]):
        dot(axd, 1-i, v[k]['mean']*1e3, v[k]['lo']*1e3, v[k]['hi']*1e3, col, mk, 30, lw=2.0)
    axd.set_yticks([1, 0], ['clinical history', 'lateral view']); axd.set_ylim(-0.6, 1.6); axd.set_xlim(-1.2, 5.2); ygrid_off(axd)
    axd.set_xlabel('cost reduction per patient for routing (×10$^{-3}$)'); letter(axd, 'D', -0.17)
    save(fig, 'Fig4_information_value')


# ============================================================== Fig. 5: realized risk against target
def riskplot(ax, lo, hi):
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    xs = np.array([lo, hi]); ax.fill_between(xs, xs, hi, color=BRICK, alpha=0.07, lw=0, zorder=0); ax.plot(xs, xs, color=BRICK, lw=1.0, zorder=1)
    ax.set_xlabel('target'); ax.set_ylabel('realized risk'); ax.set_aspect('equal')
    fmt = FuncFormatter(lambda v, _: f'{v:g}'); ax.xaxis.set_major_formatter(fmt); ax.yaxis.set_major_formatter(fmt)
    ax.xaxis.set_minor_formatter(FuncFormatter(lambda v, _: '')); ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ''))
HARM_MK = {'fn': 'o', 'severe': '^'}
def rpoint(ax, a, r, hi=None, lo=None, color=NAVY, filled=True, harm='fn', dx=1.0, floor=None):
    x = a*dx
    if floor is not None and r < floor:
        ax.scatter([x], [floor], marker='v', s=22, color=color if filled else SURF, edgecolor=color, lw=1.0, zorder=4); return
    if hi is not None:
        ax.vlines(x, lo if lo is not None else r, hi, color=color, lw=1.0, zorder=3)
    ax.scatter([x], [r], marker=HARM_MK[harm], s=24, color=color if filled else SURF, edgecolor=SURF if filled else color, lw=0.6 if filled else 1.1, zorder=4)

def fig5():
    g = rd('gate_at_guaranteed_risk'); g = g[g.method == 'ltt']; fr = rd('fresh_cohort_gate'); ex = rd('external_nih_gate'); cf = rd('critical_finding_guarantee')
    cx = pd.read_csv(RX/'cxp_gate.csv'); cx = cx[cx.gate == 'UDMS']
    fig, axs = plt.subplots(2, 3, figsize=(7.4, 5.3)); axs = axs.ravel(); LO, HI = 0.003, 0.4
    ax = axs[0]; riskplot(ax, LO, HI)
    for gate, dx in [('U', 0.94), ('UDMS', 1.06)]:
        for _, q in g[g.gate == gate].iterrows(): rpoint(ax, q.alpha, q.realised_risk, q.max_fold_risk, None, GATE[gate][0], True, q.harm, dx)
    ax = axs[1]; riskplot(ax, LO, HI)
    for gate, dx in [('U', 0.94), ('UDMS', 1.06)]:
        for _, q in fr[fr.gate == gate].iterrows(): rpoint(ax, q.alpha, q.risk, q.risk_hi, q.risk_lo, GATE[gate][0], True, q.harm, dx)
    ax = axs[2]; riskplot(ax, 0.0003, 0.05); exu = ex[ex.gate == 'UDMS']
    for _, q in exu.iterrows():
        rpoint(ax, q.alpha, q.risk_mimic_calibrated, q.risk_hi_mimic, None, OCHRE, False, q.harm, 0.94, floor=0.0004)
        rpoint(ax, q.alpha, q.risk_nih_recalibrated, q.risk_hi_nih, None, TEAL, True, q.harm, 1.06)
    for ax, sc in [(axs[3], 'natural'), (axs[4], 'image_only')]:
        riskplot(ax, LO, HI)
        for _, q in cx[cx.scenario == sc].iterrows():
            rpoint(ax, q.alpha, q.risk_mimic_calibrated, q.risk_hi_mimic, None, OCHRE, False, q.harm, 0.94)
            rpoint(ax, q.alpha, q.risk_cxp_recalibrated, q.risk_hi_cxp, None, TEAL, True, q.harm, 1.06)
    ax = axs[5]; riskplot(ax, 0.001, 0.06); sh = cf[(cf.method == 'shared_score_single_threshold') & (cf.gate == 'UDMS')]
    fmk = {'Edema': 'o', 'Consolidation': 's', 'Pneumonia': '^', 'Pneumothorax': 'D'}
    for frac, filled in [(0.75, False), (0.5, True)]:
        q = sh[sh.target_fraction == frac].iloc[0]
        for l, m in fmk.items():
            ax.scatter([q[f'target_{l}']], [q[f'risk_{l}']], marker=m, s=24, color=NAVY if filled else SURF, edgecolor=NAVY, lw=1.0, zorder=4)
    ax.legend(handles=legend_handles([(NAVY, m, True, l, '', 0) for l, m in fmk.items()] + [(NAVY, '', False, 'open: 75% of answer-all', '', 0), (NAVY, '', True, 'filled: 50% of answer-all', '', 0)]),
              loc='upper left', fontsize=6, handletextpad=0.1, labelspacing=0.3)
    for i, ax in enumerate(axs): letter(ax, 'ABCDEF'[i], -0.12)
    h = legend_handles([(BLUE, 'o', True, 'uncertainty only', '', 0), (NAVY, 'o', True, 'four-signal', '', 0), (OCHRE, 'o', False, 'source-calibrated threshold', '', 0),
                        (TEAL, 'o', True, 'locally recalibrated threshold', '', 0), (GREY, 'o', True, 'burden', '', 0), (GREY, '^', True, 'critical-miss rate', '', 0)])
    fig.legend(handles=h, loc='lower center', ncol=6, bbox_to_anchor=(0.5, -0.03), handletextpad=0.1, columnspacing=1.0)
    fig.tight_layout(h_pad=1.2, w_pad=1.4, rect=(0, 0.04, 1, 1))
    save(fig, 'Fig5_risk_control')


# ============================================================== Fig. 6: risk-coverage curves and cohort slopegraph
def fig6():
    g = rd('gate_at_guaranteed_risk'); g = g[g.method == 'ltt']
    cg = pd.read_csv(RX/'cxp_gate.csv'); cg = cg[(cg.scenario == 'natural') & (cg.harm == 'fn') & (cg.alpha == 0.03)].set_index('gate')
    fig = plt.figure(figsize=(7.4, 3.0)); gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.82], wspace=0.42)
    for j, harm in enumerate(['fn', 'severe']):
        ax = fig.add_subplot(gs[j])
        for gate in ['oracle', 'L2D_U', 'ambiguity', 'entropy', 'U', 'UDMS']:
            col, lab, mk = GATE[gate]; q = g[(g.harm == harm) & (g.gate == gate)].sort_values('alpha')
            ax.plot(100*(1-q.referral), q.realised_risk, color=col, ls='--' if gate == 'oracle' else '-', lw=1.8 if gate == 'UDMS' else 1.3,
                    marker=mk, ms=3.6, mec=SURF, mew=0.4, zorder=4 if gate == 'UDMS' else 3)
        ax.set_xlim(0, 100); ax.set_xlabel('answered automatically (%)'); ax.set_ylabel('realized burden' if harm == 'fn' else 'realized critical-miss rate')
        ax.set_ylim(0, None); letter(ax, 'AB'[j], -0.18)
    ax = fig.add_subplot(gs[2]); ax.grid(False); ax.spines['bottom'].set_visible(False)
    for k in ['L2D_U', 'ambiguity', 'entropy', 'U', 'UDMS']:
        col = GATE[k][0]; m = 100*g[(g.harm == 'fn') & (g.alpha == 0.03) & (g.gate == k)].referral.iloc[0]; c = 100*cg.loc[k, 'referral_cxp_recalibrated']
        ax.plot([0, 1], [m, c], color=col, lw=1.8 if k == 'UDMS' else 1.3, marker='o', ms=4, mec=SURF, mew=0.5)
    ax.set_xticks([0, 1], ['MIMIC', 'CheXpert\nPlus']); ax.tick_params(axis='x', length=0); ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(0, 100); ax.set_ylabel('referred at burden 0.03 (%)'); ax.yaxis.grid(True, color=GRID); letter(ax, 'C', -0.3)
    fig.legend(handles=legend_handles([(GATE[k][0], GATE[k][2] or '', True, GATE[k][1], '--' if k == 'oracle' else '-', 1.4) for k in ['UDMS', 'U', 'entropy', 'ambiguity', 'L2D_U', 'oracle']]),
               loc='lower center', bbox_to_anchor=(0.5, -0.1), ncol=6, handlelength=1.8, handletextpad=0.3, columnspacing=1.1)
    save(fig, 'Fig6_efficiency')


# ============================================================== Fig. 7: forest plots and break-even heatmap
def parse_cost(s):
    m = re.match(r'([+-][\d.]+) \[([+-][\d.]+),([+-][\d.]+)\]', s); return tuple(float(x) for x in m.groups())
def fig7():
    rq = rd('rq1_referral_contrasts'); ens = rd('ensemble_signal_contrasts'); sd = rd('seed_stability'); sr = rd('scheme_robustness'); grid = rd('ask_break_even_grid')
    cc = pd.read_csv(RX/'cxp_contrasts.csv'); ca = pd.read_csv(RX/'cxp_ask.csv'); sel = lambda df: df[(df.harm == 'fn') & (df.alpha == 0.03)]
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.2), gridspec_kw=dict(width_ratios=[1, 1]))
    ax = axs[0, 0]; zero(ax); q = sel(rq)[sel(rq).contrast == 'Full gate vs binary baseline'].iloc[0]; f3 = sel(rd('fresh_cohort_contrast')).iloc[0]; c3 = sel(cc)[sel(cc).comparison == 'UDMS vs U'].iloc[0]
    for i, (m, lo, hi, col) in enumerate([(q.delta_referral, q.lo, q.hi, NAVY), (f3.delta_referral_full_vs_U, f3.lo, f3.hi, NAVY), (c3.delta_referral, c3.lo, c3.hi, TEAL)]):
        dot(ax, 5-i, m*100, lo*100, hi*100, col, size=30, lw=1.8)
    for j in range(3): dot(ax, 2-j, sd.full_vs_binary.iloc[j]*100, color=BLUE, marker='D', size=22)
    ax.set_yticks([5, 4, 3, 2, 1, 0], ['MIMIC cross-fit', 'additional MIMIC', 'CheXpert Plus', 'fold assignment 1', 'fold assignment 2', 'fold assignment 3'])
    ax.set_ylim(-0.6, 5.6); ax.set_xlim(-1.2, 1.0); ax.set_xlabel('Δ referral, four-signal vs uncertainty only (pp)'); ygrid_off(ax); letter(ax, 'A', -0.42)
    ax = axs[0, 1]; zero(ax); items = [('D adds to U', 'disagreement D'), ('M adds to U+D', 'missing context M'), ('S adds to U+D+M', 'severity S')]
    rr = [(lab, sel(rq)[sel(rq).contrast == key].iloc[0]) for key, lab in items]
    rr += [('ensemble E (on U)', sel(ens)[sel(ens).contrast == 'E adds to U'].iloc[0]), ('ensemble E (on all)', sel(ens)[sel(ens).contrast == 'E adds to U+D+M+S'].iloc[0])]
    for i, (lab, r) in enumerate(rr): dot(ax, len(rr)-1-i, r.delta_referral*100, r.lo*100, r.hi*100, VERDICT.get(r.verdict_holm, GREY), size=28, lw=1.8)
    ax.set_yticks(np.arange(len(rr))[::-1], [r[0] for r in rr]); ax.set_ylim(-0.6, len(rr)-0.4); ax.set_xlabel('Δ referral when added (pp)'); ygrid_off(ax); letter(ax, 'B', -0.42)
    ax = axs[1, 0]; zero(ax); names = {'mcar30': '30% withheld at random', 'mcar60': '60% withheld at random', 'struct40': '40% withheld, structured'}
    ys = []
    for i, sc in enumerate(['mcar30', 'mcar60', 'struct40']):
        m, lo, hi = parse_cost(sr[sr.scheme == sc].ask_context_budget_cost.iloc[0]); dot(ax, 4-i, m*1e4, lo*1e4, hi*1e4, OCHRE, size=28, lw=1.8); ys.append((4-i, names[sc]))
    fa = res['fresh_ask_context']; dot(ax, 1, fa['delta_cost']*1e4, fa['lo']*1e4, fa['hi']*1e4, OCHRE, 's', 26, lw=1.8); ys.append((1, 'additional MIMIC'))
    a3 = ca[ca.action == 'ask_context'].iloc[0]; dot(ax, 0, a3.delta_cost*1e4, a3.lo*1e4, a3.hi*1e4, TEAL, 'o', 28, lw=1.8); ys.append((0, 'CheXpert Plus, 30% withheld'))
    ax.set_yticks([y for y, _ in ys], [n for _, n in ys]); ax.set_ylim(-0.6, 4.6); ax.set_xlim(-12.5, 4.5); ax.set_xlabel('Δ routing cost when asking (×10$^{-4}$)'); ygrid_off(ax); letter(ax, 'C', -0.42)
    ax = axs[1, 1]; gh = grid[(grid.request == 'context') & (grid.budget == 0.3)]
    pv = gh.pivot_table(index='a', columns='f', values='delta_cost')*1e4; vt = gh.pivot_table(index='a', columns='f', values='verdict', aggfunc='first')
    cmap = LinearSegmentedColormap.from_list('div', [TEAL, '#F4F6F7', BRICK]); lim = np.abs(pv.values).max()
    im = ax.imshow(pv.values, cmap=cmap, norm=TwoSlopeNorm(0, -lim, lim), aspect='auto'); ax.grid(False)
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.set_xticks(range(pv.shape[1]), [f'{c:g}' for c in pv.columns]); ax.set_yticks(range(pv.shape[0]), [f'{c:g}' for c in pv.index]); ax.tick_params(length=0)
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            sig = vt.values[i, j] in ('better', 'worse'); val = pv.values[i, j]
            ax.text(j, i, f'{val:+.1f}', ha='center', va='center', fontsize=7 if sig else 6.4, fontweight='bold' if sig else 'normal', color=SURF if abs(val) > 0.6*lim else INK)
            if sig: ax.add_patch(plt.Rectangle((j-0.48, i-0.48), 0.96, 0.96, fill=False, ec=INK, lw=1.0))
    ax.set_xlabel('request failure probability'); ax.set_ylabel('request workload'); letter(ax, 'D', -0.25)
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.ax.tick_params(labelsize=6, length=2); cb.outline.set_visible(False); cb.set_label('Δ cost (×10$^{-4}$)', fontsize=6.6)
    fig.tight_layout(h_pad=2.2, w_pad=2.4)
    save(fig, 'Fig7_signals_and_ask')


# ============================================================== Fig. 8 and S4: subgroup forest plots
def subgroups(rows, auroc, n, order, nice, name, xlim):
    y = np.arange(len(order))[::-1]
    fig, axs = plt.subplots(1, 4, figsize=(7.4, 3.4), sharey=True, gridspec_kw=dict(wspace=0.14))
    ax = axs[0]; ax.scatter([auroc[o] for o in order], y, s=26, color=NAVY, zorder=3, edgecolor=SURF, lw=0.5)
    ax.set_yticks(y, [f'{nice[o]}  ({n[o]:,})' for o in order]); ax.set_xlim(*xlim); ax.set_xlabel('macro-AUROC'); ygrid_off(ax); letter(ax, 'A', -0.04)
    q = rows[(rows.harm == 'fn') & (rows.alpha == 0.03)].set_index('group')
    ax = axs[1]; ax.barh(y, [100*q.loc[o, 'referral'] for o in order], color=OCHRE, height=0.58); ygrid_off(ax)
    for y0, o in zip(y, order): ax.text(100*q.loc[o, 'referral']+1.2, y0, f"{100*q.loc[o, 'referral']:.0f}", va='center', fontsize=6.2, color=INK2)
    ax.set_xlabel('referred (%)'); ax.set_xlim(0, 100*q.referral.max()*1.25); letter(ax, 'B', -0.04)
    for ax, harm, alpha, s in [(axs[2], 'fn', 0.03, 'C'), (axs[3], 'severe', 0.10, 'D')]:
        qq = rows[(rows.harm == harm) & (rows.alpha == alpha)].set_index('group')
        ax.axvspan(1, 2, color=BRICK, alpha=0.07, lw=0); ax.axvline(1, color=BRICK, lw=1.0)
        for y0, o in zip(y, order):
            r = qq.loc[o]; dot(ax, y0, r.risk/alpha, r.lo/alpha, r.hi/alpha, BRICK if r.risk/alpha > 1 else NAVY, size=24, lw=1.3)
        ax.set_xlim(0, 1.45); ax.set_xlabel('burden / target 0.03' if harm == 'fn' else 'critical misses / target 0.10'); ygrid_off(ax); letter(ax, s, -0.04)
    for ax in axs:
        for yy in [y[1]-0.5, y[4]-0.5]: ax.axhline(yy, color=AXIS, lw=0.6)
    save(fig, name)

def fig8():
    sg = rd('mimic_subgroup_risk', RB); au = rd('mimic_subgroup_auroc', RB).set_index('group'); u = sg[sg.gate == 'UDMS']
    order = ['sex=F', 'sex=M', 'age<40', 'age 40-64', 'age>=65', 'race=WHITE', 'race=BLACK', 'race=HISPANIC', 'race=ASIAN', 'race=OTHER/UNKNOWN']
    nice = dict(zip(order, ['Women', 'Men', 'Age < 40', 'Age 40-64', 'Age ≥ 65', 'White', 'Black', 'Hispanic', 'Asian', 'Other / unknown']))
    subgroups(u, au.macro_auroc.to_dict(), {o: int(u[u.group == o].n.iloc[0]) for o in order}, order, nice, 'Fig8_subgroups', (0.74, 0.90))

def figS4():
    u = pd.read_csv(RX/'cxp_subgroups.csv'); u = u[u.gate == 'UDMS']
    order = ['sex=F', 'sex=M', 'age<40', 'age 40-64', 'age>=65', 'race=White', 'race=Black', 'race=Hispanic', 'race=Asian', 'race=Other/unknown']
    nice = dict(zip(order, ['Women', 'Men', 'Age < 40', 'Age 40-64', 'Age ≥ 65', 'White', 'Black', 'Hispanic', 'Asian', 'Other / unknown']))
    base = u[(u.harm == 'fn') & (u.alpha == 0.03)].set_index('group')
    subgroups(u, base.macro_auroc.to_dict(), {o: int(base.loc[o, 'n']) for o in order}, order, nice, 'FigS4_subgroups_chexpert_plus', (0.66, 0.82))


# ============================================================== Supplement
def figS1():
    d = rd('decision_curve'); fig, ax = plt.subplots(figsize=(4.0, 2.9))
    sty = [('binary_UDMS', 'four-signal', NAVY, '-'), ('binary_U', 'uncertainty only', BLUE, '-'), ('binary_entropy', 'entropy', TEAL, '-'),
           ('binary_L2D', 'surrogate learning-to-defer', BRICK, '-'), ('oracle_binary', 'oracle', GREY, '--'), ('random', 'random', GREY, ':')]
    for k, lab, col, ls in sty[::-1]:
        r = d[d.policy == k]; ax.plot(r.price_of_workload, r.net_benefit*1e3, color=col, ls=ls, lw=1.8 if k == 'binary_UDMS' else 1.3)
    ax.legend(handles=legend_handles([(c, '', True, l, ls, 1.5) for _, l, c, ls in sty]), loc='upper right', handlelength=2.2, fontsize=6.4)
    ax.set_xlabel('price of one unit of clinician workload'); ax.set_ylabel('net benefit (×10$^{-3}$)'); ax.set_ylim(-2, None)
    save(fig, 'FigS3_decision_curve')

def figS2():
    mi = rd('classifier_per_label').set_index('label').auroc_image_only
    nih = rd('external_nih_transfer_auroc').set_index('label').auroc_image_only
    tr = pd.read_csv(RX/'cxp_transfer_auroc.csv'); cx = tr[tr.input == 'img'].set_index('label').auroc
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.5))
    for ax, ext, s in [(axs[0], nih, 'A'), (axs[1], cx, 'B')]:
        ax.plot([0.45, 1], [0.45, 1], color=INK2, lw=0.8, ls=(0, (3, 2)), zorder=1); ax.fill_between([0.45, 1], [0.45, 1], 0.45, color=BRICK, alpha=0.05, lw=0)
        xs = mi.reindex(ext.index); ax.scatter(xs, ext, s=26, color=BLUE, edgecolor=SURF, lw=0.5, zorder=3)
        off = {'A': {'Pneumothorax': (-5, -4, 'right')}, 'B': {'Cardiomegaly': (-4, 3, 'right'), 'Pneumothorax': (-5, -4, 'right'), 'Atelectasis': (3, -9, 'left'), 'Fracture': (3, -9, 'left')}}[s]
        for lab in ext.index:
            dx, dy, ha = off.get(lab, (3, 2, 'left'))
            ax.annotate(lab, (xs[lab], ext[lab]), xytext=(dx, dy), textcoords='offset points', fontsize=5.6, color=INK2, ha=ha)
        ax.set_xlim(0.58, 0.97); ax.set_ylim(0.45, 0.92); ax.set_xlabel('AUROC on MIMIC (cross-fitted)'); ax.set_ylabel('external AUROC'); letter(ax, s, -0.12)
    save(fig, 'FigS1_transfer')

def figS3():
    nih = rd('external_nih_contrast'); nih = nih[nih.comparison == 'Full gate vs U']; cc = pd.read_csv(RX/'cxp_contrasts.csv'); cc = cc[cc.comparison == 'UDMS vs U']
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(wspace=0.55))
    for ax, ct, s in [(axs[0], nih, 'A'), (axs[1], cc, 'B')]:
        zero(ax); ct = ct.reset_index(drop=True)
        for i, r in ct.iterrows(): dot(ax, len(ct)-1-i, r.delta_referral*100, r.lo*100, r.hi*100, VERDICT.get(r.verdict_holm, GREY), size=26, lw=1.8)
        ax.set_yticks(np.arange(len(ct))[::-1], [('burden ' if h == 'fn' else 'critical ')+f'{a:.3g}' for h, a in zip(ct.harm, ct.alpha)]); ygrid_off(ax)
        ax.set_xlabel('Δ referral, four-signal vs uncertainty only (pp)'); letter(ax, s, -0.3)
    fig.legend(handles=legend_handles([(TEAL, 'o', True, 'fewer referrals', '', 0), (BRICK, 'o', True, 'more referrals', '', 0), (GREY, 'o', True, 'inconclusive (Holm)', '', 0)]),
               loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.08), handletextpad=0.1)
    save(fig, 'FigS2_external_contrasts')


if __name__ == '__main__':
    for f in [fig4, fig5, fig6, fig7, fig8, figS1, figS2, figS3, figS4]:
        f()

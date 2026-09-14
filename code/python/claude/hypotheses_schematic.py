# schematic: one example neuron's tuning over normed stim space under 3 hypotheses (cols) across contexts (rows)
# cols 1-3 share the 0-1 stim axis; col 4 = H3 re-visualized (each context's panel cut to its sampled range and slid so the peaks line up)
# row order is scrambled in H1/H2 so the eye reads the context label, not the row position
import numpy as np, matplotlib.pyplot as plt, sys
sys.path.insert(0, '/home/nuttidalab/Documents/structuring_contexts/code/python'); from utils import plot_style; plot_style('poster')

threshs, cond_colors = {'C1': .25, 'C2': .5, 'C3': .75}, {'C1': 'orangered', 'C2': 'gray', 'C3': 'deepskyblue'}
stim_ranges = {'C1': (0, .75), 'C2': (0, 1), 'C3': (.25, 1)}          # context-dependent sampling of normed stim space
n_samples = 8
peaks = {'H1': {'C1': .5, 'C2': .5, 'C3': .5},        # tuned at the centre of stim space in every context
         'H2': {'C1': .25, 'C2': .5, 'C3': .75},      # tuned at each context's threshold
         'H3': {'C1': .75, 'C2': .5, 'C3': .25}}      # tuned away from the threshold, mirror of H2
baseline, amp, width = 1, 9, .15    # Hz; gaussian bump
tuning = lambda stim, peak: baseline + amp * np.exp(-(stim - peak) ** 2 / (2 * width ** 2))

# (title, hypothesis, shifted?, row order top -> bottom)
columns = [('H1: in readout', 'H1', False, ['C1', 'C3', 'C2']),
           ('H2: in encoding', 'H2', False, ['C2', 'C3', 'C1']),
           ('H3: in context space', 'H3', False, ['C1', 'C2', 'C3']),
           ('H3, re-visualized', 'H3', True, ['C1', 'C2', 'C3'])]

# layout in figure fractions: every column is a band holding shifted stim coords -.25..1.25 (the shifted H3 needs the widest), same scale everywhere so panel widths compare
n_rows = 3; span = 1.5
col_w, col_gap, left0 = .2, .04, .05
row_h, row_gap, bottom0 = .22, .07, .08
fig = plt.figure(figsize=(16, 8)); fig.suptitle('Hypotheses on how Neurons may Represent Context Changes', y=1.06)   # lifted clear of the column titles

for col, (title, hyp, shifted, row_order) in enumerate(columns):
    col_left = left0 + col * (col_w + col_gap)
    fig.text(col_left + col_w / 2, bottom0 + n_rows * (row_h + row_gap) - .02, title, ha='center', va='bottom', fontsize=24)   # column title at the band centre
    for row, cond in enumerate(row_order):
        lo, hi = stim_ranges[cond]; peak, thresh, color = peaks[hyp][cond], threshs[cond], cond_colors[cond]
        # shared axis: panel spans 0-1, no slide; shifted: panel spans only the sampled range, slid so the peak lands at the column centre
        xlo, xhi, shift = (lo, hi, .5 - peak) if shifted else (0, 1, 0)
        left = col_left + (xlo + shift + .25) / span * col_w; width_frac = (xhi - xlo) / span * col_w
        bottom = bottom0 + (n_rows - 1 - row) * (row_h + row_gap)
        ax = fig.add_axes([left, bottom, width_frac, row_h])

        samples = np.linspace(lo, hi, n_samples); dense = np.linspace(lo, hi, 200)
        ax.plot(dense, tuning(dense, peak), color=color, linewidth=2)
        ax.scatter(samples, tuning(samples, peak), color=color, edgecolors='k', zorder=3)
        ax.axvline(thresh, color='k', linestyle=':')
        xticks = np.arange(xlo, xhi + .01, .25)
        ax.set(xlim=(xlo - .02, xhi + .02), xticks=xticks, xticklabels=[f'{t:g}'.lstrip('0') or '0' for t in xticks], ylim=(0, 11), yticks=[0, 5, 10])   # short labels ('.25') so talk-size ticks don't collide
        if row == n_rows - 1: ax.set(xlabel='stim')
        # every panel names its context, since rows are scrambled across columns
        if col == 0: ax.set(ylabel=f'{cond}\nFR (Hz)')
        else: ax.set(ylabel=cond, yticklabels=[])

plt.savefig(sys.argv[1], dpi=200, bbox_inches='tight'); print('saved', sys.argv[1])

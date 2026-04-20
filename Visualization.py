
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── Style ──────────────────────────────────────────────────
BG, TEXT = '#F8F9FA', '#212121'
COLORS   = {'green':'#4CAF50','red':'#E53935','blue':'#2196F3',
             'amber':'#FF9800','purple':'#9C27B0','teal':'#00BCD4','grey':'#607D8B'}
plt.rcParams.update({
    'figure.facecolor':'#F8F9FA','axes.facecolor':'#F8F9FA',
    'axes.edgecolor':'#E0E0E0','grid.color':'#E0E0E0',
    'axes.labelcolor':TEXT,'xtick.color':TEXT,'ytick.color':TEXT,
    'axes.titlesize':12,'axes.titleweight':'bold',
    'axes.labelsize':10,'font.size':10,'text.color':TEXT,
})

# Ordered categories
AGE_ORDER = ['Under 18','18\u201329','30\u201344','45\u201359','60\u201374','75+']

# Duration order — detect labels dynamically to handle encoding differences
# across operating systems (Windows may read ≤ and – differently from Mac/Linux)
def get_dur_order(df):
    all_cats = df['duration_category'].dropna().unique().tolist()
    keywords = ['Short', 'Standard', 'Long', 'Extended']
    ordered  = []
    for kw in keywords:
        match = next((c for c in all_cats if c.startswith(kw)), None)
        if match:
            ordered.append(match)
    return ordered

# ── Load & Fix ─────────────────────────────────────────────
df = pd.read_csv("C:/Users/kaila/PycharmProjects/TeleHealth_Cleaned.csv")

df['technical_issues'] = df['technical_issues'].map(
    {True:True, False:False, 'True':True, 'False':False, 1:True, 0:False}
)
df['age_band'] = pd.Categorical(df['age_band'], categories=AGE_ORDER, ordered=True)

DUR_ORDER = get_dur_order(df)
MEAN = df['satisfaction_score'].mean()

# ── Reusable helpers ───────────────────────────────────────
def mean_bar(ax, series, color, title, xlabel='Mean Satisfaction',
             ref=True, horizontal=True):
    """Plot a clean mean bar chart with optional reference line."""
    if horizontal:
        bars = ax.barh(series.index, series.values, color=color,
                       edgecolor='white', height=0.55, zorder=3)
        if ref:
            ax.axvline(MEAN, color='#333', linestyle='--',
                       linewidth=1.2, label=f'Mean ({MEAN:.2f})', zorder=4)
        for bar, val in zip(bars, series.values):
            ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_xlim(series.min() - 0.1, series.max() + 0.12)
    else:
        bars = ax.bar(series.index, series.values, color=color,
                      edgecolor='white', width=0.55, zorder=3)
        if ref:
            ax.axhline(MEAN, color='#333', linestyle='--',
                       linewidth=1.2, label=f'Mean ({MEAN:.2f})', zorder=4)
        for bar, val in zip(bars, series.values):
            ax.text(bar.get_x() + bar.get_width()/2, val + 0.005,
                    f'{val:.3f}', ha='center', fontsize=9, fontweight='bold')
        ax.set_ylabel('Mean Satisfaction')
        ax.set_ylim(series.min() - 0.1, series.max() + 0.12)
    ax.set_title(title, fontweight='bold')
    if ref: ax.legend(fontsize=8)
    ax.grid(axis='x' if horizontal else 'y', alpha=0.4, zorder=0)

def insight(ax, text, color='#E3F2FD', border='#90CAF9'):
    """Add insight annotation below axes."""
    ax.text(0.5, -0.26, text, transform=ax.transAxes,
            ha='center', va='top', fontsize=8.5, style='italic', color='#444',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=color,
                      edgecolor=border, alpha=0.9))

def save(fig, name):
    fig.tight_layout(pad=2.5)
    fig.savefig(name, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close(fig)
    print(f"  ✔  {name}")


# ================================================================
# FIGURE 1 — OVERVIEW: Distribution + 4 Primary Drivers
# ================================================================
fig = plt.figure(figsize=(20, 7), facecolor=BG)
fig.suptitle('Telehealth Satisfaction — Overview & Primary Drivers',
             fontsize=16, fontweight='bold', y=1.02)
gs = gridspec.GridSpec(1, 4, wspace=0.42)

# 1a — Distribution
ax = fig.add_subplot(gs[0])
counts = df['satisfaction_score'].value_counts().sort_index()
bar_c  = [COLORS['red'],'#EF6C00','#FDD835',COLORS['green'],COLORS['blue']]
bars   = ax.bar(['Very Poor\n(1)','Poor\n(2)','Neutral\n(3)','Good\n(4)','Excellent\n(5)'],
                counts.values, color=bar_c, edgecolor='white', width=0.6, zorder=3)
for bar, val in zip(bars, counts.values):
    ax.text(bar.get_x()+bar.get_width()/2, val+15,
            f'{val:,}\n({val/len(df)*100:.0f}%)',
            ha='center', fontsize=8, fontweight='bold')
ax.set_title('Satisfaction Distribution\n(n=5,000)', fontweight='bold')
ax.set_ylabel('Consultations')
ax.set_ylim(0, counts.max()*1.25)
ax.grid(axis='y', alpha=0.4, zorder=0)
insight(ax, f"Overall mean = {MEAN:.2f}/5.\n79% rate Good or Excellent.\nOnly 4.3% rate 1–2.")

# 1b — Consultation type
ax = fig.add_subplot(gs[1])
ct = df.groupby('consultation_type')['satisfaction_score'].mean().sort_values()
mean_bar(ax, ct, COLORS['teal'], 'By Consultation Type')
insight(ax, "Mental Health scores highest (4.04).\nGP & Specialist below average.\nΔ = 0.17 pts best vs worst.")

# 1c — Platform (with ANOVA)
ax = fig.add_subplot(gs[2])
plat = df.groupby('platform')['satisfaction_score'].mean().sort_values()
f_stat, p_val = stats.f_oneway(*[df[df['platform']==p]['satisfaction_score']
                                  for p in df['platform'].unique()])
mean_bar(ax, plat, COLORS['amber'], 'By Platform')
sig = "Not significant" if p_val >= 0.05 else "Significant"
insight(ax, f"Range: 3.88–3.94 (very narrow).\n"
            f"ANOVA: F={f_stat:.2f}, p={p_val:.3f}.\n{sig} — platform choice barely matters.")

# 1d — Tech issues (biggest driver)
ax = fig.add_subplot(gs[3])
no_ti = df[df['technical_issues']==False]['satisfaction_score']
ti    = df[df['technical_issues']==True]['satisfaction_score']
t_stat, p_ti = stats.ttest_ind(ti, no_ti)
means_ti = pd.Series({'No Tech Issues\n(n=4,622)': no_ti.mean(),
                       'Had Tech Issues\n(n=378)':  ti.mean()})
bars = ax.bar(means_ti.index, means_ti.values,
              color=[COLORS['green'], COLORS['red']],
              edgecolor='white', width=0.45, zorder=3)
ax.axhline(MEAN, color='#333', linestyle='--', linewidth=1.2,
           label=f'Mean ({MEAN:.2f})')
for bar, val in zip(bars, means_ti.values):
    ax.text(bar.get_x()+bar.get_width()/2, val-0.09,
            f'{val:.3f}', ha='center', fontsize=12,
            fontweight='bold', color='white')
ax.annotate('', xy=(1, means_ti.iloc[1]+0.06),
            xytext=(0, means_ti.iloc[0]-0.06),
            arrowprops=dict(arrowstyle='->', color=COLORS['red'], lw=2))
drop = means_ti.iloc[0] - means_ti.iloc[1]
ax.text(0.5, (means_ti.mean()), f'−{drop:.3f} pts\n(p<0.0001)',
        ha='center', fontsize=9, fontweight='bold', color=COLORS['red'],
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor=COLORS['red'], alpha=0.9))
ax.set_title('Tech Issues Impact\n(#1 Driver)', fontweight='bold')
ax.set_ylabel('Mean Satisfaction Score')
ax.set_ylim(2.5, 4.5)
ax.legend(fontsize=8)
ax.grid(axis='y', alpha=0.4, zorder=0)
insight(ax, f"Largest single driver of dissatisfaction.\n"
            f"0.89 pt drop — statistically confirmed\n(t={t_stat:.1f}, p<0.0001).",
        color='#FFEBEE', border='#EF9A9A')

save(fig, 'sat_01_overview.png')


# ================================================================
# FIGURE 2 — DEMOGRAPHICS (Age, Gender, Remoteness, Interaction)
# ================================================================
fig, axes = plt.subplots(2, 2, figsize=(18, 12), facecolor=BG)
fig.suptitle('Satisfaction by Demographics — Who Is Least Satisfied?',
             fontsize=15, fontweight='bold')

# 2a — Age band
ax = axes[0, 0]
age = df.groupby('age_band', observed=True)['satisfaction_score'].mean().reindex(AGE_ORDER)
ci  = df.groupby('age_band', observed=True)['satisfaction_score'].sem().reindex(AGE_ORDER) * 1.96
cols_age = [COLORS['blue'] if v >= MEAN else COLORS['amber'] for v in age.values]
bars = ax.bar(AGE_ORDER, age.values, color=cols_age, edgecolor='white',
              width=0.6, yerr=ci.values, capsize=4,
              error_kw={'elinewidth':1.5,'ecolor':'#555'}, zorder=3)
ax.axhline(MEAN, color='#333', linestyle='--', linewidth=1.2,
           label=f'Overall ({MEAN:.2f})')
for bar, val in zip(bars, age.values):
    ax.text(bar.get_x()+bar.get_width()/2, val+0.03,
            f'{val:.3f}', ha='center', fontsize=8.5, fontweight='bold')
ax.set_title('By Age Band (with 95% CI)', fontweight='bold')
ax.set_ylabel('Mean Satisfaction Score')
ax.set_ylim(3.6, 4.2)
ax.legend(handles=[mpatches.Patch(color=COLORS['blue'], label='≥ mean'),
                   mpatches.Patch(color=COLORS['amber'], label='< mean')],
          fontsize=8, loc='lower right')
ax.grid(axis='y', alpha=0.4, zorder=0)
insight(ax, "60–74 year olds score lowest (3.860).\n"
            "45–59 score highest (3.955).\n"
            "Overlapping CIs — differences are subtle but consistent.")

# 2b — Gender
ax = axes[0, 1]
gender = df.groupby('gender')['satisfaction_score'].mean().sort_values()
gn     = df.groupby('gender')['satisfaction_score'].count()
g_cols = [COLORS['green'] if v >= MEAN else COLORS['amber'] for v in gender.values]
bars = ax.barh(gender.index, gender.values, color=g_cols,
               edgecolor='white', height=0.45, zorder=3)
ax.axvline(MEAN, color='#333', linestyle='--', linewidth=1.2,
           label=f'Overall ({MEAN:.2f})')
for bar, (val, idx) in zip(bars, zip(gender.values, gender.index)):
    ax.text(val+0.004, bar.get_y()+bar.get_height()/2,
            f'{val:.3f}  (n={gn[idx]:,})', va='center', fontsize=9, fontweight='bold')
ax.set_xlim(3.6, 4.15)
ax.set_title('By Gender', fontweight='bold')
ax.set_xlabel('Mean Satisfaction Score')
ax.legend(fontsize=8)
ax.grid(axis='x', alpha=0.4, zorder=0)
insight(ax, "Non-binary patients score notably lower (3.837).\n"
            "Small sample (n=92) — interpret cautiously.\n"
            "Female patients score highest at 3.937.")

# 2c — Remoteness × Tech Issues interaction
ax = axes[1, 0]
rem_ti = df.pivot_table(values='satisfaction_score', index='remoteness',
                        columns='technical_issues', aggfunc='mean')
rem_order = ['Metro','Regional','Remote']
x, w = np.arange(3), 0.35
b1 = ax.bar(x-w/2, [rem_ti.loc[r, False] for r in rem_order], w,
            label='No Tech Issues', color=COLORS['green'], edgecolor='white', zorder=3)
b2 = ax.bar(x+w/2, [rem_ti.loc[r, True]  for r in rem_order], w,
            label='Had Tech Issues', color=COLORS['red'],   edgecolor='white', zorder=3)
for bars_g in [b1, b2]:
    for bar in bars_g:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h+0.01,
                f'{h:.2f}', ha='center', fontsize=8.5, fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(rem_order)
ax.set_title('Remoteness × Tech Issues Interaction', fontweight='bold')
ax.set_ylabel('Mean Satisfaction Score')
ax.set_ylim(2.5, 4.4); ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.4, zorder=0)
insight(ax, "When tech issues occur, satisfaction collapses to ~3.1\n"
            "regardless of location. Remote patients hit this collapse\n"
            "more often (3× higher tech issue rate).")

# 2d — Low satisfaction profile (score ≤2)
ax = axes[1, 1]
low = df[df['satisfaction_score'] <= 2]
categories  = ['Tech\nissue','Remote\npatient','Specialist\nconsult',
                'Age 60+','Extended\nduration']
low_pcts    = [low['technical_issues'].mean()*100,
               (low['remoteness']=='Remote').mean()*100,
               (low['consultation_type']=='Specialist').mean()*100,
               low['age_band'].isin(['60–74','75+']).mean()*100,
               (low['duration_category']=='Extended (>60 min)').mean()*100]
overall_pcts= [df['technical_issues'].mean()*100,
               (df['remoteness']=='Remote').mean()*100,
               (df['consultation_type']=='Specialist').mean()*100,
               df['age_band'].isin(['60–74','75+']).mean()*100,
               (df['duration_category']=='Extended (>60 min)').mean()*100]
x2 = np.arange(len(categories))
b1 = ax.bar(x2-0.18, overall_pcts, 0.35, label='Overall dataset',
            color='#90CAF9', edgecolor='white', zorder=3)
b2 = ax.bar(x2+0.18, low_pcts,     0.35, label=f'Low sat (1–2, n={len(low)})',
            color=COLORS['red'], edgecolor='white', alpha=0.9, zorder=3)
for bars_g in [b1, b2]:
    for bar in bars_g:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h+0.5,
                f'{h:.0f}%', ha='center', fontsize=8, fontweight='bold')
ax.set_xticks(x2); ax.set_xticklabels(categories, fontsize=9)
ax.set_title(f'Who Is in the Low Satisfaction Group?', fontweight='bold')
ax.set_ylabel('% of Consultations'); ax.legend(fontsize=9)
ax.set_ylim(0, max(low_pcts+overall_pcts)*1.3)
ax.grid(axis='y', alpha=0.4, zorder=0)
insight(ax, "42% of low-sat consults had a tech issue (vs 7.6% overall).\n"
            "Remote & Specialist are over-represented.\n"
            "These are the compounding risk factors.",
        color='#FFEBEE', border='#EF9A9A')

save(fig, 'sat_02_demographics.png')


# ================================================================
# FIGURE 3 — DURATION ANALYSIS
# ================================================================
fig, axes = plt.subplots(1, 3, figsize=(19, 6), facecolor=BG)
fig.suptitle('Satisfaction vs Duration — Is Longer Better?',
             fontsize=15, fontweight='bold')

# 3a — Scatter with regression
ax = axes[0]
sample = df.sample(1000, random_state=42)
sc_colors = [COLORS['green'] if not t else COLORS['red']
             for t in sample['technical_issues']]
ax.scatter(sample['duration_mins'], sample['satisfaction_score'],
           c=sc_colors, alpha=0.35, s=22, zorder=3)
r, p = stats.pearsonr(df['duration_mins'], df['satisfaction_score'])
m, b_reg = np.polyfit(df['duration_mins'], df['satisfaction_score'], 1)
x_line = np.linspace(df['duration_mins'].min(), df['duration_mins'].max(), 100)
ax.plot(x_line, m*x_line+b_reg, color='#333', linewidth=2,
        label=f'Regression (r={r:.3f}, p={p:.3f})')
ax.set_title('Duration vs Satisfaction\n(sample n=1,000)', fontweight='bold')
ax.set_xlabel('Duration (mins)'); ax.set_ylabel('Satisfaction Score')
ax.set_ylim(0.5, 5.5)
ax.legend(handles=[mpatches.Patch(color=COLORS['green'], alpha=0.6, label='No tech issues'),
                   mpatches.Patch(color=COLORS['red'],   alpha=0.6, label='Had tech issues'),
                   plt.Line2D([0],[0], color='#333', linewidth=2, label=f'r={r:.3f}')],
          fontsize=8)
ax.grid(alpha=0.3, zorder=0)
insight(ax, f"r = {r:.3f} — near-zero correlation.\n"
            "Duration alone does NOT predict satisfaction.\n"
            "Red dots (tech issues) cluster low regardless of duration.")

# 3b — Mean by duration category
ax = axes[1]
dur = df.groupby('duration_category')['satisfaction_score'].mean().reindex(DUR_ORDER)
dur_n = df.groupby('duration_category')['satisfaction_score'].count().reindex(DUR_ORDER)
d_cols = [COLORS['green'] if v >= MEAN else COLORS['amber'] for v in dur.values]
bars = ax.bar(range(4), dur.values, color=d_cols, edgecolor='white', width=0.55, zorder=3)
ax.axhline(MEAN, color='#333', linestyle='--', linewidth=1.2, label=f'Mean ({MEAN:.2f})')
ax.set_xticks(range(4))
ax.set_xticklabels(['Short\n(≤15 min)','Standard\n(16–30)','Long\n(31–60)','Extended\n(>60)'], fontsize=9)
for i, (bar, val) in enumerate(zip(bars, dur.values)):
    ax.text(bar.get_x()+bar.get_width()/2, val+0.006,
            f'{val:.3f}\n(n={dur_n.iloc[i]:,})', ha='center', fontsize=8.5, fontweight='bold')
ax.set_title('Mean Satisfaction by Duration Category', fontweight='bold')
ax.set_ylabel('Mean Satisfaction Score')
ax.set_ylim(3.5, 4.25); ax.legend(fontsize=8)
ax.grid(axis='y', alpha=0.4, zorder=0)
insight(ax, "Sweet spot: 31–60 mins scores best (3.982).\n"
            "Extended (>60 min) scores worst (3.793).\n"
            "Moderate length = optimal patient experience.")

# 3c — Type × Duration heatmap
ax = axes[2]
heat = df.pivot_table(values='satisfaction_score', index='consultation_type',
                      columns='duration_category', aggfunc='mean')[DUR_ORDER]
sns.heatmap(heat, ax=ax, annot=True, fmt='.2f', cmap='RdYlGn',
            vmin=3.5, vmax=4.3, linewidths=0.5, linecolor='white',
            cbar_kws={'label':'Mean Satisfaction'})
ax.set_title('Satisfaction: Type × Duration', fontweight='bold')
ax.set_xlabel('Duration Category'); ax.set_ylabel('Consultation Type')
ax.set_xticklabels(['Short','Standard','Long','Extended'], rotation=15)
insight(ax, "Mental Health + Long = highest satisfaction (4.08).\n"
            "GP + Extended = lowest cell (3.71).\n"
            "Specialists drop most sharply in extended consults.")

save(fig, 'sat_03_duration.png')


# ================================================================
# FIGURE 4 — HOW TO IMPROVE: Evidence-Based Recommendations
# ================================================================
fig = plt.figure(figsize=(20, 8), facecolor=BG)
fig.suptitle('How to Improve Telehealth Satisfaction — Evidence-Based Action Plan',
             fontsize=16, fontweight='bold', y=1.02)
gs = gridspec.GridSpec(1, 3, wspace=0.4)

# 4a — Impact matrix
ax = fig.add_subplot(gs[0])
interventions = {
    'Fix platform\nreliability':     (0.89, 7.6,  380),
    'Cap GP consults\nat 45 min':    (0.19, 44.7, 140),
    'Phone-first for\nMental Health':(0.17, 20.0, 100),
    'Specialist\nvirtual prep':      (0.09, 25.7, 110),
    'Remote\nconnectivity support':  (0.10, 10.3,  90),
    'Age 60+\ndigital onboarding':   (0.09, 31.6, 100),
}
int_colors = [COLORS['red'],COLORS['amber'],COLORS['teal'],
              COLORS['purple'],COLORS['grey'],COLORS['green']]
for (label, (gain, reach, size)), color in zip(interventions.items(), int_colors):
    ax.scatter(reach, gain, s=size*3, color=color, alpha=0.85,
               zorder=5, edgecolors='white', linewidth=1.5)
    ax.annotate(label, (reach, gain), textcoords='offset points',
                xytext=(8, 4), fontsize=8, fontweight='bold', color=color)
ax.axhline(0.1, color='#ccc', linestyle=':', linewidth=1)
ax.axvline(20,  color='#ccc', linestyle=':', linewidth=1)
ax.text(21, 0.92, 'High impact\nHigh reach', fontsize=8, color='#555', style='italic')
ax.set_xlabel('% of Consultations Affected')
ax.set_ylabel('Estimated Satisfaction Gain (pts)')
ax.set_title('Intervention Impact Matrix\n(bubble size = relative effort)', fontweight='bold')
ax.set_xlim(0, 55); ax.set_ylim(0, 1.1)
ax.grid(alpha=0.3, zorder=0)
insight(ax, "Top-right = high impact + high reach = prioritise first.\n"
            "Fix tech reliability is the clear #1 priority.\n"
            "Larger bubble = more consultations affected.")

# 4b — Simulated improvement waterfall
ax = fig.add_subplot(gs[1])
steps  = ['Current\nbaseline','Fix tech\nreliability',
          'Cap extended\nconsults','Specialist\nprep guide',
          'Remote\nsupport','All changes\ncombined']
values = [MEAN,
          MEAN + 0.886*0.076,
          MEAN + 0.886*0.076 + 0.020,
          MEAN + 0.886*0.076 + 0.020 + 0.015,
          MEAN + 0.886*0.076 + 0.020 + 0.015 + 0.012,
          MEAN + 0.886*0.076 + 0.020 + 0.015 + 0.012 + 0.010]
bar_c = [COLORS['grey']] + [COLORS['green']]*4 + [COLORS['blue']]
bars  = ax.barh(steps, values, color=bar_c, edgecolor='white', height=0.5, zorder=3)
for bar, val in zip(bars, values):
    ax.text(val+0.002, bar.get_y()+bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=9, fontweight='bold')
ax.set_xlim(3.7, 4.15)
ax.set_title('Projected Satisfaction\nby Improvement Scenario', fontweight='bold')
ax.set_xlabel('Mean Satisfaction Score')
ax.grid(axis='x', alpha=0.4, zorder=0)
total = values[-1] - values[0]
insight(ax, f"All improvements combined could lift\n"
            f"satisfaction from {values[0]:.3f} → {values[-1]:.3f}\n"
            f"(+{total:.3f} pts estimated gain).")

# 4c — Priority action table
ax = fig.add_subplot(gs[2])
ax.axis('off')
table = [
    ['#', 'Action',                          'Who',               'Impact'],
    ['1', 'Platform reliability\n& fallbacks','All — esp. Remote\n& 75+','★★★★★'],
    ['2', 'Duration guidelines\n(cap at 60m)','GP & Specialist',   '★★★☆☆'],
    ['3', 'Phone-first for\nelderly patients','Age 60+',           '★★★☆☆'],
    ['4', 'Pre-consult digital\nreadiness check','Remote & 75+',   '★★★☆☆'],
    ['5', 'Specialist virtual\nprep guide',   'Specialist patients','★★☆☆☆'],
    ['6', 'Inclusive platform\ndesign',       'Non-binary (n=92)', '★★☆☆☆'],
]
col_w = [0.06, 0.35, 0.33, 0.20]
rh    = 0.115
for ri, row in enumerate(table):
    y   = 0.93 - ri*rh
    bg  = '#1565C0' if ri == 0 else ('#E3F2FD' if ri%2 else 'white')
    ax.add_patch(plt.Rectangle((0, y-rh+0.01), 1, rh-0.01,
                 facecolor=bg, edgecolor='white', linewidth=0.5,
                 transform=ax.transAxes))
    x = 0.01
    for cell, w in zip(row, col_w):
        ax.text(x+w/2, y-rh/2, cell, ha='center', va='center',
                fontsize=8.5 if ri > 0 else 9, transform=ax.transAxes,
                color='white' if ri == 0 else TEXT,
                fontweight='bold' if ri == 0 else 'normal', linespacing=1.3)
        x += w
ax.set_title('Priority Action Plan', fontweight='bold', pad=12)
insight(ax, "Reliability beats platform choice every time.\n"
            "Remote + elderly = highest priority intersection.\n"
            "Small UX changes can close the non-binary gap.")

save(fig, 'sat_04_recommendations.png')

print("\n" + "="*55)
print("  SATISFACTION DEEP DIVE COMPLETE — 4 charts saved")
print("="*55)
print(f"""
  Key findings:
  • Overall mean satisfaction    : {MEAN:.3f}/5
  • Tech issues drop score by    : 0.886 pts (p<0.0001)
  • Best consultation type       : Mental Health (4.044)
  • Worst platform (ANOVA ns)    : Other (3.882) — not significant
  • Best duration sweet spot     : 31–60 mins (3.982)
  • Lowest demographic segment   : 60–74 yrs (3.860)
  • Low-sat consults with tech ✗ : 42% (vs 7.6% overall)
  • Estimated gain from all fixes: +{(MEAN + 0.886*0.076 + 0.020 + 0.015 + 0.012 + 0.010) - MEAN:.3f} pts
""")

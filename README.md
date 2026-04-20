# Australian Telehealth Adoption Analysis
An end-to-end data science project covering synthetic data generation, cleaning, exploratory analysis, statistical testing, and Tableau storytelling — built to demonstrate real-world analytics capability across the full project lifecycle.

## Problem Statement
## Understanding Telehealth Adoption Patterns in Australia: Who is using Virtual Care,How Often and what drives engagement?
Since covid 19 pandemic accelerated telehealth uptake, virtual health consultations have become a permanenet ficture in Australia's healthcare landscape. However adoption remains uneven across different age groups,geographies and clinical specialities.
Health insurers and providers need to understand who is using telehealth,how frequently what barriers exist,and whether virtual care is delivering comparable outcomes to in person visits.
This project aims to analyse telehealth adoption and usage patterns using a sysntehtic dataset,uncover key drivers of engagement,identify underdeserved segments and communicate findings through mu;ltiple analytics platforms.

## Core question answered:
Does patient satisfaction vary by platform, consultation type, duration, and demographics — and how can it be improved?

## Synthetic Data Set Creation
A realistic dataset of 5,020 rows × 20 columns was generated using Python with:

Population-weighted sampling — state and remoteness distributions mirror real Australian ABS demographics (NSW 32%, VIC 26%, QLD 20%)
Causally linked variables — technical issues increase with age (75+ = +10%) and remoteness (Remote = +15%); satisfaction decreases when tech issues occur; follow-up probability increases for specialists and older patients
Realistic imperfections — 3–5% missing values per column, 20 exact duplicate rows, and 10 outlier duration values (0, 500, 999 mins) deliberately seeded for the cleaning exercise
Fixed random seed (seed=42) for full reproducibility

## Data Cleaning & Feature Engineering

The dataset undergoes a full preprocessing pipeline including:

- Handling missing values:
  - Median imputation for age
  - Mode imputation for categorical variables
  - Group-based imputation for duration and satisfaction
- Data type corrections (boolean, datetime)
- Duplicate removal
- Outlier detection using IQR method
- Feature engineering:
  - Age bands
  - Satisfaction labels
  - Duration categories
  - Cost flags
  - Time-based features (year, month, quarter)
 
  ## EDA & Satisfaction Deep Dive
  Key Findings
1. Technical issues are the #1 driver of dissatisfaction
Patients who experienced technical issues rated satisfaction 0.89 points lower on average (3.10 vs 3.99). This difference is statistically significant (t = −20.93, p < 0.0001). Technical issues account for 42% of all low-satisfaction consultations despite affecting only 7.6% of all consults.
2. Platform choice is statistically irrelevant
Mean satisfaction ranges from 3.88 to 3.94 across platforms — a difference of just 0.06 points. ANOVA confirms this is not statistically significant (F = 0.76, p = 0.52). Reliability of the platform matters far more than which platform is used.
3. Mental Health consultations score highest
Mental Health scores 4.04 — the highest of all consultation types. GP and Specialist consultations score below the overall mean (3.88). The delta between best and worst type is 0.17 points.
4. Duration sweet spot is 31–60 minutes
Pearson correlation between duration and satisfaction is r = 0.03 (near-zero). However, extended consultations (>60 mins) score worst at 3.79, while the 31–60 min range scores best at 3.98. Duration alone does not predict satisfaction once consultation type is controlled.
5. Equity gaps compound for vulnerable segments

Remote patients experience 3.2× more technical issues than Metro patients (20.0% vs 6.3%)
Uninsured patients pay 12× more than Public patients ($71 vs $6 average)
Patients aged 60–74 score lowest (3.860) and face higher technical barriers
Non-binary patients score 3.837 — below average, though small sample (n=92)

## Suggested Improvement
Fix platform reliability  +0.067 pts
Cap extended consults at 60 min  +0.020 pts
Specialist virtual prep guide   +0.015 pts
Remote connectivity support  +0.012 pts
All combined           +0.124 pts


## Key Takeaways

Fix reliability, not the platform — investing in a new video platform will not improve satisfaction; ensuring the existing platform works reliably will
Remote + elderly = highest risk intersection — these patients face both the most technical barriers and the lowest satisfaction scores
Uninsured patients face a 12× cost gap — telehealth has not achieved cost equity for those without insurance
Mental Health telehealth works — patients strongly prefer virtual delivery for mental health; this is the consultation type where telehealth performs best
43% usage decline is not failure — it reflects post-COVID normalisation, not disengagement; GP and Mental Health demand remains resilient

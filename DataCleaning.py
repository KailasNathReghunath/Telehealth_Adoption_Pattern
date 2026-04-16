import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("C:/Users/kaila/PycharmProjects/TeleHealth_Adoption_Pattern.csv")
df.info()
# Handling Naan with Uninsured

n_unisured = df['insurance_type'].isna().sum()
df['insurance_type'] = df['insurance_type'].fillna('Uninsured')

# Removing duplicate rows
n_before = len(df)
df = df.drop_duplicates(keep='first').reset_index(drop=True)
n_dupes = n_before-len(df)

# Converting consultation_date str to datetime
df['consultation_date'] = pd.to_datetime(df['consultation_date'],errors='coerce')
n_nat = df['consultation_date'].isna().sum()

# Extracting year,month ets for analysis
df['consult_year'] = df['consultation_date'].dt.year
df['consult_month'] = df['consultation_date'].dt.month
df['consult_quarter'] = df['consultation_date'].dt.quarter
df['consult_month_year'] = df['consultation_date'].dt.to_period('M').astype(str)

# Handling Boolean
bool_cols = ['repeat_patient','technical_issues','follow_up_required','claimed_medicare']
for col in bool_cols:
    n_missing = df[col].isna().sum()
    df[col] = df[col].astype('boolean')

# Handling missing value
# Age using median
n_age = df['age'].isna().sum()
age_median = df['age'].median()
df['age_imputed'] = df['age'].isna()
df['age'] = df['age'].fillna(age_median)
df['age'] = df['age'].round(0).astype(int)

# Gender using Unknown
n_gender = df['gender'].isna().sum()
df['gender'] = df['gender'].fillna('Unknown')

# Platform using mode
n_platform = df['platform'].isna().sum()
platform_mode = df['platform'].mode()[0]
df['platform'] = df['platform'].fillna(platform_mode)

# Duration mins groupwise median
n_dur = df['duration_mins'].isna().sum()
df['duration_imputed'] = df['duration_mins'].isna()
df['duration_mins'] = df.groupby('consultation_type')['duration_mins'].transform(lambda x: x.fillna(x.median()))

# Repeat patient  technical issue follow up req and claimed medicare
for col in bool_cols:
    n_null = df[col].isna().sum()
    if n_null > 0:
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)

# Satisfaction score median per consulation
n_sat = df['satisfaction_score'].isna().sum()
df['satisfaction_score'] = df.groupby('consultation_type')['satisfaction_score'].transform(lambda x: x.fillna(x.median()))
df['satisfaction_score'] = df['satisfaction_score'].round(0).astype(int)

# Cost to patient
n_cost = df['cost_to_patient'].isna().sum()
df['cost_to_patient'] = df.groupby('insurance_type')['cost_to_patient'].transform(lambda x: x.fillna(x.median()))
df['cost_to_patient'] = df['cost_to_patient'].round(2)

# Diagnosis category clinically imp so no guessing unknow
n_diag = df['diagnosis_category'].isna().sum()
df['diagnosis_category'] = df['diagnosis_category'].fillna('Unknown')

# Handling outliers IQR

Q1 = df['duration_mins'].quantile(0.25)
Q3 = df['duration_mins'].quantile(0.75)
IQR = Q3 - Q1
lower_fence = max(0,Q1-1.5*IQR)
upper_fence = Q3+1.5*IQR

n_low = (df['duration_mins']< lower_fence).sum()
n_high = (df['duration_mins']>upper_fence).sum()
df['duration_outlier'] = ((df['duration_mins']<lower_fence )|(df['duration_mins']>upper_fence))

df['duration_mins'] = df['duration_mins'].clip(lower=lower_fence,upper = upper_fence)
df['duration_mins'] = df['duration_mins'].round(0).astype(int)

# Checking for outlier check cost_to_patient
df.info(f"Min: ${df['cost_to_patient'].min():.2f}")
df.info(f"Max: ${df['cost_to_patient'].max():.2f}")
df.info(f"Negative values: ${(df['cost_to_patient']<0).sum()}")

# Adding feature col
# Age band
bins = [0,17,29,44,59,74,120]
labels = ['Under 18','18-29','30-44','45-59','60-74','75+']
df['age_band']=pd.cut(df['age'],bins=bins,labels=labels, right = True)

# Satisfaction label
sat_map = {1:'Very Poor',2:'Poor',3:'Neutral',4:'Good',5:'Excellent'}
df['satisfaction_label'] = df['satisfaction_score'].map(sat_map)

# Consult duration category
def dur_cat(d):
    if d <= 15:
        return 'Short (<=15 min)'
    elif d <= 30:
        return 'Standard(16-30 min)'
    elif d <= 60:
        return 'Long (31-60 min)'
    else:
        return 'Extended (>60 min)'

df['duration_category'] = df['duration_mins'].apply(dur_cat)

# Finance flag
df['high_cost_flag'] = ((df['insurance_type']=='Uninsured') & (df['cost_to_patient']> 50))

# Final data types and col order
cat_cols = ['gender','state','remoteness','insurance_type','consultation_type','platform','diagnosis_category','age_band',
            'satisfaction_label','duration_category','provider_speciality']
for col in cat_cols:
    df[col] = df[col].astype('category')

# Reorder columns
col_order = [
    # Identifiers
    'consultation_id','patient_id',
    # Patient demographics
    'age','age_band','age_imputed','gender',
    # Geography
    'state', 'remoteness',
    # Insurance and finance
    'insurance_type','cost_to_patient','claimed_medicare','high_cost_flag',
    # Consultation
    'consultation_date','consult_year','consult_month','consult_quarter','consult_month_year',
    'consultation_type','platform','diagnosis_category',
    # Duration
    'duration_mins','duration_category','duration_imputed','duration_outlier',
    # Provider
    'provider_id','provider_speciality',
    # Outcomes
    'repeat_patient', 'technical_issues','follow_up_required', 'satisfaction_score','satisfaction_label'
]
df = df[col_order]

# Final Validation Report
nulls_after = df.isnull().sum()
nulls_after = nulls_after[nulls_after>0]

if len(nulls_after)>0:
    print("Zero missing values in all cols")
else:
    print(nulls_after)

# Exporting clean data set
output_path = "C:/Users/kaila/PycharmProjects/TeleHealth_Cleaned.csv"
df.to_csv(output_path, index=False)
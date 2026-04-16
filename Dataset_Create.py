# Design
# Older and remote patients have higher technical issues rate
# Satisfaction drop when tech issues occur
# Cost vary realistically by insurance type
# Followup prob increases for Specialist and older patients


# Importing packages

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('en_AU')
np.random.seed(42)
random.seed(42)

N = 5000

# Reference Data
states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']

# Weights given based on population dist
state_weights = [0.32, 0.26, 0.20, 0.10, 0.07, 0.02, 0.02, 0.02]

#Mapping remoteness based on Australian Geographic Reality
remoteness_by_state = {
    'NSW' :['Metro','Regional','Remote'],
    'VIC' :['Metro','Regional','Remote'],
    'QLD' :['Metro','Regional','Remote'],
    'WA' :['Metro','Regional','Remote'],
    'SA' :['Metro','Regional','Remote'],
    'TAS' :['Regional','Remote'],
    'ACT' :['Metro'],
    'NT' :['Regional','Remote']
}

# Remoteness weight given based on data from ABS - 60/30/10 split
remoteness_weights = {'Metro':0.60, 'Regional':0.30, 'Remote': 0.10}

#Consultation types
consultation_types = ['GP', 'Specialist', 'Mental Health', 'Allied Health']
# Based on assumption
consult_weights = [0.45,0.30,0.20,0.10]

# Platforms types and weight based on assumption
platforms = ["Phone", 'Zoom', 'Proprietary App', 'Other']
platform_weights = [0.40, 0.30, 0.20, 0.10]

# Insurance types and based on assumption
insurance_types = ['Public', 'Private', 'None']
insurance_weights = [0.45, 0.40, 0.15]

# Diagnosis Categories and Weight
diagnosis_categories = ['Mental Health', 'Musculoskeletal', 'Respiratory',
                        'Cradiovascular', 'Diabetes', 'Dermatology', 'General']
diagnosis_weights = [0.25, 0.15, 0.15, 0.10, 0.10, 0.10, 0.15]

provider_specialities = ['GP', 'Psychiatrist', 'Psychologist',
                         'Physiotherapist', 'Cardiologist', 'Dermatologits', 'Endocrinologist']

# Generate provider pool
num_providers = 200
# PRV0001,PRV0070
provider_ids = [f"PRV{str(i).zfill(4)}" for i in range(1, num_providers+1)]
# Dictionary assigning provider as key to provider_specialities
provider_speciality_map = {pid: random.choice(provider_specialities) for pid in provider_ids}

# Date range Jan 2022 - Dec 2024 considering covid time
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date-start_date).days+1

# Date generation with a skew showing reduction from covid time
def random_date():
    # More during covid time
    year = np.random.choice([2022,2023,2024], p=[0.42, 0.33, 0.25])
    month = np.random.randint(1,13)
    # To remove invalid dates Feb 30 and 31's
    day = np.random.randint(1,29)
    try:
        return datetime(year,month,day)
    except ValueError:
        return datetime(year,month,29)

# Build records
records = []
patient_ids = [f"PAT{str(i).zfill(5)}" for i in range(1,3001)] # 3000 unique patients

for i in range(N):
    consultation_id = f"CONS{str(i+1).zfill(5)}"
    patient_id = random.choice(patient_ids)
    age = int(np.random.choice(range(5,90),
                               p = np.array([
                                   *[0.5]*15,   # 5-19
                                   *[1.5]*20,   # 20-39
                                   *[2.0]*20,   # 40-59
                                   *[1.8]*15,   # 60-74
                                   *[0.8]*15,   # 75-89

                               ]) /sum( [*[0.5]*15, *[1.5]*20, *[2.0]*20, *[1.8]*15, *[0.8]*15]))
                               )

    gender = random.choices(['Male','Female','Non-binary'], weights = [0.48,0.50,0.02])[0]
    state = random.choices(states,weights = state_weights)[0]
    remoteness_opts = remoteness_by_state[state]
    remoteness = random.choices(remoteness_opts,weights = [remoteness_weights[r] for r in remoteness_opts])[0]
    insurance_type = random.choices(insurance_types,weights=insurance_weights)[0]
    consultation_date = random_date().strftime("%Y-%m-%d")
    consultation_type = random.choices(consultation_types,weights=consult_weights)[0]
    platform = random.choices(platforms,weights=platform_weights)[0]

    # Durations
    duration_base = {'GP': 15,'Specialist': 30, 'Mental Health': 50, 'Allied Health': 40}
    duration_mins = max(5,int(np.random.normal(duration_base[consultation_type],10)))

    #Repeat patient : especially older patients and chronic
    repeat_prob = 0.55 if age > 50 else 0.35
    repeat_patient = random.random() < repeat_prob

    # Technical Issue
    tech_issue_prob = 0.05
    if remoteness == 'Remote': tech_issue_prob += 0.15
    if age > 65: tech_issue_prob += 0.10
    if platform == 'Phone': tech_issue_prob -= 0.03
    technical_issues = random.random()<max(0,tech_issue_prob)

    # Satisfaction
    base_satisfaction = 4.0
    if technical_issues: base_satisfaction -= 1.0
    if duration_mins > 60: base_satisfaction -= 0.3
    if consultation_type == 'Mental Health': base_satisfaction += 0.2
    satisfaction_score = int(np.clip(round(np.random.normal(base_satisfaction,0.8)),1,5))

    # Follow up - specialist and older patients
    followup_prob = 0.20
    if consultation_type == 'Specialist' : followup_prob += 0.20
    if age > 60: followup_prob += 0.10
    if technical_issues : followup_prob += 0.10
    follow_up_required = random.random() < followup_prob

    #Cost - based on insurance
    cost_base = {'Public':0, 'Private': 25, 'None':80}
    cost_to_patient = round(max(0, np.random.normal(cost_base[insurance_type],15)),2)
    provider_id = random.choice(provider_ids)
    provider_speciality = provider_speciality_map[provider_id]
    claimed_medicare = random.choices([True,False],weights = [0.7,0.3])[0]
    diagnosis_category = random.choices(diagnosis_categories, weights = diagnosis_weights)[0]

    # Introducing realistic missing val
    def maybe_null(val,prob=0.03):
        return None if random.random()<prob else val

    records.append({
        'consultation_id':consultation_id,
        'patient_id':patient_id,
        'age':maybe_null(age,0.02),
        'gender':maybe_null(gender,0.02),
        'state':state,
        'remoteness_opts':remoteness,
        'insurance_type':maybe_null(insurance_type,0.03),
        'consultation_date':consultation_date,
        'platform':maybe_null(platform,0.03),
        'duration_mins':maybe_null(duration_mins,0.02),
        'repeat_patient':maybe_null(repeat_patient,0.03),
        'technical_issues':maybe_null(technical_issues,0.02),
        'satisfaction_score':maybe_null(satisfaction_score,0.04),
        'follow_up_required':maybe_null(follow_up_required,0.03),
        'cost_to_patient':maybe_null(cost_to_patient,0.03),
        'provider_id':provider_id,
        'provider_speciality':provider_speciality,
        'claimed_medicare':maybe_null(claimed_medicare,0.02),
        'diagnosis_category':maybe_null(diagnosis_category,0.03)

    })

# Introducing duplicate values
duplicates =random.sample(records,20)
records.extend(duplicates)

# Introduce 10 rows with outlier data
for _ in range(10):
    idx = random.randint(0,len(records)-1)
    records[idx]['duration_mins'] = random.choice([0,500,999])

df = pd.DataFrame(records)
df = df.sample(frac=1,random_state=42).reset_index(drop=True)

output_path = "C:/Users/kaila/PycharmProjects/TeleHealth_Adoption_Pattern.csv"
df.to_csv(output_path, index=False)

print(f"Dataset generated : {len(df)} rows x {len(df.columns)} columns")
print(f"\n Shape: {df.shape}")
print(f"\n Missing values per column:")
print(df.isnull().sum())
print(f"\n Sample records:")
print(df.head())
df = pd.read_csv("C:/Users/kaila/PycharmProjects/TeleHealth_Adoption_Pattern.csv")


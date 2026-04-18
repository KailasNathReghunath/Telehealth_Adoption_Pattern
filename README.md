# Problem Statement
## Understanding Telehealth Adoption Patterns in Australia: Who is using Virtual Care,How Often and what drives engagement?
Since covid 19 pandemic accelerated telehealth uptake, virtual health consultations have become a permanenet ficture in Australia's healthcare landscape. However adoption remains uneven across different age groups,geographies and clinical specialities.
Health insurers and providers need to understand who is using telehealth,how frequently what barriers exist,and whether virtual care is delivering comparable outcomes to in person visits.
This project aims to analyse telehealth adoption and usage patterns using a sysntehtic dataset,uncover key drivers of engagement,identify underdeserved segments and communicate findings through mu;ltiple analytics platforms.
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

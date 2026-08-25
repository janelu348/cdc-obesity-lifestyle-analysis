# Adult Obesity and Lifestyle Factors in the United States

## Project Overview

This project studies the relationship between adult obesity, physical inactivity, and low fruit consumption across U.S. states and demographic groups.

The analysis uses aggregated estimates from the CDC Behavioral Risk Factor Surveillance System for 2017, 2019, and 2021.

## Research Question

How are physical inactivity and low fruit consumption associated with adult obesity prevalence across U.S. states and demographic groups?

## Variables

**Target variable**

- `obesity_pct`: Adult obesity prevalence.

**Predictors**

- `no_leisure_activity_pct`: Adults who reported no leisure-time physical activity.
- `low_fruit_consumption_pct`: Adults who consumed fruit less than once daily.

All variables are percentages.

## Data Source

The data comes from the CDC Nutrition, Physical Activity, and Obesity dataset:

[CDC Open Data Page](https://data.cdc.gov/Nutrition-Physical-Activity-and-Obesity/Nutrition-Physical-Activity-and-Obesity-Behavioral/hn4x-zwk7)

The original CSV contains 110,880 rows. It remains unchanged.

The preparation process created:

- 151 state-year rows for modeling.
- 3,834 state-year-demographic rows for subgroup exploration.
- Data from 50 states and Washington, D.C.
- Estimates from 2017, 2019, and 2021.

## Project Steps

1. Loaded and reviewed the original CDC data.
2. Selected the three main health questions.
3. Reshaped the questions into separate columns.
4. Created state-level and demographic datasets.
5. Explored trends, correlations, and demographic differences.
6. Compared regression models using grouped cross-validation.
7. Interpreted the best model and its coefficients.
8. Created an interactive dashboard.

## Exploratory Findings

- The average state obesity rate increased from 30.6% in 2017 to 33.5% in 2021.
- Physical inactivity had a positive correlation of 0.59 with obesity.
- Low fruit consumption had a positive correlation of 0.77 with obesity.
- West Virginia had the highest state obesity rate in 2021 at 40.6%.
- Obesity estimates varied across demographic categories.

## Model Comparison

The following models were compared:

- Linear Regression
- Gradient Boosting
- Random Forest
- Mean Baseline

Grouped cross-validation was used to keep observations from the same state together.

| Model | MAE | R² |
|---|---:|---:|
| Linear Regression | 1.997 | 0.619 |
| Gradient Boosting | 2.149 | 0.571 |
| Random Forest | 2.147 | 0.554 |
| Mean Baseline | 3.453 | -0.052 |

Linear Regression had the lowest MAE and the highest R² score. Therefore, it was selected as the final model.

## Linear Regression Results

The coefficient for physical inactivity was **0.246**.

A one-percentage-point increase in physical inactivity was associated with a 0.246-percentage-point increase in predicted obesity, while low fruit consumption remained the same.

The coefficient for low fruit consumption was **0.586**.

A one-percentage-point increase in low fruit consumption was associated with a 0.586-percentage-point increase in predicted obesity, while physical inactivity remained the same.

Low fruit consumption had the larger coefficient in this model.

## Important Limitation

This project uses aggregated survey estimates. The results show associations between variables, but they do not prove causation.

The analysis does not show that physical inactivity or low fruit consumption directly causes obesity.

## Project Structure

```text
cdc_obesity_portfolio/
├── README.md
├── obesity_lifestyle_analysis.ipynb
├── prepare_data.py
├── requirements.txt
├── data/
│   ├── obesity_lifestyle_model_data.csv
│   └── obesity_lifestyle_demographic_data.csv
└── app.py
```

## Tools Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Plotly
- Streamlit
- Google Colab

## Run the Dashboard

From the project folder, install the required libraries:

`pip install -r requirements.txt`

Then start the Streamlit dashboard:

`streamlit run app.py`

## Author

Janeth Garcia Rodriguez

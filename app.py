from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# Page settings
st.set_page_config(
    page_title="U.S. Adult Obesity Dashboard",
    page_icon="📊",
    layout="wide"
)


# Soft pink colors
SOFT_PINK = "#D8A7B1"
MEDIUM_PINK = "#C98FA1"
DARK_PINK = "#9D5C73"
BACKGROUND = "#FFF8FA"
GRID_COLOR = "#F1DDE2"
TEXT_COLOR = "#5F4B52"

PINK_SCALE = [
    "#FFF8FA",
    "#F3DCE2",
    "#D8A7B1",
    "#C47F95",
    "#9D5C73"
]


# Custom page style
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF8FA;
    }

    h1, h2, h3 {
        color: #5F4B52;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #F1DDE2;
        border-radius: 12px;
        padding: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# File paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MODEL_FILE = (
    DATA_DIR
    / "obesity_lifestyle_model_data.csv"
)

DEMOGRAPHIC_FILE = (
    DATA_DIR
    / "obesity_lifestyle_demographic_data.csv"
)


@st.cache_data
def load_data():
    model = pd.read_csv(MODEL_FILE)
    demographic = pd.read_csv(DEMOGRAPHIC_FILE)

    model["year"] = model["year"].astype(int)
    demographic["year"] = demographic["year"].astype(int)

    return model, demographic


try:
    model_data, demographic_data = load_data()

except FileNotFoundError:
    st.error(
        "The prepared data files were not found. "
        "Make sure the two CSV files are inside the data folder."
    )
    st.stop()


# Title and description
st.title("U.S. Adult Obesity and Lifestyle Dashboard")

st.write(
    "Explore adult obesity, physical inactivity, and low fruit "
    "consumption across U.S. states. The data comes from CDC "
    "BRFSS estimates for 2017, 2019, and 2021."
)


# Sidebar filters
st.sidebar.header("Filters")

available_years = sorted(
    model_data["year"].unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Year",
    available_years,
    index=len(available_years) - 1
)

available_states = sorted(
    model_data["state"].unique().tolist()
)

selected_states = st.sidebar.multiselect(
    "States",
    available_states,
    placeholder="Leave empty to show all states"
)


# Apply filters
filtered_model = model_data[
    model_data["year"] == selected_year
].copy()

filtered_demographic = demographic_data[
    demographic_data["year"] == selected_year
].copy()

if selected_states:
    filtered_model = filtered_model[
        filtered_model["state"].isin(selected_states)
    ]

    filtered_demographic = filtered_demographic[
        filtered_demographic["state"].isin(selected_states)
    ]


if filtered_model.empty:
    st.warning("No data is available for these filters.")
    st.stop()


# Summary metrics
metric_1, metric_2, metric_3 = st.columns(3)

metric_1.metric(
    "Average obesity rate",
    f"{filtered_model['obesity_pct'].mean():.1f}%"
)

metric_2.metric(
    "Average physical inactivity",
    f"{filtered_model['no_leisure_activity_pct'].mean():.1f}%"
)

metric_3.metric(
    "Average low fruit consumption",
    f"{filtered_model['low_fruit_consumption_pct'].mean():.1f}%"
)


# Map
st.subheader(f"Adult Obesity Rates in {selected_year}")

map_figure = px.choropleth(
    filtered_model,
    locations="state_abbr",
    locationmode="USA-states",
    scope="usa",
    color="obesity_pct",
    hover_name="state",
    hover_data={
        "state_abbr": False,
        "obesity_pct": ":.1f",
        "no_leisure_activity_pct": ":.1f",
        "low_fruit_consumption_pct": ":.1f"
    },
    color_continuous_scale=PINK_SCALE,
    labels={
        "obesity_pct": "Obesity (%)",
        "no_leisure_activity_pct": "Physical inactivity (%)",
        "low_fruit_consumption_pct": "Low fruit consumption (%)"
    }
)

map_figure.update_layout(
    paper_bgcolor=BACKGROUND,
    plot_bgcolor=BACKGROUND,
    font_color=TEXT_COLOR,
    margin=dict(l=0, r=0, t=10, b=0)
)

st.plotly_chart(
    map_figure,
    use_container_width=True
)


# Function for scatterplots
def create_scatterplot(data, predictor, x_label, title):
    figure = px.scatter(
        data,
        x=predictor,
        y="obesity_pct",
        hover_name="state",
        labels={
            predictor: x_label,
            "obesity_pct": "Adult obesity rate (%)"
        },
        title=title
    )

    figure.update_traces(
        marker={
            "color": MEDIUM_PINK,
            "size": 10,
            "opacity": 0.85,
            "line": {
                "color": "white",
                "width": 1
            }
        }
    )

    clean_data = data[
        [predictor, "obesity_pct"]
    ].dropna()

    if (
        len(clean_data) >= 2
        and clean_data[predictor].nunique() > 1
    ):
        slope, intercept = np.polyfit(
            clean_data[predictor],
            clean_data["obesity_pct"],
            1
        )

        line_x = np.linspace(
            clean_data[predictor].min(),
            clean_data[predictor].max(),
            100
        )

        line_y = slope * line_x + intercept

        figure.add_trace(
            go.Scatter(
                x=line_x,
                y=line_y,
                mode="lines",
                name="Trend line",
                line={
                    "color": DARK_PINK,
                    "width": 2
                }
            )
        )

    figure.update_layout(
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font_color=TEXT_COLOR,
        legend_title_text="",
        xaxis_gridcolor=GRID_COLOR,
        yaxis_gridcolor=GRID_COLOR
    )

    return figure


# Scatterplots
st.subheader("Lifestyle Factors and Obesity")

chart_1, chart_2 = st.columns(2)

physical_activity_chart = create_scatterplot(
    filtered_model,
    "no_leisure_activity_pct",
    "No leisure-time physical activity (%)",
    "Obesity and Physical Inactivity"
)

fruit_chart = create_scatterplot(
    filtered_model,
    "low_fruit_consumption_pct",
    "Fruit consumption less than once daily (%)",
    "Obesity and Low Fruit Consumption"
)

chart_1.plotly_chart(
    physical_activity_chart,
    use_container_width=True
)

chart_2.plotly_chart(
    fruit_chart,
    use_container_width=True
)


# Demographic exploration
st.subheader("Demographic Exploration")

demographic_categories = sorted(
    filtered_demographic[
        "stratification_category"
    ].dropna().unique().tolist()
)

selected_category = st.selectbox(
    "Demographic category",
    demographic_categories
)

category_data = filtered_demographic[
    filtered_demographic[
        "stratification_category"
    ] == selected_category
].copy()

box_figure = px.box(
    category_data,
    x="obesity_pct",
    y="stratification",
    points="outliers",
    labels={
        "obesity_pct": "Adult obesity rate (%)",
        "stratification": selected_category
    },
    title=f"Obesity Rates by {selected_category}"
)

box_figure.update_traces(
    fillcolor=SOFT_PINK,
    line_color=DARK_PINK,
    marker_color=MEDIUM_PINK
)

box_figure.update_layout(
    paper_bgcolor=BACKGROUND,
    plot_bgcolor=BACKGROUND,
    font_color=TEXT_COLOR,
    xaxis_gridcolor=GRID_COLOR,
    yaxis_gridcolor=GRID_COLOR,
    showlegend=False
)

st.plotly_chart(
    box_figure,
    use_container_width=True
)


# Data table
st.subheader("Filtered State Data")

display_data = filtered_model[
    [
        "state",
        "year",
        "obesity_pct",
        "no_leisure_activity_pct",
        "low_fruit_consumption_pct"
    ]
].sort_values(
    "obesity_pct",
    ascending=False
).round(1)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)


# Limitation
st.info(
    "These results show associations between aggregated "
    "state-level estimates. They do not prove causation."
)

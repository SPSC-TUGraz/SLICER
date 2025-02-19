import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

age_data = {
    "Age Group": ["20 or younger", "21-30", "31-40", "41-50", "51-60", "70+"],
    "Participants": [4, 40, 3, 3, 2, 1],
}

region_data = {
    "Region": [
        "Styria", "Upper Austria", "Lower Austria", "Tyrol",
        "Bavaria", "South Tyrol", "Carinthia", "Vorarlberg"
    ],
    "Primary school": [28, 8, 5, 3, 1, 1, 1, 0],
    "Current residence": [51, 0, 0, 0, 0, 0, 0, 0],
    "Longest residence": [32, 7, 5, 3, 1, 1, 1, 2],
}

age_df = pd.DataFrame(age_data)
region_df = pd.DataFrame(region_data)

num_colors = 3
colors = px.colors.n_colors('rgb(30, 60, 90)','rgb(85, 170, 255)',num_colors,colortype="rgb")

fig = make_subplots(
    rows=1, cols=2, 
    subplot_titles=["Age Distribution", "Region of Primary School"],
    specs=[[{"type": "bar"}, {"type": "bar"}]]
)

fig.add_trace(
    go.Bar(
        x=age_df["Age Group"],
        y=age_df["Participants"],
        text=age_df["Participants"],
        textposition="outside",
        marker=dict(color=colors[1]),
        showlegend=False
    ),
    row=1, col=1
)

fig.add_trace(
    go.Bar(
        x=region_df["Region"],
        y=region_df["Primary school"],
        name="Primary school",
        marker=dict(color=colors[0])
    ),
    row=1, col=2
)

fig.add_trace(
    go.Bar(
        x=region_df["Region"],
        y=region_df["Current residence"],
        name="Current residence",
        marker=dict(color=colors[1])
    ),
    row=1, col=2
)

fig.add_trace(
    go.Bar(
        x=region_df["Region"],
        y=region_df["Longest residence"],
        name="Longest residence",
        marker=dict(color=colors[2])
    ),
    row=1, col=2
)

fig.update_layout(
    title_text="Participant Demographics",
    title_x=0.5,
    height=500,
    width=1000,
    font=dict(size=15)
)

# fig.update_layout(
#     legend=dict(
#         x=0.75,  # Position bei rechtem Subplot
#         y=-0.3,  # Unterhalb des Diagramms
#         xanchor="center",
#         orientation="h"  # Horizontale Ausrichtung
#     )
# )

fig.show()

import plotly.graph_objects as go
import plotly.express as px

labels = [
    "Other disfluency", "Other speaker audible", "Leading FP", 
    "Hard to understand", "Rare word", "Short FP", 
    "Coupled FP (und äh)", "Laughter", "Not enough words", 
    "Name", "Repetition", "Other"
]
values = [198, 74, 50, 49, 40, 39, 36, 30, 27, 25, 21]
other_value = 703 - sum(values)
values.append(other_value)

num_colors = len(values)
colors = px.colors.n_colors('rgb(30, 60, 90)','rgb(85, 170, 255)',num_colors,colortype="rgb")
# colors = px.colors.make_colorscale(colorlist)
# colors = px.colors.sequential.Blues

fig = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hoverinfo='label+percent',
    textinfo='label+percent',
    marker=dict(colors=colors),
    rotation=0,
    hole=0.3,
    showlegend=False,
    sort=False
)])

fig.update_layout(
    title='Reasons for exclusion from experiment',
    title_x=0.5,
    font=dict(size=15)
)

fig.show()

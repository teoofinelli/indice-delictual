import plotly.express as px

def plot_barrios(df):
    top_barrios = df["barrio"].value_counts().head(10)
    fig = px.bar(
        top_barrios,
        x=top_barrios.index,
        y=top_barrios.values,
        labels={"x": "Barrio", "y": "Cantidad"},
        title="Top 10 Barrios con más hechos"
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def plot_evolucion(df):
    evolucion = df.groupby(["año", "mes"]).size().reset_index(name="hechos")
    fig = px.line(
        evolucion,
        x="mes",
        y="hechos",
        color="año",
        markers=True,
        labels={"mes": "Mes", "hechos": "Cantidad"},
        title="Evolución temporal por mes"
    )
    return fig

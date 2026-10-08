"""Consistent Plotly theme for the GenAI Innovation Studio (light theme)."""

# Anchored to the light palette:
#   Primary:    #2563EB
#   Text:       #111827
#   Muted text: #6B7280
#   Grid:       #E5E7EB

THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#111827", family="Inter, sans-serif", size=12),
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
        linecolor="#D1D5DB",
        tickfont=dict(color="#4B5563"),
        title=dict(font=dict(color="#1F2937")),
    ),
    yaxis=dict(
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
        linecolor="#D1D5DB",
        tickfont=dict(color="#4B5563"),
        title=dict(font=dict(color="#1F2937")),
    ),
    colorway=["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"],
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#DBEAFE",
        borderwidth=1,
        font=dict(color="#1F2937"),
    ),
)


def apply(fig, height: int = 300):
    """Apply the light theme to a Plotly figure."""
    fig.update_layout(**THEME, height=height)
    return fig
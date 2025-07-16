import plotly.graph_objects as go
import pandas as pd

def create_time_series_chart(data):
    """
    Create a time series chart for confirmed cases and predictions.
    
    Args:
        data (pd.DataFrame): DataFrame with columns 'data', 'casos_confirmados', and optionally 'previsao'
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    # Add confirmed cases trace
    fig.add_trace(go.Scatter(
        x=data['data'],
        y=data['casos_confirmados'],
        mode='lines+markers',
        name='Casos Reais',
        line=dict(color='blue'),
        marker=dict(size=6)
    ))
    
    # Add predictions trace if available
    if 'previsao' in data.columns:
        fig.add_trace(go.Scatter(
            x=data['data'],
            y=data['previsao'],
            mode='lines+markers',
            name='Previsão',
            line=dict(color='red', dash='dash'),
            marker=dict(size=6)
        ))
    
    # Update layout
    fig.update_layout(
        title="Tendência de Casos de Dengue",
        xaxis_title="Data",
        yaxis_title="Número de Casos",
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )
    
    return fig
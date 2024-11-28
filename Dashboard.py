import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from data_pipeline import DataPipeline
from config import *

app = dash.Dash (__name__)
pipeline = DataPipeline ()

app.layout = html.Div ([
    html.H1 ('Stock Market Dashboard'),

    dcc.Interval (
        id='interval-component',
        interval=60 * 1000,  # updates every minute
        n_intervals=0
    ),

    html.Div ([
        html.Div ([
            dcc.Dropdown (
                id='stock-selector',
                options=[{'label': s, 'value': s} for s in STOCK_SYMBOLS],
                value=STOCK_SYMBOLS [0]
            ),
            dcc.Graph (id='stock-graph'),
        ], style={'width': '70%', 'display': 'inline-block'}),

        html.Div ([
            html.H3 ('Latest Market News'),
            html.Div (id='news-container', style={
                'height': '400px',
                'overflowY': 'scroll'
            })
        ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'})
    ])
])


@app.callback (
    [Output ('stock-graph', 'figure'),
     Output ('news-container', 'children')],
    [Input ('interval-component', 'n_intervals'),
     Input ('stock-selector', 'value')]
)
def update_dashboard(n, symbol):
    pipeline.update ()

    # Update stock graph
    stock_data = pipeline.get_stock_history (symbol)

    figure = {
        'data': [{
            'x': stock_data ['timestamp'],
            'y': stock_data ['price'],
            'type': 'line',
            'name': symbol
        }],
        'layout': {
            'title': f'{symbol} Stock Price',
            'yaxis': {'title': 'Price ($)'},
            'xaxis': {'title': 'Time'}
        }
    }

    # Update news feed
    news_data = pipeline.get_latest_news ()
    news_items = [
        html.Div ([
            html.H4 (row ['title']),
            html.P (row ['description']),
            html.A ('Read more', href=row ['url'], target='_blank'),
            html.Hr ()
        ]) for _, row in news_data.iterrows ()
    ]

    return figure, news_items


if __name__ == '__main__':
    app.run_server (debug=True)

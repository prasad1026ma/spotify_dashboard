import dash
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from Sankey import make_sankey, _code_mapping, stacking
from analysis_functions import (create_sankey, read_and_clean_csv, create_facet_plot,
                                create_facet_histogram_plot, create_mean_val, create_bar)

app = Dash(__name__, suppress_callback_exceptions=True)

# initializing color schema
colors = {
    'background': '#000000',
    'panel': '#7A7A7A',
    'text': '#ffffff',
    'blue': '#4a74f5',
    'purple': '#a55af4'
}

df_spotify = read_and_clean_csv('spotify-2023.csv', 'track_name', 'artist(s)_name', 'artist_count',
                                'released_year', 'released_month', 'in_spotify_playlists', 'in_spotify_charts',
                                'streams', 'bpm', 'key', 'mode', 'danceability_%', 'valence_%', 'energy_%',
                                'acousticness_%',
                                'instrumentalness_%', 'liveness_%', 'speechiness_%', encoding='ISO-8859-1')
# comparing bpm, mode, and key
facet_scatter = create_facet_plot(df_spotify, 'key', 'bpm', 'mode')

mean_streams = create_mean_val(df_spotify)
bar = create_bar(df_spotify)

def create_range_slider():
    """
    This function creates a range slider based on the dash component
    range slider

    to allow user to select only certain months to look at
    :return: a dash slider based on the months of the mean_streams
    """
    # Finds the minimum and maximum months based on the mean_streams series
    min_month = mean_streams.index.min()
    max_month = mean_streams.index.max()

    # Creates the slider based on the months in the series
    slider = dcc.RangeSlider(
        id='range-slider',
        min=min_month,
        max=max_month,
        step=1,
        value=[min_month, max_month],
        marks={str(i): str(i) for i in range(min_month, max_month + 1)}
    )
    return slider

@app.callback(
    Output('graph-streams-month', 'figure'),
    Input('range-slider', 'value')
)
def update_bar_graph(value):
    """
    This function is used to update the bar graph based on the values
    in the slider places by the user
    :param value: an integer showing the released month value from the slider
    :return: a bar graph based on the updated values in the slider
    """
    # Filters the data to only include the months that are on the slider
    filtered_data = df_spotify[(df_spotify['released_month'] >= value[0]) & (df_spotify['released_month'] <= value[1])]

    # Recreates the bar chart based on these values
    updated_bar = create_bar(filtered_data)

    return updated_bar

def default_tab_content():
    return html.Div([])

@app.callback(
Output('tab-content-div', 'children'),
    Input('tabs-vertical', 'value'),
)
def render_content(tab):
    """
    This function is used to create the content inside the dashboard based on various components
    :param tab: this string will give the current tab the dashboard is on
    :return:
    """
    sankey_content = None
    content = None
    if tab == 'tab-1':
        slider = create_range_slider()
        return html.Div([
            html.Div(
                dcc.Graph(
                    id='graph-streams-month',
                    figure=bar,
                    style={'margin-top': '0'}
                )
            ),
            html.Div([
                html.Label('Range Slider'),
                slider
            ])
        ])
    elif tab == 'tab-2':
        # Only include col1-dropdown and col2-dropdown when on "Sankey Generator" tab
        return html.Div([
        html.Div(children='''
                Choose two columns to create a Sankey diagram:
            ''', style={'color':'white','font-size': '20px'}),
        dcc.Dropdown(
            id='col1-dropdown',
            options=[{'label': col, 'value': col} for col in df_spotify.columns],
            value='released_year'
        ),
        dcc.Dropdown(
            id='col2-dropdown',
            options=[{'label': col, 'value': col} for col in df_spotify.columns],
            value='mode'
        ),
        html.Div(id='sankey-chart'),
        dcc.Graph(id='sankey-chart')
    ])
    elif tab == 'tab-3':
        return html.Div([
            dcc.Graph(
                id='BPM-Key-Mode',
                figure=facet_scatter,
                style={'margin-top': '0'}
            )
        ])

    return content

@app.callback(
    Output('sankey-chart', 'figure'),
    Input('col1-dropdown', 'value'),
    Input('col2-dropdown', 'value')
)
def update_sankey( col1, col2):
    sankey_fig = create_sankey(df_spotify, col1, col2)
    return sankey_fig


app.layout = html.Div(style={'background': '#1F1F1F', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'start'}, children=[
    html.H1(
        'Spotify Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'background': '#7A7A7A',
            'lineHeight': '100px',
            'height': '100px',
            'marginBottom': '0px',
            'padding': '10px 0',
            'fontSize': '24px',
            'font-family': 'Times New Roman'
        }
    ),
    # Create a wrapper Div
    html.Div(style={'display': 'flex', 'flexDirection': 'row'}, children=[
        # Left column for tabs
        html.Div(className='col-3', style={'flex': '0 0 20%', 'flexDirection': 'column', 'justifyContent': 'start'}, children=[
            dcc.Tabs(
                id='tabs-vertical',
                value='tab-1',
                children=[
                    dcc.Tab(label='Streaming Statistics', value='tab-1', className='tab-card',
                            style={'backgroundColor': '#7A7A7A', 'height': '200px'},
                            selected_style={'backgroundColor': '#B8B8B8', 'padding': '0'}),
                    dcc.Tab(label='Sankey Generator', value='tab-2', className='tab-card',
                            style={'backgroundColor': '#7A7A7A', 'height': '200px'},
                            selected_style={'backgroundColor': '#B8B8B8'}),
                    dcc.Tab(label='Musical  Statistics', value='tab-3', className='tab-card',
                            style={'backgroundColor': '#7A7A7A', 'height': '200px'},
                            selected_style={'backgroundColor': '#B8B8B8'}),
                ], vertical=True, className='vertical-tabs')
        ]),
        # Right column with tab content
        html.Div(id='tab-content-div', style={'flex': '1'}),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)
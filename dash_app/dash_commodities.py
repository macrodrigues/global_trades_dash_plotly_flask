"""Script to render the Dash application.

Takes into account the commodities.

"""

import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from .preprocessing import clean_df
from .components.table_categories import gen_table_categories, categories_dict

# DATAFRAME
df = clean_df(pd.read_csv('data/commodity_trade_statistics_data.csv'))

# INPUT VALUES
years = list(df.year.drop_duplicates())
years.sort()
flows = list(df['flow'].drop_duplicates())
flows.sort()

# CUSTOMIZATION
colors_traces = [
    '#004242',
    '#008080',
    '#3ab09e',
    '#44d7a8',
    '#48d1cc',
    '#7fffd4',
    '#aaf0d1']


def dash_app_commodities(flask_app, path):
    """Launch Dash app on Flask server.

    Route for commodities page. It displays two plots, a bar plot having the
    total trades by category along the years. And it also displays a line plot
    showing the Trades per year, and per category, by selecting the flow.

    """
    app = Dash(
        __name__,
        server=flask_app,  # rendered by the flask app
        url_base_pathname=path,  # the flask route for this page
        external_stylesheets=[dbc.themes.BOOTSTRAP]  # bootstrap components
    )

    app.layout = html.Div([
                    html.H1(
                        className='main-title',
                        children='Global trades by Commodities'
                    ),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="Total traded by category along the years"
                        ),
                        html.Div([
                            html.Div([  # contains the dropdown and it title
                                html.H4(
                                    children='Flow',
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align': 'center'}),
                                dcc.Dropdown(
                                    id='flow-picker-bar',
                                    options=flows,
                                    value=flows[0]),
                            ], style={
                                # z-index added, to be sure that the widget is
                                # above the graph
                                'width': '130px',
                                'display': 'inline-block',
                                'margin-top': "2%",
                                'z-index': '1'}),
                        ], className='dropdowns-container'),                        
                        html.Div([  # contains the bar plot and a table
                            dcc.Graph(id='graph-evolution-categories'),
                            dbc.Table(
                                # calls the bootstrap table
                                gen_table_categories(),
                                bordered=True,
                                hover=True,
                                responsive=True,
                                striped=False,
                                style={'font-size': '1vw'})],
                            className='evolution-graph',
                        ),
                        dcc.RangeSlider(
                            id='range-slider',
                            marks=years,
                            step=1,
                            value=[0, 1],  # takes the first two dates
                            updatemode='mouseup',
                            vertical=False
                        )
                    ]),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="""Total traded by category in the
                              last 20 years"""
                        ),
                        html.Div([
                            html.Div([  # contains the dropdown and it title
                                html.H4(
                                    children='Flow',
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align': 'center'}),
                                dcc.Dropdown(
                                    id='flow-picker',
                                    options=flows,
                                    value=flows[0]),
                            ], style={
                                # z-index added, to be sure that the widget is
                                # above the graph
                                'width': '130px',
                                'display': 'inline-block',
                                'margin': "2% 2% 2% 2%",
                                'z-index': '1'}),
                        ], className='dropdowns-container'),
                        html.Div([  # contains the line plot
                            dcc.Graph(
                                id='graph-commodities',
                                style={
                                    'margin-top': '-10%',
                                    'z-index': '0'}),
                        ]),
                    ], className='page-container'),
                    html.Div([  # Links to route to other pages
                        dcc.Link(
                            dbc.Button(
                                "To main page",
                                className='button-next'),
                            href="/",
                            refresh=True,
                            style={'margin': '2%'}),
                        dcc.Link(
                            dbc.Button(
                                'To countries',
                                className='button-next'),
                            href="/countries/",
                            refresh=True,
                            style={'margin': '2%'})
                    ], className='buttons-container')
                ])

    @app.callback(  # decorator for inputs and outputs of update_bar_plot()
        Output(
            component_id='graph-evolution-categories',
            component_property='figure'),
        [
            Input(component_id='range-slider', component_property='value'),
            Input(component_id='flow-picker-bar', component_property='value')]
        )
    def update_bar_plot(years_input, flows_input):
        """Dynamic bar plot.

        This function takes a range of years as an input from the slider
        component and prompts a Plotly bar plot, having the sum of the total
        traded in USD by category.

        """
        years_range = years[years_input[0]:years_input[1]]
        if not years_range:
            years_range = [years[years_input[0]]]
        # df with values within the year range
        df_short = df[df['year'].isin(years_range)]
        # df with values from the selected flow
        df_short = df_short[df_short['flow'] == flows_input]
        # df with the sum of total traded by category
        df_short = df_short.groupby(['category_num']).sum().\
            sort_values(by='trade_usd', ascending=False)
        categories = [categories_dict[i] for i in list(df_short.index)]
        data = go.Bar(  # build bar plot
                    x=list(df_short.index),
                    y=list(df_short['trade_usd']),
                    marker=dict(
                        color=[1, 2, 3, 4, 5, 6, 7],  # categories numbers
                        colorscale='teal'),
                    meta=categories,
                    # shows this legend when hover
                    hovertemplate="""<br>Total USD: %{y} $<br>Category:%{meta}
                    <extra></extra>""")
        layout = go.Layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    bargap=0.1,
                    width=450,
                    height=350,
                    bargroupgap=0.1,
                    showlegend=False,  # table being used for legend
                    template='plotly_white',
                    yaxis=dict(
                        title='Trade (USD)',
                        title_standoff=40,
                        showgrid=False,
                        side='left'),
                    xaxis=dict(
                        title='Category',
                        autorange=True,
                        showgrid=False,
                        type='category'))
        fig = go.Figure({'data': data, 'layout': layout})
        return fig

    @app.callback(  # decorator for inputs and outputs of update_line_plot()
        Output(component_id='graph-commodities', component_property='figure'),
        [Input(component_id='flow-picker', component_property='value')])
    def update_line_plot(flows_input):
        """Dynamic line plot.

        This function takes a flow input and generates a line plot with
        the total traded per category in the last 20 years

        """
        df_short = df[df['year'] >= 1986]  # get data for last 20 years
        df_short = df_short[df_short.flow == flows_input]  # filter by flow
        traces = []  # make an empty list of traces (categories)
        for i, category in enumerate(df_short['category_num'].unique()):
            df_by_cat = df_short[df_short['category_num'] == category]
            df_by_cat = df_by_cat.groupby('year').sum()
            traces.append(
                go.Line(
                    x=list(df_by_cat.groupby('year').sum().index),
                    y=df_by_cat['trade_usd'],
                    mode='lines+markers',
                    name=categories_dict[category],
                    # meta variable allows to add an extra feature to the
                    # hover legend
                    meta=categories_dict[category],
                    line=dict(color=colors_traces[i]),
                    hovertemplate="""<br>Year: %{x}<br>Total USD: %{y} $
                    <br>Category: %{meta}<extra></extra>""",
                    showlegend=True))

        return {
            'data': traces,  # these are go.Scatter() objects
            'layout': go.Layout(  # plot's layout
                        height=550,
                        xaxis={
                            'showgrid': False,
                            'title': {'text': 'Last 20 Years'},
                            'title_standoff': 40,
                            'nticks': 30
                            },
                        yaxis={
                            'title': 'Trade (USD)',
                            'showgrid': False,
                            'automargin': True,
                            'rangemode': 'tozero',
                            'autorange': True},
                        legend_title_text='Category',
                        legend={
                            'font': {'size': 9},
                            'y': 0.5})}

    return app.server

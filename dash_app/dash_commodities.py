import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from .preprocessing import clean_df
from .components.table_categories import gen_table_categories, categories_dict

# DATAFRAME
df = pd.read_csv('data/commodity_trade_statistics_data.csv')
df = clean_df(df)

# INPUT VALUES
years = list(df.year.drop_duplicates())
years.sort()
flows = list(df['flow'].drop_duplicates())
flows.sort()

# CUSTOMIZATION
colors_traces_lineplot = [
    '#004242', 
    '#008080', 
    '#3ab09e', 
    '#44d7a8', 
    '#48d1cc', 
    '#7fffd4',
    '#aaf0d1']

def dash_app_commodities(flask_app, path):
    app = Dash(
        __name__,
        server = flask_app, # rendered by the flask app
        url_base_pathname=path, # the flask route for this page
        external_stylesheets = \
            [dbc.themes.BOOTSTRAP] # allow bootstrap components
    )

    app.layout = html.Div([
                    html.H1(
                        className='main-title',
                        children= 'Global trades by Commodities'
                    ),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="Total traded by category along the years" 
                        ),
                        html.Div([
                            dcc.Graph(id='graph-evolution-categories'),
                            dbc.Table(
                                gen_table_categories(), 
                                bordered=True,
                                hover=True,
                                responsive=True,
                                striped=False,
                                style={'font-size':'1vw'})],
                            className='evolution-graph',
                        ),
                        dcc.RangeSlider(
                            id='range-slider',
                            marks=years,
                            step=1,
                            value = [0, 1],
                            updatemode='mouseup', 
                            vertical= False
                        )
                    ]),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children=\
                                "Total traded by category in the last 20 years" 
                        ),
                        html.Div([
                            html.Div([
                                html.H4(
                                    children='Flow',
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align':'center'}),
                                dcc.Dropdown(
                                    id='flow-picker', 
                                    options=flows,
                                   value=flows[0]),
                            ], style={
                                'width': '130px', 
                                'display':'inline-block',
                                'margin': "2% 2% 2% 2%",
                                'z-index': '1'}),
                        ], className='dropdowns-container'),
                        html.Div([
                            dcc.Graph(
                                id='graph-commodities',
                                style={
                                    'margin-top':'-10%',
                                    'z-index': '0'}),
                        ]),
                ], className= 'page-container'),
                    html.Div([
                        dcc.Link(
                            dbc.Button(
                                "To main page",
                                className='button-next'),
                            href="/",
                            refresh = True,
                            style={'margin':'2%'}),
                        dcc.Link(
                            dbc.Button(
                                'To countries',
                                className='button-next'),
                            href="/countries/",
                            refresh = True,
                            style={'margin':'2%'})
                    ], className = 'buttons-container')
                ])
    
    @app.callback( # decorator for inputs and outputs of update_bar_plot()
        Output(
            component_id='graph-evolution-categories',
            component_property='figure'),
        [Input(component_id='range-slider', component_property='value')])
    
    def update_bar_plot(years_input):
        """ This function takes a range of years as an input from the slider 
        component and prompts a Plotly bar plot, having the sum of the total
        traded in USD by category """
        years_range = years[years_input[0]:years_input[1]]
        if not years_range:
            years_range = [years[years_input[0]]]
        # df with values within the year range
        df_short = df[df['year'].isin(years_range)] 
        # df with the sum of total traded by category
        df_short = df_short.groupby(['category_num']).sum().\
            sort_values(by='trade_usd', ascending=False)
        data = go.Bar( # build bar plot
                    x=list(df_short.index),
                    y=list(df_short['trade_usd']),
                    marker=dict(
                        color=[1, 2, 3, 4, 5, 6, 7], # categories numbers
                        colorscale='teal'),
                    # shows this legend when hover
                    hovertemplate='<br>Total USD: %{y} $<br>')
        layout = go.Layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    bargap=0.1,
                    width = 450,
                    height = 350, 
                    bargroupgap=0.1,
                    showlegend=False, # table being used for legend
                    template = 'plotly_white',
                    yaxis=dict(
                        title='Total traded (USD)',
                        title_standoff = 40,
                        showgrid = False, 
                        side= 'left'),
                    xaxis=dict(
                        title='Category',
                        autorange = True,
                        showgrid = False,
                        type= 'category'))
        fig = go.Figure({'data':data, 'layout':layout})
        return fig
       
    @app.callback( # decorator for inputs and outputs of update_line_plot()
        Output(component_id='graph-commodities', component_property='figure'),
        [Input(component_id='flow-picker', component_property='value')])

    def update_line_plot(flows_input):
        """ This function takes a flow input an generates a line plot with 
         the total traded per category in the last 20 years """
        df_short = df[df['year'] >= 1986] # get data for last 20 years
        df_short = df_short[df_short.flow == flows_input] # filter by flow
        traces = [] # make an empty list of traces (categories)
        for i, category in enumerate(df_short['category_num'].unique()):
            df_by_cat = df_short[df_short['category_num'] == category]
            df_by_cat = df_by_cat.groupby('year').sum()
            traces.append(
                go.Line(
                    x = list(df_by_cat.groupby('year').sum().index),
                    y = df_by_cat['trade_usd'],
                    mode='lines+markers',
                    name = category,
                    # meta variable allows to add an extra feature to the
                    # hover legend
                    meta = str(category) + ') ' + categories_dict[category],
                    line=dict(color=colors_traces_lineplot[i]),
                    hovertemplate=\
                        '<br>Year: %{x}<br>Traded: %{y}<br>Category: %{meta}<br>',
                    showlegend=True))
            
        return {
            'data': traces, # these are go.Scatter() objects
            'layout':go.Layout( # plot's layout
                        height = 550,
                        xaxis = {
                            'showgrid': False,
                            'title': dict(text = 'Last 20 Years'),
                            'title_standoff':40,
                            'nticks':30
                            },
                        yaxis = dict(
                            title='Trade (USD)',
                            showgrid=False,
                            automargin=True,
                            rangemode='tozero',
                            autorange = True),
                        legend_title_text='Category')}

    return app.server
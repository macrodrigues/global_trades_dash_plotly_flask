from .dash_commodities import Dash, html, dcc, pd, go, dbc, Input, Output
from .dash_commodities import years, categories_dict, df, clean_df
from .dash_commodities import colors_traces
from .preprocessing import get_df_european_countries
import math

# DATAFRAMES
df = clean_df(df)
countries_top_50 = list(df.groupby('country_or_area').sum().\
    sort_values(by='trade_usd', ascending=False).head(50).index)

df_europe = get_df_european_countries(
    pd.read_csv('data/list-european-countries.csv'), 
    df)


def dash_app_countries(flask_app, path):
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
                        children= 'Global trades by Countries'
                    ),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="Top 50 countries on total trades, along the years" 
                        ),
                        html.Div([
                            html.H4(
                                children='Countries',
                                style={
                                    'font-size': '1.2vw',
                                    'text-align':'center',
                                    'padding-top':'3%'}),        
                            dcc.Dropdown(
                                id='countries-picker', 
                                options=countries_top_50,
                                value = countries_top_50[10],
                                style={
                                'width': '150px', 
                                'margin': 'auto',}),
                            dcc.Graph(id='graph-evolution-countries'),
                        ]),
                        dcc.RangeSlider(
                            id='range-slider',
                            marks=years,
                            step=1,
                            value = [0, 1],
                            updatemode='mouseup', 
                            vertical= False
                    )]),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children=\
                                "Trades by European Countries" 
                        ),
                        html.Div([
                            html.Div([
                                html.H4(
                                    children='Year',
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align':'center'}),
                                dcc.Dropdown(
                                    id='years-picker', 
                                    options=years,
                                   value=years[-1]),
                            ], style={
                                'width': '130px', 
                                'display':'inline-block',
                                'margin': "2% 2% 2% 2%",
                                'z-index': '1'}),
                        ], className='dropdowns-container'),
                        html.Div([
                            dcc.Graph(
                                id='graph-european-countries',
                                style={
                                    'margin-top':'-10%',
                                    'z-index': '0'})
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
                                'To commodities',
                                className='button-next'),
                            href="/commodities/",
                            refresh = True,
                            style={'margin':'2%'})
                    ], className = 'buttons-container')
                ])
    
    @app.callback( # decorator for inputs and outputs of update_bar_plot()
    Output(
        component_id='graph-evolution-countries',
        component_property='figure'),
    [Input(component_id='range-slider', component_property='value'),
     Input(component_id='countries-picker', component_property='value')])

    def update_pie_plot(years_input, selected_country):
        years_range = years[years_input[0]:years_input[1]]
        if not years_range:
            years_range = [years[years_input[0]]]
        # df with values within the year range
        df_short = df[df['year'].isin(years_range)]
        df_top_50 = df_short[df_short['country_or_area'].isin(countries_top_50)]
        df_top_50 = df_top_50[df_top_50['country_or_area'] == selected_country]
        df_top_50 = df_top_50.groupby('category').sum()
        categories_raw = list(df_top_50.index)
        categories_nums = [int(category[1]) for category in categories_raw]
        categories = [categories_dict[i] for i in categories_nums]
        data = go.Pie( 
            labels=categories, 
            values=df_top_50['trade_usd'],
            hovertemplate='<br>Category: %{label}<br>Total USD: %{value} $<br>Percentage: %{percent}')
        layout = go.Layout(
            margin=dict(l=20, r=20, t=20, b=20),
            legend= dict(y=0.5),
            legend_title_text='Categories')
        fig = go.Figure({'data':data, 'layout':layout})
        fig.update_traces(marker=dict(colors=colors_traces))
        return fig

    @app.callback( # decorator for inputs and outputs of update_bubble_plot()
    Output(
        component_id='graph-european-countries',
        component_property='figure'),
    [Input(component_id='years-picker', component_property='value')])

    def update_bubble_plot(years_input):
        df_short = df_europe[df_europe.year == years_input]
        traces = []
        for i, category in enumerate(df_short['category_num'].unique()):
            df_by_cat = df_short[df_short['category_num'] == category]
            df_by_cat = df_by_cat.groupby('country_or_area').sum()
            traces.append(
                go.Scatter(
                    x = df_by_cat.index,
                    y = df_by_cat['trade_usd'],
                    marker=dict(
                        size=df_by_cat['weight_kg'].\
                            apply(lambda x: 0 if math.isnan(x) else x),
                        sizeref = 5e7), # define mass as marker,
                    text=df_by_cat['weight_kg'].\
                        apply(lambda x: 0 if math.isnan(x) else x),
                    mode = 'markers',
                    line=dict(color=colors_traces[i]),
                    hovertemplate=\
                        '<br>Country: %{x}<br>Weight: %{text} Kg<br>Total USD: %{y} $',
                    name = categories_dict[category]
                ))
        return {
            'data': traces, # these are go.Scatter() objects
            'layout':go.Layout( # plot's layout
                xaxis = {
                    'showgrid': False,
                    'title': dict(text = 'European countries'),
                    'title_standoff':40,
                    'nticks':30
                    },
                yaxis = {
                    'title':'Trade (USD)' , 
                    'showgrid': False,
                    'automargin': True,
                    'rangemode':'tozero'},
                legend_title_text='Categories')}

    return app.server
from .dash_commodities import Dash, html, dcc, pd, go, dbc, Input, Output
from .dash_commodities import years, categories_dict, df, clean_df

# DATAFRAME
df = clean_df(df)
countries_top_50 = list(df.groupby('country_or_area').sum().\
    sort_values(by='trade_usd', ascending=False).head(50).index)


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
            legend= dict(y=0.5))
        fig = go.Figure({'data':data, 'layout':layout})
        return fig

    return app.server
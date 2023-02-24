"""Script to render the Dash applicationtaking into account the countries."""

from .dash_commodities import Dash, html, dcc, pd, go, dbc, Input, Output
from .dash_commodities import years, categories_dict, df, clean_df
from .dash_commodities import colors_traces, flows
from .preprocessing import get_df_european_countries
import math

# DATAFRAMES
df = clean_df(df)
df_europe = get_df_european_countries(
    pd.read_csv('data/list-european-countries.csv'),
    df)

# LISTS
countries_top_50 = list(df.groupby('country_or_area').sum().sort_values(
    by='trade_usd',
    ascending=False).head(50).index)


def dash_app_countries(flask_app, path):
    """Launch Dash app on Flask server.

    Route for countries page. It displays two plots, a pie chart having
    the categories most traded per country (Only takes into account the
    50 countries with the most trades). And it also displays a bubble plot
    showing the Trades and weights per european country.

    """
    app = Dash(
        __name__,
        server=flask_app,  # rendered by the flask app
        url_base_pathname=path,  # the flask route for this page
        external_stylesheets=[dbc.themes.BOOTSTRAP]   # bootstrap components
    )

    app.layout = html.Div([
                    html.H1(
                        className='main-title',
                        children='Global trades by Countries'
                    ),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="""Categories traded by country along
                            the years"""
                        ),
                        html.Div([
                            html.Div([
                                html.H4(  # title of the dropdwon
                                    children="""Top 50 countries with the
                                    most trades""",
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align': 'center',
                                        'padding-top': '3%'}),
                                dcc.Dropdown(  # top 50 countries
                                    id='countries-picker',
                                    options=countries_top_50,
                                    value=countries_top_50[10],
                                    style={
                                        'width': '150px',
                                        'margin': 'auto'})]),
                            html.Div([
                                html.H4(  # title of the dropdwon
                                    children='Flows',
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align': 'center'}),
                                dcc.Checklist(  # year's dropdown
                                    id='flows-picker-pie',
                                    options=flows,
                                    value=[flows[0]],
                                    inline=True,
                                    className='label-checkbox'),
                            ], style={
                                'display': 'inline-block',
                                'margin': "1%",
                                'z-index': '1'}),
                        ], className='dropdowns-container'),
                        dcc.Graph(
                            id='graph-evolution-countries'),
                        dcc.RangeSlider(  # slider for the year's range
                            id='range-slider',
                            marks=years,
                            step=1,
                            value=[0, 1],  # first two years
                            updatemode='mouseup',
                            vertical=False)
                    ]),
                    html.Div([
                        html.H3(
                            className='subtitle',
                            children="""Trades and respective Weights (in Kg)
                            by European Countries"""
                        ),
                        html.Div([
                            html.Div([
                                html.H4(  # title of the dropdwon
                                    children='Year',
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align': 'center'}),
                                dcc.Dropdown(  # year's dropdown
                                    id='years-picker',
                                    options=years,
                                    value=years[-1]),
                            ], style={
                                'width': '130px',
                                'display': 'inline-block',
                                'margin': "1%",
                                "margin-top": '2%',
                                'z-index': '1'}),
                            html.Div([
                                html.H4(  # title of the dropdwon
                                    children='Flows',
                                    style={
                                        'font-size': '1.2vw',
                                        'text-align': 'center'}),
                                dcc.Checklist(  # year's dropdown
                                    id='flows-picker',
                                    options=flows,
                                    value=[flows[0]],
                                    inline=True,
                                    className='label-checkbox'),
                            ], style={
                                'display': 'inline-block',
                                'margin': "1%",
                                "margin-top": '2%',
                                'z-index': '1'}),
                        ], className='dropdowns-container'),
                        html.Div([
                            dcc.Graph(
                                id='graph-european-countries',
                                style={
                                    'margin-top': '-10%',
                                    'z-index': '0'})
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
                                'To commodities',
                                className='button-next'),
                            href="/commodities/",
                            refresh=True,
                            style={'margin': '2%'})
                    ], className='buttons-container')
                ])

    @app.callback(  # decorator for inputs and outputs of update_bar_plot()
        Output(
            component_id='graph-evolution-countries',
            component_property='figure'),
        [
            Input(component_id='range-slider', component_property='value'),
            Input(component_id='countries-picker', component_property='value'),
            Input(component_id='flows-picker-pie', component_property='value')
        ])
    def update_pie_plot(years_input, selected_country, flows_input):
        """Dynamic pie plot.

        It takes two arguments, the year's range and the selected country, and
        constructs a dynamic pie plot using plotly.graph_objects.

        """
        years_range = years[years_input[0]:years_input[1]]
        if not years_range:
            years_range = [years[years_input[0]]]
        # df with values within the year range
        df_short = df[df['year'].isin(years_range)]
        df_short = df_short[df_short['flow'].isin(flows_input)]
        df_top_50 = df_short[
            df_short['country_or_area'].isin(countries_top_50)]
        df_top_50 = df_top_50[df_top_50['country_or_area'] == selected_country]
        df_top_50 = df_top_50.groupby('category').sum()
        categories_raw = list(df_top_50.index)  # list elements from index
        # it filters the categories to take only the numbers (position 1)
        categories_nums = [int(category[1]) for category in categories_raw]
        # by having only the numbers we can pass it into the dictionary
        categories = [categories_dict[i] for i in categories_nums]
        data = go.Pie(
            labels=categories,
            values=df_top_50['trade_usd'],
            # <extra></extra> removes the traces when hovering
            hovertemplate="""<br>Category: %{label}
            <br>Total USD: %{value} $
            <br>Percentage: %{percent}<extra></extra>""")
        layout = go.Layout(
            margin={'l': 20, 'r': 20, 't': 20, 'b': 20},
            legend={'y': 0.5},
            legend_title_text='Categories')
        fig = go.Figure({'data': data, 'layout': layout})
        # add set of colors defined before
        fig.update_traces(marker={'colors': colors_traces})
        return fig

    @app.callback(  # decorator for inputs and outputs of update_bubble_plot()
        Output(
            component_id='graph-european-countries',
            component_property='figure'),
        [
            Input(component_id='years-picker', component_property='value'),
            Input(component_id='flows-picker', component_property='value')])
    def update_bubble_plot(years_input, flows_picker):
        """Dynamic bublle plot.

        It takes two arguments, the year's range and flow, and
        constructs a dynamic bubble plot using plotly.graph_objects.

        """
        df_short = df_europe[df_europe.year == years_input]
        df_short = df_short[df_short.flow.isin(flows_picker)]
        traces = []
        for i, category in enumerate(df_short['category_num'].unique()):
            df_by_cat = df_short[df_short['category_num'] == category]
            df_by_cat = df_by_cat.groupby('country_or_area').sum()
            traces.append(
                go.Scatter(
                    x=df_by_cat.index,
                    y=df_by_cat['trade_usd'],
                    marker=dict(
                        size=df_by_cat['weight_kg'].apply(
                            lambda x: 0 if math.isnan(x) else x),
                        sizeref=5e7),  # define weight as marker size,
                    # text is the same as size, only to use on overtemplate
                    text=df_by_cat['weight_kg'].apply(
                            lambda x: 0 if math.isnan(x) else x),
                    mode='markers',
                    line=dict(color=colors_traces[i]),
                    # <extra></extra> removes the traces when hovering
                    hovertemplate="""<br>Country: %{x}
                    <br>Weight: %{text} Kg
                    <br>Total USD: %{y} $<extra></extra>""",
                    name=categories_dict[category]  # traces legend
                ))
        return {
            'data': traces,  # these are go.Scatter() objects
            'layout': go.Layout(  # plot's layout
                xaxis={
                    'showgrid': False,
                    'title': {'text': 'European countries'},
                    'title_standoff': 15,
                    'automargin': True,
                    'nticks': 30
                    },
                yaxis={
                    'title': 'Trade (USD)',
                    'showgrid': False,
                    'automargin': True,
                    'rangemode': 'tozero'},
                legend={'y': 0.5},
                legend_title_text='Categories')}

    return app.server

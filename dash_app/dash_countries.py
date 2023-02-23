from .dash_commodities import Dash, html, dcc, pd, go, dbc, Input, Output

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
                    )])

    return app.server
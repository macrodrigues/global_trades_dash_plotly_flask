from dash import Dash, html, dcc

def run_dash_1(server):
    app = Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
    )

    app.layout = html.Div([
                html.H1('Hello App')
                ])
    
    return app.server
"""This script launches the Flask server.

It has the functions having the Dash framework. These Dash functions are
bridged to the Flask Server, and they will
only render the Dash application when routed to the given paths

"""

from flask import Flask, render_template
from dash_app.dash_commodities import dash_app_commodities
from dash_app.dash_countries import dash_app_countries

server = Flask(__name__)  # Flask server
# functions having the dash applications
dash_app_commodities(server, path='/commodities/')
dash_app_countries(server, path='/countries/')


@server.route('/')  # home page renders the 'index.html'
def index():
    """Render index.html."""
    return render_template('index.html')


if __name__ == '__main__':
    server.run()

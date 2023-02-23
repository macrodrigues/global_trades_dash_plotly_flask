import pandas as pd
from flask import Flask, render_template
from dash import Dash, html, dcc
from dash_app.dash_commodities import dash_app_commodities
from dash_app.dash_countries import dash_app_countries

server = Flask(__name__)
dash_app_commodities(server, path = '/commodities/')
dash_app_countries(server, path = '/countries/')

@server.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    server.run(host="0.0.0.0", port = 7000)


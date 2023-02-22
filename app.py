import pandas as pd
from flask import Flask, render_template
from dash import Dash, html, dcc
from dash_app import dash_app_global

server = Flask(__name__)
dash_app_global(server, path = '/commodities/')

@server.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    server.run(host="0.0.0.0", port = 7000)


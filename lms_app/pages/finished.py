#Libraries
import dash_bootstrap_components as dbc
import os
import pandas as pd
import dash
from dash import Dash, dcc, html
from dash import dash_table as dt
from dash.dependencies import Input, Output, State
from flask import Flask
from time import sleep
from datetime import date
import pages.ui_assets as ui

from pages.finished_callbacks import add_finished_callbacks

add_finished_callbacks(dash)


dash.register_page(__name__, 
                    path='/finished',
                    title='Last Mile: Quote Request Form',
                    name='Last Mile: Quote Request Form')

layout = dbc.Container([
    html.Br(),
    html.Br(),

    ui.create_small_quote_card(),
    html.Div(style={'border-width':'1px', 'border-style':'solid', 'border-color':'black', 'border-top-width': '0px'}, children = [
        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.Col([
                html.H4('A representative will be in touch with you shortly. Thank you for completing the form.', 
                        style={'font-weight':'bold', 'text-align': 'center'})
            ],width={"size": 10, "offset": 1}, md=10, align='stretch'),
        ]),

        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.Col([
                html.Div(id='confirmation-div'),
            ],width={"size": 6, "offset": 3}, md=6, align='stretch'),
        ]),

        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.Col([
                dcc.Loading(children = [html.Div(id='prompt')], fullscreen = True),
            ],width={"size": 10, "offset": 1}, md=10, align='stretch'),
        ]),

        html.Br(),

    ])
])
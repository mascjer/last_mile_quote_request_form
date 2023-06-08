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


dash.register_page(__name__, 
                    path='/local_pick_delivery_service',
                    title='Last Mile: Quote Request Form',
                    name='Last Mile: Quote Request Form')

layout = dbc.Container([
    html.Br(),
    html.Br(),

    ui.create_small_quote_card(),
    html.Div(style={'border-width':'1px', 'border-style':'solid', 'border-color':'black', 'border-top-width': '0px'}, children = [
        html.Br(),

         dbc.Row([
            dbc.Col([
                ui.local_pick_drop_service(),
            ],width={"size": 11, "offset": 1}, md=12, align='stretch'),
        ]),
        
    ])

])
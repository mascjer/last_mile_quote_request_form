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
from pages.air_euv_callbacks import add_air_euv_callbacks



dash.register_page(__name__, 
                    path='/air_euv',
                    title='Last Mile: Quote Request Form',
                    name='Last Mile: Quote Request Form')

add_air_euv_callbacks(dash)


layout = dbc.Container([
    html.Br(),
    html.Br(),

    ui.create_small_quote_card(),
    html.Div(style={'border-width':'1px', 'border-style':'solid', 'border-color':'black', 'border-top-width': '0px'}, children = [
        html.Br(),

        dbc.Row([
            dbc.Col([
                ui.create_air_euv(),
            ],width={"size": 11, "offset": 1}, md=12, align='stretch'),
        ]),

        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.Button('Submit', id='submit-btn', n_clicks = 0, style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'50px'}),
                ]),
                dbc.Row([
                    html.P('*Please wait until browser is done updating after submitting*', style={'font-weight':'bold', 'color': 'red','font-size': '11px', 'font-style' : 'italic'})
                ])
            ],width={"size": 11, "offset": 1}, md=12, align='stretch'),
        ]),

        html.Br(),

         dbc.Row([
            dbc.Col([
                dbc.Row([
                    html.P('For any Expedite questions, please reach out to Airdomestic@chrobinson.com. For any EUV questions, please reach out to 530EUV@chrobinson.com.', style={'font-weight':'bold', 'font-style' : 'italic', 'text-align': 'center'})
                ])
            ], md=12, align='stretch'),
        ]),

        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.Col([
                html.Div(id='output_air_euv')
            ],width={"size": 11, "offset": 1}, md=10, align='stretch'),
        ]),

        html.Br(),
        html.Br(),

    ])

])
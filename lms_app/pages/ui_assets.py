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
import base64
import tempfile

app = dash.Dash(__name__)

states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CAN', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID',
          'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
          'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
          'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
          'WI', 'WY'] 

origin_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CAN', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID',
          'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
          'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
          'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
          'WI', 'WY'] 

dest_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CAN', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID',
          'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
          'MO', 'MT', 'MX', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
          'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
          'WI', 'WY'] 

#used in items selection
label_text = "Weight per Piece (pounds)"
parts = label_text.split("per")
piece_parts = parts[1].split("Piece")

timezones = {'Eastern': 'America/New_York',
            'Central': 'America/Chicago',
            'Mountain': 'America/Denver',
            'Mountain (AZ)': 'America/Phoenix',
            'Pacific': 'America/Los_Angeles',
            'Alaskan': 'America/Anchorage',
            'Hawaii': 'Pacific/Honolulu'}

times = []

for i in range(12):
    hours = i+1
    for j in range(2):
        minutes = str(j*30).zfill(2)
        time = str(hours) + ':' + str(minutes)
        times.append(time)

am_pms = ['AM', 'PM']


def create_quote_card():
    return html.Div(id = 'quote-card-div', style = {'background-color':'#0078AE'}, children =[
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H1('Last Mile Quote Request Form', style={'font-weight':'bold', 'text-align': 'center', 'color': 'white'})
            ], md=12)
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col([], md=1),
            dbc.Col([
                html.P(children = ['For additional information on Expedite Services, ',
                        html.A('click here.', href='http://worknet/lastmile/Documents/expedite_services_internal_overview%20(1).pdf', target="_blank", style={'color':'black'})], style={'color': 'white', 'font-weight':'bold'}),
            ], md=10)
        ]),


        html.Br(),
        html.Br(),
    ])


def create_small_quote_card():
     return html.Div(id = 'quote-card-div', style = {'background-color':'#0078AE'}, children =[
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H1('Last Mile Quote Request Form', style={'font-weight':'bold', 'text-align': 'center', 'color': 'white'})
            ], md=12)
        ]),
        html.Br(),
        html.Br(),
     ])


def create_footer():
    return html.Div(style = {'background-color':'#0078AE', 'width':'68%', 'margin':'auto',
                                'min-height': '5vh'}, children =[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Img(src=app.get_asset_url('chr.png'), width="610"),
                ],width={"size": 3, "offset": 3}, md=6  , align='stretch')
            ]),
            html.Br(),
    ])


def trans_mode_1():
    return html.Div(
    [
        dbc.Label("1.Select the mode of transportation needed for this quote request"),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Air Expedite', id='air-btn', color="secondary", n_clicks = 0,
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'50px'}),
                        href='/air_euv')
                ], md=2, align='stretch'),
        ]),
        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button(['EUV (exclusive use vehicle)', html.Br(), 'Ground Expedite'], id='euv-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'50px'}),
                        href='/air_euv')
                ], md=2, align='stretch'),
        ]),
        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('First Mile Pickup', id='first-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'50px'}),
                        href='/first_final_mile_service')
                ], md=2, align='stretch'),
        ]),
        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Final Mile Delivery', id='final-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'50px'}),
                        href='/first_final_mile_service')
                ], md=2, align='stretch'),
        ]),

        html.Br(),
        
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Local Pickup AND Delivery', id='pick-drop-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'50px'}),
                        href='/local_pick_delivery_service')
                ], md=2, align='stretch'),
        ]),
        dbc.Row([
                dbc.Col([
                    html.P('**Within 100 miles of each other**', style={'font-weight':'bold', 'color': 'red','font-size': '11px'}),
                ]),
        ]),

    ]
)


def create_air_euv():
        return html.Div([
            html.Div(id='garbage-output-0'),
            html.Div(id='garbage-div-2'),

            html.Br(),
            html.P(["* - Required field"]
                ,style={'font-weight':'bold'}),

            dbc.Label("2.What is the customer's C-code*, your seven letter*, and all 7-letters/email groups to be included in communication regarding this quote?"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id='ccode-input', placeholder='Customer code'),
                ], md=2),
                dbc.Col([
                    dbc.Input(id='empcode-input', placeholder='Seven letter'),
                ], md=2),
            ]),

            html.Br(), 

            dbc.Row([
                dbc.Col([
                    dbc.Textarea(id='additional-input', placeholder='Additional seven letters/email groups'),
                ], md=4),
            ]),

            dcc.Loading(html.Div(id='ccode-div'), fullscreen = True, type = 'circle'),

            html.Br(),
            html.Br(),

            ### WILL THEY EVER NEED MORE THAN ONE?
            dbc.Label("3.What is the load number?"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id='load-num-input', placeholder='Load Number'),
                ], md=2),
            ]),

            html.Div(id='load-num-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("4.Is this quote only or freight on hand?*"),
            dbc.Col([
                    dcc.Dropdown(
                        id = 'quote-freight-drop',
                        placeholder = 'Quote/On Hand',
                        options=[
                            {'label': 'Quote Only', 'value': 'quote_only'},
                            {'label': 'Freight on Hand', 'value': 'freight_on_hand'},
                        ]
                        )
                ], md=2),

            html.Div(id='freight-div'),

            html.Br(),
            html.Br(),

            dbc.Label("5.Please enter the Origin City, State & Zip Code*"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id='o-city-input', placeholder='City'),
                ], md=2),
                dbc.Col([
                    dcc.Dropdown(id='o-state-drop', placeholder='State', options=[{'label': state, 'value': state} for state in origin_states]),
                ], md=2),
                dbc.Col([
                    dbc.Input(id='o-zip-input', placeholder='Zip Code'),
                ], md=2),
            ]),
            html.P(['EUV cannot provide service from Canada (CAN) or Puerto Rico (PR). Ignore this if you selected Air Exp.'], style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0.5%'}),

            html.Div(id='origin-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("6.What is the requested pickup date?*"),
            dbc.Row([
                dbc.Col([
                    html.Div(style={'display': 'inline-block', 'border-radius' : '5px', 
                            'border-spacing' : '0', 'border-collapse' :'separate'}, children=[
                        dcc.DatePickerSingle(
                            id='req-pick-date',
                            initial_visible_month=date.today()
                        )
                    ])
                ], md=2, align='stretch'),
                dbc.Col([
                    dbc.Input(id='pickup-addtional-input', placeholder='Additional Information'),
                ], md=4),
            ]),

            html.Div(id='request-pick-date-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("7.What is the origin open time?*"),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='pick-open-time-drop',
                        placeholder = 'Time',
                        options=[{'label': time, 'value': time} for time in times]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'pick-open-am-pm-drop',
                        placeholder = 'AM/PM',
                        options=[{'label': am_pm, 'value': am_pm} for am_pm in am_pms]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'pick-open-timezone-drop',
                        placeholder = 'Timezone',
                        options=[{'label': timezone, 'value': abbreviation} for timezone, abbreviation in timezones.items()]
                        )
                ], md=2),
            ]),

            html.Div(id='origin-open-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("8.What is the origin close time?*"),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='pick-close-time-drop',
                        placeholder = 'Time',
                        options=[{'label': time, 'value': time} for time in times]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'pick-close-am-pm-drop',
                        placeholder = 'AM/PM',
                        options=[{'label': am_pm, 'value': am_pm} for am_pm in am_pms]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'pick-close-timezone-drop',
                        placeholder = 'Timezone',
                        options=[{'label': timezone, 'value': abbreviation} for timezone, abbreviation in timezones.items()]
                        )
                ], md=2),
            ]),
            html.Div(id='origin-close-ae-div'),
            html.Div(id='origin-close-warning-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("9.Please enter the Destination City, State & Zip Code*"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id='d-city-input', placeholder='City'),
                ], md=2),
                dbc.Col([
                    dcc.Dropdown(id='d-state-drop', placeholder='State', options=[{'label': state, 'value': state} for state in dest_states]),
                ], md=2),
                dbc.Col([
                    dbc.Input(id='d-zip-input', placeholder='Zip Code'),
                ], md=2),
            ]),

            html.P(['EUV cannot provide service from Canada (CAN) or Puerto Rico (PR). Ignore this if you selected Air Exp.'], style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0.5%'}),

            html.Div(id='dest-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("10.What is the requested delivery day?*"),
            dbc.Row([
                dbc.Col([
                        html.Div(style={'display': 'inline-block', 'border-radius' : '5px', 
                                'border-spacing' : '0', 'border-collapse' :'separate'}, children=[
                            dcc.DatePickerSingle(
                                id='req-del-date',
                                initial_visible_month=date.today()
                            )
                        ])
                    ], md=2, align='stretch'),

                dbc.Col([
                        dbc.Input(id='delivery-addtional-input', placeholder='Additional Information'),
                ], md=4),
            ]),

            html.Div(id='request-del-date-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("11.What is the receiver open time?*"),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='drop-open-time-drop',
                        placeholder = 'Time',
                        options=[{'label': time, 'value': time} for time in times]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'drop-open-am-pm-drop',
                        placeholder = 'AM/PM',
                        options=[{'label': am_pm, 'value': am_pm} for am_pm in am_pms]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'drop-open-timezone-drop',
                        placeholder = 'Timezone',
                        options=[{'label': timezone, 'value': abbreviation} for timezone, abbreviation in timezones.items()]
                        )
                ], md=2),
            ]),

            html.Div(id='dest-open-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("12.What is the receiver close time?*"),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='drop-close-time-drop',
                        placeholder = 'Time',
                        options=[{'label': time, 'value': time} for time in times]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'drop-close-am-pm-drop',
                        placeholder = 'AM/PM',
                        options=[{'label': am_pm, 'value': am_pm} for am_pm in am_pms]
                        )
                ], md=2),

                dbc.Col([
                    dcc.Dropdown(
                        id = 'drop-close-timezone-drop',
                        placeholder = 'Timezone',
                        options=[{'label': timezone, 'value': abbreviation} for timezone, abbreviation in timezones.items()]
                        )
                ], md=2),
            ]),

            html.Div(id='dest-close-ae-div'),
            html.Div(id='dest-close-warning-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("13.Is freight palletized?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
                id="palletized-radio",
            ),

            html.Div(id='freight-palletized-div'),

            dbc.Label("If no, how is the freight packaged?"),
            dbc.Col([
                dbc.Input(id='packaging-input', placeholder='Packaging Type', disabled = True),
            ], md=10),

            html.Div(id='packaging-div'),

            html.Br(),
            html.Br(),

            dbc.Label("14.Please select the amount of unique pallet/packaging type dimensions for pickup or delivery*"),
            dbc.Row([
                html.P(["*EX: if you have 2 packages that each weigh 30 pounds at 12x24x36 inches, 1 package that weighs 50 pounds at 18x12x36 inches", html.Br(),
                    "and 3 packages that weigh 50 pounds at 12x24x36 inches, you would slide the bar to 3 unique items. If all pieces have the same weight", html.Br(),
                    "and dimensions, do not slide the bar and simply enter the quantity under field 15.*"]
                    ,style={'font-style':'italic', 'font-weight':'bold'}),
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Slider(1, 50, step=1, value=1, id='count-input', 
                               tooltip={"placement": "bottom", "always_visible": True}
                               )
                ], md=10),
            ]),
            html.Div(id='items-div'),

            html.Br(),
            html.Br(),

            dbc.Label("15.What are the unique quantites, weights and dimensions of the freight?*"),

            html.Div(id='input-prompt', children=[
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                #dbc.Label('Item #',style={'font-weight':'bold', 'text-align': 'center'})
                            ], md=1),
                            dbc.Col([
                                dbc.Label('Quantity',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                            dbc.Col([
                                dbc.Label(
                                    [
                                        parts[0],
                                        html.Span("per", style={'color': 'red'}),
                                        piece_parts[0],
                                        html.Span("Piece", style={'color': 'red'}),
                                        piece_parts[1]
                                    ],
                                    style={'font-weight': 'bold', 'text-align': 'center'}
                                )
                            ],md= 2),
                            dbc.Col([
                                dbc.Label('Length (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                            dbc.Col([
                                dbc.Label('Width (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                            dbc.Col([
                                dbc.Label('Height (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                        ]),
                    ], md=11)
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                html.Div(id='pieces-div', children=[]),
                ], md=11)
            ]),

            html.Div(id='output-prompt', children=[
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                #dbc.Label('Item #',style={'font-weight':'bold', 'text-align': 'center'})
                            ], md=1),
                            dbc.Col([
                                dbc.Label('Quantity',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                            dbc.Col([
                                dbc.Label('Weight per Piece (pounds)',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                            dbc.Col([
                                dbc.Label('Length (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                            dbc.Col([
                                dbc.Label('Width (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                            dbc.Col([
                                dbc.Label('Height (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                            ],md= 2),
                        ]),
                    ], md=11)
                ]),
            ]),
            
            html.Div(id='container-output'),

            html.Br(),
            html.Br(),

            dbc.Label("16.Is the freight stackable?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
                id="stackable-radio",
            ),
            html.Div(id='stackable-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("17.Is additional insurance needed?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
                id="additional-insurance-radio",
            ),

            html.Div(id='additional-insurance-div'),
            html.Div(id='additional-insurance-div1'),

            dbc.Label("If yes, what is the total value of the load (USD)?"),
            dbc.Col([
                dbc.Input(id='value-input', placeholder='Value (USD)', disabled = True),
            ], md=10),

            html.Div(id='value-div'),

            html.Br(),
            html.Br(),

            dbc.Label("18.What is the commodity?*"),
            dbc.Col([
                dbc.Input(id='commodity-input', placeholder='Commodity description'),
            ], md=10),

            html.Div(
                html.P('***Cannot ship carbon black, cannot insure one-of-a-kind artwork***', 
                        style={'font-weight':'bold', 'color': 'gray', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            ),
            html.Div(id='commodity-div'),

            html.Br(),
            html.Br(),

            dbc.Label("19.Is the freight haz mat?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
                id="hazmat-input",
            ),
            html.Div(id='shared-hazmat-div'),
            dbc.Label("If haz mat, please enter UN #, Class #, and Packing Group #"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id='un-input', placeholder='UN #', disabled=True)
                ], md=2),
                dbc.Col([
                    dbc.Input(id='class-input', placeholder='Class #', disabled=True)
                ], md=2),
                dbc.Col([
                    dbc.Input(id='packing-input', placeholder='Packing Group #', disabled=True)
                ], md=2),
            ]),
            html.Div(id='shared-special-hazmat-div'),

            html.Br(),
            html.Br(),

            dbc.Label("20.Will a delay in transit cause a line-down situation?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
                id="situation-input",
            ),

            html.Div(id='linedown-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("21.Can the freight breakdown?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
                id="breakdown-input",
            ),

            html.Div(id='breakdown-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("22.Please select ALL PICKUP scope of work required:"),
            dbc.Checklist( id = 'pick-scope-check',
            options=[
                {'label': 'After or Before Hours Pickup', 'value': 'after_or_before_hours_pickup'},
                {'label': 'Afternoon Special Pickup', 'value': 'afternoon_special_pickup'},
                {'label': 'Pickup Appointment/Special', 'value': 'pickup_appointment/special'},
                {'label': 'Convention Center Pickup', 'value': 'convention_center_pickup'},
                {'label': 'Extra Man Pickup **will be calculated after service is performed', 'value': 'extra_man_pickup'},
                {'label': 'Hospital Pickup', 'value': 'hospital_pickup'},
                {'label': 'Hotel Pickup', 'value': 'hotel_pickup'},
                {'label': 'Inside Pickup **room of choice to the first floor only', 'value': 'inside_pickup'},
                {'label': 'Liftgate Pickup', 'value': 'liftgate_pickup'},
                {'label': 'Pack & palletize', 'value': 'pack_and_palletize_pickup'},
                {'label': 'Dock high needed for pickup', 'value': 'dock_high_pickup'},
                {'label': 'Mall Pickup ', 'value': 'mall_pickup'},
                {'label': 'Military Base Pickup', 'value': 'military_base_pickup'},
                {'label': 'Morning special pickup', 'value': 'morning_special_pickup'},
                {'label': 'Pallet Jack for pickup', 'value': 'pallet_jack_pickup'},
                {'label': 'Residental Pickup', 'value': 'residential_pickup'},
                {'label': 'School/University Pickup', 'value': 'school/university_pickup'},
                {'label': 'Other', 'value': 'Other'},
                ]
            ),
            dbc.Col([
                dbc.Input(id='pick-other-input', placeholder='If other is checked, enter scope here', disabled=True),
            ], md=10),
            #html.Div(id='q19-div'), #not needed, scope not required field
            html.Div(id='pick-scope-other-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("23.Please select ALL DELIVERY scope of work required:"),
            dbc.Checklist( id = 'drop-scope-check',
            options=[
                {'label': 'After or Before Hours Delivery', 'value': 'after_or_before_hours_delivery'},
                {'label': 'Afternoon Special Delivery', 'value': 'afternoon_special_delivery'},
                {'label': 'Delivery Appointment/Special', 'value': 'delivery_appointment/special'},
                {'label': 'Convention Center Delivery', 'value': 'convention_center_delivery'},
                {'label': 'Extra Man Delivery **will be calculated after service is performed', 'value': 'extra_man_delivery'},
                {'label': 'Hospital Delivery', 'value': 'hospital_delivery'},
                {'label': 'Hotel Delivery', 'value': 'hotel_delivery'},
                {'label': 'Inside Delivery **room of choice to the first floor only', 'value': 'inside_delivery'},
                {'label': 'Liftgate Delivery', 'value': 'liftgate_delivery'},
                {'label': 'Pack & palletize', 'value': 'pack_and_palletize_delivery'},
                {'label': 'Dock high needed for Delivery', 'value': 'dock_high_delivery'},
                {'label': 'Mall Delivery ', 'value': 'mall_delivery'},
                {'label': 'Military Base Delivery', 'value': 'military_base_delivery '},
                {'label': 'Morning special Delivery', 'value': 'morning_special_delivery'},
                {'label': 'Pallet Jack for Delivery', 'value': 'pallet_jack_delivery'},
                {'label': 'Residental Delivery', 'value': 'residential_delivery'},
                {'label': 'School/University Delivery', 'value': 'school/university_delivery'},
                {'label': 'Debris Removal 1 (Shrink wrap & skid removal only; up to two skids)', 'value': 'debris_removal_1'},
                {'label': 'Debris Removal 2 (Cardboard, shrink wrap and skid; up to two skids)', 'value': 'debris_removal_2'},
                {'label': 'Other', 'value': 'Other'},
                ]
            ),
            dbc.Col([
                dbc.Input(id='drop-other-input', placeholder='If other is checked, enter scope here', disabled=True),
            ], md=10),

            #html.Div(id='q20-div'), #not needed, scope not required field
            html.Div(id='drop-scope-other-ae-div'),

            html.Br(),
            html.Br(),

            dbc.Label("24.Please check this button if you need additional BDM support"),
            dbc.Col([
                dcc.Dropdown(
                        id = 'additional-support-drop',
                        placeholder = 'Yes/No',
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                    ),
            ], md=2),

            html.Div(id='additional-support-div'),

        ])


def first_final_service():
    return html.Div([
        dbc.Label("2.What type of service are they requesting?"),

        html.Div(id='garbage-div'),
        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Business Pickup or Delivery', id='store-pick-drop-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'60px'}),
                        href='/first_final_mile')
                ], md=2, align='stretch'),
        ]),
        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Residential Pickup or Delivery', id='res-pick-drop-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '200px', 'height':'60px'}),
                        href='/first_final_mile')
                ], md=2, align='stretch'),
        ]),
        dbc.Row([
                dbc.Col([
                    html.P('**Curbside, porch or garage ONLY**', style={'font-weight':'bold', 'color': 'red','font-size': '11px'}),
                ]),
        ]),
        
        html.Br(),

        
    ])


def local_pick_drop_service():
    return html.Div([
        dbc.Label("2.What type of service are they requesting?"),

        html.Div(id='garbage-div-pd'),

        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Residential Pickup/Residential Delivery', id='res-pick-res-drop-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '250px', 'height':'60px'}),
                        href='/local_pick_delivery')
                ], md=2, align='stretch'),
        ]),

        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Residential Pickup/Business Delivery', id='res-pick-bus-drop-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '250px', 'height':'60px'}),
                        href='/local_pick_delivery')
                ], md=2, align='stretch'),
        ]),

        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Business Pickup/Business Delivery', id='bus-pick-bus-drop-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '250px', 'height':'60px'}),
                        href='/local_pick_delivery')
                ], md=2, align='stretch'),
        ]),

        html.Br(),
        dbc.Row([
                dbc.Col([
                    dcc.Link(
                        dbc.Button('Business Pickup/Residential Delivery', id='bus-pick-res-drop-btn', color="secondary", n_clicks = 0, 
                            style = {'background-color':'#0078AE', 'color': 'white','border-width':'0px','font-size': '14px', 'width': '250px', 'height':'60px'}),
                        href='/local_pick_delivery')
                ], md=2, align='stretch'),
        ]),
        
        html.Br(),

        
    ])


def create_first_final():
    return html.Div([
        html.Div(id='garbage-output-0'),
        html.Div(id='garbage-div-1'),

        html.Br(),
        html.P(["* - Required field"]
                ,style={'font-weight':'bold'}),
        #html.Br(),
        
        dbc.Label("3.What is the customer's C-code*, your seven letter*, and all 7-letters/email groups to be included in communication regarding this quote?"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id='ccode-input', placeholder='Customer code'),
                ], md=2),
                dbc.Col([
                    dbc.Input(id='empcode-input', placeholder='Seven letter'),
                ], md=2),
            ]),

            html.Br(), 
            
            dbc.Row([
                dbc.Col([
                    dbc.Textarea(id='additional-input', placeholder='Additional seven letters/email groups'),
                ], md=4),
            ]),

        dcc.Loading(html.Div(id='ccode-div'), fullscreen = True, type = 'circle'),

        html.Br(),
        html.Br(),

        dbc.Label("4.Please enter the w-code or address for the pickup and/or delivery*"),
        html.P(["*Providing an address assists our carriers in providing accurate quotes based off of location. IE: malls, busy streets, parking lot sizes, etc.*"]
                ,style={'font-style':'italic', 'font-weight':'bold'}),
            dbc.RadioItems(inline=True,
                options=[
                    {"label": "Warehouse", "value": "warehouse"},
                    {"label": "Address", "value": "address"},
                ],
                id="warehouse-address-input",
        ),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='wcode-input', placeholder='Warehouse code', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='address-input', placeholder='Address', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='city-input', placeholder='City', disabled=True)
            ], md=2),
            dbc.Col([
                dcc.Dropdown(id='state-drop', placeholder='State', options=[{'label': state, 'value': state} for state in states], disabled=True),
            ], md=2),
            dbc.Col([
                dbc.Input(id='zip-input', placeholder='Zip code', disabled=True)
            ], md=2),
        ]),

        html.Div(id='warehouse-address-ffm-div'),
        html.Div(id='warehouse-ffm-div'),
        html.Div(id='address-ffm-div'),

        html.Br(),
        html.Br(),

        dbc.Label("5.Please enter the on-site contact information - name, phone number and email:"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='contact-name-input', placeholder='Name')
            ], md=2),
            dbc.Col([
                dbc.Input(id='contact-phone-input', placeholder='Phone (XXX) XXX-XXXX')
            ], md=2),
            dbc.Col([
                dbc.Input(id='contact-email', placeholder='Email')
            ], md=2),
        ]),

        html.Div(id='poc-ffm-div'),

        html.Br(),
        html.Br(),

        dbc.Label("6.Please select the time expectation for pickup/delivery*"),
        dbc.RadioItems(
            options=[
                {"label": "Same Day", "value": "same_day"},
                {"label": "Next Day", "value": "next_day"},
                {"label": "Sometime within the week", "value": "next_week"},
                {"label": "Customer specific date", "value": "customer_specific_date"},
            ],
            id="date-exp-input",
        ),

        dbc.Row([
            dbc.Col([
                dcc.DatePickerSingle(
                                id = 'date-exp-date',
                                min_date_allowed=date(1900,1,1),
                                max_date_allowed=date(2999,12,31),
                                initial_visible_month=date.today(),
                                clearable=True,
                                disabled = True,
                                #date = date(1900,1,1),
                            ),
            ], md=2),
            dbc.Col([
                    dbc.Input(id='customer-addtional-input', placeholder='Additional Information', disabled='True'),
            ], md=4),
        ]),

        html.Div(id='date-exp-ffm-div'),
        html.Div(id='cust-date-ffm-div'),

        html.Br(),
        html.Br(),

        dbc.Label("7.Is this quote only or freight on hand?*"),
            dbc.Col([
                    dcc.Dropdown(
                        id = 'quote-freight-drop',
                        placeholder = 'Quote/On Hand',
                        options=[
                            {'label': 'Quote Only', 'value': 'quote_only'},
                            {'label': 'Freight on Hand', 'value': 'freight_on_hand'},
                        ]
                        )
                ], md=2),
        html.Div(id='freight-div'),

        html.Br(),
        html.Br(),

        dbc.Label("8.Enter description of commodity*"),
        dbc.Col([
            dbc.Input(id='commodity-input', placeholder='Commodity description'),
        ], md=10),

        html.Div(
                html.P('***Cannot ship carbon black, cannot insure one-of-a-kind artwork***', 
                        style={'font-weight':'bold', 'color': 'gray', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            ),
        html.Div(id='commodity-div'),

        html.Br(),
        html.Br(),

        dbc.Label("9.Is freight palletized?*"),
        dbc.RadioItems(
            options=[
                {"label": "Yes", "value": True},
                {"label": "No", "value": False},
            ],
            id="palletized-radio",
        ),

        html.Div(id='freight-palletized-div'),

        dbc.Label("If no, how is the freight packaged?"),
        dbc.Col([
            dbc.Input(id='packaging-input', placeholder='Packaging Type', disabled = True),
        ], md=10),

        html.Div(id='packaging-div'),

        html.Br(),
        html.Br(),

        dbc.Label("10.Please select the amount of unique pallet/packaging type dimensions for pickup or delivery*"),
        dbc.Row([
                html.P(["*EX: if you have 2 packages that each weigh 30 pounds at 12x24x36 inches, 1 package that weighs 50 pounds at 18x12x36 inches", html.Br(),
                    "and 3 packages that weigh 50 pounds at 12x24x36 inches, you would slide the bar to 3 unique items. If all pieces have the same weight", html.Br(),
                    "and dimensions, do not slide the bar and simply enter the quantity under field 11.*"]
                    ,style={'font-style':'italic', 'font-weight':'bold'}),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Slider(1, 50, step=1, value=1, id='count-input', 
                            tooltip={"placement": "bottom", "always_visible": True}
                            )
            ], md=10),
        ]),
        html.Div(id='items-div'),

        html.Br(),
        html.Br(),

        dbc.Label("11.What are the unique quantites, weights and dimensions of the freight?*"),
        html.Div(id='input-prompt', children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            #dbc.Label('Item #',style={'font-weight':'bold', 'text-align': 'center'})
                        ], md=1),
                        dbc.Col([
                            dbc.Label('Quantity',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label(
                                    [
                                        parts[0],
                                        html.Span("per", style={'color': 'red'}),
                                        piece_parts[0],
                                        html.Span("Piece", style={'color': 'red'}),
                                        piece_parts[1]
                                    ],
                                    style={'font-weight': 'bold', 'text-align': 'center'}
                                )
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Length (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Width (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Height (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                    ]),
                ], md=11)
            ]),
        ]),
        dbc.Row([
            dbc.Col([
            html.Div(id='pieces-div', children=[]),
            ], md=11)
        ]),

        html.Div(id='output-prompt', children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            #dbc.Label('Item #',style={'font-weight':'bold', 'text-align': 'center'})
                        ], md=1),
                        dbc.Col([
                            dbc.Label('Quantity',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Weight per Piece (pounds)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Length (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Width (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Height (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                    ]),
                ], md=11)
            ]),
        ]),
            
        html.Div(id='container-output'),

        html.Br(),
        html.Br(),

        dbc.Label("12.Is the freight haz mat?*"),
        dbc.RadioItems(
            options=[
                {"label": "Yes", "value": True},
                {"label": "No", "value": False},
            ],
            id="hazmat-input",
        ),
        html.Div(id='shared-hazmat-div'),
        dbc.Label("If haz mat, please enter UN #, Class #, and Packing Group #"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='un-input', placeholder='UN #', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='class-input', placeholder='Class #', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='packing-input', placeholder='Packing Group#', disabled=True)
            ], md=2),
        ]),

        html.Div(id='shared-special-hazmat-div'),

        html.Br(),
        html.Br(),

        dbc.Label("13.Is additional insurance needed?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
            id="additional-insurance-radio",
        ),

        html.Div(id='additional-insurance-div'),
        html.Div(id='additional-insurance-div1'),

        dbc.Label("If yes, what is the total value of the load (USD)?"),
        dbc.Col([
            dbc.Input(id='value-input', placeholder='Value (USD)', disabled = True),
        ], md=10),

        html.Div(id='value-div'),

        html.Br(),
        html.Br(),

        dbc.Label("14.Please select ALL scope of work required:*"),
        dbc.Checklist( id = 'scope-check',
        options=[
            {'label': 'Two-Man Team', 'value': 'two_man_team'},
            {'label': 'Precall', 'value': 'precall'},
            {'label': 'Liftgate', 'value': 'liftgate'},
            {'label': 'Pallet Jack', 'value': 'pallet_jack'},
            {'label': 'Inside Pickup/Delivery', 'value': 'inside_pickup/delivery'},
            {'label': 'Unpack', 'value': 'Unpack'},
            {'label': 'Debris Removal', 'value': 'debris_removal'},
            {'label': 'Assembly/Disassembly', 'value': 'assembly/disassembly'},
            {'label': 'Appointment Required (1 hour)', 'value': 'appointment_required'},
            {'label': 'Repack/Palletize', 'value': 'repack/palletize'},
            {'label': 'Stairs', 'value': 'stairs'},
            {'label': 'Other', 'value': 'Other'},
            ]
        ),
        dbc.Col([
            dbc.Input(id='other-input', placeholder='If other is checked, enter scope here', disabled=True),
        ], md=10),
        html.Div(id='scope-ffm-div'),
        html.Div(id='other-scope-ffm-div'),

        html.Br(),
        html.Br(),

        dbc.Label("15.Is this a first-floor pickup/delivery?*"),
        dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id = 'first-floor-drop',
                        placeholder = 'Yes/No',
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                        )
                ], md=2),
            ]),

        html.Div(id='first-floor-ffm-div'),
        
        html.Br(),

        dbc.Label("If no, is there a freight elevator?*"),
        dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id = 'freight-elevator-drop',
                        placeholder = 'Yes/No',
                        disabled = True,
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                        )
                ], md=2),
        ]),

        #html.Div(id='freight-elevator-ffm-div'),

        html.Br(),
        html.Br(),

        dbc.Label("16.Please check this button if you need additional BDM support"),
        dbc.Col([
            dcc.Dropdown(
                        id = 'additional-support-drop',
                        placeholder = 'Yes/No',
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                    ),
        ], md=2),

        html.Div(id='additional-support-div'),

    ])


def create_local_pick_delivery():
     return html.Div([
        html.Div(id='garbage-output-0'),
        html.Div(id='garbage-div-3'),

        html.Br(),
        html.P(["* - Required field"]
                ,style={'font-weight':'bold'}),
        #html.Br(),
        
        dbc.Label("3.What is the customer's C-code*, your seven letter*, and all 7-letters/email groups to be included in communication regarding this quote?"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id='ccode-input', placeholder='Customer code'),
                ], md=2),
                dbc.Col([
                    dbc.Input(id='empcode-input', placeholder='Seven letter'),
                ], md=2),
            ]),

            html.Br(), 
            
            dbc.Row([
                dbc.Col([
                    dbc.Textarea(id='additional-input', placeholder='Additional seven letters/email groups'),
                ], md=4),
            ]),

        dcc.Loading(html.Div(id='ccode-div'), fullscreen = True, type = 'circle'),

        html.Br(),
        html.Br(),

        dbc.Label("4.Please enter the w-code or address for the pickup*"),
        html.P(["*Providing an address assists our carriers in providing accurate quotes based off of location. IE: malls, busy streets, parking lot sizes, etc.*"]
                ,style={'font-style':'italic', 'font-weight':'bold'}),
            dbc.RadioItems(inline=True,
                options=[
                    {"label": "Warehouse", "value": "warehouse"},
                    {"label": "Address", "value": "address"},
                ],
                id="pick-warehouse-address-input",
        ),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='pick-wcode-input', placeholder='Warehouse code', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='pick-address-input', placeholder='Address', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='pick-city-input', placeholder='City', disabled=True)
            ], md=2),
            dbc.Col([
                dcc.Dropdown(id='pick-state-drop', placeholder='State', options=[{'label': state, 'value': state} for state in states], disabled=True),
            ], md=2),
            dbc.Col([
                dbc.Input(id='pick-zip-input', placeholder='Zip code', disabled=True)
            ], md=2),
        ]),

        html.Div(id='pick-warehouse-address-pd-div'),
        html.Div(id='pick-warehouse-pd-div'),
        html.Div(id='pick-address-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("5.Please enter the pickup on-site contact information - name, phone number and email:"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='pick-contact-name-input', placeholder='Name')
            ], md=2),
            dbc.Col([
                dbc.Input(id='pick-contact-phone-input', placeholder='Phone (XXX) XXX-XXXX')
            ], md=2),
            dbc.Col([
                dbc.Input(id='pick-contact-email', placeholder='Email')
            ], md=2),
        ]),

        html.Div(id='pick-poc-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("6.Please select the time expectation for pickup*"),
        dbc.RadioItems(
            options=[
                {"label": "Same Day", "value": "same_day"},
                {"label": "Next Day", "value": "next_day"},
                {"label": "Sometime within the week", "value": "next_week"},
                {"label": "Customer specific date (time is optional)", "value": "customer_specific_date"},
            ],
            id="pick-date-exp-input",
        ),

        dbc.Row([
            dbc.Col([
                dcc.DatePickerSingle(
                                id = 'pick-date-exp-date',
                                min_date_allowed=date(1900,1,1),
                                max_date_allowed=date(2999,12,31),
                                initial_visible_month=date.today(),
                                clearable=True,
                                disabled = True,
                                #date = date(1900,1,1),
                            ),
            ], md=2),
            
            dbc.Col([
                    dcc.Dropdown(
                        id='pick-time-drop',
                        placeholder = 'Time',
                        options=[{'label': time, 'value': time} for time in times],
                        disabled = True
                        )
            ], md=2),

            dbc.Col([
                dcc.Dropdown(
                    id = 'pick-am-pm-drop',
                    placeholder = 'AM/PM',
                    options=[{'label': am_pm, 'value': am_pm} for am_pm in am_pms],
                    disabled = True
                    )
            ], md=2),

            dbc.Col([
                dcc.Dropdown(
                    id = 'pick-timezone-drop',
                    placeholder = 'Timezone',
                    options=[{'label': timezone, 'value': abbreviation} for timezone, abbreviation in timezones.items()],
                    disabled = True
                    )
            ], md=2),
        ]),

        html.Br(),

        dbc.Row([
          dbc.Col([
                    dbc.Input(id='pick-customer-addtional-input', placeholder='Additional Information', disabled='True'),
            ], md=4),
        ]),

        html.Div(id='pick-date-exp-pd-div'),
        html.Div(id='pick-cust-date-pd-div'),
        html.Div(id='pick-cust-date-time-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("7.Please enter the w-code or address for the delivery*"),
        html.P(["*Providing an address assists our carriers in providing accurate quotes based off of location. IE: malls, busy streets, parking lot sizes, etc.*"]
                ,style={'font-style':'italic', 'font-weight':'bold'}),
            dbc.RadioItems(inline=True,
                options=[
                    {"label": "Warehouse", "value": "warehouse"},
                    {"label": "Address", "value": "address"},
                ],
                id="drop-warehouse-address-input",
        ),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='drop-wcode-input', placeholder='Warehouse code', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='drop-address-input', placeholder='Address', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='drop-city-input', placeholder='City', disabled=True)
            ], md=2),
            dbc.Col([
                dcc.Dropdown(id='drop-state-drop', placeholder='State', options=[{'label': state, 'value': state} for state in states], disabled=True),
            ], md=2),
            dbc.Col([
                dbc.Input(id='drop-zip-input', placeholder='Zip code', disabled=True)
            ], md=2),
        ]),

        html.Div(id='drop-warehouse-address-pd-div'),
        html.Div(id='drop-warehouse-pd-div'),
        html.Div(id='drop-address-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("8.Please enter the delivery on-site contact information - name, phone number and email:"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='drop-contact-name-input', placeholder='Name')
            ], md=2),
            dbc.Col([
                dbc.Input(id='drop-contact-phone-input', placeholder='Phone (XXX) XXX-XXXX')
            ], md=2),
            dbc.Col([
                dbc.Input(id='drop-contact-email', placeholder='Email')
            ], md=2),
        ]),

        html.Div(id='drop-poc-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("9.Please select the time expectation for delivery*"),
        dbc.RadioItems(
            options=[
                {"label": "Same Day", "value": "same_day"},
                {"label": "Next Day", "value": "next_day"},
                {"label": "Sometime within the week", "value": "next_week"},
                {"label": "Customer specific date (time is optional)", "value": "customer_specific_date"},
            ],
            id="drop-date-exp-input",
        ),

        dbc.Row([
            dbc.Col([
                dcc.DatePickerSingle(
                                id = 'drop-date-exp-date',
                                min_date_allowed=date(1900,1,1),
                                max_date_allowed=date(2999,12,31),
                                initial_visible_month=date.today(),
                                clearable=True,
                                disabled = True,
                                #date = date(1900,1,1),
                            ),
            ], md=2),

            dbc.Col([
                    dcc.Dropdown(
                        id='drop-time-drop',
                        placeholder = 'Time',
                        options=[{'label': time, 'value': time} for time in times],
                        disabled = True
                        )
            ], md=2),

            dbc.Col([
                dcc.Dropdown(
                    id = 'drop-am-pm-drop',
                    placeholder = 'AM/PM',
                    options=[{'label': am_pm, 'value': am_pm} for am_pm in am_pms],
                    disabled = True
                    )
            ], md=2),

            dbc.Col([
                dcc.Dropdown(
                    id = 'drop-timezone-drop',
                    placeholder = 'Timezone',
                    options=[{'label': timezone, 'value': abbreviation} for timezone, abbreviation in timezones.items()],
                    disabled = True
                    )
            ], md=2),
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col([
                    dbc.Input(id='drop-customer-addtional-input', placeholder='Additional Information', disabled='True'),
            ], md=4),
        ]),

        html.Div(id='drop-date-exp-pd-div'),
        html.Div(id='drop-cust-date-pd-div'),
        html.Div(id='drop-cust-date-time-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("10.Is this quote only or freight on hand?*"),
            dbc.Col([
                    dcc.Dropdown(
                        id = 'quote-freight-drop',
                        placeholder = 'Quote/On Hand',
                        options=[
                            {'label': 'Quote Only', 'value': 'quote_only'},
                            {'label': 'Freight on Hand', 'value': 'freight_on_hand'},
                        ]
                        )
                ], md=2),
        html.Div(id='freight-div'),

        html.Br(),
        html.Br(),

        dbc.Label("11.Enter description of commodity*"),
        dbc.Col([
            dbc.Input(id='commodity-input', placeholder='Commodity description'),
        ], md=10),

        html.Div(
                html.P('***Cannot ship carbon black, cannot insure one-of-a-kind artwork***', 
                        style={'font-weight':'bold', 'color': 'gray', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            ),
        html.Div(id='commodity-div'),

        html.Br(),
        html.Br(),

        dbc.Label("12.Is freight palletized?*"),
        dbc.RadioItems(
            options=[
                {"label": "Yes", "value": True},
                {"label": "No", "value": False},
            ],
            id="palletized-radio",
        ),

        html.Div(id='freight-palletized-div'),

        dbc.Label("If no, how is the freight packaged?"),
        dbc.Col([
            dbc.Input(id='packaging-input', placeholder='Packaging Type', disabled = True),
        ], md=10),

        html.Div(id='packaging-div'),

        html.Br(),
        html.Br(),

        dbc.Label("13.Please select the amount of unique pallet/packaging type dimensions for pickup or delivery*"),
        dbc.Row([
                html.P(["*EX: if you have 2 packages that each weigh 30 pounds at 12x24x36 inches, 1 package that weighs 50 pounds at 18x12x36 inches", html.Br(),
                    "and 3 packages that weigh 50 pounds at 12x24x36 inches, you would slide the bar to 3 unique items. If all pieces have the same weight", html.Br(),
                    "and dimensions, do not slide the bar and simply enter the quantity under field 11.*"]
                    ,style={'font-style':'italic', 'font-weight':'bold'}),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Slider(1, 50, step=1, value=1, id='count-input', 
                            tooltip={"placement": "bottom", "always_visible": True}
                            )
            ], md=10),
        ]),
        html.Div(id='items-div'),

        html.Br(),
        html.Br(),

        dbc.Label("14.What are the unique quantites, weights and dimensions of the freight?*"),
        html.Div(id='input-prompt', children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            #dbc.Label('Item #',style={'font-weight':'bold', 'text-align': 'center'})
                        ], md=1),
                        dbc.Col([
                            dbc.Label('Quantity',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label(
                                    [
                                        parts[0],
                                        html.Span("per", style={'color': 'red'}),
                                        piece_parts[0],
                                        html.Span("Piece", style={'color': 'red'}),
                                        piece_parts[1]
                                    ],
                                    style={'font-weight': 'bold', 'text-align': 'center'}
                                )
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Length (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Width (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Height (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                    ]),
                ], md=11)
            ]),
        ]),
        dbc.Row([
            dbc.Col([
            html.Div(id='pieces-div', children=[]),
            ], md=11)
        ]),

        html.Div(id='output-prompt', children=[
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            #dbc.Label('Item #',style={'font-weight':'bold', 'text-align': 'center'})
                        ], md=1),
                        dbc.Col([
                            dbc.Label('Quantity',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Weight per Piece (pounds)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Length (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Width (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                        dbc.Col([
                            dbc.Label('Height (inches)',style={'font-weight':'bold', 'text-align': 'center'})
                        ],md= 2),
                    ]),
                ], md=11)
            ]),
        ]),
            
        html.Div(id='container-output'),

        html.Br(),
        html.Br(),

        dbc.Label("15.Is the freight haz mat?*"),
        dbc.RadioItems(
            options=[
                {"label": "Yes", "value": True},
                {"label": "No", "value": False},
            ],
            id="hazmat-input",
        ),
        html.Div(id='shared-hazmat-div'),
        dbc.Label("If haz mat, please enter UN #, Class #, and Packing Group #"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='un-input', placeholder='UN #', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='class-input', placeholder='Class #', disabled=True)
            ], md=2),
            dbc.Col([
                dbc.Input(id='packing-input', placeholder='Packing Group#', disabled=True)
            ], md=2),
        ]),

        html.Div(id='shared-special-hazmat-div'),

        html.Br(),
        html.Br(),

        dbc.Label("16.Is additional insurance needed?*"),
            dbc.RadioItems(
                options=[
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ],
            id="additional-insurance-radio",
        ),

        html.Div(id='additional-insurance-div'),
        html.Div(id='additional-insurance-div1'),

        dbc.Label("If yes, what is the total value of the load (USD)?"),
        dbc.Col([
            dbc.Input(id='value-input', placeholder='Value (USD)', disabled = True),
        ], md=10),

        html.Div(id='value-div'),

        html.Br(),
        html.Br(),

        dbc.Label("17.Please select ALL scope of work required for pickup:*"),
        dbc.Checklist( id = 'pd-pick-scope-check',
        options=[
            {'label': 'Two-Man Team', 'value': 'two_man_team'},
            {'label': 'Precall', 'value': 'precall'},
            {'label': 'Liftgate', 'value': 'liftgate'},
            {'label': 'Pallet Jack', 'value': 'pallet_jack'},
            {'label': 'Inside Pickup/Delivery', 'value': 'inside_pickup/delivery'},
            {'label': 'Unpack', 'value': 'Unpack'},
            {'label': 'Debris Removal', 'value': 'debris_removal'},
            {'label': 'Assembly/Disassembly', 'value': 'assembly/disassembly'},
            {'label': 'Appointment Required (1 hour)', 'value': 'appointment_required'},
            {'label': 'Repack/Palletize', 'value': 'repack/palletize'},
            {'label': 'Stairs', 'value': 'stairs'},
            {'label': 'Other', 'value': 'Other'},
            ]
        ),
        dbc.Col([
            dbc.Input(id='pd-pick-other-input', placeholder='If other is checked, enter scope here', disabled=True),
        ], md=10),
        html.Div(id='pick-scope-pd-div'),
        html.Div(id='pick-other-scope-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("18.Please select ALL scope of work required for delivery:*"),
        dbc.Checklist( id = 'pd-drop-scope-check',
        options=[
            {'label': 'Two-Man Team', 'value': 'two_man_team'},
            {'label': 'Precall', 'value': 'precall'},
            {'label': 'Liftgate', 'value': 'liftgate'},
            {'label': 'Pallet Jack', 'value': 'pallet_jack'},
            {'label': 'Inside Pickup/Delivery', 'value': 'inside_pickup/delivery'},
            {'label': 'Unpack', 'value': 'Unpack'},
            {'label': 'Debris Removal', 'value': 'debris_removal'},
            {'label': 'Assembly/Disassembly', 'value': 'assembly/disassembly'},
            {'label': 'Appointment Required (1 hour)', 'value': 'appointment_required'},
            {'label': 'Repack/Palletize', 'value': 'repack/palletize'},
            {'label': 'Stairs', 'value': 'stairs'},
            {'label': 'Other', 'value': 'Other'},
            ]
        ),
        dbc.Col([
            dbc.Input(id='pd-drop-other-input', placeholder='If other is checked, enter scope here', disabled=True),
        ], md=10),
        html.Div(id='drop-scope-pd-div'),
        html.Div(id='drop-other-scope-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("19.Is this a first-floor pickup?*"),
        dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id = 'pick-first-floor-drop',
                        placeholder = 'Yes/No',
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                        )
                ], md=2),
            ]),

        html.Div(id='pick-first-floor-pd-div'),
        
        html.Br(),

        dbc.Label("If no, is there a freight elevator?*"),
        dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id = 'pick-freight-elevator-drop',
                        placeholder = 'Yes/No',
                        disabled = True,
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                        )
                ], md=2),
        ]),

        html.Div(id='pick-freight-elevator-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("20.Is this a first-floor delivery?*"),
        dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id = 'drop-first-floor-drop',
                        placeholder = 'Yes/No',
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                        )
                ], md=2),
            ]),

        html.Div(id='drop-first-floor-pd-div'),
        
        html.Br(),

        dbc.Label("If no, is there a freight elevator?*"),
        dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id = 'drop-freight-elevator-drop',
                        placeholder = 'Yes/No',
                        disabled = True,
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                        )
                ], md=2),
        ]),

        html.Div(id='drop-freight-elevator-pd-div'),

        html.Br(),
        html.Br(),

        dbc.Label("21.Please check this button if you need additional BDM support"),
        dbc.Col([
            dcc.Dropdown(
                        id = 'additional-support-drop',
                        placeholder = 'Yes/No',
                        options=[
                            {'label': 'Yes', 'value': True},
                            {'label': 'No', 'value': False},
                        ]
                    ),
        ], md=2),

        html.Div(id='additional-support-div'),

    ])
     

def create_warehouseing():
    return html.Div([
        html.Br(),
        dbc.Label("3.Please enter your seven letter and we will reach out directly to better understand the requirements:"),
        dbc.Col([
            dbc.Input(id='empcode-input', placeholder='Seven letter')
        ], md=10),
        html.Div(id='empcode-warehousing-div'),
        
        html.Br(),

        html.Div(id='output-warehousing-div'),
    ])
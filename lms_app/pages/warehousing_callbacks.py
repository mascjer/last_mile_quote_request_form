#Libraries
import dash_bootstrap_components as dbc
import pandas as pd
import dash
from dash import Dash, dcc, html, dash_table, MATCH, ALL
from dash.dependencies import Input, Output, State
from flask import Flask
from datetime import date
from dash import dash_table as dt
import pages.ui_assets as ui
from dash.exceptions import PreventUpdate
from datetime import datetime
import re
import pytz

from database_functions import *
from pages.non_callback_functions import *
from pages.dataframe_builder import *
from pages.send_email import *


def add_warehousing_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON WAREHOUSING
    '''

    @dash.callback(
        Output("empcode-warehousing-div","children"),
        Input("submit-btn","n_clicks"),
        State("empcode-input", "value"),
        prevent_intial_call=True
    )
    def check_codes(n_clicks, empcode):
        if n_clicks > 0:
            empcode_exists = check_emp_codes(empcode)
            if empcode_exists == False:
                import_seven_letter(None)
                return html.P('Seven letter is invalid', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_seven_letter(empcode)
                return ''
        else:
            return ''


    @dash.callback(
        Output('output-warehousing-div', 'children'),
        Input("submit-btn","n_clicks"),
        State("empcode-input", "value"),
        prevent_intial_call=True
    )
    def submit_warehousing(n_clicks, empcode):
        prelim_df = send_request_df()
        valid_to_proceed = check_trans_mode_service(prelim_df)
        if valid_to_proceed == True:
            if n_clicks > 0:
                request_df = send_request_df()

                import_quote_date()

                new_quote_id = create_new_quote_id()

                request_df = request_df.assign(QUOTE_ID=new_quote_id)

                empcode_exists = check_emp_codes(empcode)

                if empcode_exists == False:
                    return html.P('Enter a valid seven letter', style={'font-weight':'bold', 'color': 'red'})
                else:
                    import_seven_letter(empcode)
                    write_to_lms_quote(request_df)
                    request_df = request_df.assign(SEVEN_LETTER=empcode)
                    send_warehousing_email(request_df)
                    return dcc.Location(pathname="/finished", id="finished-page")

            else:
                return ['']
        else:
            return dcc.Location(pathname="/", id="warehousing-redirect")
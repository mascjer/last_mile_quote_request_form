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
import numpy as np

from database_functions import *
from pages.non_callback_functions import *
from pages.dataframe_builder import *
from pages.send_email import *


def add_finished_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON THE FINISHED PAGE
    '''

    @dash.callback(
        Output("confirmation-div","children"),
        Input("confirmation-div","children")
    )
    def populate_tables(children):
        request_df_output = send_request_df()
        valid_to_proceed = check_trans_mode_service(request_df_output)

        if valid_to_proceed == True:
            nice_request_df = prettify_df(request_df_output)

            return [
                dt.DataTable(
                    data = nice_request_df.to_dict('records'),
                    style_header={'backgroundColor': "#0078AE",
                                'fontWeight': 'bold',
                                'color': 'white',
                                'textAlign': 'center',},  
                    style_cell={'textAlign': 'center',},               
                    ),
            ]
        return dcc.Location(pathname="/", id="finished-redirect")



    def prettify_df(df):
        df = df.drop(columns=['QUOTE_ID', 'QUOTE_DATE'])
        df = df.dropna(axis='columns')

        names_list = df.columns.values.tolist()
        names_array = np.array(names_list)
        values_list = df.loc[0, :].values.tolist()
        values_array = np.array(values_list)


        array = np.column_stack((names_array,values_array))

        df = pd.DataFrame(array, columns = ['Prompt','Entry'])
        df = df.applymap(lambda x: prettify_outputs(x))

        return df
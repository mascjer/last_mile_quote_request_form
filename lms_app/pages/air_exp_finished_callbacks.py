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


def add_air_exp_finished_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON THE FINISHED PAGE
    '''

    @dash.callback(
        Output("confirmation-div-1","children"),
        Input("data-storage-final-session","data")
    )
    def populate_ae_tables(final_data):
        good_modes = ['air_expedite','exclusive_use_vehicle']

        if final_data is not None:
            if final_data['TRANSPORTATION_MODE'] in good_modes:
                final_request_df = pd.DataFrame.from_dict([final_data])
                nice_request_df = prettify_df(final_request_df)              

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

            else:
                return dcc.Location(pathname="/", id="first-final-redirect")
        else:
            return dcc.Location(pathname="/", id="first-final-redirect")
        
    
    @dash.callback(
        Output("prompt-1","children"),
        Input("data-storage-final-session","data"),
        Input("data-storage-pick-scope-final","data"),
        Input("data-storage-drop-scope-final","data"),
        Input("data-storage-ae-item-final","data")
    )
    def populate_tables(final_data, final_pick_scope, final_drop_score, final_item):
        good_modes = ['air_expedite','exclusive_use_vehicle']

        if final_data is not None:
            if final_data['TRANSPORTATION_MODE'] in good_modes:
                data_to_database = pd.DataFrame.from_dict([final_data])
                pick_scope_to_database = pd.DataFrame.from_dict([final_pick_scope])
                drop_scope_to_database = pd.DataFrame.from_dict([final_drop_score])
                item_to_database = pd.DataFrame.from_dict(final_item)

                pick_scope_to_database = explode_scope_data(pick_scope_to_database)
                drop_scope_to_database = explode_scope_data(drop_scope_to_database)

                scope_to_database = pd.concat([pick_scope_to_database, drop_scope_to_database], ignore_index=True)

                quote_id = data_to_database['QUOTE_ID'][0]
                quote_date = data_to_database['QUOTE_DATE'][0]

                if quote_already_exists(quote_id, quote_date) == False:
                    write_to_lms_quote(data_to_database)
                    write_to_lms_quote_scope(scope_to_database)
                    write_to_lms_quote_items(item_to_database)
                    return ['']
                
                else:
                    return html.H4('Your qoute has already been submitted and stored.', 
                        style={'font-weight':'bold', 'text-align': 'center'})

            else:
                return dcc.Location(pathname="/", id="air-euv-redirect")
        else:
            return dcc.Location(pathname="/", id="air-euv-redirect")
    

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
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
        Input("data-storage-final","data")
    )
    def populate_tables(final_data):
        good_modes = ['first_mile','final_mile']
        good_services = ['store_pickup/delivery','residential_pickup/delivery']

        if final_data is not None:
            if final_data['TRANSPORTATION_MODE'] in good_modes and final_data['SERVICE'] in good_services:
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
        Output("prompt","children"),
        Input("data-storage-final","data"),
        Input("data-storage-scope-final","data"),
        Input("data-storage-item-final","data")
    )
    def populate_tables(final_data, final_scope, final_item):
        good_modes = ['first_mile','final_mile']
        good_services = ['store_pickup/delivery','residential_pickup/delivery']

        if final_data is not None:
            if final_data['TRANSPORTATION_MODE'] in good_modes and final_data['SERVICE'] in good_services:
                data_to_database = pd.DataFrame.from_dict([final_data])
                scope_to_database = pd.DataFrame.from_dict([final_scope])
                item_to_database = pd.DataFrame.from_dict(final_item)

                scope_to_database = explode_scope_data(scope_to_database)

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
                return dcc.Location(pathname="/", id="first-final-redirect")
        else:
            return dcc.Location(pathname="/", id="first-final-redirect")


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
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


def add_local_pick_delivery_finished_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON THE LOCAL PiCK AND DELIVERY FINISHED PAGE
    '''

    ### populates table with data on page
    @dash.callback(
        Output("confirmation-div-2","children"),
        Input("data-storage-final-session-pd","data")
    )
    def populate_ae_tables(final_data):
        good_modes = ['local_pick_and_delivery']
        good_services = ['residential_pickup_and_residential_delivery','residential_pickup_and_business_delivery',
                         'business_pickup_and_business_delivery', 'business_pickup_and_residential_delivery']

        if final_data is not None:
            if final_data['TRANSPORTATION_MODE'] in good_modes and final_data['SERVICE'] in good_services:
                final_request_df = pd.DataFrame.from_dict([final_data])
                final_request_df = fix_column_names(final_request_df)
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
                return dcc.Location(pathname="/", id="local-pd-final-redirect")
        else:
            return dcc.Location(pathname="/", id="local-pd-final-redirect")
        
    ### SENDS DATA TO DATABASE
    @dash.callback(
        Output("prompt-2","children"),
        Input("data-storage-final-session-pd","data"),
        Input("data-storage-pick-scope-final-pd","data"),
        Input("data-storage-drop-scope-final-pd","data"),
        Input("data-storage-item-final-pd","data")
    )
    def populate_tables(final_data, final_pick_scope, final_drop_score, final_item):
        good_modes = ['local_pick_and_delivery']
        good_services = ['residential_pickup_and_residential_delivery','residential_pickup_and_business_delivery',
                         'business_pickup_and_business_delivery', 'business_pickup_and_residential_delivery']

        if final_data is not None:
            if final_data['TRANSPORTATION_MODE'] in good_modes and final_data['SERVICE'] in good_services:
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
                return [] #dcc.Location(pathname="/", id="local-pd-final-redirect")
        else:
            return []#dcc.Location(pathname="/", id="local-pd-final-redirect")
        

    ### MAKES TABLE OUTPUT NICER
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
    

    #fixes the column names for output as the database has 
    #different column names than what the user would expect
    def fix_column_names(df):
        df = df.rename(columns = {
                                'SECOND_WAREHOUSE_CODE':'DELIVERY_WAREHOUSE_CODE',
                                'SECOND_WAREHOUSE_ADDRESS':'DELIVERY_WAREHOUSE_ADDRESS',
                                'SECOND_WAREHOUSE_CITY':'DELIVERY_WAREHOUSE_CITY',
                                'SECOND_WAREHOUSE_STATE':'DELIVERY_WAREHOUSE_STATE',
                                'SECOND_WAREHOUSE_ZIP':'DELIVERY_WAREHOUSE_ZIP',
                                'SECOND_CONTACT_NAME':'DELIVERY_CONTACT_NAME',
                                'SECOND_CONTACT_PHONE':'DELIVERY_CONTACT_PHONE',
                                'SECOND_CONTACT_EMAIL':'DELIVERY_CONTACT_EMAIL',
                                'SECOND_TIME_EXPECTATION':'DELIVERY_TIME_EXPECTATION',
                                'SECOND_TIME_EXPECTATION_TIME':'DELIVERY_TIME_EXPECTATION_TIME',
                                'SECOND_FIRST_FLOOR_PICKUP':'FIRST_FLOOR_DELIVERY',
                                'SECOND_HAS_FREIGHT_ELEVATOR':'DELIVERY_HAS_FREIGHT_ELEVATOR',
                                'WAREHOUSE_CODE':'PICKUP_WAREHOUSE_CODE',
                                'WAREHOUSE_ADDRESS':'PICKUP_WAREHOUSE_ADDRESS',
                                'WAREHOUSE_CITY':'PICKUP_WAREHOUSE_CITY',
                                'WAREHOUSE_STATE':'PICKUP_WAREHOUSE_STATE',
                                'WAREHOUSE_ZIP':'PICKUP_WAREHOUSE_ZIP',
                                'CONTACT_NAME':'PICKUP_CONTACT_NAME',
                                'CONTACT_PHONE':'PICKUP_CONTACT_PHONE',
                                'CONTACT_EMAIL':'PICKUP_CONTACT_EMAIL',
                                'TIME_EXPECTATION':'PICKUP_TIME_EXPECTATION',
                                'TIME_EXPECTATION_TIME':'PICKUP_TIME_EXPECTATION_TIME',
                                'HAS_FREIGHT_ELEVATOR':'PICKUP_HAS_FREIGHT_ELEVATOR',
        })

        return df
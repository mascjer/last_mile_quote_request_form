#Libraries
import dash_bootstrap_components as dbc
import pandas as pd
import dash
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
from flask import Flask
from datetime import date
from dash import dash_table as dt
import numpy as np
import pages.ui_assets as ui
import json
from dash.exceptions import PreventUpdate
from pages.non_callback_functions import *
from database_functions import *
from pages.dataframe_builder import *
from pages.send_email import *

#Used for debugging with pandas
'''
pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)
'''


def add_local_pick_delivery_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON THE LOCAL PICK AND DELIVERY QUOTE
    '''

    ### CHECKS IF PICK WAREHOUSE OR PICK ADDRESS IS CHOSEN
    @dash.callback(
        Output("pick-warehouse-address-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-warehouse-address-input", "value"),
    )
    def check_pick_address_warehouse_radio(n_clicks, warehouse_address):
        if n_clicks > 0:
            warehouse_address_exists = valid_input(warehouse_address)
            if warehouse_address_exists == False:
                return html.P('Select warehouse or address', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''

    ### CONTROLS DISABLED/ENABLED ENTRIES FOR PICK ADDRESS
    @dash.callback(
        Output("pick-wcode-input","disabled"),
        Output("pick-address-input","disabled"),
        Output("pick-city-input","disabled"),
        Output("pick-state-drop","disabled"),
        Output("pick-zip-input","disabled"),
        Output("pick-wcode-input","value"),
        Output("pick-address-input","value"),
        Output("pick-city-input","value"),
        Output("pick-state-drop","value"),
        Output("pick-zip-input","value"),
        Input("pick-warehouse-address-input","value"),
        Input("pick-wcode-input","value"),
        Input("pick-address-input","value"),
        Input("pick-city-input","value"),
        Input("pick-state-drop","value"),
        Input("pick-zip-input","value"),
        prevent_intial_call=True
    )
    def pick_address_entry(address_type, wcode, address, city, state, zip):
        if address_type == 'warehouse':
            return False, True, False,  False,  True, wcode, None, city, state, None
        elif address_type == 'address':
            return True, False, False,  False,  False, None, address, city, state, zip
        else:
            return True, True, True, True, True, None, None, None, None, None

    
    ### CHECKS IF PICK WCODE ENTERED IS VALID   
    @dash.callback(
        Output("pick-warehouse-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-warehouse-address-input", "value"),
        State("pick-wcode-input", "value"),
        State("pick-city-input","value"),
        State("pick-state-drop","value"),
    )
    def check_pick_wcode(n_clicks, radio_btn, wcode, city, state):
        str = 'Submit a valid: '
        if n_clicks > 0:
            if radio_btn == 'warehouse':
                wcode_exists = valid_input(wcode)
                city_exists = valid_input(city)
                state_exists = valid_input(state)

                false_list = []

                if city_exists == False:
                    false_list.append('City')

                if state_exists == False:
                    false_list.append('State')

                print('checking wcode')
                if wcode_exists == True:
                    wcode = wcode.upper()
                    valid_wcode = check_w_codes(wcode)
                    if valid_wcode == False:
                        false_list.append('Warehouse Code')
                        combined_str = ', '.join(false_list)
                        output_str = str+combined_str
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                    else:
                        return ''
                else:
                    false_list.append('Warehouse Code')
                    combined_str = ', '.join(false_list)
                    output_str = str+combined_str
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''
    

    ### CHECKS IF PICK ADDRESS IS ENTERED
    @dash.callback(
        Output("pick-address-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-warehouse-address-input", "value"),
        State("pick-address-input","value"),
        State("pick-city-input","value"),
        State("pick-state-drop","value"),
        State("pick-zip-input","value"),
    )
    def check_pick_address(n_clicks, radio_btn, address, city, state, zip):
        if n_clicks > 0:
            if radio_btn == 'address':
                address_exists = valid_input(address)
                city_exists = valid_input(city)
                state_exists = valid_input(state)
                zip_exists = check_zip_code(zip)

                false_list = []

                if address_exists == False:
                    false_list.append('Address')

                if city_exists == False:
                    false_list.append('City')

                if state_exists == False:
                    false_list.append('State')

                if zip_exists == False:
                    false_list.append('Zip Code (XXXXX or XXXXX-XXXX)')

                str = 'Submit a valid: '
                combined_str = ', '.join(false_list)
                output_str = str+combined_str

                if address_exists == False or city_exists == False or state_exists == False or zip_exists == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return '' 
            else:
                return ''
        else:
            return ''
        
    
    ### CHECKS IF PICK TIME EXP IS SELECTED
    @dash.callback(
        Output("pick-date-exp-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-date-exp-input", "value"),
    )
    def check_pick_date_exp_radio(n_clicks, date_exp):
        if n_clicks > 0:
            date_exp_exists = valid_input(date_exp)
            if date_exp_exists == False:
                return html.P('Select a time expectation', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''
        
    
    ### CHECKS IF CUSTOMER SPECIFIC DATE PICK IS SELECTED
    ### SO THEN IT CAN ENABLE THE FIELDS
    @dash.callback(
        Output("pick-date-exp-date","disabled"),
        Output("pick-date-exp-date","date"),
        Output("pick-customer-addtional-input","disabled"),
        Output("pick-customer-addtional-input","value"),
        Output("pick-time-drop","disabled"),
        Output("pick-time-drop","value"),
        Output("pick-am-pm-drop","disabled"),
        Output("pick-am-pm-drop","value"),
        Output("pick-timezone-drop","disabled"),
        Output("pick-timezone-drop","value"),
        Input("pick-date-exp-input","value"),
        Input("pick-date-exp-date","date"),
        Input("pick-customer-addtional-input","value"),
        Input("pick-time-drop","value"),
        Input("pick-am-pm-drop","value"),
        Input("pick-timezone-drop","value"),
        prevent_intial_call=True
    )
    def enable_disable_pick_specific_date(scope, date, additional_input, 
            time_drop, am_pm, timezone):
        if 'customer_specific_date' in scope:
            return False, date, False, additional_input, False, time_drop, False, am_pm, False, timezone
        else:
            return True, None, True, None, True, None, True, None, True, None
        
    
    ### CHECKS IF CUSTOMER SPECIFIC DATE PICK IS ENTERED WHEN SELECTED
    @dash.callback(
        Output("pick-cust-date-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-date-exp-input", "value"),
        State("pick-date-exp-date", "date"),
    )
    def check_pick_cust_specific_date_radio(n_clicks, date_exp, date):
        date_exp_list = ['next_week', 'next_day', 'same_day']
        if n_clicks > 0:
            date_exp_exists = valid_input(date_exp)
            if date_exp_exists == True and date_exp not in date_exp_list:
                date_exists = valid_input(date)
                if date_exists == False:
                    return html.P('Select a customer specific date', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            else:
                return ''
        else:
            return ''
        
    
    ### CHECKS IF PICK CONTACT INFO IS VALID
    @dash.callback(
        Output("pick-poc-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-contact-name-input", "value"),
        State("pick-contact-phone-input", "value"),
        State("pick-contact-email", "value"),
        prevent_intial_call=True
    )
    def check_codes(n_clicks, name, phone, email):
        if n_clicks > 0:
            phone_valid = check_phone_number(phone)
            name_exists = valid_input(name)
            email_valid = check_email_string(email)
            phone_exists = valid_input(phone)
            email_exists = valid_input(email)

            false_list = []

            if phone_exists == True:
                if phone_valid == False:
                    false_list.append('Contact Phone Number (XXX) XXX-XXXX')

            if email_exists == True:
                if email_valid == False:
                    false_list.append('Contact Email')

            str = 'These entries were invalid: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if phone_exists == True :
                if  phone_valid == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            elif email_exists == True:
                if  email_valid == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            else:
                return ''
        else:
            return ''
        
    
    ### CHECKS IF DROP WAREHOUSE OR DROP ADDRESS IS CHOSEN
    @dash.callback(
        Output("drop-warehouse-address-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-warehouse-address-input", "value"),
    )
    def check_pick_address_warehouse_radio(n_clicks, warehouse_address):
        if n_clicks > 0:
            warehouse_address_exists = valid_input(warehouse_address)
            if warehouse_address_exists == False:
                return html.P('Select warehouse or address', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''
        

    ### CONTROLS DISABLED/ENABLED ENTRIES FOR DROP ADDRESS
    @dash.callback(
        Output("drop-wcode-input","disabled"),
        Output("drop-address-input","disabled"),
        Output("drop-city-input","disabled"),
        Output("drop-state-drop","disabled"),
        Output("drop-zip-input","disabled"),
        Output("drop-wcode-input","value"),
        Output("drop-address-input","value"),
        Output("drop-city-input","value"),
        Output("drop-state-drop","value"),
        Output("drop-zip-input","value"),
        Input("drop-warehouse-address-input","value"),
        Input("drop-wcode-input","value"),
        Input("drop-address-input","value"),
        Input("drop-city-input","value"),
        Input("drop-state-drop","value"),
        Input("drop-zip-input","value"),
        prevent_intial_call=True
    )
    def drop_address_entry(address_type, wcode, address, city, state, zip):
        if address_type == 'warehouse':
            return False, True, False,  False,  True, wcode, None, city, state, None
        elif address_type == 'address':
            return True, False, False,  False,  False, None, address, city, state, zip
        else:
            return True, True, True, True, True, None, None, None, None, None
        

    ### CHECKS IF DROP WCODE ENTERED IS VALID   
    @dash.callback(
        Output("drop-warehouse-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-warehouse-address-input", "value"),
        State("drop-wcode-input", "value"),
        State("drop-city-input","value"),
        State("drop-state-drop","value"),
    )
    def check_drop_wcode(n_clicks, radio_btn, wcode, city, state):
        str = 'Submit a valid: '
        if n_clicks > 0:
            if radio_btn == 'warehouse':
                wcode_exists = valid_input(wcode)
                city_exists = valid_input(city)
                state_exists = valid_input(state)

                false_list = []

                if city_exists == False:
                    false_list.append('City')

                if state_exists == False:
                    false_list.append('State')

                print('checking wcode')
                if wcode_exists == True:
                    wcode = wcode.upper()
                    valid_wcode = check_w_codes(wcode)
                    if valid_wcode == False:
                        false_list.append('Warehouse Code')
                        combined_str = ', '.join(false_list)
                        output_str = str+combined_str
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                    else:
                        return ''
                else:
                    false_list.append('Warehouse Code')
                    combined_str = ', '.join(false_list)
                    output_str = str+combined_str
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''
        
    
    ### CHECKS IF DROP ADDRESS IS ENTERED
    @dash.callback(
        Output("drop-address-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-warehouse-address-input", "value"),
        State("drop-address-input","value"),
        State("drop-city-input","value"),
        State("drop-state-drop","value"),
        State("drop-zip-input","value"),
    )
    def check_drop_address(n_clicks, radio_btn, address, city, state, zip):
        if n_clicks > 0:
            if radio_btn == 'address':
                address_exists = valid_input(address)
                city_exists = valid_input(city)
                state_exists = valid_input(state)
                zip_exists = check_zip_code(zip)

                false_list = []

                if address_exists == False:
                    false_list.append('Address')

                if city_exists == False:
                    false_list.append('City')

                if state_exists == False:
                    false_list.append('State')

                if zip_exists == False:
                    false_list.append('Zip Code (XXXXX or XXXXX-XXXX)')

                str = 'Submit a valid: '
                combined_str = ', '.join(false_list)
                output_str = str+combined_str

                if address_exists == False or city_exists == False or state_exists == False or zip_exists == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return '' 
            else:
                return ''
        else:
            return ''
        

    ### CHECKS IF DROP TIME EXP IS SELECTED
    @dash.callback(
        Output("drop-date-exp-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-date-exp-input", "value"),
    )
    def check_drop_date_exp_radio(n_clicks, date_exp):
        if n_clicks > 0:
            date_exp_exists = valid_input(date_exp)
            if date_exp_exists == False:
                return html.P('Select a time expectation', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''
        
    
    ### CHECKS IF CUSTOMER SPECIFIC DATE DROP IS SELECTED
    ### SO THEN IT CAN ENABLE THE FIELDS
    @dash.callback(
        Output("drop-date-exp-date","disabled"),
        Output("drop-date-exp-date","date"),
        Output("drop-customer-addtional-input","disabled"),
        Output("drop-customer-addtional-input","value"),
        Output("drop-time-drop","disabled"),
        Output("drop-time-drop","value"),
        Output("drop-am-pm-drop","disabled"),
        Output("drop-am-pm-drop","value"),
        Output("drop-timezone-drop","disabled"),
        Output("drop-timezone-drop","value"),
        Input("drop-date-exp-input","value"),
        Input("drop-date-exp-date","date"),
        Input("drop-customer-addtional-input","value"),
        Input("drop-time-drop","value"),
        Input("drop-am-pm-drop","value"),
        Input("drop-timezone-drop","value"),
        prevent_intial_call=True
    )
    def enable_disable_drop_specific_date(scope, date, additional_input, 
            time_drop, am_pm, timezone):
        if 'customer_specific_date' in scope:
            return False, date, False, additional_input, False, time_drop, False, am_pm, False, timezone
        else:
            return True, None, True, None, True, None, True, None, True, None
        
    
    ### CHECKS IF CUSTOMER SPECIFIC DATE DROP IS ENTERED WHEN SELECTED
    @dash.callback(
        Output("drop-cust-date-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-date-exp-input", "value"),
        State("drop-date-exp-date", "date"),
    )
    def check_drop_cust_specific_date_radio(n_clicks, date_exp, date):
        date_exp_list = ['next_week', 'next_day', 'same_day']
        if n_clicks > 0:
            date_exp_exists = valid_input(date_exp)
            if date_exp_exists == True and date_exp not in date_exp_list:
                date_exists = valid_input(date)
                if date_exists == False:
                    return html.P('Select a customer specific date', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            else:
                return ''
        else:
            return ''


    #DISABLES/ENABLES OTHER PICK SCOPE
    @dash.callback(
        Output("pd-pick-other-input","disabled"),
        Output("pd-pick-other-input","value"),
        Input("pd-pick-scope-check","value"),
        prevent_intial_call=True
    )
    def other_pick_entry(scope):
        if 'Other' in scope or scope is None:
            return False, ''
        else:
            return True, None
        

    #DISABLES/ENABLES OTHER DOP SCOPE
    @dash.callback(
        Output("pd-drop-other-input","disabled"),
        Output("pd-drop-other-input","value"),
        Input("pd-drop-scope-check","value"),
        prevent_intial_call=True
    )
    def other_drop_entry(scope):
        if 'Other' in scope or scope is None:
            return False, ''
        else:
            return True, None
        
    
    #CHECKS PICK SCOPE TO SEE IF EMPTY
    @dash.callback(
        Output("pick-scope-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pd-pick-scope-check", "value"),
    )
    def check_pick_scope(n_clicks, scope):
        if n_clicks > 0:
            if not scope:
                return html.P('Select scope(s) of work', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''
        
    #CHECKS OTHER PICK SCOPE TO SEE IF EMPTY IF CHECKED
    @dash.callback(
        Output("pick-other-scope-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pd-pick-scope-check", "value"),
        State("pd-pick-other-input", "value"),
        State("pd-pick-other-input", "disabled"),
    )
    def check_pick_scope_other(n_clicks, scope, other, disabled):

        if n_clicks > 0:
        
            if scope is not None:
                if 'Other' in scope:
                    if disabled == False:
                        other_exists = valid_input(other)
                        if other_exists == False:
                            return html.P('Submit a valid other scope', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                        else:

                            return ''
                    else:
                        return ''
                else:
                    return ''
            else:
                return ''

        else:
            return ''
        

    #CHECKS DROP SCOPE TO SEE IF EMPTY
    @dash.callback(
        Output("drop-scope-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pd-drop-scope-check", "value"),
    )
    def check_drop_scope(n_clicks, scope):
        if n_clicks > 0:
            if not scope:
                return html.P('Select scope(s) of work', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''
        

    #CHECKS OTHER PICK SCOPE TO SEE IF EMPTY IF CHECKED
    @dash.callback(
        Output("drop-other-scope-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pd-drop-scope-check", "value"),
        State("pd-drop-other-input", "value"),
        State("pd-drop-other-input", "disabled"),
    )
    def check_drop_scope_other(n_clicks, scope, other, disabled):

        if n_clicks > 0:
        
            if scope is not None:
                if 'Other' in scope:
                    if disabled == False:
                        other_exists = valid_input(other)
                        if other_exists == False:
                            return html.P('Submit a valid other scope', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                        else:

                            return ''
                    else:
                        return ''
                else:
                    return ''
            else:
                return ''

        else:
            return ''
        

    #ENABLES FREIGHT ELEVATOR IF NOT FIRST FLOOR PICKUP
    @dash.callback(
        Output("pick-freight-elevator-drop","disabled"),
        Output("pick-freight-elevator-drop","value"),
        Input("pick-first-floor-drop","value"),
        Input("pick-freight-elevator-drop","value"),
        prevent_intial_call=True
    )
    def enable_disable_pick_freight_elevator(first_floor, freight_elevator):
        if first_floor == '':
            first_floor = None

        if first_floor == None:
            True, None
        else:
            if first_floor == False:
                return False, freight_elevator
            else:
                return True, None

    
    #CHECKS FIRST FLOOR PICKUP
    @dash.callback(
        Output("pick-first-floor-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-first-floor-drop", "value"),
    )
    def check_pick_first_floor_pick(n_clicks, first_floor):
        if n_clicks > 0:
            first_floor_exists = valid_input(first_floor)
            if first_floor_exists == False:
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''

    
    #CHECKS FREIGHT ELEVATOR IF NOT FIRST FLOOR PICK
    @dash.callback(
        Output("pick-freight-elevator-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-first-floor-drop", "value"),
        State("pick-freight-elevator-drop", "value"),
    )
    def check_pick_freight_elevator(n_clicks, first_floor, freight_elavator):
        if n_clicks > 0:
            if first_floor == False:
                freight_elavator_exists = valid_input(freight_elavator)
                if freight_elavator_exists == False:
                    return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            else:
                return ''
        else:
            return ''
        

    #ENABLES FREIGHT ELEVATOR IF NOT FIRST FLOOR DROP
    @dash.callback(
        Output("drop-freight-elevator-drop","disabled"),
        Output("drop-freight-elevator-drop","value"),
        Input("drop-first-floor-drop","value"),
        Input("drop-freight-elevator-drop","value"),
        prevent_intial_call=True
    )
    def enable_disable_drop_freight_elevator(first_floor, freight_elevator):
        if first_floor == '':
            first_floor = None

        if first_floor == None:
            True, None
        else:
            if first_floor == False:
                return False, freight_elevator
            else:
                return True, None

    
    #CHECKS FIRST FLOOR PICKUP
    @dash.callback(
        Output("drop-first-floor-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-first-floor-drop", "value"),
    )
    def check_drop_first_floor_pick(n_clicks, first_floor):
        if n_clicks > 0:
            first_floor_exists = valid_input(first_floor)
            if first_floor_exists == False:
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''

    
    #CHECKS FREIGHT ELEVATOR IF NOT FIRST FLOOR PICK
    @dash.callback(
        Output("drop-freight-elevator-pd-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-first-floor-drop", "value"),
        State("drop-freight-elevator-drop", "value"),
    )
    def check_drop_freight_elevator(n_clicks, first_floor, freight_elavator):
        if n_clicks > 0:
            if first_floor == False:
                freight_elavator_exists = valid_input(freight_elavator)
                if freight_elavator_exists == False:
                    return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            else:
                return ''
        else:
            return ''
    

    # inserts transmode and service into a new data storage
    @dash.callback(
        Output('garbage-div-pd', 'children'),
        Output('data-storage-2', 'data'),
        Output('res-pick-res-drop-btn','n_clicks'),
        Output('res-pick-bus-drop-btn','n_clicks'),
        Output('bus-pick-bus-drop-btn','n_clicks'),
        Output('bus-pick-res-drop-btn','n_clicks'),
        Input('res-pick-res-drop-btn','n_clicks'),
        Input('res-pick-bus-drop-btn','n_clicks'),
        Input('bus-pick-bus-drop-btn','n_clicks'),
        Input('bus-pick-res-drop-btn','n_clicks'),
        Input('data-storage', 'data')
    )
    def get_local_pick_del_service(res_pick_res_drop, res_pick_bus_drop, 
                                bus_pick_bus_drop, bus_pick_res_drop,
                                data_storage):

        clear_dataframe_after_service()

        if data_storage is not None:
        
            data_df = pd.read_json(data_storage, orient = 'split')

            service = np.NaN

            if res_pick_res_drop == 1 and res_pick_bus_drop+bus_pick_bus_drop+bus_pick_res_drop== 0:
                service = 'residential_pickup_and_residential_delivery'
            if res_pick_bus_drop == 1 and res_pick_res_drop+bus_pick_bus_drop+bus_pick_res_drop== 0:
                service = 'residential_pickup_and_business_delivery'
            if bus_pick_bus_drop == 1 and res_pick_res_drop+res_pick_bus_drop+bus_pick_res_drop== 0:
                service = 'business_pickup_and_business_delivery'
            if bus_pick_res_drop == 1 and res_pick_res_drop+res_pick_bus_drop+bus_pick_bus_drop== 0:
                service = 'business_pickup_and_residential_delivery'

            if service is None:
                print('not entered yet')
            if service == '':
                print('not entered yet')

            data_df['SERVICE'] = service

            return [],data_df.to_json(date_format='iso', orient='split'), 0,0,0,0
        
        else:
            return dcc.Location(pathname="/", id="first-final-redirect"),None, 0,0,0,0


    #checks if none or all time fields are in the pickup time exp
    @dash.callback(
        Output('pick-cust-date-time-pd-div', 'children'),
        Input("submit-btn","n_clicks"),
        State("pick-time-drop", "value"),
        State("pick-am-pm-drop", "value"),
        State("pick-timezone-drop", "value"),
    )
    def check_pick_times(n_clicks, time, am_pm, timezone):
        if n_clicks > 0:
            time_exists = valid_input(time)
            ap_pm_exists = valid_input(am_pm)
            timezone_exists = valid_input(timezone)

            if time_exists == True and ap_pm_exists == True and timezone_exists == True:
                return []
            elif time_exists == False and ap_pm_exists == False and timezone_exists == False:
                return []
            else:
                return html.P('All time related fields must be entered if specifying a time', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})


    #checks if none or all time fields are in the delivery time exp
    @dash.callback(
        Output('drop-cust-date-time-pd-div', 'children'),
        Input("submit-btn","n_clicks"),
        State("drop-time-drop", "value"),
        State("drop-am-pm-drop", "value"),
        State("drop-timezone-drop", "value"),
    )
    def check_pick_times(n_clicks, time, am_pm, timezone):
        if n_clicks > 0:
            time_exists = valid_input(time)
            ap_pm_exists = valid_input(am_pm)
            timezone_exists = valid_input(timezone)

            if time_exists == True and ap_pm_exists == True and timezone_exists == True:
                return []
            elif time_exists == False and ap_pm_exists == False and timezone_exists == False:
                return []
            else:
                return html.P('All time related fields must be entered if specifying a time', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})


    #gets all data from all fields and stores it in a temp data storage
    @dash.callback(
        Output('garbage-div-3', 'children'),
        Output("data-storage-pd-display","data"),
        Output("data-storage-pd-final","data"),
        Output("data-storage-pd-prelim-pick-scope","data"),
        Output("data-storage-pd-prelim-drop-scope","data"),
        Output('data-storage-pd-item', 'data'),
        Input('data-storage-2', 'data'),
        Input('data-storage-prelim-item', 'data'),
        State("ccode-input", "value"),
        State("empcode-input", "value"),
        State("additional-input", "value"),
        State("pick-warehouse-address-input", "value"),
        State("pick-wcode-input", "value"),
        State("pick-address-input", "value"),
        State("pick-city-input", "value"),
        State("pick-state-drop", "value"),
        State("pick-zip-input", "value"),
        State("pick-contact-name-input", "value"),
        State("pick-contact-phone-input", "value"),
        State("pick-contact-email", "value"),
        State("pick-date-exp-input", "value"),
        State("pick-date-exp-date", "date"),
        State("pick-time-drop", "value"),
        State("pick-am-pm-drop", "value"),
        State("pick-timezone-drop", "value"),
        State("pick-customer-addtional-input", "value"),
        State("drop-warehouse-address-input", "value"),
        State("drop-wcode-input", "value"),
        State("drop-address-input", "value"),
        State("drop-city-input", "value"),
        State("drop-state-drop", "value"),
        State("drop-zip-input", "value"),
        State("drop-contact-name-input", "value"),
        State("drop-contact-phone-input", "value"),
        State("drop-contact-email", "value"),
        State("drop-date-exp-input", "value"),
        State("drop-date-exp-date", "date"),
        State("drop-time-drop", "value"),
        State("drop-am-pm-drop", "value"),
        State("drop-timezone-drop", "value"),
        State("drop-customer-addtional-input", "value"),
        State("quote-freight-drop", "value"),
        State("commodity-input", "value"),
        State("palletized-radio", "value"),
        State("packaging-input", "value"),
        State("hazmat-input", "value"),
        State("un-input", "value"),
        State("class-input", "value"),
        State("packing-input", "value"),
        State("additional-insurance-radio", "value"),
        State("value-input", "value"),
        State("pd-pick-scope-check", "value"),
        State("pd-pick-other-input", "value"),
        State("pd-drop-scope-check", "value"),
        State("pd-drop-other-input", "value"),
        State("pick-first-floor-drop", "value"),
        State("pick-freight-elevator-drop", "value"),
        State("drop-first-floor-drop", "value"),
        State("drop-freight-elevator-drop", "value"),
        State("additional-support-drop", "value")
    )
    def store_data(data_storage, prelim_item_storage, #data storages
                    ccode, empcode, additional, pick_address_type, pick_wcode, 
                    pick_address, pick_city, pick_state, pick_zip, pick_contact_name,
                    pick_contact_phone, pick_contact_email, pick_date_exp, 
                    pick_date_exp_date, pick_date_exp_time, pick_date_exp_am_pm,
                    pick_date_exp_timezone, pick_additional_cust_info,
                    drop_address_type, drop_wcode, drop_address, drop_city, 
                    drop_state, drop_zip, drop_contact_name,
                    drop_contact_phone, drop_contact_email, drop_date_exp, 
                    drop_date_exp_date, drop_date_exp_time, drop_date_exp_am_pm,
                    drop_date_exp_timezone, drop_additional_cust_info,
                    quote_or_on_hand, commodity, palletized, packaging, 
                    hazmat, un, haz_class, packing, additional_insurance, 
                    value, pick_scope, pick_other, drop_scope, drop_other,
                    pick_first_floor, pick_freight_elevator, drop_first_floor, 
                    drop_freight_elevator, additional_support):
        
        good_modes = ['local_pick_and_delivery']
        good_services = ['residential_pickup_and_residential_delivery','residential_pickup_and_business_delivery',
                         'business_pickup_and_business_delivery', 'business_pickup_and_residential_delivery']
        
        quote_date = import_quote_date()

        if data_storage is not None:
            if pd.read_json(data_storage, orient = 'split')['TRANSPORTATION_MODE'].iloc[0] in good_modes and pd.read_json(data_storage, orient = 'split')['SERVICE'].iloc[0] in good_services:
                
                quote_id = create_quote_id(empcode, quote_date)
                prelim_item_storage['QUOTE_ID'] = quote_id

                key_order=['QUOTE_ID', 'QUANTITY', 'WEIGHT', 'LENGTH', 'WIDTH', 'HEIGHT']
                prelim_item_storage = {k : prelim_item_storage[k] for k in key_order}

                return [], {'QUOTE_ID': quote_id, 'TRANSPORTATION_MODE': pd.read_json(data_storage, orient = 'split')['TRANSPORTATION_MODE'].iloc[0],  
                            'SERVICE': pd.read_json(data_storage, orient = 'split')['SERVICE'].iloc[0],  
                            'CUSTOMER_CODE': ccode,'SEVEN_LETTER': empcode, 'QUOTE_OR_ON_HAND': quote_or_on_hand,
                            'ADDITIONAL_INSURANCE': additional_insurance, 'VALUE': get_value(additional_insurance, value), 'COMMODITY':commodity, 
                            'PACKAGING': get_packaging(palletized, packaging), 'IS_HAZ_MAT':hazmat, 'UN_NUMBER':un, 'CLASS_NUMBER':haz_class, 
                            'PACKING_GROUP_NUMBER':packing, 'ADDITIONAL_SUPPORT_NEEDED':get_additional_support(additional_support), 
                            'IS_PALLETIZED':palletized, 'FIRST_FLOOR_PICKUP':pick_first_floor,'PICKUP_HAS_FREIGHT_ELEVATOR':pick_freight_elevator,
                            'PICKUP_CONTACT_NAME':pick_contact_name, 'PICKUP_CONTACT_PHONE':pick_contact_phone, 'PICKUP_CONTACT_EMAIL':pick_contact_email,
                            'PICKUP_WAREHOUSE_CODE':pick_wcode, 'PICKUP_WAREHOUSE_ADDRESS':pick_address, 'PICKUP_WAREHOUSE_CITY':pick_city, 'PICKUP_WAREHOUSE_STATE':pick_state,
                            'PICKUP_WAREHOUSE_ZIP':pick_zip, 'PICKUP_TIME_EXPECTATION':get_date_exp(pick_date_exp, pick_date_exp_date), 'QUOTE_DATE':quote_date,
                            'PICKUP_TIME_EXPECTATION_TIME': get_time(pick_date_exp_date, pick_date_exp_time, pick_date_exp_am_pm, pick_date_exp_timezone), 
                            'DELIVERY_WAREHOUSE_CODE': drop_wcode, 'DELIVERY_WAREHOUSE_ADDRESS': drop_address,
                            'DELIVERY_WAREHOUSE_CITY': drop_city, 'DELIVERY_WAREHOUSE_STATE': drop_state, 'DELIVERY_WAREHOUSE_ZIP': drop_zip,
                            'DELIVERY_CONTACT_NAME': drop_contact_name, 'DELIVERY_CONTACT_PHONE': drop_contact_phone, 'DELIVERY_CONTACT_EMAIL': drop_contact_email,
                            'DELIVERY_TIME_EXPECTATION': get_date_exp(drop_date_exp, drop_date_exp_date), 
                            'DELIVERY_TIME_EXPECTATION_TIME': get_time(drop_date_exp_date, drop_date_exp_time, drop_date_exp_am_pm, drop_date_exp_timezone),
                            'FIRST_FLOOR_DELIVERY': drop_first_floor, 'DELIVERY_HAS_FREIGHT_ELEVATOR': drop_freight_elevator
                            }, {'QUOTE_ID': quote_id, 'TRANSPORTATION_MODE': pd.read_json(data_storage, orient = 'split')['TRANSPORTATION_MODE'].iloc[0],  
                            'SERVICE': pd.read_json(data_storage, orient = 'split')['SERVICE'].iloc[0],  
                            'CUSTOMER_CODE': ccode,'SEVEN_LETTER': empcode, 'QUOTE_OR_ON_HAND': quote_or_on_hand,
                            'ADDITIONAL_INSURANCE': additional_insurance, 'VALUE': get_value(additional_insurance, value), 'COMMODITY':commodity, 
                            'PACKAGING': get_packaging(palletized, packaging), 'IS_HAZ_MAT':hazmat, 'UN_NUMBER':un, 'CLASS_NUMBER':haz_class, 
                            'PACKING_GROUP_NUMBER':packing, 'ADDITIONAL_SUPPORT_NEEDED':get_additional_support(additional_support), 
                            'IS_PALLETIZED':palletized, 'FIRST_FLOOR_PICKUP':pick_first_floor,'HAS_FREIGHT_ELEVATOR':pick_freight_elevator,
                            'CONTACT_NAME':pick_contact_name, 'CONTACT_PHONE':pick_contact_phone, 'CONTACT_EMAIL':pick_contact_email,
                            'WAREHOUSE_CODE':pick_wcode, 'WAREHOUSE_ADDRESS':pick_address, 'WAREHOUSE_CITY':pick_city, 'WAREHOUSE_STATE':pick_state,
                            'WAREHOUSE_ZIP':pick_zip, 'TIME_EXPECTATION':get_date_exp(pick_date_exp, pick_date_exp_date), 'QUOTE_DATE':quote_date,
                            'TIME_EXPECTATION_TIME': None, 'SECOND_WAREHOUSE_CODE': drop_wcode, 'SECOND_WAREHOUSE_ADDRESS': drop_address,
                            'SECOND_WAREHOUSE_CITY': drop_city, 'SECOND_WAREHOUSE_STATE': drop_state, 'SECOND_WAREHOUSE_ZIP': drop_zip,
                            'SECOND_CONTACT_NAME': drop_contact_name, 'SECOND_CONTACT_PHONE': drop_contact_phone, 'SECOND_CONTACT_EMAIL': drop_contact_email,
                            'SECOND_TIME_EXPECTATION': get_date_exp(drop_date_exp, drop_date_exp_date), 'SECOND_TIME_EXPECTATION_TIME': None,
                            'SECOND_FIRST_FLOOR_PICKUP': drop_first_floor, 'SECOND_HAS_FREIGHT_ELEVATOR': drop_freight_elevator
                            }, {'QUOTE_ID': quote_id, 'STOP_TYPE': 'P', 
                                'SCOPE': parse_scopes(pick_scope, pick_other)}, {'QUOTE_ID': quote_id, 
                                                                                 'STOP_TYPE': 'D', 'SCOPE': parse_scopes(drop_scope, drop_other)}, prelim_item_storage
        

            else:
                dcc.Location(pathname="/", id="first-final-redirect"), None, None, None, None, None
        else:
            return dcc.Location(pathname="/", id="first-final-redirect"), None, None, None, None, None


    #stores data from temp storages in final storages ready for input
    #into database and email to business
    @dash.callback(
        Output("data-storage-final-session-pd", "data"),
        Output("data-storage-pick-scope-final-pd", "data"),
        Output("data-storage-drop-scope-final-pd", "data"),
        Output("data-storage-item-final-pd", "data"),
        Output("output_local_pick_delivery", "children"),
        Input("submit-btn","n_clicks"),
        Input('data-storage-pd-display', 'data'),
        Input('data-storage-pd-final', 'data'),
        Input("data-storage-pd-prelim-pick-scope","data"),
        Input("data-storage-pd-prelim-drop-scope","data"),
        Input('data-storage-pd-item', 'data'),
        State("pick-warehouse-address-input", "value"),
        State("additional-input", "value"),
        State("pick-customer-addtional-input", "value"),
        State("drop-customer-addtional-input", "value"),
        State("drop-warehouse-address-input", "value"),
        State("pick-date-exp-date", "date"),
        State("pick-time-drop", "value"),
        State("pick-am-pm-drop", "value"),
        State("pick-timezone-drop", "value"),
        State("drop-date-exp-date", "date"),
        State("drop-time-drop", "value"),
        State("drop-am-pm-drop", "value"),
        State("drop-timezone-drop", "value"),
    )
    def send_data(n_clicks, final_data_storage_display, final_data, pick_scope_storage, drop_scope_storage, item_storage,
                  pick_address_type, additional_contacts, pick_additional_cust_info, drop_additional_cust_info,
                  drop_address_type, pick_date, pick_time, pick_am_pm, pick_timezone, drop_date, drop_time, drop_am_pm, drop_timezone):
        if n_clicks > 0:
            print('----------data----------')
            print(final_data_storage_display)
            print(final_data)
            print(pick_scope_storage)
            print(drop_scope_storage)
            print(item_storage)
            print('after data n clicks:', n_clicks)
            print('------------------------')

            columns_to_drop = ['PICKUP_CONTACT_NAME', 'PICKUP_CONTACT_PHONE', 'PICKUP_CONTACT_EMAIL', 'DELIVERY_CONTACT_NAME', 
                               'DELIVERY_CONTACT_PHONE', 'DELIVERY_CONTACT_EMAIL', 'PICKUP_TIME_EXPECTATION_TIME', 
                               'DELIVERY_TIME_EXPECTATION_TIME'] #non-required fields
            missing_list = []

            if get_ccode(final_data_storage_display['CUSTOMER_CODE']) == None:
                missing_list.append(prettify_strings('CUSTOMER_CODE'))

            if get_empcode(final_data_storage_display['SEVEN_LETTER']) == None:
                missing_list.append(prettify_strings('SEVEN_LETTER'))

            if pick_address_type == None or pick_address_type == '':
                missing_list.append('Pickup Address Type')
                columns_to_drop.append('PICKUP_WAREHOUSE_ADDRESS')
                columns_to_drop.append('PICKUP_WAREHOUSE_ZIP')
                columns_to_drop.append('PICKUP_WAREHOUSE_CODE')
                columns_to_drop.append('PICKUP_WAREHOUSE_CITY')
                columns_to_drop.append('PICKUP_WAREHOUSE_STATE')

            if drop_address_type == None or pick_address_type == '':
                missing_list.append('Delivery Address Type')
                columns_to_drop.append('DELIVERY_WAREHOUSE_ADDRESS')
                columns_to_drop.append('DELIVERY_WAREHOUSE_ZIP')
                columns_to_drop.append('DELIVERY_WAREHOUSE_CODE')
                columns_to_drop.append('DELIVERY_WAREHOUSE_CITY')
                columns_to_drop.append('DELIVERY_WAREHOUSE_STATE')

            if final_data_storage_display['IS_HAZ_MAT'] == None or final_data_storage_display['IS_HAZ_MAT'] == '' or final_data_storage_display['IS_HAZ_MAT'] == False:
                columns_to_drop.append('UN_NUMBER')
                columns_to_drop.append('CLASS_NUMBER')
                columns_to_drop.append('PACKING_GROUP_NUMBER')

            if pick_address_type == 'warehouse':
                columns_to_drop.append('PICKUP_WAREHOUSE_ADDRESS')
                columns_to_drop.append('PICKUP_WAREHOUSE_ZIP')
                
                if get_wcode(final_data_storage_display['PICKUP_WAREHOUSE_CODE']) == None:
                    missing_list.append(prettify_strings('PICKUP_WAREHOUSE_CODE'))
            
            if drop_address_type == 'warehouse':
                columns_to_drop.append('DELIVERY_WAREHOUSE_ADDRESS')
                columns_to_drop.append('DELIVERY_WAREHOUSE_ZIP')
                
                if get_wcode(final_data_storage_display['DELIVERY_WAREHOUSE_CODE']) == None:
                    missing_list.append(prettify_strings('DELIVERY_WAREHOUSE_CODE'))

            if pick_address_type == 'address':
                columns_to_drop.append('PICKUP_WAREHOUSE_CODE')
            
            if drop_address_type == 'address':
                columns_to_drop.append('DELIVERY_WAREHOUSE_CODE')

            if final_data_storage_display['ADDITIONAL_INSURANCE'] == None or not final_data_storage_display['ADDITIONAL_INSURANCE'] or final_data_storage_display['ADDITIONAL_INSURANCE']== False:
                columns_to_drop.append('VALUE')

            if final_data_storage_display['FIRST_FLOOR_PICKUP'] == None or final_data_storage_display['FIRST_FLOOR_PICKUP'] or final_data_storage_display['FIRST_FLOOR_PICKUP'] == True:
                columns_to_drop.append('PICKUP_HAS_FREIGHT_ELEVATOR')

            if final_data_storage_display['FIRST_FLOOR_DELIVERY'] == None or final_data_storage_display['FIRST_FLOOR_DELIVERY'] or final_data_storage_display['FIRST_FLOOR_DELIVERY'] == True:
                columns_to_drop.append('DELIVERY_HAS_FREIGHT_ELEVATOR')

            for key, value in final_data_storage_display.items():
                if value is None and key not in columns_to_drop:
                    missing_list.append(prettify_strings(key))

            if check_for_invalids(item_storage) ==  True:
                missing_list.append('Items (Quantity, Dimensions)')

            if pick_scope_storage['SCOPE'] == None or not pick_scope_storage['SCOPE']:
                missing_list.append('Pickup Scope')

            if drop_scope_storage['SCOPE'] == None or not drop_scope_storage['SCOPE']:
                missing_list.append('Delivery Scope')

            pick_time_exists = valid_input(pick_time)
            pick_ap_pm_exists = valid_input(pick_am_pm)
            pick_timezone_exists = valid_input(pick_timezone)

            pick_time_list_num = [pick_time_exists, pick_ap_pm_exists, pick_timezone_exists].count(True)

            if 0 < pick_time_list_num < 3:
                missing_list.append('Pickup Time Elements')

            pick_local_time = None
            if pick_time_list_num >= 3:
                pick_local_time = get_local_time(pick_date, pick_time, pick_am_pm, pick_timezone)

            drop_time_exists = valid_input(drop_time)
            drop_ap_pm_exists = valid_input(drop_am_pm)
            drop_timezone_exists = valid_input(drop_timezone)

            drop_time_list_num = [drop_time_exists, drop_ap_pm_exists, drop_timezone_exists].count(True)

            if 0 < drop_time_list_num < 3:
                missing_list.append('Delivery Time Elements')

            drop_local_time = None
            if drop_time_list_num >= 3:
                drop_local_time = get_local_time(drop_date, drop_time, drop_am_pm, drop_timezone)

            #remove dups
            missing_list = list(set(missing_list))

            missing_str = ', '.join(str(e) for e in missing_list)
            missing_str = 'These entries are missing: ' + missing_str + '.'

            time.sleep(3)

            if len(missing_list) != 0:
                    return final_data, pick_scope_storage, drop_scope_storage, item_storage, html.P(missing_str, style={'font-weight':'bold', 'text-align': 'center', 'color': 'red'})
            
            else:
                send_pd_quote_email(final_data_storage_display, item_storage, pick_scope_storage, drop_scope_storage, 
                                    additional_contacts, pick_additional_cust_info, drop_additional_cust_info, pick_local_time, drop_local_time)
                return final_data, pick_scope_storage, drop_scope_storage, item_storage, dcc.Location(pathname="/local_pick_delivery_finished", id="finished-page")
        else:
            return None, None, None, None, []


    #used to put together all time related elements
    def get_time(date, time, am_pm, timezone):
        date_valid = valid_input(date)
        time_valid = valid_input(time)
        am_pm_valid = valid_input(am_pm)
        timezone_valid = valid_input(timezone)

        if date_valid == True and time_valid == True and am_pm_valid == True and timezone_valid == True:
            utc_time_string = create_date_strings(date, time, am_pm, timezone)
            return utc_time_string
        else:
            return None
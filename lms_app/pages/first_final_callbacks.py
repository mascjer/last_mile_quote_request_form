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


def add_first_final_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON THE FIRST/FINAL MILE QUOTE
    '''

    @dash.callback(
        Output('garbage-div', 'children'),
        Output('data-storage-1', 'data'),
        Output('store-pick-drop-btn','n_clicks'),
        Output('res-pick-drop-btn','n_clicks'),
        Input('store-pick-drop-btn','n_clicks'),
        Input('res-pick-drop-btn','n_clicks'),
        Input('data-storage', 'data')
    )
    def get_first_final_service(store, residential, data_storage):

        clear_dataframe_after_service()

        if data_storage is not None:
        
            data_df = pd.read_json(data_storage, orient = 'split')

            service = np.NaN

            if store == 1 and residential == 0:
                service = 'store_pickup/delivery'
            if residential == 1 and store == 0:
                service = 'residential_pickup/delivery'

            if service is None:
                print('not entered yet')
            if service == '':
                print('not entered yet')

            data_df['SERVICE'] = service

            return [],data_df.to_json(date_format='iso', orient='split'), 0,0
        
        else:
            return dcc.Location(pathname="/", id="first-final-redirect"),None, 0,0


    @dash.callback(
        Output("other-input","disabled"),
        Output("other-input","value"),
        Input("scope-check","value"),
        prevent_intial_call=True
    )
    def other_scope_entry(scope):
        if 'Other' in scope:
            return False, ''
        else:
            return True, None

    
    @dash.callback(
        Output("wcode-input","disabled"),
        Output("address-input","disabled"),
        Output("city-input","disabled"),
        Output("state-drop","disabled"),
        Output("zip-input","disabled"),
        Output("wcode-input","value"),
        Output("address-input","value"),
        Output("city-input","value"),
        Output("state-drop","value"),
        Output("zip-input","value"),
        Input("warehouse-address-input","value"),
        Input("wcode-input","value"),
        Input("address-input","value"),
        Input("city-input","value"),
        Input("state-drop","value"),
        Input("zip-input","value"),
        prevent_intial_call=True
    )
    def address_entry(address_type, wcode, address, city, state, zip):
        if address_type == 'warehouse':
            return False, True, False,  False,  True, wcode, None, city, state, None
        elif address_type == 'address':
            return True, False, False,  False,  False, None, address, city, state, zip
        else:
            return True, True, True, True, True, None, None, None, None, None
    
    
    @dash.callback(
    Output("date-exp-date","disabled"),
    Output("date-exp-date","date"),
    Output("customer-addtional-input","disabled"),
    Output("customer-addtional-input","value"),
    Input("date-exp-input","value"),
    Input("date-exp-date","date"),
    Input("customer-addtional-input","value"),
    prevent_intial_call=True
    )
    def enable_disable_specific_date(scope,date, additional_input):
        if 'customer_specific_date' in scope:
            return False, date, False, additional_input
        else:
            return True, None, True, None


    @dash.callback(
        Output("freight-elevator-drop","disabled"),
        Output("freight-elevator-drop","value"),
        Input("first-floor-drop","value"),
        Input("freight-elevator-drop","value"),
        prevent_intial_call=True
    )
    def enable_disable_freight_elevator(first_floor, freight_elevator):
        if first_floor == None:
            True, None
        else:
            if first_floor == False:
                return False, freight_elevator
            else:
                return True, None

    
    @dash.callback(
        Output("first-floor-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("first-floor-drop", "value"),
    )
    def check_first_floor_pick(n_clicks, first_floor):
        if n_clicks > 0:
            first_floor_exists = valid_input(first_floor)
            if first_floor_exists == False:
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("freight-elevator-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("first-floor-drop", "value"),
        State("freight-elevator-drop", "value"),
    )
    def check_freight_elevator(n_clicks, first_floor, freight_elavator):
        if n_clicks > 0:
            if first_floor == True:
                freight_elavator_exists = valid_input(freight_elavator)
                if freight_elavator_exists == False:
                    return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            else:
                return ''
        else:
            return ''

    
    @dash.callback(
        Output("scope-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("scope-check", "value"),
    )
    def check_scope(n_clicks, scope):
        if n_clicks > 0:
            if not scope:
                return html.P('Select scope(s) of work', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("other-scope-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("scope-check", "value"),
        State("other-input", "value"),
        State("other-input", "disabled"),
    )
    def check_scope_other(n_clicks, scope, other, disabled):

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


    @dash.callback(
        Output("poc-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("contact-name-input", "value"),
        State("contact-phone-input", "value"),
        State("contact-email", "value"),
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
                    import_phone(None)

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
    

    @dash.callback(
        Output("warehouse-address-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("warehouse-address-input", "value"),
    )
    def check_address_warehouse_radio(n_clicks, warehouse_address):
        if n_clicks > 0:
            warehouse_address_exists = valid_input(warehouse_address)
            if warehouse_address_exists == False:
                return html.P('Select warehouse or address', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("warehouse-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("warehouse-address-input", "value"),
        State("wcode-input", "value"),
        State("city-input","value"),
        State("state-drop","value"),
    )
    def check_wcode(n_clicks, radio_btn, wcode, city, state):
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


    @dash.callback(
        Output("address-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("warehouse-address-input", "value"),
        State("address-input","value"),
        State("city-input","value"),
        State("state-drop","value"),
        State("zip-input","value"),
    )
    def check_address(n_clicks, radio_btn, address, city, state, zip):
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


    @dash.callback(
        Output("date-exp-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("date-exp-input", "value"),
    )
    def check_date_exp_radio(n_clicks, date_exp):
        if n_clicks > 0:
            date_exp_exists = valid_input(date_exp)
            if date_exp_exists == False:
                return html.P('Select a time expectation', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''

    @dash.callback(
        Output("cust-date-ffm-div","children"),
        Input("submit-btn","n_clicks"),
        State("date-exp-input", "value"),
        State("date-exp-date", "date"),
    )
    def check_cust_specific_date_radio(n_clicks, date_exp, date):
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
    


    @dash.callback(
        Output('garbage-div-1', 'children'),
        Output("data-storage-ffm-display","data"),
        Output("data-storage-ffm-final","data"),
        Output("data-storage-ffm-prelim-scope","data"),
        Output('data-storage-item', 'data'),
        Input('data-storage-1', 'data'),
        Input('data-storage-prelim-item', 'data'),
        State("ccode-input", "value"),
        State("empcode-input", "value"),
        State("additional-input", "value"),
        State("warehouse-address-input", "value"),
        State("wcode-input", "value"),
        State("address-input", "value"),
        State("city-input", "value"),
        State("state-drop", "value"),
        State("zip-input", "value"),
        State("contact-name-input", "value"),
        State("contact-phone-input", "value"),
        State("contact-email", "value"),
        State("date-exp-input", "value"),
        State("date-exp-date", "date"),
        State("customer-addtional-input", "value"),
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
        State("scope-check", "value"),
        State("other-input", "value"),
        State("first-floor-drop", "value"),
        State("freight-elevator-drop", "value"),
        State("additional-support-drop", "value")
    )
    def store_data(data_storage, prelim_item_storage, ccode, empcode, additional, address_type, 
                            wcode, address, city, state, zip, contact_name, contact_phone, 
                            contact_email, date_exp, date_exp_date, additional_cust_info,
                            quote_or_on_hand, commodity, palletized, packaging, 
                            hazmat, un, haz_class, packing, additional_insurance, 
                            value, scope, other, first_floor, freight_elevator,
                            additional_support):

        good_modes = ['first_mile','final_mile']
        good_services = ['store_pickup/delivery','residential_pickup/delivery']

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
                            'IS_PALLETIZED':palletized, 'FIRST_FLOOR_PICKUP':first_floor,'HAS_FREIGHT_ELEVATOR':freight_elevator,
                            'CONTACT_NAME':contact_name, 'CONTACT_PHONE':contact_phone, 'CONTACT_EMAIL':contact_email,
                            'WAREHOUSE_CODE':wcode, 'WAREHOUSE_ADDRESS':address, 'WAREHOUSE_CITY':city, 'WAREHOUSE_STATE':state,
                            'WAREHOUSE_ZIP':zip, 'TIME_EXPECTATION':get_date_exp(date_exp, date_exp_date), 'QUOTE_DATE':quote_date
                            }, {'QUOTE_ID':quote_id, 'TRANSPORTATION_MODE': pd.read_json(data_storage, orient = 'split')['TRANSPORTATION_MODE'].iloc[0],  
                            'SERVICE': pd.read_json(data_storage, orient = 'split')['SERVICE'].iloc[0],  
                            'CUSTOMER_CODE': ccode,'SEVEN_LETTER': empcode, 'QUOTE_OR_ON_HAND': quote_or_on_hand,
                            'ADDITIONAL_INSURANCE': additional_insurance, 'VALUE': get_value(additional_insurance, value), 'COMMODITY':commodity, 
                            'PACKAGING': get_packaging(palletized, packaging), 'IS_HAZ_MAT':hazmat, 'UN_NUMBER':un, 'CLASS_NUMBER':haz_class, 
                            'PACKING_GROUP_NUMBER':packing, 'ADDITIONAL_SUPPORT_NEEDED':get_additional_support(additional_support), 
                            'LOAD_NUM':None,  'ORIGIN_CITY':None, 'ORIGIN_STATE':None, 'ORIGIN_ZIP':None, 
                            'REQUESTED_PICKUP_DATE':None, 'ORIGIN_OPEN_TIME':None,  'ORIGIN_CLOSE_TIME':None, 
                            'DESTINATION_CITY':None, 'DESTINATION_STATE':None, 'DESTINATION_ZIP':None, 
                            'REQUESTED_DELIVERY_DATE':None, 'DESTINATION_OPEN_TIME':None, 'DESTINATION_CLOSE_TIME':None, 
                            'IS_STACKABLE':None, 'CAUSE_LINE_DOWN':None, 'CAN_BREAKDOWN':None, 
                            'IS_PALLETIZED':palletized, 'FIRST_FLOOR_PICKUP':first_floor,'HAS_FREIGHT_ELEVATOR':freight_elevator,
                            'CONTACT_NAME':contact_name, 'CONTACT_PHONE':contact_phone, 'CONTACT_EMAIL':contact_email,
                            'WAREHOUSE_CODE':wcode, 'WAREHOUSE_ADDRESS':address, 'WAREHOUSE_CITY':city, 'WAREHOUSE_STATE':state,
                            'WAREHOUSE_ZIP':zip, 'TIME_EXPECTATION':get_date_exp(date_exp, date_exp_date), 'QUOTE_DATE':quote_date
                            }, {'QUOTE_ID': quote_id, 'STOP_TYPE': 'first_final', 'SCOPE': parse_scopes(scope, other)}, prelim_item_storage
            else:
                dcc.Location(pathname="/", id="first-final-redirect"),None, None, None, None
        else:
            return dcc.Location(pathname="/", id="first-final-redirect"),None, None, None, None



    @dash.callback(
        Output("data-storage-final", "data"),
        Output("data-storage-scope-final", "data"),
        Output("data-storage-item-final", "data"),
        Output("output_first_final", "children"),
        Input("submit-btn","n_clicks"),
        Input('data-storage-ffm-display', 'data'),
        Input('data-storage-ffm-final', 'data'),
        Input("data-storage-ffm-prelim-scope","data"),
        Input('data-storage-item', 'data'),
        State("warehouse-address-input", "value"),
        State("additional-input", "value"),
        State("customer-addtional-input", "value"),
    )
    def send_data(n_clicks, final_data_storage_display, final_data, scope_storage, item_storage, address_type, additional_contacts, additional_cust_info):
        if n_clicks > 0:

            print('----------data----------')
            print(final_data_storage_display)
            print(final_data)
            print(n_clicks)
            print('after data n clicks:', n_clicks)
            print('------------------------')

            columns_to_drop = ['CONTACT_NAME', 'CONTACT_PHONE', 'CONTACT_EMAIL'] #non-required fields
            missing_list = []

            if get_ccode(final_data_storage_display['CUSTOMER_CODE']) == None:
                missing_list.append(prettify_strings('CUSTOMER_CODE'))

            if get_empcode(final_data_storage_display['SEVEN_LETTER']) == None:
                missing_list.append(prettify_strings('SEVEN_LETTER'))


            if address_type == None or address_type == '':
                missing_list.append('Address Type')
                columns_to_drop.append('WAREHOUSE_ADDRESS')
                columns_to_drop.append('WAREHOUSE_ZIP')
                columns_to_drop.append('WAREHOUSE_CODE')
                columns_to_drop.append('WAREHOUSE_CITY')
                columns_to_drop.append('WAREHOUSE_STATE')

            if final_data_storage_display['IS_HAZ_MAT'] == None or final_data_storage_display['IS_HAZ_MAT'] == '' or final_data_storage_display['IS_HAZ_MAT'] == False:
                columns_to_drop.append('UN_NUMBER')
                columns_to_drop.append('CLASS_NUMBER')
                columns_to_drop.append('PACKING_GROUP_NUMBER')

            if address_type == 'warehouse':
                columns_to_drop.append('WAREHOUSE_ADDRESS')
                columns_to_drop.append('WAREHOUSE_ZIP')
                
                if get_wcode(final_data_storage_display['WAREHOUSE_CODE']) == None:
                    missing_list.append(prettify_strings('WAREHOUSE_CODE'))

            if address_type == 'address':
                columns_to_drop.append('WAREHOUSE_CODE')
            
            if final_data_storage_display['ADDITIONAL_INSURANCE'] == None or not final_data_storage_display['ADDITIONAL_INSURANCE'] or final_data_storage_display['ADDITIONAL_INSURANCE']== False:
                columns_to_drop.append('VALUE')

            if final_data_storage_display['FIRST_FLOOR_PICKUP'] == None or final_data_storage_display['FIRST_FLOOR_PICKUP'] or final_data_storage_display['FIRST_FLOOR_PICKUP'] == True:
                columns_to_drop.append('HAS_FREIGHT_ELEVATOR')

            for key, value in final_data_storage_display.items():
                if value is None and key not in columns_to_drop:
                    missing_list.append(prettify_strings(key))

            if check_for_invalids(item_storage) ==  True:
                missing_list.append('Items (Quantity, Dimensions)')

            if scope_storage['SCOPE'] == None or not scope_storage['SCOPE']:
                missing_list.append('Scope')

            #remove dups
            missing_list = list(set(missing_list))

            missing_str = ', '.join(str(e) for e in missing_list)
            missing_str = 'These entries are missing: ' + missing_str + '.'

            time.sleep(3)

            if len(missing_list) != 0:
                    return final_data, scope_storage, item_storage, html.P(missing_str, style={'font-weight':'bold', 'text-align': 'center', 'color': 'red'})
            else:
                send_quote_email(final_data_storage_display, item_storage, scope_storage, additional_contacts, additional_cust_info)
                return final_data, scope_storage, item_storage, dcc.Location(pathname="/finished", id="finished-page")
        
        else:
            return None, None, None, []
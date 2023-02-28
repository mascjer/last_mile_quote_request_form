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
        #Output('local-pick-drop-btn','n_clicks'),
        Output('store-pick-drop-btn','n_clicks'),
        Output('res-pick-drop-btn','n_clicks'),
        #Output('warehousing-btn','n_clicks'),
        #Input('local-pick-drop-btn','n_clicks'),
        Input('store-pick-drop-btn','n_clicks'),
        Input('res-pick-drop-btn','n_clicks'),
        #Input('warehousing-btn','n_clicks'),
    )
    def get_first_final_service(store, residential):

        clear_dataframe_after_service()
        
        service = np.NaN

        if store == 1 and residential == 0:
            service = 'store_pickup/delivery'
        if residential == 1 and store == 0:
            service = 'residential_pickup/delivery'

        if service is None:
            print('not entered yet')
        if service == '':
            print('not entered yet')
        else:
            import_service(service)
        
        return 0,0

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
                import_first_floor_pick(None)
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_first_floor_pick(first_floor)
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
                    import_has_freight_elevator(None)
                    return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    import_has_freight_elevator(freight_elavator)
                    return ''
            else:
                import_has_freight_elevator(None)
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
                import_stop_type(None)
                return html.P('Select scope(s) of work', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_stop_type('FIRSTFINAL')
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
                            import_other_scope(None)
                            return html.P('Submit a valid other scope', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                        else:
                            import_other_scope(other_exists)
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

            if name_exists == False:
                import_name(None)
            else:
                import_name(name)

            if phone_exists == True:
                if phone_valid == False:
                    false_list.append('Contact Phone Number (XXX) XXX-XXXX')
                    import_phone(None)
                else:
                    import_phone(phone)
            else:
                import_phone(None)

            if email_exists == True:
                if email_valid == False:
                    false_list.append('Contact Email')
                    import_contact_email(None)
                else:
                    import_contact_email(email) 
            else:
                import_contact_email(None)

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
                    import_city(None)
                else:
                    import_city(city)

                if state_exists == False:
                    false_list.append('State')
                    import_state(None)
                else:
                    import_state(state)


                if wcode_exists == True:
                    wcode = wcode.upper()
                    valid_wcode = check_w_codes(wcode)
                    if valid_wcode == False:
                        false_list.append('Warehouse Code')
                        import_wcode(None)
                        combined_str = ', '.join(false_list)
                        output_str = str+combined_str
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                    else:
                        import_wcode(wcode)
                        return ''
                else:
                    false_list.append('Warehouse Code')
                    import_wcode(None)
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
                    import_address(None)
                else:
                    import_address(address)

                if city_exists == False:
                    false_list.append('City')
                    import_city(None)
                else:
                    import_city(city)

                if state_exists == False:
                    false_list.append('State')
                    import_state(None)
                else:
                    import_state(state)

                if zip_exists == False:
                    false_list.append('Zip Code (XXXXX or XXXXX-XXXX)')
                    import_zip(None)
                else:
                    import_zip(zip)

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
                import_time_exp(None)
                return html.P('Select a time expectation', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                if import_time_exp != 'customer_specific_date':
                    return import_time_exp(date_exp)
                else:
                    return import_time_exp(None)
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
                    import_time_exp(date)
                    return ''
            else:
                return ''
        else:
            return ''
    

    @dash.callback(
        Output("output_first_final", "children"),
        Input("submit-btn","n_clicks"),
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
        State("additional-support-checklist", "value"),
        prevent_intial_call=True
    )
    def get_final_small_form(n_clicks, ccode, empcode, additional, address_type, 
                            wcode, address, city, state, zip, contact_name, contact_phone, 
                            contact_email, date_exp, date_exp_date, additional_cust_info,
                            quote_or_on_hand, commodity, palletized, packaging, 
                            hazmat, un, haz_class, packing, additional_insurance, 
                            value, scope, other, first_floor, freight_elevator,
                            additional_support):

        prelim_df = send_request_df()
        valid_to_proceed = check_trans_mode_service(prelim_df)

        if valid_to_proceed == True:
            if n_clicks > 0:
                if additional_support is not None:
                    additional_support = additional_support[0]
                small_form_cols = ['Transportation Mode', 'Service', 'Customer Code', 
                                    'Seven Letter', 'Additional Groups', 'Address Type', 
                                    'Warehouse Code', 'Address',  'City', 'State', 'Zip', 
                                    'Contact Name', 'Contact Phone #', 'Contact Email', 
                                    'Time Expectation', 'Specific Time Expectation', 
                                    'Additional Information', 'Quote Only or Freight on Hand', 
                                    'Commodity', 'Palletized Freight', 'Packaging',
                                    'Haz Mat', 'UN #', 'Class #', 'Packing Group #', 
                                    'Additional Insurance', 'Value', 'Scope',
                                    'First-Floor Pickup', 'Freight Elevator', 
                                    'Additional Support Needed', 'Items (Quantity, Dimensions)']

                scope_list = parse_scopes(scope, other)
                import_scopes(scope_list)

                item_df = send_item_df()
                scope_df = explode_scope_data(send_scope_df())
                request_df = wait_for_codes(send_request_df(), ccode, empcode)

                request_df.WAREHOUSE_CODE = wcode

                invalids = check_for_invalids(item_df)

                trans_mode = request_df['TRANSPORTATION_MODE'][0]
                service = request_df['SERVICE'][0]

                if invalids == True:
                    items = None
                else:
                    items = 'Full'

                small_form_data = [trans_mode, service, ccode, empcode, additional, address_type, 
                                    wcode, address, city, state, zip, contact_name, contact_phone, 
                                    contact_email, date_exp, date_exp_date, additional_cust_info,
                                    quote_or_on_hand, commodity, palletized, packaging, 
                                    hazmat, un, haz_class, packing, additional_insurance, 
                                    value, scope, first_floor, freight_elevator, additional_support,
                                    items]


                small_form_display = pd.DataFrame([small_form_data], columns=small_form_cols)

                missing_list = []

                if small_form_display['Haz Mat'].iloc[0] == None or not small_form_display['Haz Mat'].iloc[0] or small_form_display['Haz Mat'].iloc[0] == False:
                    small_form_display = small_form_display.drop(columns=['UN #', 'Class #', 'Packing Group #'])

                if small_form_display['Time Expectation'].iloc[0] == 'next_week' or small_form_display['Time Expectation'].iloc[0] == 'next_day' or small_form_display['Time Expectation'].iloc[0] == 'same_day':
                    small_form_display = small_form_display.drop(columns=['Specific Time Expectation'])

                if small_form_display['Address Type'].iloc[0] == 'warehouse':
                    small_form_display = small_form_display.drop(columns=['Address', 'Zip'])

                if small_form_display['Address Type'].iloc[0] == 'address':
                    small_form_display = small_form_display.drop(columns=['Warehouse Code'])

                if small_form_display['Additional Insurance'].iloc[0] == None or not small_form_display['Additional Insurance'].iloc[0] or small_form_display['Additional Insurance'].iloc[0] == False:
                    small_form_display = small_form_display.drop(columns=['Value'])

                if small_form_display['First-Floor Pickup'].iloc[0] == None or not small_form_display['First-Floor Pickup'].iloc[0] or small_form_display['First-Floor Pickup'].iloc[0] == True:
                    small_form_display = small_form_display.drop(columns=['Freight Elevator'])

                if small_form_display['Palletized Freight'].iloc[0] == None or small_form_display['Palletized Freight'].iloc[0] == True:
                    small_form_display = small_form_display.drop(columns=['Packaging'])

                columns_to_drop = ['Additional Groups', 'Contact Name', 'Contact Phone #', 'Contact Email',
                                'Additional Information', 'Additional Support Needed'] #non-required fields

                for (columnName, columnData) in small_form_display.iteritems():
                    if columnData.values[0] == None or not columnData.values[0]:
                        if columnData.values[0] == False:
                            print('sorry if you see this, its bad coding but I needed a placeholder for this specific instance')
                        elif columnName in columns_to_drop:
                            print('sorry if you see this, its bad coding but I needed a placeholder for this specific instance')
                        else:
                            missing_list.append(columnName)

                missing_str = ', '.join(str(e) for e in missing_list)
                missing_str = 'These entries are missing: ' + missing_str + '.'

                import_quote_date()
                new_quote_id = create_new_quote_id()
                request_df = request_df.assign(QUOTE_ID=new_quote_id)
                scope_df = scope_df.assign(QUOTE_ID=new_quote_id)
                item_df = item_df.assign(QUOTE_ID=new_quote_id)

                item_df_total_weight = item_df[['QUANTITY', 'WEIGHT']]
                item_df_total_weight['QUANTITY'] = item_df_total_weight['QUANTITY'].astype('float64') 
                item_df_total_weight['WEIGHT'] = item_df_total_weight['WEIGHT'].astype('float64') 
                item_df_total_weight['ROW_WEIGHT'] = item_df_total_weight['QUANTITY'] * item_df_total_weight['WEIGHT']
                total_weight = item_df_total_weight['ROW_WEIGHT'].sum()

                small_form_display['Total Weight'] = total_weight

                if len(missing_list) != 0:
                    n_clicks = 0
                    return html.P(missing_str, style={'font-weight':'bold', 'text-align': 'center', 'color': 'red'})
                else:
                    dcc.Loading(children = [html.Div(id='prompt')], fullscreen = True)
                    write_to_lms_quote(request_df)
                    write_to_lms_quote_scope(scope_df)
                    write_to_lms_quote_items(item_df)
                    send_quote_email(small_form_display, item_df, scope_df, city = small_form_display['City'][0], 
                                    state = small_form_display['State'][0])
                    return dcc.Location(pathname="/finished", id="finished-page"), ''
            else:
                return '', ''
        else:
            return dcc.Location(pathname="/", id="first-final-redirect"), ''




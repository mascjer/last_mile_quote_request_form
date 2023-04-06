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


#Used for debugging with pandas
pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)


def add_air_euv_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON AIR EXP/EUV
    '''

    @dash.callback(
    Output("pick-other-input","disabled"),
    Output("pick-other-input","value"),
    Input("pick-scope-check","value"),
    prevent_intial_call=True
    )
    def other_pick_entry(scope):
        if 'Other' in scope or scope is None:
            return False, ''
        else:
            return True, None


    @dash.callback(
        Output("load-num-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("load-num-input", "value"),
    )
    def check_load_num(n_clicks, load_num):
        if n_clicks > 0:
            load_num_exists = valid_input(load_num)
            if load_num_exists == False:
                return '' #html.P('Submit a load number', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("drop-other-input","disabled"),
        Output("drop-other-input","value"),
        Input("drop-scope-check","value"),
        prevent_intial_call=True
    )
    def other_drop_entry(scope):
        if 'Other' in scope or scope is None:
            return False, ''
        else:
            return True, None


    @dash.callback(
        Output("origin-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("o-city-input", "value"),
        State("o-zip-input", "value"),
        State("o-state-drop", "value"),
        prevent_intial_call=True
    )
    def check_origin(n_clicks, o_city, o_zip, o_state):
        if n_clicks > 0:
            zip_valid = check_zip_code(o_zip)
            city_exists = valid_input(o_city)
            state_exists = valid_input(o_state)

            false_list = []

            if city_exists == False:
                false_list.append('City')

            if state_exists == False:
                false_list.append('State')

            if zip_valid == False:
                false_list.append('Zip Code (#####, #####-##### or A#A#A# for CAN)')

            str = 'Submit a valid: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if city_exists == False or state_exists == False or zip_valid == False:
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("request-pick-date-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("req-pick-date", "date"),
        prevent_intial_call=True
    )
    def check_request_pick_date(n_clicks, date):
        if n_clicks > 0:
            output_str = 'Requested pickup date cannot be empty'
            if date is None:
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            elif date == '':
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''

    
    @dash.callback(
        Output("origin-open-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-open-time-drop", "value"),
        State("pick-open-am-pm-drop", "value"),
        State("pick-open-timezone-drop", "value"),
        prevent_intial_call=True
    )
    def check_origin_open_time(n_clicks, time, am_pm, tz):
        if n_clicks > 0:
            time_exists = valid_input(time)
            am_pm_exists = valid_input(am_pm)
            tz_exists = valid_input(tz)

            false_list = create_time_false_list(time_exists, am_pm_exists, tz_exists)

            str = 'Open time is missing: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if time_exists == False or am_pm_exists == False or tz_exists == False:
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("origin-close-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-close-time-drop", "value"),
        State("pick-close-am-pm-drop", "value"),
        State("pick-close-timezone-drop", "value"),
        prevent_intial_call=True
    )
    def check_origin_close_time(n_clicks, time, am_pm, tz):
        if n_clicks > 0:
            time_exists = valid_input(time)
            am_pm_exists = valid_input(am_pm)
            tz_exists = valid_input(tz)

            false_list = create_time_false_list(time_exists, am_pm_exists, tz_exists)

            str = 'Close time is missing: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if time_exists == False or am_pm_exists == False or tz_exists == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("origin-close-warning-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("req-pick-date", "date"),
        State("pick-open-time-drop", "value"),
        State("pick-open-am-pm-drop", "value"),
        State("pick-open-timezone-drop", "value"),
        State("pick-close-time-drop", "value"),
        State("pick-close-am-pm-drop", "value"),
        State("pick-close-timezone-drop", "value"),
        prevent_intial_call=True
    )
    def check_origin_pen_close_time_difference(n_clicks, date, open_time, open_am_pm, open_tz, close_time, close_am_pm, close_tz):
        output_str = 'Close time must be later than open time'
        if n_clicks > 0:
            if date is None:
                return ''
            elif date == '':
                return ''
            else:
                open_time_exists = valid_input(open_time)
                open_am_pm_exists = valid_input(open_am_pm)
                open_tz_exists = valid_input(open_tz)
                close_time_exists = valid_input(close_time)
                close_am_pm_exists = valid_input(close_am_pm)
                close_tz_exists = valid_input(close_tz)

                if open_time_exists == False or open_am_pm_exists == False or open_tz_exists == False or close_time_exists == False or close_am_pm_exists == False or close_tz_exists == False:
                    return ''
                else:
                    utc_open_str_obj = create_date_strings(date, open_time, open_am_pm, open_tz)
                    utc_close_str_obj = create_date_strings(date, close_time, close_am_pm, close_tz)

                    diff = utc_close_str_obj - utc_open_str_obj

                    if diff.total_seconds() < 1:
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                    else:
                        return ''
        else:
            return ''


    @dash.callback(
        Output("dest-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("d-city-input", "value"),
        State("d-zip-input", "value"),
        State("d-state-drop", "value"),
        prevent_intial_call=True
    )
    def check_dest(n_clicks, d_city, d_zip, d_state):
        if n_clicks > 0:
            zip_valid = check_zip_code(d_zip)
            city_exists = valid_input(d_city)
            state_exists = valid_input(d_state)

            false_list = []

            if city_exists == False:
                false_list.append('City')

            if state_exists == False:
                false_list.append('State')

            if zip_valid == False:
                false_list.append('Zip Code (#####, #####-##### or A#A#A# for CAN)')

            str = 'Submit a valid: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if city_exists == False or state_exists == False or zip_valid == False:
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else: 
                return ''
        else:
            return ''


    @dash.callback(
        Output("request-del-date-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("req-del-date", "date"),
        prevent_intial_call=True
    )
    def check_request_del_date(n_clicks, date):
        if n_clicks > 0:
            output_str = 'Requested pickup date cannot be empty'
            if date is None:
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            elif date == '':
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''

    
    @dash.callback(
        Output("dest-open-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-open-time-drop", "value"),
        State("drop-open-am-pm-drop", "value"),
        State("drop-open-timezone-drop", "value"),
        prevent_intial_call=True
    )
    def check_dest_open_time(n_clicks, time, am_pm, tz):
        if n_clicks > 0:
            time_exists = valid_input(time)
            am_pm_exists = valid_input(am_pm)
            tz_exists = valid_input(tz)

            false_list = create_time_false_list(time_exists, am_pm_exists, tz_exists)

            str = 'Open time is missing: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if time_exists == False or am_pm_exists == False or tz_exists == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("dest-close-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-close-time-drop", "value"),
        State("drop-close-am-pm-drop", "value"),
        State("drop-close-timezone-drop", "value"),
        prevent_intial_call=True
    )
    def check_dest_close_time(n_clicks, time, am_pm, tz):
        if n_clicks > 0:
            time_exists = valid_input(time)
            am_pm_exists = valid_input(am_pm)
            tz_exists = valid_input(tz)

            false_list = create_time_false_list(time_exists, am_pm_exists, tz_exists)

            str = 'Close time is missing: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if time_exists == False or am_pm_exists == False or tz_exists == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("dest-close-warning-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("req-del-date", "date"),
        State("drop-open-time-drop", "value"),
        State("drop-open-am-pm-drop", "value"),
        State("drop-open-timezone-drop", "value"),
        State("drop-close-time-drop", "value"),
        State("drop-close-am-pm-drop", "value"),
        State("drop-close-timezone-drop", "value"),
        prevent_intial_call=True
    )
    def check_dest_open_close_time_difference(n_clicks, date, open_time, open_am_pm, open_tz, close_time, close_am_pm, close_tz):
        output_str = 'Close time must be later than open time'
        if n_clicks > 0:
            if date is None:
                return ''
            elif date == '':
                return ''
            else:
                open_time_exists = valid_input(open_time)
                open_am_pm_exists = valid_input(open_am_pm)
                open_tz_exists = valid_input(open_tz)
                close_time_exists = valid_input(close_time)
                close_am_pm_exists = valid_input(close_am_pm)
                close_tz_exists = valid_input(close_tz)

                if open_time_exists == False or open_am_pm_exists == False or open_tz_exists == False or close_time_exists == False or close_am_pm_exists == False or close_tz_exists == False:
                    return ''
                else:
                    utc_open_str_obj = create_date_strings(date, open_time, open_am_pm, open_tz)
                    utc_close_str_obj = create_date_strings(date, close_time, close_am_pm, close_tz)

                    diff = utc_close_str_obj - utc_open_str_obj

                    if diff.total_seconds() < 1:
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                    else:
                        return ''
        else:
            return ''


    @dash.callback(
        Output("stackable-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("stackable-radio", "value"),
    )
    def check_stackable(n_clicks, stackable):
        if n_clicks > 0:
            stackable_exists = valid_input(stackable)
            if stackable_exists == False:
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("linedown-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("situation-input", "value"),
    )
    def check_linedown_situation(n_clicks, situation):
        if n_clicks > 0:
            situation_exists = valid_input(situation)
            if situation_exists == False:
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    @dash.callback(
        Output("breakdown-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("breakdown-input", "value"),
    )
    def check_breakdown(n_clicks, breakdown):
        if n_clicks > 0:
            breakdown_exists = valid_input(breakdown)
            if breakdown_exists == False:
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                return ''
        else:
            return ''


    
    #not needed since scope isn't required
    @dash.callback(
        Output("q19-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-scope-check", "value"),
    )
    def check_q19_pick_scope(n_clicks, pick_scope):
        if n_clicks > 0:
            if not pick_scope:
                return ''
            else:
                return ''
        else:
            return ''
    


    #needed just in case other scope is selected but nothing is entered
    @dash.callback(
        Output("pick-scope-other-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("pick-scope-check", "value"),
        State("pick-other-input", "value"),
        State("pick-other-input", "disabled"),
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


    
    #not needed since scope isn't required
    @dash.callback(
        Output("q20-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-scope-check", "value"),
    )
    def check_q20_drop_scope(n_clicks, drop_scope):
        if n_clicks > 0:
            if not drop_scope:
                return ''
            else:
                return ''
        else:
            return ''
    

    #needed just in case other scope is selected but nothing is entered
    @dash.callback(
        Output("drop-scope-other-ae-div","children"),
        Input("submit-btn","n_clicks"),
        State("drop-scope-check", "value"),
        State("drop-other-input", "value"),
        State("drop-other-input", "disabled"),
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
    

    @dash.callback(
        Output('garbage-div-2', 'children'),
        Output("data-storage-ae-display","data"),
        Output("data-storage-ae-final","data"),
        Output("data-storage-ae-prelim-pick-scope","data"),
        Output("data-storage-ae-prelim-drop-scope","data"),
        Output('data-storage-ae-item', 'data'),
        Input('data-storage', 'data'),
        Input('data-storage-prelim-item', 'data'),
        State("ccode-input", "value"),
        State("empcode-input", "value"),
        State("additional-input", "value"),
        State("load-num-input", "value"),
        State("quote-freight-drop", "value"),
        State("o-city-input", "value"),
        State("o-state-drop", "value"),
        State("o-zip-input", "value"),
        State("req-pick-date", "date"),
        State("pickup-addtional-input", "value"),
        State("pick-open-time-drop", "value"),
        State("pick-open-am-pm-drop", "value"),
        State("pick-open-timezone-drop", "value"),
        State("pick-close-time-drop", "value"),
        State("pick-close-am-pm-drop", "value"),
        State("pick-close-timezone-drop", "value"),
        State("d-city-input", "value"),
        State("d-state-drop", "value"),
        State("d-zip-input", "value"),
        State("req-del-date", "date"),
        State("delivery-addtional-input", "value"),
        State("drop-open-time-drop", "value"),
        State("drop-open-am-pm-drop", "value"),
        State("drop-open-timezone-drop", "value"),
        State("drop-close-time-drop", "value"),
        State("drop-close-am-pm-drop", "value"),
        State("drop-close-timezone-drop", "value"),
        State("palletized-radio", "value"),
        State("packaging-input", "value"),
        State("stackable-radio", "value"),
        State("additional-insurance-radio", "value"),
        State("value-input", "value"),
        State("commodity-input", "value"),
        State("hazmat-input", "value"),
        State("un-input", "value"),
        State("class-input", "value"),
        State("packing-input", "value"),
        State("situation-input", "value"),
        State("breakdown-input", "value"),
        State("pick-scope-check", "value"),
        State("pick-other-input", "value"),
        State("drop-scope-check", "value"),
        State("drop-other-input", "value"),
        State("additional-support-drop", "value")
    )
    def store_data(data_storage, prelim_item_storage, ccode, 
            empcode, additional, load_num, quote_or_on_hand, org_city, org_state, org_zip,
            req_pick, pick_additional_info, pick_open_time, pick_open_am_pm, pick_open_timezone, pick_close_time, pick_close_am_pm, 
            pick_close_timezone, dest_city, dest_state, dest_zip, req_drop, drop_addtional_info, open_drop_time, open_drop_am_pm, 
            open_drop_timezone,close_drop_time, close_drop_am_pm, close_drop_timezone, palletized, packaging,
            stackable, additional_insurance, value, commodity, hazmat, un, haz_class, packing, situation, breakdown, pick_scope,
            pick_other, drop_scope, drop_other, additional_support):
        good_modes = ['air_expedite','exclusive_use_vehicle']

        quote_date = import_quote_date()

        if data_storage is not None:
            if pd.read_json(data_storage, orient = 'split')['TRANSPORTATION_MODE'].iloc[0] in good_modes:
                
                quote_id = create_quote_id(empcode, quote_date)
                prelim_item_storage['QUOTE_ID'] = quote_id

                key_order=['QUOTE_ID', 'QUANTITY', 'WEIGHT', 'LENGTH', 'WIDTH', 'HEIGHT']
                prelim_item_storage = {k : prelim_item_storage[k] for k in key_order}

                return [],{'QUOTE_ID':quote_id, 'TRANSPORTATION_MODE': pd.read_json(data_storage, orient = 'split')['TRANSPORTATION_MODE'].iloc[0],  
                            'CUSTOMER_CODE': ccode,'SEVEN_LETTER': empcode, 'QUOTE_OR_ON_HAND': quote_or_on_hand,
                            'ADDITIONAL_INSURANCE': additional_insurance, 'VALUE': get_value(additional_insurance, value), 'COMMODITY':commodity, 
                            'PACKAGING': get_packaging(palletized, packaging), 'IS_HAZ_MAT':hazmat, 'UN_NUMBER':un, 'CLASS_NUMBER':haz_class, 
                            'PACKING_GROUP_NUMBER':packing, 'ADDITIONAL_SUPPORT_NEEDED':get_additional_support(additional_support), 
                            'LOAD_NUM':load_num,  'ORIGIN_CITY':org_city, 'ORIGIN_STATE':org_state, 'ORIGIN_ZIP':org_zip, 
                            'REQUESTED_PICKUP_DATE': req_pick, 
                            'ORIGIN_OPEN_TIME': get_open_time(req_pick, pick_open_time, pick_open_am_pm, pick_open_timezone),  
                            'ORIGIN_CLOSE_TIME': get_close_time(req_pick, pick_open_time, pick_open_am_pm, pick_open_timezone, 
                                                                    pick_close_time, pick_close_am_pm, pick_close_timezone), 
                            'DESTINATION_CITY':dest_city, 'DESTINATION_STATE':dest_state, 'DESTINATION_ZIP':dest_zip, 
                            'REQUESTED_DELIVERY_DATE':req_drop, 
                            'DESTINATION_OPEN_TIME': get_open_time(req_drop, open_drop_time, open_drop_am_pm, open_drop_timezone),  
                            'DESTINATION_CLOSE_TIME': get_close_time(req_drop, open_drop_time, open_drop_am_pm, open_drop_timezone, 
                                                                        close_drop_time, close_drop_am_pm, close_drop_timezone),  
                            'IS_STACKABLE':stackable, 'CAUSE_LINE_DOWN':situation, 'CAN_BREAKDOWN':breakdown, 'IS_PALLETIZED':palletized, 
                            'QUOTE_DATE': quote_date
                            }, {'QUOTE_ID':quote_id, 'TRANSPORTATION_MODE': pd.read_json(data_storage, orient = 'split')['TRANSPORTATION_MODE'].iloc[0],  
                            'SERVICE': None, 'CUSTOMER_CODE': ccode,'SEVEN_LETTER': empcode, 'QUOTE_OR_ON_HAND': quote_or_on_hand,
                            'ADDITIONAL_INSURANCE': additional_insurance, 'VALUE': get_value(additional_insurance, value), 'COMMODITY':commodity, 
                            'PACKAGING': get_packaging(palletized, packaging), 'IS_HAZ_MAT':hazmat, 'UN_NUMBER':un, 'CLASS_NUMBER':haz_class, 
                            'PACKING_GROUP_NUMBER':packing, 'ADDITIONAL_SUPPORT_NEEDED':get_additional_support(additional_support), 
                            'LOAD_NUM':load_num,  'ORIGIN_CITY':org_city, 'ORIGIN_STATE':org_state, 'ORIGIN_ZIP':org_zip, 
                            'REQUESTED_PICKUP_DATE': req_pick, 
                            'ORIGIN_OPEN_TIME': get_open_time(req_pick, pick_open_time, pick_open_am_pm, pick_open_timezone),
                            'ORIGIN_CLOSE_TIME': get_close_time(req_pick, pick_open_time, pick_open_am_pm, pick_open_timezone, 
                                                                    pick_close_time, pick_close_am_pm, pick_close_timezone),  
                            'DESTINATION_CITY':dest_city, 'DESTINATION_STATE':dest_state, 'DESTINATION_ZIP':dest_zip, 
                            'REQUESTED_DELIVERY_DATE':req_drop, 
                            'DESTINATION_OPEN_TIME': get_open_time(req_drop, open_drop_time, open_drop_am_pm, open_drop_timezone),  
                            'DESTINATION_CLOSE_TIME': get_close_time(req_drop, open_drop_time, open_drop_am_pm, open_drop_timezone, 
                                                                        close_drop_time, close_drop_am_pm, close_drop_timezone),  
                            'IS_STACKABLE':stackable, 'CAUSE_LINE_DOWN':situation, 'CAN_BREAKDOWN':breakdown, 'IS_PALLETIZED':palletized, 
                            'QUOTE_DATE': quote_date
                            }, {'QUOTE_ID': quote_id, 'STOP_TYPE': 'P', 
                                'SCOPE': parse_scopes(pick_scope, pick_other)}, {'QUOTE_ID': quote_id, 
                                                                                 'STOP_TYPE': 'D', 'SCOPE': parse_scopes(drop_scope, drop_other)}, prelim_item_storage
            else:
                return dcc.Location(pathname="/", id="air-euv-redirect"),None, None, None, None, None

        else:
            return dcc.Location(pathname="/", id="air-euv-redirect"),None, None, None, None, None


    @dash.callback(
        Output("data-storage-final-session", "data"),
        Output("data-storage-pick-scope-final", "data"),
        Output("data-storage-drop-scope-final", "data"),
        Output("data-storage-ae-item-final", "data"),
        Output("output_air_euv", "children"),
        Input("submit-btn","n_clicks"),
        Input('data-storage-ae-display', 'data'),
        Input('data-storage-ae-final', 'data'),
        Input("data-storage-ae-prelim-pick-scope","data"),
        Input("data-storage-ae-prelim-drop-scope","data"),
        Input('data-storage-ae-item', 'data'),
        State("additional-input", "value"),
        State("pickup-addtional-input", "value"),
        State("delivery-addtional-input", "value"),
    )
    def send_data(n_clicks, final_data_storage_display, final_data, pick_scope_storage, drop_scope_storage, item_storage, 
                  additional_contacts, pickup_additional_input, drop_additional_input):
        if n_clicks > 0:
            print('----------data----------')
            print(final_data_storage_display)
            print(n_clicks)
            print('after data n clicks:', n_clicks)
            print('------------------------')

            columns_to_drop = ['LOAD_NUM']
            missing_list = []

            if get_ccode(final_data_storage_display['CUSTOMER_CODE']) == None:
                missing_list.append(prettify_strings('CUSTOMER_CODE'))

            if get_empcode(final_data_storage_display['SEVEN_LETTER']) == None:
                missing_list.append(prettify_strings('SEVEN_LETTER'))

            if final_data_storage_display['IS_HAZ_MAT'] == None or final_data_storage_display['IS_HAZ_MAT'] == '' or final_data_storage_display['IS_HAZ_MAT'] == False:
                columns_to_drop.append('UN_NUMBER')
                columns_to_drop.append('CLASS_NUMBER')
                columns_to_drop.append('PACKING_GROUP_NUMBER')
            
            if final_data_storage_display['ADDITIONAL_INSURANCE'] == None or not final_data_storage_display['ADDITIONAL_INSURANCE'] or final_data_storage_display['ADDITIONAL_INSURANCE']== False:
                columns_to_drop.append('VALUE')

            for key, value in final_data_storage_display.items():
                if value is None and key not in columns_to_drop:
                    missing_list.append(prettify_strings(key))

            if check_for_invalids(item_storage) ==  True:
                missing_list.append('Items (Quantity, Dimensions)')

            #remove dups
            missing_list = list(set(missing_list))

            missing_str = ', '.join(str(e) for e in missing_list)
            missing_str = 'These entries are missing: ' + missing_str + '.'

            time.sleep(3)

            if len(missing_list) != 0:
                return final_data, pick_scope_storage, drop_scope_storage, item_storage, html.P(missing_str, style={'font-weight':'bold', 'text-align': 'center', 'color': 'red'})
            else:
                send_air_euv_email(final_data, item_storage, pick_scope_storage, drop_scope_storage, additional_contacts, pickup_additional_input, drop_additional_input)
                return final_data, pick_scope_storage, drop_scope_storage, item_storage, dcc.Location(pathname="/air_exp_finished", id="finished-page")
        
        else:
            return None, None, None, None, []

    
    def get_open_time(req_date, req_time, am_pm, timezone):
        date_valid = valid_input(req_date)
        time_valid = valid_input(req_time)
        am_pm_valid = valid_input(am_pm)
        timezone_valid = valid_input(timezone)

        if date_valid == True and time_valid == True and am_pm_valid == True and timezone_valid == True:
            utc_time_string = create_date_strings(req_date, req_time, am_pm, timezone)
            return utc_time_string
        else:
            return None


    def get_close_time(req_date, open_time, open_am_pm, open_timezone, close_time, close_am_pm, close_timezone):
        date_valid = valid_input(req_date)
        open_time_valid = valid_input(open_time)
        open_am_pm_valid = valid_input(open_am_pm)
        open_timezone_valid = valid_input(open_timezone)
        close_time_valid = valid_input(close_time)
        close_am_pm_valid = valid_input(close_am_pm)
        close_timezone_valid = valid_input(close_timezone)

        if (date_valid == True and open_time_valid == True and open_am_pm_valid == True 
            and open_timezone_valid == True and close_time_valid == True and close_am_pm_valid == True 
            and close_timezone_valid == True):

            utc_open_str_obj = create_date_strings(req_date, open_time, open_am_pm, open_timezone)
            utc_close_str_obj = create_date_strings(req_date, close_time, close_am_pm, close_timezone)

            diff = utc_close_str_obj - utc_open_str_obj

            if diff.total_seconds() < 1:
                return None
            else:
                return utc_close_str_obj

        else:
            return None

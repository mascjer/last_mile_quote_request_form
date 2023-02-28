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
                import_load_num(None)
                return '' #html.P('Submit a load number', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_load_num(load_num)
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
                import_origin_city(None)
            else:
                import_origin_city(o_city)

            if state_exists == False:
                false_list.append('State')
                import_origin_state(None)
            else:
                import_origin_state(o_state)

            if zip_valid == False:
                false_list.append('Zip Code (XXXXX or XXXXX-XXXX)')
                import_origin_zip(None)
            else:
                import_origin_zip(o_zip)

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
                import_req_pick_date(None)
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            elif date == '':
                import_req_pick_date(None)
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_req_pick_date(date)
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
                import_origin_open_time(None)
                import_origin_close_time(None)
                return ''
            elif date == '':
                import_origin_open_time(None)
                import_origin_close_time(None)
                return ''
            else:
                open_time_exists = valid_input(open_time)
                open_am_pm_exists = valid_input(open_am_pm)
                open_tz_exists = valid_input(open_tz)
                close_time_exists = valid_input(close_time)
                close_am_pm_exists = valid_input(close_am_pm)
                close_tz_exists = valid_input(close_tz)

                if open_time_exists == False or open_am_pm_exists == False or open_tz_exists == False or close_time_exists == False or close_am_pm_exists == False or close_tz_exists == False:
                    import_origin_open_time(None)
                    import_origin_close_time(None)
                    return ''
                else:
                    utc_open_str_obj = create_date_strings(date, open_time, open_am_pm, open_tz)
                    utc_close_str_obj = create_date_strings(date, close_time, close_am_pm, close_tz)

                    diff = utc_close_str_obj - utc_open_str_obj

                    if diff.total_seconds() < 1:
                        import_origin_open_time(None)
                        import_origin_close_time(None)
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                    else:
                        import_origin_open_time(utc_open_str_obj)
                        import_origin_close_time(utc_close_str_obj)
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
                import_dest_city(None)
            else:
                import_dest_city(d_city)

            if state_exists == False:
                false_list.append('State')
                import_dest_state(None)
            else:
                import_dest_state(d_state)

            if zip_valid == False:
                false_list.append('Zip Code (XXXXX or XXXXX-XXXX)')
                import_dest_zip(None)
            else:
                import_dest_zip(d_zip)

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
                import_req_del_date(None)
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            elif date == '':
                import_req_del_date(None)
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_req_del_date(date)
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
                import_dest_open_time(None)
                import_dest_close_time(None)
                return ''
            elif date == '':
                import_dest_open_time(None)
                import_dest_close_time(None)
                return ''
            else:
                open_time_exists = valid_input(open_time)
                open_am_pm_exists = valid_input(open_am_pm)
                open_tz_exists = valid_input(open_tz)
                close_time_exists = valid_input(close_time)
                close_am_pm_exists = valid_input(close_am_pm)
                close_tz_exists = valid_input(close_tz)

                if open_time_exists == False or open_am_pm_exists == False or open_tz_exists == False or close_time_exists == False or close_am_pm_exists == False or close_tz_exists == False:
                    import_dest_open_time(None)
                    import_dest_close_time(None)
                    return ''
                else:
                    utc_open_str_obj = create_date_strings(date, open_time, open_am_pm, open_tz)
                    utc_close_str_obj = create_date_strings(date, close_time, close_am_pm, close_tz)

                    diff = utc_close_str_obj - utc_open_str_obj

                    if diff.total_seconds() < 1:
                        import_dest_open_time(None)
                        import_dest_close_time(None)
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                    else:
                        import_dest_open_time(utc_open_str_obj)
                        import_dest_close_time(utc_close_str_obj)
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
                import_stackable_freight(None)
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_stackable_freight(stackable)
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
                import_cause_line_down(None)
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_cause_line_down(situation)
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
                import_can_breakdown(None)
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_can_breakdown(breakdown)
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
                import_pick_stop_type(None)
                return ''
            else:
                import_pick_stop_type('P')
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
                            import_other_pick_scope(None)
                            return html.P('Submit a valid other scope', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                        else:
                            import_other_pick_scope(other_exists)
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
                import_drop_stop_type(None)
                return ''
            else:
                import_drop_stop_type('D')
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
                            import_other_drop_scope(None)
                            return html.P('Submit a valid other scope', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                        else:
                            import_other_drop_scope(other_exists)
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
        Output("output_air_euv", "children"),
        Input("submit-btn","n_clicks"),
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
        State("additional-support-checklist", "value"),
        prevent_intial_call=True
    )
    def get_final_large_form(n_clicks, ccode, empcode, additional, load_num, quote_or_on_hand, 
            org_city, org_state, org_zip,
            req_pick, pick_additional_info, pick_open_time, pick_open_am_pm, pick_open_timezone, pick_close_time, pick_close_am_pm, 
            pick_close_timezone, dest_city, dest_state, dest_zip, req_drop, drop_addtional_info, open_drop_time, open_drop_am_pm, 
            open_drop_timezone,close_drop_time, close_drop_am_pm, close_drop_timezone, palletized, packaging,
            stackable, additional_insurance, value, commodity, hazmat, un, haz_class, packing, situation, breakdown, pick_scope,
            pick_other, drop_scope, drop_other, additional_support):

        prelim_df = send_request_df()
        valid_to_proceed = check_trans_mode_service(prelim_df)
        

        if valid_to_proceed == True:
            if n_clicks > 0:    
                if additional_support is not None:
                    additional_support = additional_support[0]
                    
                large_form_cols = ['Transportation Mode', 'Customer Code', 'Seven Letter', 'Additional Groups', 'Load Number',
                    'Quote Only or Freight on Hand', 'Origin City', 'Origin State', 
                    'Origin Zip Code', 'Requested Pickup Date', 'Pickup Addtional Info', 'Origin Open Time', 'Origin Open AM/PM', 'Origin Open Timezone', 
                    'Origin Close Time', 'Origin Close AM/PM', 'Origin Close Timezone', 'Destination City', 'Destination State',
                    'Destination Zip Code', 'Requested Delivery Day', 'Delivery Addtional Info', 'Receiver Open Time', 'Receiver Open AM/PM', 
                    'Receiver Open Timezone','Receiver Close Time', 'Receiver Close AM/PM', 'Receiver Close Timezone', 
                    'Palletized Freight', 'Packaging', 'Freight Stackable', 'Additional Insurance', 'Value', 'Commodity', 'Haz Mat', 'UN #', 'Class #', 'Packing Group #', 
                    'Line-Down Situation', 'Freight Breakdown', 'Pickup Scope', 'Other Pickup Scope', 'Delivery Scope', 'Other Delivery Scope', 
                    'Additional Support Needed', 'Items (Quantity, Dimensions)']

                pick_scope_list = parse_scopes(pick_scope, pick_other)
                drop_scope_list = parse_scopes(drop_scope, drop_other)

                import_pick_scopes(pick_scope_list)
                import_drop_scopes(drop_scope_list)

                pick_scope_df = get_pick_scope_data()
                drop_scope_df = get_drop_scope_data()

                scope_df = concat_scope_dfs(pick_scope_df, drop_scope_df)
                item_df = send_item_df()

                request_df = wait_for_codes(send_request_df(), ccode, empcode)

                invalids = check_for_invalids(item_df)

                origin_open_time = request_df['ORIGIN_OPEN_TIME'][0]
                origin_close_time = request_df['ORIGIN_CLOSE_TIME'][0]
                dest_open_time = request_df['DESTINATION_OPEN_TIME'][0]
                dest_close_time = request_df['DESTINATION_CLOSE_TIME'][0]

                if invalids == True:
                    items = None
                else:
                    items = 'Full'

                trans_mode = request_df['TRANSPORTATION_MODE'][0]

                large_form_data = [trans_mode, ccode, empcode, additional, load_num, quote_or_on_hand, 
                                    org_city, org_state, org_zip,
                                    req_pick, pick_additional_info, pick_open_time, pick_open_am_pm, pick_open_timezone, pick_close_time, pick_close_am_pm, 
                                    pick_close_timezone, dest_city, dest_state, dest_zip, req_drop, drop_addtional_info, open_drop_time, open_drop_am_pm, 
                                    open_drop_timezone,close_drop_time, close_drop_am_pm, close_drop_timezone, palletized, packaging,
                                    stackable, additional_insurance, value, commodity, hazmat, un, haz_class, packing, situation, breakdown, 
                                    pick_scope, pick_other, drop_scope, drop_other, additional_support, items]

                large_form_display = pd.DataFrame([large_form_data], columns=large_form_cols)

                missing_list = []

                if large_form_display['Haz Mat'].iloc[0] == None or not large_form_display['Haz Mat'].iloc[0] or large_form_display['Haz Mat'].iloc[0] == False:
                    large_form_display = large_form_display.drop(columns=['UN #', 'Class #', 'Packing Group #'])

                if large_form_display['Additional Insurance'].iloc[0] == None or not large_form_display['Additional Insurance'].iloc[0] or large_form_display['Additional Insurance'].iloc[0] == False:
                    large_form_display = large_form_display.drop(columns=['Value'])

                if large_form_display['Palletized Freight'].iloc[0] == None or large_form_display['Palletized Freight'].iloc[0] == True:
                    large_form_display = large_form_display.drop(columns=['Packaging'])

                if large_form_display['Pickup Scope'].iloc[0] == None or not large_form_display['Pickup Scope'].iloc[0] or 'Other' not in large_form_display['Pickup Scope'].iloc[0]:
                    large_form_display = large_form_display.drop(columns=['Other Pickup Scope'])

                if large_form_display['Delivery Scope'].iloc[0] == None or not large_form_display['Delivery Scope'].iloc[0] or 'Other' not in large_form_display['Delivery Scope'].iloc[0]:
                    large_form_display = large_form_display.drop(columns=['Other Delivery Scope'])

                columns_to_drop = ['Additional Groups', 'Additional Support Needed',
                                    'Pickup Addtional Info', 'Delivery Addtional Info', 'Pickup Scope', 'Delivery Scope', 'Load Number'] #non-required fields

                for (columnName, columnData) in large_form_display.iteritems():
                    if columnData.values[0] == None or not columnData.values[0]:
                        if columnData.values[0] == False:
                            print('sorry if you see this, its bad coding but I needed a placeholder for this specific instance')
                        elif columnName in columns_to_drop:
                            print('sorry if you see this, its bad coding but I needed a placeholder for this specific instance')
                        else:
                            missing_list.append(columnName)
                    


                if origin_open_time is None:
                    missing_list.append('Origin Open Time (INVALID)')
                if origin_close_time is None:
                    missing_list.append('Origin Close Time (INVALID)')
                if dest_open_time is None:
                    missing_list.append('Receiver Open Time (INVALID)')
                if dest_close_time is None:
                    missing_list.append('Receiver Close Time (INVALID)')

                
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

                large_form_display['Total Weight'] = total_weight

                if len(missing_list) != 0:
                    return html.P(missing_str, style={'font-weight':'bold', 'text-align': 'center', 'color': 'red'})
                else:                
                    write_to_lms_quote(request_df)
                    write_to_lms_quote_scope(scope_df)
                    write_to_lms_quote_items(item_df)
                    send_quote_email(large_form_display, item_df, scope_df, city = large_form_display['Origin City'][0], state = large_form_display['Origin State'][0])
                    return dcc.Location(pathname="/finished", id="finished-page")
            else:
                return ['']
        else:
            return dcc.Location(pathname="/", id="air-euv-redirect")








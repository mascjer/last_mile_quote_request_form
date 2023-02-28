#for functions used on multiple pages
from datetime import datetime
import re
import pytz
import pandas as pd
import numpy as np

global request_df
global pick_scope_df
global drop_scope_df
global scope_df

request_form_data = {'QUOTE_ID':1, 'TRANSPORTATION_MODE':[None], 'SERVICE':[None], 'CUSTOMER_CODE':[None],
        'SEVEN_LETTER':[None], 'QUOTE_OR_ON_HAND':[None], 'ADDITIONAL_INSURANCE':[None], 'VALUE':[None], 'COMMODITY':[None], 
        'PACKAGING':[None], 'IS_HAZ_MAT':[None], 'UN_NUMBER':[None], 'CLASS_NUMBER':[None], 
        'PACKING_GROUP_NUMBER':[None], 'ADDITIONAL_SUPPORT_NEEDED':[None], 'LOAD_NUM':[None],  'ORIGIN_CITY':[None], 
        'ORIGIN_STATE':[None], 'ORIGIN_ZIP':[None], 'REQUESTED_PICKUP_DATE':[None], 'ORIGIN_OPEN_TIME':[None],
        'ORIGIN_CLOSE_TIME':[None], 'DESTINATION_CITY':[None], 'DESTINATION_STATE':[None], 
        'DESTINATION_ZIP':[None], 'REQUESTED_DELIVERY_DATE':[None], 'DESTINATION_OPEN_TIME':[None],
        'DESTINATION_CLOSE_TIME':[None], 'IS_STACKABLE':[None], 'CAUSE_LINE_DOWN':[None],
        'CAN_BREAKDOWN':[None], 'IS_PALLETIZED':[None], 'FIRST_FLOOR_PICKUP':[None],'HAS_FREIGHT_ELEVATOR':[None],
        'CONTACT_NAME':[None], 'CONTACT_PHONE':[None], 'CONTACT_EMAIL':[None],
        'WAREHOUSE_CODE':[None], 'WAREHOUSE_ADDRESS':[None], 'WAREHOUSE_CITY':[None], 'WAREHOUSE_STATE':[None],
        'WAREHOUSE_ZIP':[None], 'TIME_EXPECTATION':[None], 'QUOTE_DATE':[None]
        }
request_df = pd.DataFrame(request_form_data)

scope_data = {'QUOTE_ID':'temp_id', 'STOP_TYPE':[None], 'SCOPE':[None], 'INCLUDES_OTHER_SCOPE':[None]}
pick_scope_df = pd.DataFrame(scope_data) # for air and euv since they have two scopes
drop_scope_df = pd.DataFrame(scope_data) # for air and euv since they have two scopes
scope_df = pd.DataFrame(scope_data) # for first final since they have one scope

### USED IN AIR_EUV_CALLBACKS ###
def import_pick_stop_type(stop_type):
    pick_scope_df['STOP_TYPE'] = [stop_type]


### USED IN AIR_EUV_CALLBACKS ###
def import_pick_scopes(scopes):
    pick_scope_df['SCOPE'] = [scopes]


### USED IN AIR_EUV_CALLBACKS ###
def import_other_pick_scope(other_scope):
    pick_scope_df['INCLUDES_OTHER_SCOPE'] = [other_scope]


### USED IN AIR_EUV_CALLBACKS ###
def get_pick_scope_data():
    return pick_scope_df


### USED IN AIR_EUV_CALLBACKS ###
def import_drop_stop_type(stop_type):
    drop_scope_df['STOP_TYPE'] = [stop_type]


### USED IN AIR_EUV_CALLBACKS ###
def import_drop_scopes(scopes):
    drop_scope_df['SCOPE'] = [scopes]


### USED IN AIR_EUV_CALLBACKS ###
def import_other_drop_scope(other_scope):
    drop_scope_df['INCLUDES_OTHER_SCOPE'] = [other_scope]


### USED IN AIR_EUV_CALLBACKS ###
def get_drop_scope_data():
    return drop_scope_df


### USED IN AIR_EUV_CALLBACKS ###
def concat_scope_dfs(pick_scope, drop_scope):
    pick_scope = pick_scope.explode('SCOPE')
    drop_scope = drop_scope.explode('SCOPE')

    pieces = (pick_scope, drop_scope) 

    scope = pd.concat(pieces, ignore_index=True)

    return scope


### USED IN FIRST_CALLBACKS ###
def import_stop_type(stop_type):
    scope_df['STOP_TYPE'] = [stop_type]


### USED IN AIR_EUV_CALLBACKS ###
def import_other_scope(other_scope):
    scope_df['INCLUDES_OTHER_SCOPE'] = [other_scope]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_scopes(scopes):
    scope_df['SCOPE'] = [scopes]


### USED IN FIRST_FINAL_CALLBACKS ###
def send_scope_df():
    return scope_df


def explode_scope_data(scope_df):
    scope_df = scope_df.explode('SCOPE')
    return scope_df


### USED IN SHARED_CALLBACKS ###
def retrieve_item_df(df):
    global item_df
    item_df = df


### USED IN AIR_EUV_CALLBACKS ###
def send_item_df():
    return item_df


### USED IN AIR_EUV_CALLBACKS ###
def send_request_df():
    return request_df


### USED IN SHARED_CALLBACKS ###
def import_trans_mode(trans_mode):
    request_df['TRANSPORTATION_MODE'] = [trans_mode]


#USED IN FIRST_FINAL_CALLBACKS
def import_service(service):
    request_df['SERVICE'] = [service]


### USED IN SHARED_CALLBACKS ###
def import_customer_code(customer_code):
    request_df['CUSTOMER_CODE'] = [customer_code]


### USED IN SHARED_CALLBACKS ###
def import_seven_letter(seven_letter):
    request_df['SEVEN_LETTER'] = [seven_letter]


### USED IN SHARED_CALLBACKS ###
def import_quote_or_on_hand(quote_or_on_hand):
    request_df['QUOTE_OR_ON_HAND'] = [quote_or_on_hand]


### USED IN SHARED_CALLBACKS ###
def import_additional_insurance(additional_insurance):
    request_df['ADDITIONAL_INSURANCE'] = [additional_insurance]


### USED IN SHARED_CALLBACKS ###
def import_value(value):
    request_df['VALUE'] = [value]


### USED IN SHARED_CALLBACKS ###
def import_commodity(commodity):
    request_df['COMMODITY'] = [commodity]


### USED IN SHARED_CALLBACKS ###
def import_packaging(packaging):
    request_df['PACKAGING'] = [packaging]
    

### USED IN SHARED_CALLBACKS ###
def import_haz_mat(haz_mat):
    request_df['IS_HAZ_MAT'] = [haz_mat]


### USED IN SHARED_CALLBACKS ###
def import_un_num(un_num):
    request_df['UN_NUMBER'] = [un_num]


### USED IN SHARED_CALLBACKS ###
def import_class_num(class_num):
    request_df['CLASS_NUMBER'] = [class_num]


### USED IN SHARED_CALLBACKS ###
def import_pg_num(pg_num):
    request_df['PACKING_GROUP_NUMBER'] = [pg_num]


### USED IN SHARED_CALLBACKS ###
def import_additional_support(additional_support):
    request_df['ADDITIONAL_SUPPORT_NEEDED'] = [additional_support]


### USED IN AIR_EUV_CALLBACKS ###
def import_load_num(load_num):
    request_df['LOAD_NUM'] = [load_num]


### USED IN AIR_EUV_CALLBACKS ###
def import_origin_city(origin_city):
    request_df['ORIGIN_CITY'] = [origin_city]


### USED IN AIR_EUV_CALLBACKS ###
def import_origin_state(origin_state):
    request_df['ORIGIN_STATE'] = [origin_state]


### USED IN AIR_EUV_CALLBACKS ###
def import_origin_zip(origin_zip):
    request_df['ORIGIN_ZIP'] = [origin_zip]


### USED IN AIR_EUV_CALLBACKS ###
def import_req_pick_date(req_pick_date):
    request_df['REQUESTED_PICKUP_DATE'] = [req_pick_date]


### USED IN AIR_EUV_CALLBACKS ###
def import_origin_open_time(origin_open_time):
    if origin_open_time:
        request_df['ORIGIN_OPEN_TIME'] = [origin_open_time.strftime('%Y-%m-%d %H:%M:%S')]
    else:
        request_df['ORIGIN_OPEN_TIME'] = None


### USED IN AIR_EUV_CALLBACKS ###
def import_origin_close_time(origin_close_time):
    if origin_close_time:
        request_df['ORIGIN_CLOSE_TIME'] = [origin_close_time.strftime('%Y-%m-%d %H:%M:%S')]
    else:
        request_df['ORIGIN_CLOSE_TIME'] = None


### USED IN AIR_EUV_CALLBACKS ###
def import_dest_city(dest_city):
    request_df['DESTINATION_CITY'] = [dest_city]


### USED IN AIR_EUV_CALLBACKS ###
def import_dest_state(dest_state):
    request_df['DESTINATION_STATE'] = [dest_state]


### USED IN AIR_EUV_CALLBACKS ###
def import_dest_zip(dest_zip):
    request_df['DESTINATION_ZIP'] = [dest_zip]


### USED IN AIR_EUV_CALLBACKS ###
def import_req_del_date(req_del_date):
    request_df['REQUESTED_DELIVERY_DATE'] = [req_del_date]


### USED IN AIR_EUV_CALLBACKS ###
def import_dest_open_time(dest_open_time):
    if dest_open_time:
        request_df['DESTINATION_OPEN_TIME'] = [dest_open_time.strftime('%Y-%m-%d %H:%M:%S')]
    else:
        request_df['DESTINATION_OPEN_TIME'] = None


### USED IN AIR_EUV_CALLBACKS ###
def import_dest_close_time(dest_close_time):

    if dest_close_time:
        request_df['DESTINATION_CLOSE_TIME'] = [dest_close_time.strftime('%Y-%m-%d %H:%M:%S')]
    else:
        request_df['DESTINATION_CLOSE_TIME'] = None


### USED IN AIR_EUV_CALLBACKS ###
def import_stackable_freight(stackable_freight):
    request_df['IS_STACKABLE'] = [stackable_freight]


### USED IN AIR_EUV_CALLBACKS ###
def import_cause_line_down(line_down):
    request_df['CAUSE_LINE_DOWN'] = [line_down]


### USED IN AIR_EUV_CALLBACKS ###
def import_can_breakdown(breakdown):
    request_df['CAN_BREAKDOWN'] = [breakdown]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_is_palletized(palletized):
    request_df['IS_PALLETIZED'] = [palletized]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_first_floor_pick(first_floor):
    request_df['FIRST_FLOOR_PICKUP'] = [first_floor]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_has_freight_elevator(freight_elevator):
    request_df['HAS_FREIGHT_ELEVATOR'] = [freight_elevator]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_name(name):
    request_df['CONTACT_NAME'] = [name]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_phone(phone):
    request_df['CONTACT_PHONE'] = [phone]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_contact_email(email):
    request_df['CONTACT_EMAIL'] = [email]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_wcode(wcode):
    request_df['WAREHOUSE_CODE'] = [wcode]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_address(address):
    request_df['WAREHOUSE_ADDRESS'] = [address]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_city(city):
    request_df['WAREHOUSE_CITY'] = [city]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_state(state):
    request_df['WAREHOUSE_STATE'] = [state]


### USED IN FIRST_FINAL_CALLBACKS ###
def import_zip(zip):
    request_df['WAREHOUSE_ZIP'] = [zip]


### USED IN FIRST_FINAL_CALLBACKS, AIR_EUV_CALLBACKS  ###
def import_time_exp(time_exp):
    request_df['TIME_EXPECTATION'] = [time_exp]


### USED IN FIRST_FINAL_CALLBACKS, AIR_EUV_CALLBACKS ###
def import_quote_date():
    utc_time = datetime.utcnow()
    utc_time_string = utc_time.strftime('%Y-%m-%d %H:%M:%S')

    request_df['QUOTE_DATE'] = [utc_time_string]

### USED TO CLEAR QUOTE DATE ###
def clear_quote_date(quote_date):
    request_df['QUOTE_DATE'] = quote_date


def clear_dataframe():
    import_service(None)
    import_customer_code(None)
    import_seven_letter(None)
    import_quote_or_on_hand(None)
    import_additional_insurance(None)
    import_value(None)
    import_commodity(None)
    import_packaging(None)
    import_haz_mat(None)
    import_un_num(None)
    import_class_num(None)
    import_pg_num(None)
    import_additional_support(None)
    import_load_num(None)
    import_origin_city(None)
    import_origin_state(None)
    import_origin_zip(None)
    import_req_pick_date(None)
    import_origin_open_time(None)
    import_origin_close_time(None)
    import_dest_city(None)
    import_dest_state(None)
    import_dest_zip(None)
    import_req_del_date(None)
    import_dest_open_time(None)
    import_dest_close_time(None)
    import_stackable_freight(None)
    import_cause_line_down(None)
    import_can_breakdown(None)
    import_is_palletized(None)
    import_first_floor_pick(None)
    import_has_freight_elevator(None)
    import_name(None)
    import_phone(None)
    import_contact_email(None)
    import_wcode(None)
    import_address(None)
    import_city(None)
    import_state(None)
    import_zip(None)
    import_time_exp(None)
    clear_quote_date(None)


def clear_dataframe_after_service():
    import_customer_code(None)
    import_seven_letter(None)
    import_quote_or_on_hand(None)
    import_additional_insurance(None)
    import_value(None)
    import_commodity(None)
    import_packaging(None)
    import_haz_mat(None)
    import_un_num(None)
    import_class_num(None)
    import_pg_num(None)
    import_additional_support(None)
    import_load_num(None)
    import_origin_city(None)
    import_origin_state(None)
    import_origin_zip(None)
    import_req_pick_date(None)
    import_origin_open_time(None)
    import_origin_close_time(None)
    import_dest_city(None)
    import_dest_state(None)
    import_dest_zip(None)
    import_req_del_date(None)
    import_dest_open_time(None)
    import_dest_close_time(None)
    import_stackable_freight(None)
    import_cause_line_down(None)
    import_can_breakdown(None)
    import_is_palletized(None)
    import_first_floor_pick(None)
    import_has_freight_elevator(None)
    import_name(None)
    import_phone(None)
    import_contact_email(None)
    import_wcode(None)
    import_address(None)
    import_city(None)
    import_state(None)
    import_zip(None)
    import_time_exp(None)
    clear_quote_date(None)
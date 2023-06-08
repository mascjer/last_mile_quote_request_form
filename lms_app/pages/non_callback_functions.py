#for functions used on multiple pages
from datetime import datetime
import re
import pytz
import pandas as pd
import numpy as np
import time
import string
from pages.dataframe_builder import *
from database_functions import *


### USED iN SHARED_CALLBACKS, AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def valid_input(value):
    if value is None:
        return False
    else:
        if type(value) == bool:
            if value == '':
                return False
            else:
                return True
        else:
            value = value.strip()
            if value == '':
                return False
            elif value is None:
                return False
            else:
                return True


### USED iN SHARED_CALLBACKS ###
def valid_numeric_input(value):
    if value is None:
        return False
    elif value == '':
        return False
    else:
        if value.isnumeric():
            return True
        else:
            return False


### USED iN SHARED_CALLBACKS ###
def create_false_list(quantity_exists, weight_exists, length_exists, width_exists, height_exists):
    false_list = []
    if quantity_exists == False:
        false_list.append('Quantity')
    if weight_exists == False:
        false_list.append('Weight')
    if length_exists == False:
        false_list.append('Length')
    if width_exists == False:
        false_list.append('Width')
    if height_exists == False:
        false_list.append('Height')

    return false_list


### USED AIR_EUV_CALLBACKS, FIRST_FiNAL_CALLBACKS ###
def parse_scopes(scope, other):
    scope_list = []
    if scope is not None:
        for i in range(len(scope)):
            item = scope[i]
            scope_list.append(item)

        if other is not None and 'Other' in scope:
            scope_list.append('Other: ' + other)
            scope_list.remove('Other')

        return scope_list

    else:
        return None


### USED AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def check_zip_code(S):

    if S is None:
        return False
    elif S == '':
        return False
    else:
        S = S.strip()
        if S =='':
            return False
        elif S is None:
            return False
        else:
            spaceless = S.replace(' ','')
            print(spaceless)
            if re.match('^(\d{5})([- ])?(\d{4})?$', spaceless): #american zip code 
                print('american')
                return True
            elif re.match('[ABCEGHJKLMNPRSTVXY][0-9][ABCEGHJKLMNPRSTVWXYZ]?[0-9][ABCEGHJKLMNPRSTVWXYZ][0-9]', spaceless): #canadian
                print('canadian')
                return True
            else:
                return False


### USED ALL CALLBACKS ###
def check_email_string(S):
    if S is None:
        return False
    elif S == '':
        return False
    else:
        S = S.strip()
        if S =='':
            return False
        elif S is None:
            return False
        else:
            spaceless = S.replace(' ','')
            if not re.match('[^@]+@[^@]+\.[^@]+', spaceless):
                return False
            else:
                return True


### USED AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def check_for_invalids(items):
    items = pd.DataFrame.from_dict(items)

    item_list = items.values.tolist()
    true_list = []
    for i in range(len(item_list)):
        t_f = '***Invalid***' in item_list[i]
        if t_f == True:
            true_list.append(i)
    
    if true_list:
        return True
    else:
        return False


def check_for_nones(scopes):
    return None not in scopes.values()


### USED AIR_EUV_CALLBACKS, FIRST_FINAL_CALLBACKS ###
def wait_for_codes(request_df, ccode, empcode):
    if ccode == '':
        ccode = None
    if empcode == '':
        empcode = None

    if ccode is not None:
        ccode = ccode.upper()
    if empcode is not None:
        empcode = empcode.upper()

    ccode_valid = check_c_codes(ccode)
    empcode_valid = check_c_codes(ccode)

    if ccode_valid == True and empcode_valid == True:
        
        ccode_set = request_df.CUSTOMER_CODE[0] == ccode
        empcode_set = request_df.SEVEN_LETTER[0] == empcode

        if ccode_set == True:
            if empcode_set == True:
                return request_df
            else:
                time.sleep(0.1)
                return wait_for_codes(send_request_df(), ccode, empcode)
        else:
            time.sleep(0.1)
            return wait_for_codes(send_request_df(), ccode, empcode)
    else:
        request_df.CUSTOMER_CODE[0] == None
        request_df.SEVEN_LETTER[0] == None
        return request_df


### USED AIR_EUV_CALLBACKS ###
def create_date_strings(date, time, am_pm, timezone):
    str_fmt = '%Y-%m-%d %I:%M %p'
    date_str = date + ' ' + time + ' ' + am_pm

    date_str_obj = datetime.strptime(date_str, str_fmt)

    utc_date_str_obj = timezone_adjust(date_str_obj, timezone)

    return utc_date_str_obj


### USED AIR_EUV_CALLBACKS ###
def create_local_date_strings(date, time, am_pm, timezone):
    if timezone == 'America/New_York':
        timezone_adjust = 'ET'
    elif timezone == 'America/Chicago':
        timezone_adjust = 'CT'
    elif timezone == 'America/Denver':
        timezone_adjust = 'MT'
    elif timezone == 'America/Phoenix':
        timezone_adjust = 'MST (AZ)'
    elif timezone == 'America/Los_Angeles':
        timezone_adjust = 'PT'
    elif timezone == 'America/Anchorage':
        timezone_adjust = 'AK'
    elif timezone == 'Pacific/Honolulu':
        timezone_adjust = 'HAST'
    else:
        timezone_adjust = ''


    date_str = date + ' ' + time + ' ' + am_pm + ' ' + timezone_adjust

    return date_str


### USED AIR_EUV_CALLBACKS ###
def timezone_adjust(date_obj, timezone):
    tz = pytz.timezone(timezone)
    utc_tz = pytz.timezone('UTC')

    datetime = tz.localize(date_obj)

    utc_datetime = datetime.astimezone(utc_tz)

    return utc_datetime


### USED AIR_EUV_CALLBACKS ###
def create_time_false_list(time_exists, am_pm_exists, tz_exists):
    false_list = []

    if time_exists == False:
        false_list.append('Time')
    if am_pm_exists == False:
        false_list.append('AM/PM')
    if tz_exists == False:
        false_list.append('Timezone')

    return false_list


### USED FIRST_FINAL_CALLBACKS/LOCAL PICK AND DELIVERY ###
def check_phone_number(S):
    if S is None:
        return False
    elif S == '':
        return False
    else:
        S = S.strip()
        if S =='':
            return False
        elif S is None:
            return False
        else:
            spaceless = S.replace(' ','')
            if re.match('^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$', spaceless):
                return True
            elif re.match('^[0-9]{10}$', spaceless):
                return True
            else:
                return False


### USED FIRST_FiNAL_CALLBACKS ###
def remove_false_others(scope_df):
    other_flag = 0
    other_entry = 0

    for i in range(len(scope_df)):
        scope = scope_df.scope.iloc[i]
        
        if scope == 'Other':
            other_flag = 1

        if 'Other: ' in scope:
            other_entry = 1

    if other_flag == 1 and other_entry == 1:
        scope_df = scope_df[scope_df.scope != 'Other']
    else:
        scope_df = scope_df[scope_df.scope != 'Other']
        scope_df = scope_df[scope_df.scope.str.contains('Other:') == False]

    return scope_df


### USED IN WAREHOUSING_CALLBACKS, FIRST_FINAL_CALLBACKS, AIR_EUV_CALLBACKS
def check_trans_mode_service(request_df):
    trans_mode = request_df['TRANSPORTATION_MODE'][0]

    if trans_mode is not None:
        if trans_mode == 'air_expedite' or trans_mode == 'exclusive_use_vehicle':
            return True
        else:
            service = request_df['SERVICE'][0]

            if service is not None:
                return True
            else:
                return False
    else:
        return False


def get_packaging(palletized, packaging):
        if palletized == True:
            return 'pallet'
        else:
            return packaging


def get_date_exp(date_exp, date_exp_date):
        if date_exp == 'customer_specific_date':
            return date_exp_date
        else:
            return date_exp


def get_value(additional_insurance, value):
    if additional_insurance == True:
        value_exists = valid_input(value)
        if value_exists == True:
            value = value.replace('$','')
            value = value.replace(',','')

            try:
                value = float(value)
                return value
            except:
                return None
    else:
        return None


def get_additional_support(additional_support):
    print('ADDITIONAL SUPPORT: ', additional_support)
    if additional_support is not None:
        return additional_support
    else:
        return False


def get_ccode(ccode):
    if ccode is not None:
        ccode = ccode.upper()
        valid_ccode = check_c_codes(ccode)
        if valid_ccode == True:
            return ccode
        else:
            return None
    else:
        return None


def get_empcode(empcode):
    if empcode is not None:
        empcode = empcode.upper()
        valid_empcode = check_emp_codes(empcode)
        if valid_empcode == True:
            return empcode
        else:
            return None
    else:
        return None


def get_wcode(wcode):
    if wcode is not None:
        wcode = wcode.upper()
        valid_wcode = check_w_codes(wcode)
        if valid_wcode == True:
            return wcode
        else:
            return None
    else:
        return None


def prettify_strings(value):
    if isinstance(value, str):
        value = value.replace('_', ' ')
        value = string.capwords(value)
        return value
    else:
        return value
    

def create_quote_id(empcode,quote_date):
    quote_date = quote_date[2:-2]
    quote_id = empcode[:3] + quote_date
    quote_id = quote_id.replace('-', '')
    quote_id = quote_id.replace(':', '')
    quote_id = quote_id.replace(' ', '')

    quote_id = quote_id.upper()

    return quote_id

# returns a local time string for the email
def get_local_time(req_date, req_time, am_pm, timezone):
    date_valid = valid_input(req_date)
    time_valid = valid_input(req_time)
    am_pm_valid = valid_input(am_pm)
    timezone_valid = valid_input(timezone)

    if date_valid == True and time_valid == True and am_pm_valid == True and timezone_valid == True:
        local_date_string = create_local_date_strings(req_date, req_time, am_pm, timezone)
        return local_date_string
    else:
        return None
    

#returns the time in central for the quote date part of the email
def convert_utc_to_central_string(utc_time):
    """
    Convert a UTC datetime to Central time using the pytz module, and return it as a string with just the timezone abbreviation.
    
    Parameters:
    -----------
    utc_time : datetime.datetime
        The UTC datetime to convert
        
    Returns:
    --------
    str
        The Central datetime as a string with just the timezone abbreviation
    """
    # Define the UTC and Central timezones
    utc_tz = pytz.timezone('UTC')
    central_tz = pytz.timezone('US/Central')
    
    # Convert the UTC time to the Central timezone
    utc_time = utc_tz.localize(utc_time)
    central_time = utc_time.astimezone(central_tz)
    
    # Convert the Central time to a string with the timezone abbreviation
    central_time_str = central_time.strftime('%m/%d/%Y %H:%M %Z')
    
    return central_time_str


### returns string with capilatized letters
### for seven letters, customer codes, and warehouse codes
def capitalize_all(string):
    if string is None or len(string) == 0:
        return string
    else:
        return string.upper()
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


def add_warehousing_callbacks(dash):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON WAREHOUSING
    '''
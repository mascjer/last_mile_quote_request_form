#Libraries
import dash_bootstrap_components as dbc
import pandas as pd
import dash
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
from flask import Flask
from datetime import date
from dash import dash_table as dt
import pages.ui_assets as ui
from dash.exceptions import PreventUpdate
from pages.shared_callbacks import add_shared_callbacks


#Used for debugging with pandas
pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)


#Dash Components
app = Dash(__name__,
            title="Last Mile: Quote Request Form",
            external_stylesheets=[dbc.themes.SPACELAB],
            use_pages=True
           )

app.config.suppress_callback_exceptions = True

server = app.server


### dcc.Store allows us to store data on the client side.
### This is needed as if we store the data in dataframes
### in our docker container, when two people access the 
### app at the same time, they both end up manipulating
### the same DF. However, we need many data storages due
### to different requirements between air/euv and 
### first/final mile.

def serve_layout():
    return html.Div([
        dash.page_container,
    html.Br(),
    ui.create_footer(),

    #first data store for transmode
    dcc.Store(id='data-storage'),

    #first data storage for first/final mile items
    dcc.Store(id='data-storage-item'),

    #first/final data storage
    dcc.Store(id='data-storage-1'), # temp data storage for transmode/service
    dcc.Store(id='data-storage-ffm-display'), #data storage for display to user
    dcc.Store(id='data-storage-ffm-final'), #temp data storage for input into database
    dcc.Store(id='data-storage-ffm-prelim-scope'), #temp data storage for scope
    dcc.Store(id='data-storage-prelim-item'), #temp data storage for items
    dcc.Store(id='data-storage-scope-final', storage_type='session'), #data storage that holds scope data to be inputted into db
    dcc.Store(id='data-storage-item-final', storage_type='session'), #data storage that holds item data to be inputted into db
    dcc.Store(id='data-storage-final', storage_type='session'), #data storage that holds contextual data to be inputted into db

    #first data storage for items in air/euv
    dcc.Store(id='data-storage-ae-item'),

    #air/euv data storage
    dcc.Store(id='data-storage-ae-display'), #data storage for display to user
    dcc.Store(id='data-storage-ae-final'), #temp data storage for input into database
    dcc.Store(id="data-storage-ae-prelim-pick-scope"), #temp data storage for pick scope
    dcc.Store(id="data-storage-ae-prelim-drop-scope"), #temp data storage for drop scope
    dcc.Store(id='data-storage-final-session', storage_type='session'), #data storage that holds contextual data to be inputted into db
    dcc.Store(id='data-storage-pick-scope-final', storage_type='session'), #data storage that holds pick scope data to be inputted into db
    dcc.Store(id='data-storage-drop-scope-final', storage_type='session'), #data storage that holds drop scope data to be inputted into db
    dcc.Store(id='data-storage-ae-item-final', storage_type='session'), #data storage that holds item data to be inputted into db
])

app.layout = serve_layout()

add_shared_callbacks(app)

#run app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
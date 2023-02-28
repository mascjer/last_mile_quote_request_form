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



#### LastMileServicesQuoteForm.chrobinson.com URL?? ####

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
#app.enable_dev_tools(debug=True, dev_tools_hot_reload=False)
#app.css.config.serve_locally = True
#app.scripts.config.serve_locally = True


def serve_layout():
    return html.Div([
        dash.page_container,
    html.Br(),
    ui.create_footer()
])

app.layout = serve_layout()

add_shared_callbacks(app)



#run app
if __name__ == '__main__':
    #app.run_server(debug=True, use_reloader=False, host='0.0.0.0', port=8050)
    app.run_server(debug=True, host='0.0.0.0', port=8050)
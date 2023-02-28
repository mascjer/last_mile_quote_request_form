#Libraries
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import dash
from dash import Dash, dcc, html, dash_table, MATCH, ALL
from dash.dependencies import Input, Output, State
from flask import Flask
from datetime import date
from dash import dash_table as dt
import pages.ui_assets as ui
from dash.exceptions import PreventUpdate
from pages.non_callback_functions import *
from database_functions import *
from pages.dataframe_builder import *

#Used for debugging with pandas
pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)


def add_shared_callbacks(app):
    '''
    THESE CALLBACKS WILL ONLY APPEAR ON ALL OF THE QUOTES
    '''

    @app.callback(
        Output('air-btn','n_clicks'),
        Output('euv-btn','n_clicks'),
        Output('first-btn','n_clicks'),
        Output('final-btn','n_clicks'),
        Input('air-btn','n_clicks'),
        Input('euv-btn','n_clicks'),
        Input('first-btn','n_clicks'),
        Input('final-btn','n_clicks'),
    )
    def get_trans_mode(air, euv, first, final):
        
        clear_dataframe()

        trans_mode = None
        if air == 1 and euv+first+final == 0:
            trans_mode = 'air_expedite'
        if euv == 1 and air+first+final == 0:
            trans_mode = 'exclusive_use_vehicle'
        if first == 1 and air+euv+final == 0:
            trans_mode = 'first_mile'
        if final == 1 and air+euv+first == 0:
            trans_mode = 'final_mile'

        if trans_mode is not None:
            import_trans_mode(trans_mode)
        elif trans_mode != '':
            import_trans_mode(trans_mode)
        
        return 0,0,0,0


    @app.callback(
        Output("ccode-div","children"),
        Input("submit-btn","n_clicks"),
        State("ccode-input", "value"),
        State("empcode-input", "value"),
        State("additional-input", "value"),
        prevent_intial_call=True
    )
    def check_codes(n_clicks, ccode, empcode, additional):
        if n_clicks > 0:

            ccode_exists = valid_input(ccode)
            empcode_exists = valid_input(empcode)

            print(ccode_exists, empcode_exists)

            false_list = []

            if ccode_exists == False:
                false_list.append('C-Code')
                import_customer_code(None)
            else:
                ccode = ccode.upper()
                ccode_valid = check_c_codes(ccode)
                print(ccode_valid)
                if ccode_valid == False:
                    false_list.append('C-Code')
                    import_customer_code(None)
                else:
                    import_customer_code(ccode)

            if empcode_exists == False:
                false_list.append('Seven Letter')
                import_seven_letter(None)
            else:
                empcode = empcode.upper()
                empcode_valid = check_emp_codes(empcode)
                print(empcode_valid)
                if empcode_valid == False:
                    false_list.append('Seven Letter')
                    import_seven_letter(None)
                else:
                    import_seven_letter(empcode)

            str = 'Submit a valid: '
            combined_str = ', '.join(false_list)
            output_str = str+combined_str

            if ccode_exists == False or empcode_exists == False:
                return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            elif ccode_exists == True:
                ccode = ccode.upper()
                ccode_valid = check_c_codes(ccode)
                if ccode_valid == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            elif empcode_exists == True:
                empcode = empcode.upper()
                empcode_valide = check_emp_codes(empcode)
                if empcode_valide == False:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    return ''
            else:
                return ''
        else:
            return ''


    @app.callback(
        Output("freight-div","children"),
        Input("submit-btn","n_clicks"),
        State("quote-freight-drop", "value"),
    )
    def check_quote_freight(n_clicks, quote_freight):
        if n_clicks > 0:
            quote_freight_exists = valid_input(quote_freight)
            if quote_freight_exists == False:
                import_quote_or_on_hand(None)
                return html.P('Select quote only or freight on hand', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_quote_or_on_hand(quote_freight)
                return ''
        else:
            return ''


    @app.callback(
        Output("additional-support-div","children"),
        Input("submit-btn","n_clicks"),
        State("additional-support-checklist", "value"),
    )
    def check_quote_freight(n_clicks, additional_support):
        if n_clicks > 0:
            if additional_support is not None:
                if additional_support[0] == True:
                    import_additional_support(additional_support[0])
                    return ''
                else:
                    import_additional_support(False)
                    return ''
            else:
                import_additional_support(False)
                return ''
        else:
            return ''

    
    @app.callback(
        Output("freight-palletized-div","children"),
        Input("submit-btn","n_clicks"),
        State("palletized-radio", "value"),
    )
    def check_freight_palletized(n_clicks, palletized):
        if n_clicks > 0:
            palletized_exists = valid_input(palletized)
            if palletized_exists == False:
                import_is_palletized(None)
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_is_palletized(palletized)
                return ''
        else:
            return ''


    @app.callback(
        Output("commodity-div","children"),
        Input("submit-btn","n_clicks"),
        State("commodity-input", "value"),
    )
    def check_commodity(n_clicks, commodity):
        if n_clicks > 0:
            commodity_exists = valid_input(commodity)
            if commodity_exists == False:
                import_commodity(None)
                return html.P('Submit a valid commodity', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_commodity(commodity)
                return ''
        else:
            return ''


    @app.callback(
    Output("value-input","disabled"),
    Input("additional-insurance-radio","value"),
    prevent_intial_call=True
    )
    def additional_insurance_entry(additional_insurance):
        if additional_insurance is None:
            return True
        else:
            return not additional_insurance


    @app.callback(
        Output("additional-insurance-div","children"),
        Input("submit-btn","n_clicks"),
        State("additional-insurance-radio", "value"),
    )
    def check_additional_insurance(n_clicks, additional_insurance):
        if n_clicks > 0:
            additional_insurance_exists = valid_input(additional_insurance)
            if additional_insurance_exists == False:
                import_additional_insurance(None)
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0.5%'})
            else:
                import_additional_insurance(additional_insurance)
                return ''
        else:
            return ''


    @app.callback(
        Output("additional-insurance-div1","children"),
        Input("additional-insurance-radio", "value"),
    )
    def check_additional_insurance(additional_insurance):
        if additional_insurance == False:
            return html.P(['Unless additional insurance is purchased your load would be covered under', html.Br(), 'the standard cargo liability of 0.50 per lb at a max of $250 per shipment'], style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0.5%'})
        else:
            return []

    
    @app.callback(
        Output("value-div","children"),
        Input("submit-btn","n_clicks"),
        State("additional-insurance-radio", "value"),
        State("value-input", "value"),
    )
    def check_value(n_clicks, additional_insurance, value):
        output_str = 'Submit a valid value of the load'
        if n_clicks > 0:
            if additional_insurance == True:
                value_exists = valid_input(value)
                if value_exists == True:
                    value = value.replace('$','')
                    value = value.replace(',','')

                    try:
                        value = float(value)
                        import_value(value)
                        return ''
                    except:
                        import_value(None)
                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})

                else:
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
            else:
                import_value(None)
                return ''
        else:
            import_value(None)
            return ''


    @app.callback(
    Output("packaging-input","disabled"),
    Output("packaging-input","value"),
    Input("palletized-radio","value"),
    Input("packaging-input","value"),
    prevent_intial_call=True
    )
    def additional_pallet_entry(palletized, packaging):
        if palletized is None:
            return True, None
        else:
            if palletized == True:
                return palletized, None
            else:
                return palletized, packaging


    @app.callback(
        Output("packaging-div","children"),
        Input("submit-btn","n_clicks"),
        State("palletized-radio", "value"),
        State("packaging-input", "value"),
    )
    def check_packaging_type(n_clicks, palletized, packaging):
        output_str = 'Submit a valid packaging type'
        if n_clicks > 0:
            if palletized == False:
                packaging_exists = valid_input(packaging)
                if packaging_exists == False:
                    import_packaging(None)
                    return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})
                else:
                    import_packaging(packaging)
                    return ''
            else:
                import_packaging('pallet')
                return ''
        else:
            import_packaging(None)
            return ''



    @app.callback(
        Output("value-input", "value"),
        Input("additional-insurance-radio", "value"),
    )
    def clear_value(additional_insurance):
        if additional_insurance == False:
            return None


    @app.callback(
    Output("un-input","disabled"),
    Output("class-input","disabled"),
    Output("packing-input","disabled"),
    Input("hazmat-input","value"),
    prevent_intial_call=True
    )
    def hazmat_entry(hazmat):
        if hazmat is None:
            return [True, True, True]
        else:
            return [not hazmat, not hazmat, not hazmat]


    @app.callback(
        Output("shared-hazmat-div","children"),
        Input("submit-btn","n_clicks"),
        State("hazmat-input", "value"),
    )
    def check_hazmat(n_clicks, hazmat):
        if n_clicks > 0:
            hazmat_exists = valid_input(hazmat)
            if hazmat_exists == False:
                import_haz_mat(None)
                return html.P('Select yes or no', style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0.5%'})
            else:
                import_haz_mat(hazmat)
                return ''
        else:
            return ''


    @app.callback(
        Output("shared-special-hazmat-div","children"),
        Input("submit-btn","n_clicks"),
        State("hazmat-input", "value"),
        State("un-input", "value"),
        State("class-input", "value"),
        State("packing-input", "value"),
        State("un-input", "disabled"),
    )
    def check_hazmat_special(n_clicks, hazmat, un, cls, packing, un_dis):
        if n_clicks > 0:
            hazmat_exists = valid_input(hazmat)
            un_exists = valid_numeric_input(un)
            cls_exists = valid_numeric_input(cls)
            packing_exists = valid_numeric_input(packing)

            if hazmat_exists == True:
                if un_dis == False:
                    if un_exists == False or cls_exists == False or packing_exists == False:
                        false_list = []

                        if un_exists == False:
                            false_list.append('UN #')
                            import_un_num(None)
                        else:
                            import_un_num(un)

                        if cls_exists == False:
                            false_list.append('Class #')
                            import_class_num(None)
                        else:
                            import_class_num(cls)

                        if packing_exists == False:
                            false_list.append('Packing Group #')
                            import_pg_num(None)
                        else:
                            import_pg_num(packing)

                        str = 'Invalid entries: '
                        combined_str = ', '.join(false_list)
                        output_str = str+combined_str

                        return html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})

                    elif un_exists == True and cls_exists == True and packing_exists == True:
                        import_un_num(un)
                        import_class_num(cls)
                        import_pg_num(packing)
                        return ''
                    else:
                        return ''
                else:
                    import_un_num(None)
                    import_class_num(None)
                    import_pg_num(None)
                    return ''
            else:
                return ''
        else:
            return ''
    

    @app.callback(
        Output("un-input", "value"),
        Output("class-input", "value"),
        Output("packing-input", "value"),
        Input("un-input", "disabled"),
    )
    def clear_disabled(un_disabled):
        if un_disabled == True:
            return None, None, None


    @app.callback(
        Output('pieces-div', 'children'),
        Input('count-input', 'value'),
        State('pieces-div', 'children'),
        )
    def display_inputs(n_clicks, children):

        children = []

        for i in range(0,n_clicks):
            new_dropdown = html.Div([
                dbc.Row([
                            dbc.Col([
                                dbc.Label('#' + str(i+1) + ': ')
                            ], md=1),
                            dbc.Col([
                                dbc.Input(id={'type': 'quantity-input','index': i}, placeholder='Quantity', inputmode='numeric')
                            ], md=2),
                            dbc.Col([
                                dbc.Input(id={'type': 'weight-input','index': i}, placeholder='Weight (Pounds)', inputmode='numeric')
                            ], md=2),
                            dbc.Col([
                                dbc.Input(id={'type': 'length-input','index': i}, placeholder='Length (Inches)', inputmode='numeric')
                            ], md=2),
                            dbc.Col([
                                dbc.Input(id={'type': 'width-input','index': i}, placeholder='Width (Inches)', inputmode='numeric')
                            ], md=2),
                            dbc.Col([
                                dbc.Input(id={'type': 'height-input','index': i}, placeholder='Height (Inches)', inputmode='numeric')
                            ], md=2),
                        ]),
                        html.Div(id={'type': 'inputs-div','index': i})

            ])
                    
            children.append(new_dropdown)
            children.append(html.Br())

        return children


    @app.callback(
        Output({'type': 'inputs-div', 'index': ALL}, 'children'),
        Input("submit-btn","n_clicks"),
        State('count-input','value'),
        State({'type': 'weight-input', 'index': ALL}, 'value'),
        State({'type': 'length-input', 'index': ALL}, 'value'),
        State({'type': 'width-input', 'index': ALL}, 'value'),
        State({'type': 'height-input', 'index': ALL}, 'value'),
        State({'type': 'quantity-input', 'index': ALL}, 'value'),
    )
    def check_inputs(n_clicks, count, weight, length, width, height, quantity):
        if n_clicks > 0:
            item_list = []

            for i in range(0,count):
                weight_exists = valid_numeric_input(weight[i])
                length_exists = valid_numeric_input(length[i])
                width_exists = valid_numeric_input(width[i])
                height_exists = valid_numeric_input(height[i])
                quantity_exists = valid_numeric_input(quantity[i])

                if weight_exists == False or length_exists == False or width_exists == False or height_exists == False or quantity_exists == False:
                    false_list = create_false_list(quantity_exists, weight_exists, length_exists, width_exists, height_exists)

                    str = 'Invalid entries: '
                    combined_str = ', '.join(false_list)
                    output_str = str+combined_str
                    chunk_list = [html.P(output_str, style={'font-weight':'bold', 'color': 'red', 'margin-top':'0.5%', 'margin-bottom':'0%'})]
                else:
                    chunk_list = ['']
                
                item_list.append(chunk_list)

            return item_list
        else:
            return ''


    @app.callback(
    Output('container-output', 'children'),
    Output('output-prompt', 'hidden'),
    Input("submit-btn","n_clicks"),
    State('count-input','value'),
    State({'type': 'weight-input', 'index': ALL}, 'value'),
    State({'type': 'length-input', 'index': ALL}, 'value'),
    State({'type': 'width-input', 'index': ALL}, 'value'),
    State({'type': 'height-input', 'index': ALL}, 'value'),
    State({'type': 'quantity-input', 'index': ALL}, 'value'),
    )
    def display_output(n_clicks, count, weight, length, width, height, quantity):
        if n_clicks > 0:
            item_list = []

            for i in range(0,count):
                weight_exists = valid_numeric_input(weight[i])
                length_exists = valid_numeric_input(length[i])
                width_exists = valid_numeric_input(width[i])
                height_exists = valid_numeric_input(height[i])
                quantity_exists = valid_numeric_input(quantity[i])

                if weight_exists == False:
                    weight[i] = '***Invalid***'
                if length_exists == False:
                    length[i] = '***Invalid***'
                if width_exists == False:
                    width[i] = '***Invalid***'
                if height_exists == False:
                    height[i] = '***Invalid***'
                if quantity_exists == False:
                    quantity[i] = '***Invalid***'

                chunk_list = ['temp_id',  quantity[i], weight[i], length[i], width[i], height[i]]
                item_list.append(chunk_list)

            item_df = pd.DataFrame(item_list, columns = ['QUOTE_ID', 'QUANTITY', 'WEIGHT', 'LENGTH', 'WIDTH', 'HEIGHT'])
            retrieve_item_df(item_df)

            return html.Div([
                html.Div([
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label(str(i+1))
                                ],md= 1),
                                dbc.Col([
                                    dbc.Label(str(quantity[i]) )
                                ],md= 2),
                                dbc.Col([
                                    dbc.Label(str(weight[i]))
                                ],md= 2),
                                dbc.Col([
                                    dbc.Label(str(length[i]) )
                                ],md= 2),
                                dbc.Col([
                                    dbc.Label(str(width[i]) )
                                ],md= 2),
                                dbc.Col([
                                    dbc.Label(str(height[i]) )
                                ],md= 2),
                            ])
                        ], md=11)
                    ])
                ])
                for i in range(0,count)
            ]), False
        else:
            return '', True


    app.clientside_callback(
        """
        function(clicks, elemid) {
            document.getElementById(elemid).scrollIntoView({
            behavior: 'smooth'
            });
        }
        """,
        Output('garbage-output-0', 'children'),
        [Input('submit-btn', 'n_clicks')],
        [State('quote-card-div', 'id')]
    )
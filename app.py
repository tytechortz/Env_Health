from dash import Dash, html, dcc, Input, Output, State, ctx, dash_table
import dash_bootstrap_components as dbc
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from geopandas.tools import sjoin
import dash_ag_grid as dag
import json

from utils import (
    get_tract_data,
    get_block_data,
    get_block_group_data,
    get_restaurants
)

from figures_utilities import (
    get_figure
)

# columnDefs = [
#     {"field": "profileid", "headerName": "CDCID"},
#     {"field": "first_name"},
#     {"field": "geocoded_latitude"},
#     {"field": "geocoded_longitude"},
#     {
#         "field": "reporteddate",
#         "filter": "agDateColumnFilter",
#         "valueGetter": {"function": date_obj},
#         "valueFormatter": {"function": f"d3.timeFormat('%m/%d/%Y')({date_obj})"},
#     }
# ]
# df = selected_facilities

def get_facilities():
        restaurants = get_restaurants()
        restaurants = gpd.GeoDataFrame(restaurants,
            geometry = gpd.points_from_xy(restaurants['lon'], restaurants['lat']))
        restaurants = restaurants.set_crs('epsg:4269')
        return restaurants

# app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
app = Dash(__name__, suppress_callback_exceptions=True)


header = html.Div("Arapahoe County EH", className="h2 p-2 text-white bg-primary text-center")

bgcolor = "#f3f3f1"  # mapbox light map land color

template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }

# grid = dag.AgGrid(
#     id="case-grid",
#     # columnDefs=[{"headerName": i, "field": i, "editable": False} for i in case_df.columns],
#     columnDefs = columnDefs,
#     rowData=case_df.to_dict("records"),
#     dashGridOptions={"rowSelection": "muiltiple"},
#     # columnSize="sizeToFit",
#     defaultColDef={"resizable": True, "sortable": True, "filter": True},
#     csvExportParams={
#                 "fileName": "ag_grid_test.csv",
#             },  
# )

app.layout = dbc.Container([
    header,
    dbc.Row([
        html.Div([
            dbc.Card(
                dcc.Graph(id='sa-map', figure=blank_fig(500))),
        ]),
    ]), 
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id="geometry",
                options=[
                    {"label": i, "value": i}
                    for i in ["Blocks", "Block Groups", "Tracts"]
                ],
                value="Tracts",
                inline=True
            ),
        ], width=2),
        dbc.Col([
            dcc.Dropdown(
                id="tracts",
                # options=[
                #     {"label": i, "value": i}
                #     for i in all_tracts
                # ],
                multi=True,
                style={"color": "black"},
                value=(),
            ),
            # dcc.Dropdown(id='graph-type')
        ], width=8),
        dbc.Col([
                dcc.Slider(0, .5, value=.5,
                    marks={
                        0: {'label': 'Light', 'style': {'color': 'white'}},
                        .5: {'label': 'Dark', 'style': {'color': 'white'}},
                    },
                    id = 'opacity',
                ),
            ], width=2),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='tract-stats')
        ], width=4)
    ]),
    dbc.Row([
        html.Div(id='datatable'),
    ]),  
    dcc.Store(id='geo-data', storage_type='memory'),
    dcc.Store(id='all-tracts', storage_type='memory'),
    dcc.Store(id='gt-json', storage_type='memory'),
    dcc.Store(id='facilities', storage_type='session'),
])

@app.callback(
        Output('datatable-interactivity', 'data'),
        Output('datatable-interactivity', 'columns'),
        Input('facilities', 'data'),
        Input('gt-json', 'data'))
def get_facility_table(sel_data, gt_json):
    df = gpd.read_file(sel_data)
    gtj = gpd.read_file(gt_json)
    if  df.empty:
        df1 = pd.DataFrame(columns=['Permit Name', 'Address'])
        data = df1.to_dict('records')
        columns=[
            {"name": i, "id": i} for i in df1.columns
        ]
    else:
        df['id'] = df['Permit Name']
        df1 = df[['Permit Name', 'Address']]
       

        data = df1.to_dict('records')
        
        columns=[
            {"name": i, "id": i} for i in df1.columns
        ]


    return data, columns

@app.callback(
        Output('datatable', 'children'),
        Input('opacity', 'value'),
)
def display_facility_table(data):
    


    return dash_table.DataTable(id='datatable-interactivity', 
        data=[{}],
        columns=[{'name': 'Permit Name', 'id': 'Permit Name'}, {'name': 'Address', 'id': 'Address'}],
        # style_cell_conditional=[
        #     {'if': {'column_id': 'Permit Name'},
        #     'width':'100px'},
            # {'if': {'column_id': 'TMAX'},
            # 'width':'100px'},
            # {'if': {'column_id': 'TMIN'},
            # 'width':'100px'},
        # ],
        # style_data_conditional=[
        #     {
        #     'if': {'row_index': 'odd'},
        #     'backgroundColor': 'rgb(248, 248, 248)'
        #     },
        # ],
        style_header={
        'backgroundColor': 'rgb(30, 30, 30)',
        'fontWeight': 'bold',
        'color': 'white'
        },
        # editable=True,
        # filter_action="native",
        sort_action="native",
        sort_mode="multi",
        # column_selectable="single",
        # selected_columns=[],
        # selected_rows=[],
        # page_action="native",
        page_current= 0,
        page_size= 30,
        # columns=columns,
        # fixed_rows={'headers': False, 'data': 0}
        # columns=[{}],
        style_data={
            'backgroundColor': 'rgb(30,30,30)',
            'color':'white'
        }
    )



@app.callback(
        Output('tract-stats', 'children'),
        Input('geometry', 'value'),
        Input('gt-json', 'data'),
        Input('facilities', 'data'))
def get_tract_stats(geometry, gt_json, facilities):
    gtj = gpd.read_file(gt_json)
    fac = gpd.read_file(facilities)

    if gtj.empty:
        tot_pop=0
    else:
        tot_pop = gtj['Total'].sum()
    # print(tot_pop)


    return html.Div([
        dbc.Card(html.H6('Total Selected Pop = {}'.format(tot_pop)))
    ])

@app.callback(
        Output('geo-data', 'data'),
        Output('all-tracts', 'data'),
        Input('geometry', 'value'))
def get_geo_data(geometry):
    if geometry == 'Tracts':
        geo_df = get_tract_data()
        all_tracts = geo_df["GEOID"].values
        # print(all_tracts)
        tract_list_df = pd.DataFrame(all_tracts, columns=['tracts'])
        # print(tract_list_df)
    elif geometry == 'Block Groups':
        geo_df = get_block_group_data()
        # print(geo_df)
        all_tracts = geo_df["GEOID"].values
        tract_list_df = pd.DataFrame(all_tracts, columns=['tracts'])
    elif geometry == 'Blocks':
        geo_df = get_block_data()
        all_tracts = geo_df["GEOID"].values
        tract_list_df = pd.DataFrame(all_tracts, columns=["tracts"])
    return geo_df.to_json(), tract_list_df.to_json()

@app.callback(
        Output('tracts', 'options'),
        Input('geometry', 'value'),
        Input('all-tracts', 'data'))
def tract_options(geometry, tracts):
    all_tracts = pd.read_json(tracts)
    # print(type(tracts))
    options = ()
    
    options = [{'label': i, 'value': i} for i in all_tracts['tracts']]
    

    return options 


@app.callback(
        Output("tracts", "value"),
        Input("sa-map", "clickData"),
        Input("sa-map", "selectedData"),
        State("tracts", "value"),
        State("sa-map", "clickData")
)

def update_tract_dropdown(clickData, selectedData, tracts, clickData_state):

    if ctx.triggered[0]["value"] is None:
        return tracts
   
    changed_id = [p["prop_id"] for p in ctx.triggered][0]
    

    if clickData is not None and "customdata" in clickData["points"][0]:
        tract = clickData["points"][0]["customdata"]
        # print(tract)
        if tract in tracts:
            tracts.remove(tract)
        elif len(tracts) < 10:
            tracts.append(tract)
    
  
    return tracts


@app.callback(
    Output("sa-map", "figure"),
    Output('gt-json', 'data'),
    Output('facilities', 'data'),
    Input("geo-data", "data"),
    Input("geometry", "value"),
    Input("tracts", "value"),
    Input("opacity", "value"))
def update_Choropleth(geo_data, geometry, tracts, opacity):

   

    if geometry == "Block Groups":
        df = get_block_group_data()
        geo_data = gpd.read_file(geo_data)
        # print(df)

    elif geometry == "Blocks":
        df = get_block_data()
        
        geo_data = gpd.read_file(geo_data)
    elif geometry == "Tracts":
        df = get_tract_data()
        # print(df['geometry'])
        geo_data = gpd.read_file(geo_data)
       
    geo_tracts_highlights = ()
    # print(geo_data)
    if tracts != None:
        restaurants = get_facilities()
        geo_tracts_highlights = df[df['GEOID'].isin(tracts)]
        rl = sjoin(restaurants, geo_data, how='inner')
        rls = rl[rl['GEOID'].isin(tracts)]
     
        
    
    fig = get_figure(df, geo_data, rl, geo_tracts_highlights, opacity)

    return fig, geo_tracts_highlights.to_json(), rls.to_json()

if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
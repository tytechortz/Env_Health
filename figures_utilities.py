import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import geopandas as gpd


def get_Choropleth(df, geo_data, rl, marker_opacity, marker_line_width, marker_line_color, fig=None):
    # print(rl.columns)
    if fig is None:
        fig = go.Figure()

    fig.add_trace(
        go.Choroplethmapbox(
            geojson=eval(geo_data['geometry'].to_json()),
            locations=df.index,
            z=df['STATEFP'],
            marker_opacity = marker_opacity,
            marker_line_width = marker_line_width,
            marker_line_color = marker_line_color,
            customdata=df["GEOID"],
            hoverinfo='z',
            coloraxis='coloraxis'
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=rl['lat'],
            lon=rl['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=5,
                color='black',
            ),
            showlegend=False
        )
    )

    return fig


def get_map(df):

    fig = go.Figure()
  
    return fig


def get_figure(df, geo_data, rl, geo_tracts_highlights, opacity):

    # print(df)
    fig = get_Choropleth(df, geo_data, rl, marker_opacity=opacity,
                         marker_line_width=1, marker_line_color='#6666cc')
    
    
    fig.update_layout(mapbox_style="carto-positron", 
                            mapbox_zoom=10.4,
                            # mapbox_layers=layer,
                            mapbox_center={"lat": 39.65, "lon": -104.8},
                            margin={"r":0,"t":0,"l":0,"b":0},
                            autosize=True,
                            coloraxis_showscale=False,
                            uirevision='constant'),
    
                        
    
    if len(geo_tracts_highlights) != 0:
        fig = get_Choropleth(df, geo_tracts_highlights, rl, marker_opacity=1.0,
                             marker_line_width=3, marker_line_color='aqua', fig=fig)
    

    return fig
#My project is recommended to be run on zoom 75% or less
import dash
from dash import dcc, html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px
#______________________________________________________
#Creatint the function to do data cleaning
def data_cleaning(COVID):
    if COVID.isnull().values.any():  # checking if there are any null values
        # In order to use rows with NAN values, instead of deleting them, author replaces them with "No province" which will allowed to group them by provinces
        for i in COVID:
            if COVID[i].isnull().values.any():
                # For every Column NAN value must be replaced with its unique value
                if COVID[i].name == "Confirmed":
                    COVID.Confirmed = COVID_2022.Confirmed.fillna("0")
                if COVID[i].name == "Deaths":
                    COVID.Deaths = COVID_2022.Deaths.fillna("0")
                if COVID[i].name == "Recovered":
                    COVID.Recovered = COVID_2022.Recovered.fillna("0")
            if COVID[i].sum() == 0:
                del COVID[i]
        print("All NAN values were replaced by status")
    else:
        print("There are no NAN values in the data")
    return COVID
#______________________________________________________
#importing the Coronavirus tables and cutting off the data which is not needed
COVID_2022 = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/12-05-2022.csv')[['Lat','Long_','Country_Region', 'Confirmed', 'Deaths','Recovered']]
COVID_2021 = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/12-06-2021.csv')[['Lat','Long_','Country_Region', 'Confirmed', 'Deaths','Recovered']]
COVID_2020 = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/12-06-2020.csv')[['Lat','Long_','Country_Region', 'Confirmed', 'Deaths','Recovered']]
#______________________________________________________
#Cleaning the data
COVID_2022 = data_cleaning(COVID_2022)
COVID_2021 = data_cleaning(COVID_2021)
COVID_2020 = data_cleaning(COVID_2020)
#_______________________________
#Functions for DRY code (Don't repeat yourself)
def get_Map(covid_date):
    map_center = dict(lat=49.8175, lon=15.473)  # doing Czech Republic as a center of the map
    hover_data = {
        'Lat': False,
        'Long_': False,
        'Confirmed': True,
        'Deaths': True
    }  # showing data in the hover, cutting off latitude and longitude data
    hover_name = 'Country_Region'  # showing country name in the hover
    fig = px.scatter_mapbox(covid_date, lat="Lat", lon="Long_", hover_name=hover_name, hover_data=hover_data, zoom=3, #zooming in the map
                            color='Confirmed', size='Confirmed', color_continuous_scale=px.colors.cyclical.IceFire, #coloring the map
                            height=600, size_max=20, center=map_center, # sizing the map
                            title=f'COVID-19 data', labels={'Confirmed': 'Confirmed cases'}, # adding title and labels
                            template='plotly_dark',mapbox_style="carto-positron"  # adding style
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 60, "l": 10, "b": 10}, title_x=0.5, #adding margins and title position
                      title_font_size=20, title_font_color='Red') #adding title font
    return fig

def get_graph(graph_type, covid_date, column):
    fig = graph_type(covid_date, x='Country_Region', y=column, title='COVID-19 graph',  #adding main data
                     labels={column: f'{column} cases'}, template='plotly_dark') #adding labels
    fig.update_layout(title_x=0.5,title_font_color="red", title_font_size=20)  # Setting style of the title
    return fig
def get_pie(covid_date, column):
    fig = px.pie(covid_date, values=column, names='Country_Region', title='COVID-19 circle',  #adding title
                 labels={column: f'{column} cases'}, template='plotly_dark', height=1200)#adding labels
    fig.update_layout(title_x=0.5, title_font_color="red", title_font_size=20)  # Setting style of the title
    fig.update_traces(textposition='inside', textinfo='percent+label') #positioning the text inside the pie
    return fig
#_______________________________
#Creating core body,which will contain all graphs and items
app = dash.Dash()
app.layout = html.Div(children=[ #creating the layout in html.Div
# Creating the header with total cases and deaths
    html.Div(children=[
        html.H1(children='COVID-19 data', style={'color': 'red', 'text-align': 'center', 'font-size': '25px'}), #adding title
        html.Div(children=[
            html.Div(children=[
                html.H2(children='Total cases', style={'color': 'red', 'text-align': 'center', 'font-size': '15px'}), #adding title
                html.H1(children=COVID_2022['Confirmed'].sum(), style={'color': 'red', 'text-align': 'center', 'font-size': '25px'},id ='Total Cases'), #adding total cases
            ], style={'width': '50%', 'display': 'inline-block'}),
            html.Div(children=[
                html.H2(children='Total deaths', style={'color': 'red', 'text-align': 'center', 'font-size': '15px'}), #adding title
                html.H1(children=COVID_2022['Deaths'].sum(), style={'color': 'red', 'text-align': 'center', 'font-size': '25px'}, id = 'Total Deaths'), #adding total deaths
            ], style={'width': '50%', 'display': 'inline-block'}),
        ], style={'width': '100%', 'display': 'inline-block'}),
    ], style={'width': '100%', 'display': 'inline-block'}),
dcc.Graph( # map with all data
    id='map'
),
dcc.RadioItems( # Radio Buttons to chose in what year Coronavirus graph and map will show data
    options=[
        {'label': 'COVID-19 data at 2022', 'value': 'COVID_2022'},
        {'label': 'COVID-19 data at 2021', 'value': 'COVID_2021'},
        {'label': 'COVID-19 data at 2020', 'value': 'COVID_2020'},
    ],
    value='COVID_2022',
    id='radio_map'
),
dcc.Dropdown( # Dropdown for a graph that allows to choose which data will be related
    options=[
        {'label': 'Country Region to Infection Cases', 'value': 'Country_Cases'},
        {'label': 'Country Region to Deaths Cases', 'value': 'Country_Deaths'},
    ],
    style={'backgroundColor': '#7FDBFF', 'font-size': '20px', 'color': 'black'}, #adding style to the dropdown
    value='Country_Cases',
    id='dropdown_graph'
),
dcc.RadioItems( # Allows to change graph view mode
    options=[
        {'label': 'Line', 'value': 'line'},
        {'label': 'Histogram', 'value': 'hist'},
        {'label': 'Scatter', 'value': 'scatter'},
        {'label': 'Pie', 'value': 'pie'},
    ],
    value='line',
    id='radio_graph'
),
dcc.Graph( # graph with data
    id='graph'
),
], style = {'backgroundColor': '#111111', 'color': '#7FDBFF', 'margin': '-10px'})
#adding black background color and cyan text color to Radio buttons and removing indents from the layout
#_______________________________
#decorator for map
@app.callback(
    Output('map', 'figure'),
    Input('radio_map', 'value'))
#updating the map
def update_graph(radio):
    if radio == 'COVID_2022':
          return get_Map(COVID_2022)
    elif radio == 'COVID_2021':
        return get_Map(COVID_2021)
    elif radio == 'COVID_2020':
        return get_Map(COVID_2020)
#_______________________________
#decorator for total cases and deaths
@app.callback(
    Output('Total Cases', 'children'),
    Output('Total Deaths', 'children'),
    Input('radio_map', 'value'))
#updating the total cases and deaths
def update_graph(radio):
    if radio == 'COVID_2022':
        return COVID_2022['Confirmed'].sum(), COVID_2022['Deaths'].sum()
    elif radio == 'COVID_2021':
        return COVID_2021['Confirmed'].sum(), COVID_2021['Deaths'].sum()
    elif radio == 'COVID_2020':
        return COVID_2020['Confirmed'].sum(), COVID_2020['Deaths'].sum()
#_______________________________
#_______________________________
#decorator for graph
@app.callback(
    Output('graph', 'figure'),
    Input('radio_map', 'value'),
    Input('radio_graph', 'value'),
    Input('dropdown_graph', 'value'))
#updating the graph
def update_graph(year, graph_type, dropdown):
    if year == 'COVID_2022':
        if dropdown == 'Country_Cases':
            if graph_type == 'line':
                return get_graph(px.line, COVID_2022, 'Confirmed')
            elif graph_type == 'hist':
                return get_graph(px.histogram, COVID_2022, 'Confirmed')
            elif graph_type == 'scatter':
                return get_graph(px.scatter, COVID_2022, 'Confirmed')
            elif graph_type == 'pie':
                return get_pie(COVID_2022, 'Confirmed')
        elif dropdown == 'Country_Deaths':
            if graph_type == 'line':
                return get_graph(px.line, COVID_2022, 'Deaths')
            elif graph_type == 'hist':
                return get_graph(px.histogram, COVID_2022, 'Deaths')
            elif graph_type == 'scatter':
                return get_graph(px.scatter, COVID_2022, 'Deaths')
            elif graph_type == 'pie':
                return get_pie(COVID_2022, 'Deaths')
    elif year == 'COVID_2021':
        if dropdown == 'Country_Cases':
            if graph_type == 'line':
                return get_graph(px.line, COVID_2021, 'Confirmed')
            elif graph_type == 'hist':
                return get_graph(px.histogram, COVID_2021, 'Confirmed')
            elif graph_type == 'scatter':
                return get_graph(px.scatter, COVID_2021, 'Confirmed')
            elif graph_type == 'pie':
                return get_pie(COVID_2021, 'Confirmed')
        elif dropdown == 'Country_Deaths':
            if graph_type == 'line':
                return get_graph(px.line, COVID_2021, 'Deaths')
            elif graph_type == 'hist':
                return get_graph(px.histogram, COVID_2021, 'Deaths')
            elif graph_type == 'scatter':
                return get_graph(px.scatter, COVID_2021, 'Deaths')
            elif graph_type == 'pie':
                return get_pie(COVID_2021, 'Deaths')
    elif year == 'COVID_2020':
        if dropdown == 'Country_Cases':
            if graph_type == 'line':
                return get_graph(px.line, COVID_2020, 'Confirmed')
            elif graph_type == 'hist':
                return get_graph(px.histogram, COVID_2020, 'Confirmed')
            elif graph_type == 'scatter':
                return get_graph(px.scatter, COVID_2020, 'Confirmed')
            elif graph_type == 'pie':
                return get_pie(COVID_2020, 'Confirmed')
        elif dropdown == 'Country_Deaths':
            if graph_type == 'line':
                return get_graph(px.line, COVID_2020, 'Deaths')
            elif graph_type == 'hist':
                return get_graph(px.histogram, COVID_2020, 'Deaths')
            elif graph_type == 'scatter':
                return get_graph(px.scatter, COVID_2020, 'Deaths')
            elif graph_type == 'pie':
                return get_pie(COVID_2020, 'Deaths')
#_______________________________
#running the app
app.run_server(debug=True)

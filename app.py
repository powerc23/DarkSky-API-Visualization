import dash
import dash_core_components as dcc
import dash_html_components as html
import api_data
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from darksky import forecast
import pytz
from datetime import datetime

#CSS stylesheet taken from https://codepen.io/chriddyp/pen/bWLwgP.css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Creating tab styles
#Code from
tabs_styles = {
    'height': '100px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}
__name__='__main__'

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Layout structure with Dash Core Components
app.layout = html.Div(children=[

            html.H1(children='Weather Data and Forecasts',style={'color':'blue'}),
            html.H3(children='If data does not appear, please refresh your browser.'),
            html.Label(style={'color': 'red'},children='''
                Please note that this dashboard is limited to 1,000 free API calls per day.
            '''),
            html.Label(id='call-number',style={'color': 'black'}),
            html.Label([html.A('Powered by Dark Sky', href='https://darksky.net/poweredby/')]),

            html.Div([
                html.Div([
                    html.Div(id='city-select',children='''
                        Please select a city.
                    '''),
                    dcc.Dropdown(
                        id='cities-dropdown',
                        options=[{'label':i, 'value':i} for i in sorted(api_data.coords)],
                        value = 'Dublin',
                        style={'width': '50%', 'display': 'inline-block'}
                        ),
                    html.Div(children='''
                        Please select unit type.
                    '''),
                    dcc.RadioItems(
                        id='unit-type',
                        options=[
                        {'label': 'International System of Units (SI)', 'value': 'si'},
                        {'label': 'Imperial Units (US)', 'value': 'us'},
                        ],
                        value='si',
                        style={'width': '50%', 'display': 'inline-block'}
                    ),dcc.Graph(id='summary-table'),
                ],className="six columns"),
                html.Div([
                    html.Div(children='''
                            Please select data for chart.
                        '''),
                    dcc.RadioItems(
                        id='choose-data',
                        options=[
                            {'label': 'Humidity', 'value': 'humidity'},
                            {'label': 'Chance of Precipitation', 'value': 'rain_chance'},
                        ],
                        value='humidity',
                        style={'width': '50%', 'display': 'inline-block'}
                    ),
                    dcc.Graph(id ='percent-chart'),
                ],className="six columns"),
            ],className="row"),

            html.H3(children='Temperature Forecasts',style={'color':'blue'}),
            html.Div(children='''
                    Please select forecast type.
            '''),
            dcc.RadioItems(
                id='forecast-type',
                options=[
                    {'label': 'Hourly (48 hours)', 'value': 'hourly'},
                    {'label': 'Daily (7 days)', 'value': 'daily'},
                ],
                value='hourly',
                style={'width': '50%', 'display': 'inline-block'}
            ),
            dcc.Graph(id='temp-graph'),
            html.H3(children='Wind Speed Forecasts',style={'color':'blue'}),
            html.Div(id='wind-comparison',children='''
                    Please select a city for wind speed comparison.
            '''),
            dcc.Dropdown(
                id='cities-dropdown2',
                options=[{'label':i, 'value':i} for i in sorted(api_data.coords)],
                value = 'Dublin',
                style={'width': '50%', 'display': 'inline-block'}
            ),
            dcc.Graph(id='wind-graph')

])

#Updating temperature line plot
@app.callback(
    Output('temp-graph','figure'),
    [Input('cities-dropdown', 'value'),Input('unit-type','value'),Input('forecast-type','value')]
)

def update_temp_graph(value,unit,type):

    if value is None:
        #Setting Dublin as default value if drop down selection is empty
        data = forecast(*(api_data.coords.get('Dublin')),units=unit)
    else:
        data = forecast(*(api_data.coords.get(value)),units=unit)

    forecast_labels = []
    cur_temp = data.temperature
    timezone = pytz.timezone(data.timezone)

    if type == 'hourly':
        title = 'Hourly Temperature Forecasts (next 48 hours)'
        num_of_forecasts = len(data.hourly)
        # Creating list of time labels for forecasts in unix time format
        labels = [values.time for values in data.hourly[:num_of_forecasts]]

        # Converting unix time labels to date - time format
        for j in labels:
            time_format = pytz.UTC.localize(datetime.utcfromtimestamp(j))
            time_j = time_format.astimezone(timezone)
            forecast_labels.append(time_j.strftime("%D %H:%M"))

        # Creating list of hourly temperature forecasts
        temp_forecasts = [time.temperature for time in data.hourly[:num_of_forecasts]]
        trace1 = go.Scatter(x=forecast_labels, y=temp_forecasts,
                            mode='lines+markers', name='Temperature Forecast')
        trace2 = go.Scatter(x=[forecast_labels[0], forecast_labels[num_of_forecasts - 1]], y=[cur_temp, cur_temp],
                            mode='lines+markers', name='Current Temperature')
        temp_data = [trace1, trace2]
    else:
        title = 'Daily Temperature Forecasts (next 7 days)'
        num_of_forecasts = len(data.daily)
        # Creating list of time labels for forecasts in unix time format
        labels = [values.time for values in data.daily[:num_of_forecasts]]

        # Converting unix time labels to date - time format
        for j in labels:
            time_format = pytz.UTC.localize(datetime.utcfromtimestamp(j))
            time_j = time_format.astimezone(timezone)
            forecast_labels.append(time_j.strftime("%D"))

        # Creating lists of daily max and min temperature forecasts
        max_temp_forecasts = [time.temperatureMax for time in data.daily[:num_of_forecasts]]
        min_temp_forecasts = [time.temperatureMin for time in data.daily[:num_of_forecasts]]
        trace1 = go.Scatter(x=forecast_labels, y=max_temp_forecasts,
                            mode='lines+markers', name='Max Temperature Forecast')
        trace2 = go.Scatter(x=[forecast_labels[0], forecast_labels[num_of_forecasts - 1]], y=[cur_temp, cur_temp],
                            mode='lines+markers', name='Current Temperature')
        trace3 = go.Scatter(x=forecast_labels, y=min_temp_forecasts,
                            mode='lines+markers', name='Min Temperature Forecast')
        temp_data = [trace1, trace2,trace3]


    if unit=="si":
        temp_y_label = 'Temperature (degrees Celsius)'
    else:
        temp_y_label = 'Temperature (degrees Fahrenheit)'



    temp_layout = go.Layout(title=title,
                       xaxis=dict(title='Time',tickangle=45),
                       yaxis=dict(title=temp_y_label),
                       font=dict(size=10))

    return {
        'data': temp_data,
        'layout': temp_layout,
    }

#Updating wind speed bar chart
@app.callback(
    Output('wind-graph','figure'),
    [Input('cities-dropdown', 'value'),Input('unit-type','value'),Input('cities-dropdown2','value')]
)

def update_wind_graph(value,unit,city):

    if value is None:
        #Setting Dublin as default value if drop down selection is empty
        data = forecast(*(api_data.coords.get('Dublin')),units=unit)
        value = 'Dublin'
    else:
        data = forecast(*(api_data.coords.get(value)),units=unit)

    if city is None:
        compare_data = forecast(*(api_data.coords.get('Dublin')),units=unit)
        city = 'Dublin'
    else:
        compare_data = forecast(*(api_data.coords.get(city)),units=unit)

    num_of_forecasts = len(data.hourly)

    if unit=="si":
        wind_y_label = 'Wind Speed (metres per second)'
    else:
        wind_y_label = 'Wind Speed (miles per hour)'

    # Creating list of time labels for forecasts in unix time format
    labels = [values.time for values in data.hourly[:num_of_forecasts]]

    # Converting unix time labels to date - time format
    forecast_labels = []
    timezone = pytz.timezone(data.timezone)

    for j in labels:
        time_format = pytz.UTC.localize(datetime.utcfromtimestamp(j))
        time_j = time_format.astimezone(timezone)
        forecast_labels.append(time_j.strftime("%D %H:%M"))


    #Wind Speed Forecast Bar Chart
    wind_forecasts = [hour.windSpeed for hour in data.hourly[:num_of_forecasts]]
    wind_forecasts_comparison = [hour.windSpeed for hour in compare_data.hourly[:num_of_forecasts]]
    wind_title = 'Hourly Wind Speed Forecasts (next 48 hours)'
    wind_speed_trace1 = go.Bar(
        x=forecast_labels,
        y=wind_forecasts,
        name='Wind Speed in '+value,
        marker=dict(
            color='rgb(49,130,189)'
        )
    )

    wind_speed_trace2 = go.Bar(
        x=forecast_labels,
        y=wind_forecasts_comparison,
        name='Wind Speed in '+city,
        marker=dict(
            color='rgb(189,48,48)'
        )
    )

    #Only using comparison data if selected city is different to current city
    if city != value:
        wind_data = [wind_speed_trace1, wind_speed_trace2]
    else:
        wind_data = [wind_speed_trace1]

    wind_layout = go.Layout(
        xaxis=dict(tickangle=45,title='Time in '+value),
        yaxis=dict(title=wind_y_label),
        barmode='group',
        title=wind_title,
        font=dict(size=10),
        showlegend=True,
    )

    return {
        'data':wind_data,
        'layout':wind_layout
    }

#Updating percentage chart, with either humidity or chance of rain data
@app.callback(
    Output('percent-chart','figure'),
    [Input('cities-dropdown','value'),Input('choose-data', 'value')]
)

def update_pie_chart(value,dataType):

    if value is None:
        #Setting Dublin as default value if drop down selection is empty
        data = forecast(*(api_data.coords.get('Dublin')),units='si')
    else:
        data = forecast(*(api_data.coords.get(value)),units='si')

    if dataType == 'humidity':
        #Round value to two decimal places
        measure = round(data.humidity,2)
        title= 'Current Humidity'
    else:
        #Round value to two decimal places
        measure = round(data.precipProbability,2)
        title = "Chance of Precipitation"

    percentage_chart = {

            "values": [measure, (1 - measure)],
            "labels": ["{:.2%}".format(measure), " "],
            "marker": {
                'colors': [
                    'rgb(89,137,233)',
                    'rgb(228,219,219)'
                ]
            },
            "domain": {"x": [0, 0.4]},
            "name": "Gauge",
            "hole": .7,
            "type": "pie",
            "direction": "clockwise",
            "showlegend": False,
            "textinfo": "label",
            "textposition": "auto",
            "hoverinfo": "none"
        }

    percentage_layout = {
            'title': {
                'text': title,
                'x': 0.06,
                'y': 0.9,
                "font": {
                    "size": 30
                }
            },
            'xaxis': {
                'showticklabels': False,
                'showgrid': False,
                'zeroline': False,
            },
            'yaxis': {
                'showticklabels': False,
                'showgrid': False,
                'zeroline': False,
            },

            # Add percentage value to centre of pie chart
            'annotations': [
                {
                    "font": {
                        "size": 25
                    },
                    "showarrow": False,
                    "text": "{:.2%}".format(measure),
                    "x": 0.12,
                    "y": 0.5
                }
            ]
        }

    return {
        'data': [percentage_chart],
        'layout': percentage_layout
    }

#Updating summary table
@app.callback(
    Output('summary-table','figure'),
    [Input('cities-dropdown', 'value'),Input('unit-type','value')]
)

def update_summary_table(value,unit):

    if value is None:
        #Setting Dublin as default value if drop down selection is empty
        data = forecast(*(api_data.coords.get('Dublin')),units=unit)
        value = 'Dublin'
    else:
        data = forecast(*(api_data.coords.get(value)),units=unit)

    if unit == 'si':
        actual_temp_label = 'Temperature (degrees Celsius)'
        apparent_temp_label = 'Apparent Temperature (degrees Celsius)'
        wind_speed_label = 'Wind Speed (metres per second)'
    else:
        actual_temp_label = 'Temperature (degrees Fahrenheit)'
        apparent_temp_label = 'Apparent Temperature (degrees Fahrenheit)'
        wind_speed_label = 'Wind Speed (miles per hour)'

    #Gets time of country in relevant timezone
    timezone = pytz.timezone(data.timezone)
    time_format = pytz.UTC.localize(datetime.utcfromtimestamp(data.time))
    current_time = time_format.astimezone(timezone)
    time_string = current_time.strftime("%D %H:%M")

    table_trace = go.Table(
        header=dict(values=['Data', 'Current Value'],line = dict(color='#7D7F80'),
                    fill = dict(color='#a1c3d1'),
                    align = ['left'] * 5),
        cells=dict(values=[['City','Local Time', "Summary", actual_temp_label, apparent_temp_label,
                            wind_speed_label, "Air Pressure (millibars)", "Cloud Cover (%)"],
                           [value,time_string,data.summary,data.temperature,
                            data.apparentTemperature,data.windSpeed,data.pressure,
                            round((data.cloudCover*100),2)]],
        line=dict(color='#7D7F80'),
        fill=dict(color='#EDFAFF'),
        align=['left'] * 5)
    )

    table_data = [table_trace]

    return {
        'data': table_data
    }

if __name__ == '__main__':
    app.run_server(debug=True)


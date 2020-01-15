# Perform imports here:
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State
import pandas_datareader.data as web # requires v0.6.0 or later
from datetime import datetime
import dash_table_experiments as dt
import folium as fo

# Launch the application:
app = dash.Dash()
app.title = 'Crime Los Angeles'
# Create a DataFrame from the .csv file:
#df = pd.read_csv('../data/OldFaithful.csv')
df = pd.read_csv('Data/CrimeAll.csv', delimiter=',', encoding="utf-8-sig")
cd = pd.read_csv('Data/CrimeCat.csv', delimiter=',', encoding="utf-8-sig")
af = pd.read_csv('Data/AreaName.csv', delimiter=',', encoding="utf-8-sig")
df['DateOccurred'] = pd.to_datetime(df['DateOccurred'])
cl = cd['CrimeCategory']
al = af['AreaName']
options = []
for crime in cl: #df['Crime Code Description'].sort_values():
    options.append({'label':str(crime),'value':crime})

AreaList = []
for Area in al:
    AreaList.append({'label':str(Area),'value':Area})
df1= df.dropna()
label = ['77th Street','Central','Devonshire','Foothill','Harbor',
         'Hollenbeck','Hollywood','Mission','N Hollywood','Newton',
         'Northeast','Olympic','Pacific','Rampart','Southeast',
         'Southwest','Topanga','Van Nuys','West LA ','West Valley',
         'Wilshire']

colors = {'77th Street':'rgb(66, 134, 244)','Central':'rgb(65, 244, 83)',
          'Devonshire':'rgb(66, 134, 244)','Foothill':'rgb(244, 223, 65)',
          'Harbor':'rgb(66, 134, 244)','Hollenbeck':'rgb(66, 134, 244)',
          'Hollywood':'rgb(66,4, 65)','Mission':'rgb(66, 134, 244)',
          'N Hollywood':'rgb(66, 134, 244)','Newton':'rgb(244, 65, 211)',
          'Northeast':'rgb(66, 134, 244)','Olympic':'rgb(35, 1, 6)',
          'Pacific':'rgb(66, 134, 244)','Rampart':'rgb(101, 94, 119)',
          'Southeast':'rgb(14, 72, 142)','Southwest':'rgb(66, 134, 244)',
          'Topanga':'rgb(13, 142, 139)','Van Nuys':'rgb(66, 134, 244)',
          'West LA ':'rgb(21, 193, 96)','West Valley':'rgb(66, 134, 244)',
          'Wilshire':'rgb(66, 134, 244)'}

mapbox_access_token = 'MyMapboxToken'

layout_map = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#32CD32", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#32CD32',# '#fffcfc',
    paper_bgcolor= '#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    title='Crime Map Los Angeles',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-118.265101,
            lat=34.042570
        ),
        zoom=10,
    )
)



# Create a Dash layout that contains a Graph component:
app.layout = html.Div([
                
html.Div([
    html.H3('Select start and end dates:'),
    dcc.DatePickerRange(
        id='my_date_picker',
        min_date_allowed=datetime(2010, 1, 1),
        max_date_allowed=datetime.today(),
        start_date=datetime(2018, 1, 1), #datetime.today(),
        end_date=datetime(2018, 1, 12) #datetime.today()
    )
], style={'display':'inline-block'}),

html.Div([
    html.H3('Select crime :', style={'paddingRight':'30px'}),
    dcc.Dropdown(
        id='my_crime_picker',
        options= options ,#[{'label': i, 'value': i} for i in df['Item Name'].unique().sort()], #options=CrimeList.unique(), #[{'label': i, 'value': i} for i in df['Crime Code Description'].unique().sort()],
        value=['ARSON'],
        multi=True
    )
], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),

html.Div([
    html.H3('Select Precinct :', style={'paddingRight':'30px'}),
    dcc.Dropdown(
        id='my_area_picker',
        options= AreaList ,#[{'label': i, 'value': i} for i in df['Item Name'].unique().sort()], #options=CrimeList.unique(), #[{'label': i, 'value': i} for i in df['Crime Code Description'].unique().sort()],
        value=['Topanga'],
        multi=True
    )
], style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),


html.Div([
    html.Button(
        id='submit-button',
        n_clicks=0,
        children='Submit',
        style={'fontSize':24, 'marginLeft':'30px'}
    ),
], style={'display':'inline-block'}),

dcc.Checklist(id='select-all',
                  options=[{'label': 'Select All Precincts', 'value': 1}], values=[]),
    
##DataTable

dcc.Graph( id='crime_numbers'),
#html.Div([dcc.Graph( id='time_numbers2')]),
html.Div([dt.DataTable( # Initialise the rows
        rows=[{}],
        row_selectable=False,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='time_numbers')]),

html.Div([
          dcc.Graph(id='map-graph',
                    animate=True,
                    style={'margin-top': '20'})
                    ], className = "six columns"
                )    
    
])

@app.callback(
    Output('my_area_picker', 'value'),
    [Input('select-all', 'values')],
    [State('my_area_picker', 'options'),
     State('my_area_picker', 'value')])
def test(selected, options, values):
    print(selected)
    if selected[0] == 1:
        return [i['value'] for i in options]
    else:
        return values    
    
    
@app.callback(
    Output('crime_numbers', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_date_picker', 'start_date'),
     State('my_date_picker', 'end_date'),
     State('my_crime_picker','value'),
     State('my_area_picker','value')
    ])
def update_figure(n_clicks, start_date, end_date,crimelist,arealist):
    start = start_date #datetime.strptime(start_date,'%Y-%m-%d')
    end = end_date #datetime.strptime(end_date,'%Y-%m-%d')


    #df1['Counter'] = 1
    df1['DateOccurred'] = pd.to_datetime(df['DateOccurred'])
    df2 = df1[(df1['DateOccurred'] >= start) & (df1['DateOccurred'] <= end) ]
    df3 = df2[(df2['CRIMECATEGORY'].isin(crimelist))]
    df4 = df3[(df3['AreaName'].isin(arealist))]
    df5 = df4.groupby(['CrimeDesc' ]).agg({      # find the sum of the durations for each group
                                         'CrimeCount': "count" # find the number of network type entries
                                         })    # get the first date per group
    #df3 = df2.unstack
    df6 = df5.reset_index(level=[0,0])
    return {'data':[go.Bar(x=df6['CrimeDesc'],
                              y=df6['CrimeCount'],
                            #  mode='markers',
                              marker={ #'size':15,
                                      'opacity':0.5,
                                      'line':{'width':0.5,'color':'green'}})
                              ],
                              'layout':go.Layout(title='Crime Stuff',
                              xaxis = {'title':'Crime Description'},
                              yaxis = {'title':'Number of Crimes'},
                              hovermode='closest'),}
                              
@app.callback(
    Output('map-graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_date_picker', 'start_date'),
     State('my_date_picker', 'end_date'),
     State('my_crime_picker','value'),
     State('my_area_picker','value')
    ])
def update_figure(n_clicks, start_date, end_date,crimelist,arealist):
    start = start_date #datetime.strptime(start_date,'%Y-%m-%d')
    end = end_date #datetime.strptime(end_date,'%Y-%m-%d')

    df1['DateOccurred'] = pd.to_datetime(df['DateOccurred'])
    df2 = df1[(df1['DateOccurred'] >= start) & (df1['DateOccurred'] <= end) ]
    df3 = df2[(df2['CRIMECATEGORY'].isin(crimelist))]
    df4 = df3[(df3['AreaName'].isin(arealist))]
    df5 = df4[['AreaName','DateOccurred','TimeOccurred','CrimeDesc','Lat','Lon']]
    return {
        "data": [{
                "type": "scattermapbox",
                "lat": list(df5['Lat']),
                "lon": list(df5['Lon']),
                "hoverinfo": "text",
                "hovertext": [["Precinct: {} <br>DateOccurred: {} <br>TimeOccurred: {} <br>CrimeDesc: {}".format(i,j,k,l)]
                                for i,j,k,l in zip(df5['AreaName'],df5['DateOccurred'], df5['TimeOccurred'],df5['CrimeDesc'])],
                "mode": "markers",
                "name": list(df5['CrimeDesc']),
                "marker": {"color":colors,
                    "size": 6,
                    "opacity": 0.5
                }
        }],
        "layout": layout_map
    }


@app.callback(
     Output('time_numbers', 'rows'),
     [Input('submit-button', 'n_clicks')],
     [State('my_date_picker', 'start_date'),
     State('my_date_picker', 'end_date'),
     State('my_crime_picker','value'),
     State('my_area_picker','value')
     ])
def update_figurea(n_clicks, start_date, end_date,crimelist,arealist):
    start = start_date #datetime.strptime(start_date,'%Y-%m-%d')
    end = end_date #datetime.strptime(end_date,'%Y-%m-%d')
    dfa1 = df1
    dfa1['DateOccurred'] = pd.to_datetime(dfa1['DateOccurred'])
    dfa2 = dfa1[(dfa1['DateOccurred'] >= start) & (dfa1['DateOccurred'] <= end) ]
    dfa3 = dfa2[(dfa2['CRIMECATEGORY'].isin(crimelist))]
    dfa4 = dfa3[(dfa3['AreaName'].isin(arealist))]
    dfa4['Year']= pd.DatetimeIndex(dfa4['DateOccurred']).year
    dfa4['Month']= pd.DatetimeIndex(dfa4['DateOccurred']).month
    dfa4['Day']= pd.DatetimeIndex(dfa4['DateOccurred']).day_name()
    dfa4['DayNumber']= pd.DatetimeIndex(dfa4['DateOccurred']).dayofweek
    dfa5 = dfa4.groupby(['CrimeDesc','DayNumber','Day' , 'TimeRange']).agg({      
                                         'CrimeCount': "count" 
                                         })    
    dfa6 = dfa5.reset_index()
    dfa6.sort_values(['CrimeDesc','DayNumber' , 'TimeRange'])
    rows = dfa6.to_dict('records')
    return dfa6.to_dict('records')




# Add the server clause:
if __name__ == '__main__':
    app.run_server()


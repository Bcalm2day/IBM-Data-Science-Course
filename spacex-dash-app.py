# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create the sites for the dictionary in the dropdown
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=dropdown_options,                                     
                                    value = "ALL",
                                    placeholder="Select a Launch site",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    marks={0: '0', 2000: '2K', 4000: '4K', 6000: '6K', 8000: '8K', 10000: '10K'}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
    )

def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Filtrar solo los exitosos
        df_success = spacex_df[spacex_df['class'] == 1]
        # Agrupar por sitio y contar
        site_counts = df_success['Launch Site'].value_counts().reset_index()
        site_counts.columns = ['Launch Site', 'Successes']
        # Crear pie chart
        fig = px.pie(site_counts, values='Successes', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # Filtrar por sitio específico
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Crear pie chart de éxito vs. fallo
        fig = px.pie(filtered_df, names='class',
                     title=f'Success vs. Failure Launches at {selected_site}',
                     labels={0: 'Failure', 1: 'Success'})
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title='Payload vs. Outcome for Launches')
    return fig

# Run the app
if __name__ == '__main__':
    app.run()

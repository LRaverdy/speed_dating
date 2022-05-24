import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
import dash_daq as daq

############# Data ###############

dff = pd.read_csv("data_speed_dating.csv")
df = pd.read_csv("subdata_speed_dating.csv")
df['age'] = df['age'].astype(int)

# To sort by satisfaction level
satis = ['Very satisfied', 'Satisfied', 'Neutral', 'Not satisfied', 'Not satisfied at all', 'Unknown']
df['satis_2'] = pd.Categorical(df['satis_2'], categories=satis, ordered=True)

# To sort by field of study
study = df['field_of_study'].value_counts().index.tolist()
df['field_of_study'] = pd.Categorical(df['field_of_study'], categories=study, ordered=True)

# To sort by date duration
length = ['Just right', 'Too much', 'Too little', 'Unknown']
df['length'] = pd.Categorical(df['length'], categories=length, ordered=True)

# To sort by number of date sentiment
ndate = ['Just right', 'Too few', 'Too many',  'Unknown']
df['speed_date_nb'] = pd.Categorical(df['speed_date_nb'], categories=ndate, ordered=True)

# Age slider
age = sorted(df['age'].unique())
numbers = [i for i in range(18, 56)]
wrong_age = [i for i in numbers if i not in age] + [i for i in numbers if i > 39]


############ Functions ###########

# This will return a dataframe with value counts and percentage from a column
def get_proportion(data, col_name):
    count = data[col_name].value_counts()
    percentage = round((data[col_name].value_counts(normalize=True) * 100), 2)
    index = data[col_name].value_counts().index

    dic = {
        'count': count,
        'percentage': percentage
    }

    DataFrame = pd.DataFrame(dic,
                             index=index)

    return DataFrame.sort_values(by='percentage', ascending=True)


# Function that will return percentage and count
def groupby(data, col_1, col_2):
    groupby = pd.DataFrame(data.groupby([col_1, col_2]).agg({col_2: "count"})).groupby(level=0).apply(
        lambda x: round(100 * x / x.sum(), 2))
    groupby = groupby.rename(columns={col_2: 'percentage'}).reset_index()
    groupby['count'] = data.groupby([col_1, col_2])[col_2].agg(['count']).values

    return groupby


def satis_level(data, col_1, col_2):
    # Using groupby function for count and proportion
    groupby_data = groupby(data, col_1, col_2)

    index = []
    # Get a list of number to reorder level of satisfaction level
    for i in range(len(groupby_data)):
        if groupby_data[col_2][i] == 'Very satisfied':
            index.append(1)
        elif groupby_data[col_2][i] == 'Satisfied':
            index.append(2)
        elif groupby_data[col_2][i] == 'Neutral':
            index.append(3)
        elif groupby_data[col_2][i] == 'Not satisfied':
            index.append(4)
        elif groupby_data[col_2][i] == 'Not satisfied at all':
            index.append(5)
        else:
            index.append(6)

    groupby_data['index'] = index
    return groupby_data.sort_values(by='index')


def len_satis_level(data, col_1, col_2):
    groupby_data = groupby(data, col_1, col_2)

    index = []

    for i in range(len(groupby_data)):
        if groupby_data[col_2][i] == 'Just right':
            index.append(1)
        elif groupby_data[col_2][i] == 'Too little':
            index.append(2)
        elif groupby_data[col_2][i] == 'Too much':
            index.append(3)
        else:
            index.append(4)

    groupby_data['index'] = index

    return groupby_data.sort_values(by='index')


def date_nb_satis(data, col_1, col_2):
    groupby_data = groupby(data, col_1, col_2)

    index = []

    for i in range(len(groupby_data)):
        if groupby_data[col_2][i] == 'Just right':
            index.append(1)
        elif groupby_data[col_2][i] == 'Too few':
            index.append(2)
        elif groupby_data[col_2][i] == 'Too many':
            index.append(3)
        else:
            index.append(4)

    groupby_data['index'] = index

    return groupby_data.sort_values(by='index')

########################################################
###################### Dashboard #######################
########################################################

# Parameters

# Satis graph colors
satis_colors = ['lightgrey', 'darkred', 'red', '#fbff89', 'lightgreen', 'green']
duration_colors = ['darkred', 'red', 'lightgreen']
ndate_colors = ['darkred', 'red', 'lightgreen']

# Distribution graph colors
mf_colors = ['#3596b6', '#d07670']

# Hide plotly toolbar options
html_style = style={
                 "font-weight":"bold",
                 "font-size":"85%",
                 "paddingTop": 20,
                 "paddingBottom": 10,
                    }

config={'displaylogo' : False,
        'modeBarButtonsToRemove': ['zoom2d',
                                   'pan2d',
                                   'select2d',
                                   'lasso2d',
                                   'zoomIn2d',
                                   'zoomOut2d',
                                   'toImage',
                                   'resetScale2d']
    }


def study_func(data_frame, col, col2, tick_size, tick_angle):
    data = groupby(data_frame, col, 'satis_2')
    # Get rid of field od study where count < 10
    # Apply function to get count and percentage
    filter_ = get_proportion(data_frame, col).sort_values(by='percentage', ascending=False)


    # Get list of field of study names where count > 10
    filter_ = filter_[filter_['count'] > 5].index.tolist()

    # Filter data to get only rows that contain names on the list
    mask = data[data[col].str.contains('|'.join(filter_))]

    fig = px.bar(
        # Data
        mask.sort_values(by=[col], ascending=False),
        hover_data=mask,
        hover_name=col2,
        x='percentage',
        y=col,

        # Legend & annotate
        color=col2,
        text='percentage',

        # Colors
        color_discrete_sequence=['lightgrey', 'darkred', 'red', '#fbff89', 'lightgreen', 'green'],
        # Cross shape
        pattern_shape=col2,
        pattern_shape_sequence=[
            "x",
            "",
            "",
            "",
            "",
            ""]
    )

    # Titles, axes
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        # paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=10, r=10),
        # template='plotly_dark',
        title_text=f"Satisfaction by {col.replace('_', ' ').capitalize()}",
        #title_font_size=13,
        title_x=0.55,
        #title_y=.9,
        legend_traceorder="reversed",
        yaxis_title=None,
        xaxis_title=None,
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=-0.1
    )

    fig.update_traces(texttemplate='%{text} %',
                      textposition='inside',
                      textfont_size=tick_size,
                      insidetextanchor="middle")

    fig.update_yaxes(tickangle=tick_angle,
                     tickfont=dict(
                         #family='Rockwell',
                         size=tick_size
                        )
                     )

    return fig

def duration_func(data_frame, col, col2, tick_size, tick_angle):
    data = groupby(data_frame, col, col2)
    # Get rid of field od study where count < 10
    # Apply function to get count and percentage

    filter_ = get_proportion(data_frame, col).sort_values(by='percentage', ascending=False)

    # Get list of field of study names where count > 10
    filter_ = filter_[filter_['count'] > 5].index.tolist()

    # Filter data to get only rows that contain names on the list
    mask = data[data[col].str.contains('|'.join(filter_))]

    column = col2

    if column == "length":
        title =f"Thought on duration by {col.replace('_', ' ').capitalize()}"
    else:
        title= f"Thought on number of dates by {col.replace('_', ' ').capitalize()}"

    fig = px.bar(
        # Data
        mask.sort_values(by=col2, ascending=False),
        hover_data=data,
        hover_name=col2,
        x='percentage',
        y=col,

        # Legend & annotate
        color=col2,
        text='percentage',

        # Colors
        color_discrete_sequence=['lightgrey', 'darkred', 'red', 'lightgreen'],
        # Cross shape
        pattern_shape=col2,
        pattern_shape_sequence=[
            "x",
            "",
            "",
            "",
            "",
            ""]
    )

    # Titles, axes
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        # paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=10, r=10),
        # template='plotly_dark',
        title_text=title,
        #title_font_size=13,
        title_x=0.55,
        #title_y=.9,
        legend_traceorder="reversed",
        yaxis_title=None,
        xaxis_title=None,
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=-0.1
    )

    fig.update_traces(texttemplate='%{text} %',
                      textposition='inside',
                      textfont_size=tick_size,
                      insidetextanchor="middle")

    fig.update_yaxes(tickangle=tick_angle,
                     tickfont=dict(
                         #family='Rockwell',
                         size=tick_size
                        )
                     )

    return fig

# --------------------------------------------------------

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY],
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial-scale=1 , maximum-scale=1.9, minimum-scale=.5'}])

server = app.server

########################################################
###################### App Layout ######################
########################################################

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("Speed Dating Experiment EDA",
                    style={'textAlign': 'center',
                           "paddingTop": 30}),
            html.Br(),
        ],xl=4, lg=8, md=8, xs=12, align='center')
    ], justify='center', style={"background-color": "#c8daef"}),

    dbc.Row([
        dbc.Col([
            dcc.Markdown("**Les données :**", style={"font-size": 25, "paddingTop": 50}),

            dcc.Markdown([
                "Accessibles sur [Kaggle](https://www.kaggle.com/datasets/annavictoria/speed-dating-experiment), "
                "les données proviennent d'une **expérimentation de speed dating** organisée au début des années 2000 ",
                "et supervisée par les professeurs Ray Fisman et Sheena Iyengar de la Columbia Business School. \n",
                "Pendant les événements, les participants ont eu un *date* de 4 minutes avec chacun des autres participants.",
                "Pour connaître s'il ya eu match, les participants doivent **retourner un questionnaire de satisfaction.**"],
                style={"font-size": 16}),
            html.Br(),
            dcc.Markdown("**Objectifs :**", style={"font-size": 22}),

            dcc.Markdown([
                "- Analyse de la distribution des données (qui a participté, combien de personnes, leurs caractéristiques)",
                "- Visualiser le niveau de satisfaction et identifier les raisons",
                "- Restitution des résultats sous forme de rapport interactif"
            ]),
            html.Br(),
            html.Hr(),
            html.Br(),
            dcc.Markdown("**Participants :**", style={"font-size": 22})

        ],xl=8, lg=8, md=8, xs=12)
    ],justify='center', style={"background-color": "#f5f8fc"}),

################################################################
####################### Age distribution #######################
################################################################


    dbc.Row([
        dbc.Col([
            html.Br(),
            dcc.Markdown("**Genre et âge :**", style={"font-size": 18}),
            html.Div("Field of Study :", style=html_style),

            dcc.Dropdown(
            ['All'] + sorted(df['field_of_study'].unique()),
                "All",
                id="study",
                multi=False,
                style={
                    'width': "60%",
                    'color': 'black',
                    'font-size': '85%'
                }),
            ],xl=4, lg=8, md=8, xs=12),
        dbc.Col([
            html.Div("Ethnic Group", style=html_style),

            dcc.Dropdown(
                ['All'] + sorted(df['ethnic_group'].unique()),
                "All",
                id="ethnic",
                multi=False,
                style={
                    'width': "60%",
                    'color': 'black',
                    'font-size': '85%',
                    'display': 'inline_block'
                }),
        ],xl=4, lg=8, md=8, xs=12)
    ],justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id="hist",
                      figure={},
                      style={
                          "height": "300px",
                          "width": "100%"
                      },
                      config=config),
            ], xl=6, lg=6, md=8, xs=8),

        dbc.Col([
            dcc.Graph(id='gender_bar',
                      figure={},
                      style={
                          "height": "300px",
                          "width": "60%"
                      },
                      config=config)
        ], xl=2, lg=2, md=4, xs=4)
        ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div("Plus de détails :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(
                on=False,
                id='BSwitch'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div(id='txt'),
            html.Br()
        ],xl=8, lg=8, md=8, xs=12)
    ],justify='center', style={"background-color": "#f5f8fc"}),

################################################################
####################### Field of study #########################
################################################################

    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Br(),
            dcc.Markdown("**Domaine d'étude :**", style={"font-size": 18}),
            html.Br(),
            html.Div("Tranche d'âge :"),
            html.Br(),
            ], xl=8, lg=8, md=8, xs=12)
        ], justify='center', style={"background-color": "#f5f8fc"}),

####################### Filters #########################

    dbc.Row([
        dbc.Col([

            dcc.RangeSlider(
                    df['age'].min(),
                    39,
                    count=1,
                    value=[df['age'].min(),  39],
                    marks=None,
                    #marks={str(i): str(i) for i in range(df['age'].min(), df['age'].max() +1) if i not in wrong_age},
                    id='ageSlider',
                    #included=True,
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),

        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

####################### Graph #########################

    dbc.Row([
        dbc.Col([

            dcc.Graph(
                id="field_study",
                figure={},
                style={
                    'height':'600px',
                    'width':'100%'
                },
                config=config)

        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div("Plus de détails :", style={"font-weight": "bold",
                                                 "font-size": "90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

####################### Details #########################

    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(
                on=False,
                id='BSwitch2'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div(id='txt2'),
            html.Br()
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

################################################################
####################### Ethnic Group ###########################
################################################################


    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.Br(),
            dcc.Markdown("**Groupe ethnique :**", style={"font-size": 18}),
            html.Br(),
            html.Div("Tranche d'âge :"),
            html.Br(),
            ], xl=8, lg=8, md=8, xs=12)
        ], justify='center', style={"background-color": "#f5f8fc"}),

####################### Filters ###########################

    dbc.Row([
        dbc.Col([
            dcc.RangeSlider(
                    df['age'].min(),
                    39,
                    count=1,
                    value=[df['age'].min(),  39],
                    marks=None,
                    #marks={str(i): str(i) for i in range(df['age'].min(), df['age'].max() +1) if i not in wrong_age},
                    id='ageSlider2',
                    #included=True,
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

####################### Graph ###########################

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="ethnic_bar",
                figure={},
                style={
                    'height':'400px',
                    'width':'100%'
                },
                config=config
            )
        ], xl=6, lg=6, md=6, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div("Plus de détails :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(
                on=False,
                id='BSwitch3'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div(id='txt3'),
            html.Br()
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

################################################################
################### Global Satisfaction ########################
################################################################

    dbc.Row([
        dbc.Col([
            html.H4("Satisfaction :",
                    style={"font-weight": "bold"}),
            html.Br()
            ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

########################## Filters ############################

    dbc.Row([
        dbc.Col([
            html.Div("Field of Study :", style=html_style),

            dcc.Dropdown(
            ['All'] + sorted(df['field_of_study'].unique()),
                "All",
                id="study2",
                multi=False,
                style={
                    'width': "70%",
                    'color': 'black',
                    'font-size': '85%'
                }),
            ],xl=2, lg=8, md=8, xs=12),
        dbc.Col([
            html.Div("Ethnic Group", style=html_style),

            dcc.Dropdown(
                ['All'] + sorted(df['ethnic_group'].unique()),
                "All",
                id="ethnic2",
                multi=False,
                style={
                    'width': "70%",
                    'color': 'black',
                    'font-size': '85%'
                }),
            html.Br()
        ],xl=2, lg=8, md=8, xs=12)
    ],justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div("Tranche d'âge :"),
            html.Br(),
            ], xl=8, lg=8, md=8, xs=12)
        ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            dcc.RangeSlider(
                    df['age'].min(),
                    39,
                    count=1,
                    value=[df['age'].min(),  39],
                    marks=None,
                    #marks={str(i): str(i) for i in range(df['age'].min(), df['age'].max() +1) if i not in wrong_age},
                    id='ageSlider3',
                    #included=True,
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

########################## Graph ############################

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='satis_bar',
                figure={},
                style={
                    "height": "300px",
                    "width": "100%"
                },
                config=config),
            html.Br()],
            xl=6, lg=6, md=8, xs=12),
    ], justify='center', style={"background-color": "#f5f8fc"}),

########################## Boolean Switches ############################

dbc.Row([
        dbc.Col([
            html.Div("Par domaine d'étude :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(
                on=False,
                id='BSwitch4'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div(
                id = 'graph_container',
                children=[]),

        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

dbc.Row([
        dbc.Col([
            html.Div("Par groupe ethnique :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(
                on=False,
                id='BSwitch5'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            html.Div(
                id = 'graph_container2',
                children=[])
        ], xl=6, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

################################################################
################### Date duration ##############################
################################################################

    dbc.Row([
        dbc.Col([
        html.Hr(),

        dcc.Markdown("**Avis sur la durée des *dates* :**", style={"font-size": 20})

        ], xl=8, lg=8, md=8, xs=12)
    ], justify="center", style={"background-color": "#f5f8fc"}),

####################### Filters ##############################

dbc.Row([
        dbc.Col([
            html.Div("Field of Study :", style=html_style),

            dcc.Dropdown(
            ['All'] + sorted(df['field_of_study'].unique()),
                "All",
                id="study_duration",
                multi=False,
                style={
                    'width': "70%",
                    'color': 'black',
                    'font-size': '85%'
                }),

            ],xl=2, lg=8, md=8, xs=12),

        dbc.Col([
            html.Div("Ethnic Group", style=html_style),

            dcc.Dropdown(
                ['All'] + sorted(df['ethnic_group'].unique()),
                "All",
                id="ethnic_duration",
                multi=False,
                style={
                    'width': "70%",
                    'color': 'black',
                    'font-size': '85%'
                }),

            html.Br()
        ],xl=2, lg=8, md=8, xs=12)
    ],justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div("Tranche d'âge :"),
            html.Br(),

            ], xl=8, lg=8, md=8, xs=12)
        ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            dcc.RangeSlider(
                    df['age'].min(),
                    39,
                    count=1,
                    value=[df['age'].min(),  39],
                    marks=None,
                    #marks={str(i): str(i) for i in range(df['age'].min(), df['age'].max() +1) if i not in wrong_age},
                    id='ageSlider_duration',
                    #included=True,
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),

        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

####################### Graph ##############################

dbc.Row([
        dbc.Col([

            dcc.Graph(
                id='duration_bar',
                figure={},
                style={
                    "height": "300px",
                    "width": "100%"
                },
                config=config),

            html.Br()],
            xl=6, lg=6, md=8, xs=12),
    ], justify='center', style={"background-color": "#f5f8fc"}),

##################### Boolean Swicthes ###########################

dbc.Row([
        dbc.Col([
            html.Div("Par domaine d'étude :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(
                on=False,
                id='BSwitch_duration_study'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div(
                id = 'graph_container_duration_study',
                children=[]),

        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div("Par groupe ethnique :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            daq.BooleanSwitch(
                on=False,
                id='BSwitch_duration_ethnic'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div(
                id = 'graph_container_duration_ethnic',
                children=[])

        ], xl=6, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),


################################################################
################### Number of date #############################
################################################################

    dbc.Row([
        dbc.Col([
        html.Hr(),

        dcc.Markdown("**Avis sur la nombre des *dates* :**", style={"font-size": 20})

        ], xl=8, lg=8, md=8, xs=12)
    ], justify="center", style={"background-color": "#f5f8fc"}),

####################### Filters ##############################

dbc.Row([
        dbc.Col([
            html.Div("Field of Study :", style=html_style),

            dcc.Dropdown(
            ['All'] + sorted(df['field_of_study'].unique()),
                "All",
                id="study_ndate",
                multi=False,
                style={
                    'width': "70%",
                    'color': 'black',
                    'font-size': '85%'
                }),

            ],xl=2, lg=8, md=8, xs=12),

        dbc.Col([
            html.Div("Ethnic Group", style=html_style),

            dcc.Dropdown(
                ['All'] + sorted(df['ethnic_group'].unique()),
                "All",
                id="ethnic_ndate",
                multi=False,
                style={
                    'width': "70%",
                    'color': 'black',
                    'font-size': '85%'
                }),

            html.Br()
        ],xl=2, lg=8, md=8, xs=12)
    ],justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div("Tranche d'âge :"),
            html.Br(),

            ], xl=8, lg=8, md=8, xs=12)
        ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            dcc.RangeSlider(
                    df['age'].min(),
                    39,
                    count=1,
                    value=[df['age'].min(),  39],
                    marks=None,
                    #marks={str(i): str(i) for i in range(df['age'].min(), df['age'].max() +1) if i not in wrong_age},
                    id='ageSlider_ndate',
                    #included=True,
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),

        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

####################### Graph ##############################

dbc.Row([
        dbc.Col([

            dcc.Graph(
                id='ndate_bar',
                figure={},
                style={
                    "height": "300px",
                    "width": "100%"
                },
                config=config),

            html.Br()],
            xl=6, lg=6, md=8, xs=12),
    ], justify='center', style={"background-color": "#f5f8fc"}),

##################### Boolean Swicthes ###########################

dbc.Row([
        dbc.Col([
            html.Div("Par domaine d'étude :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(
                on=False,
                id='BSwitch_ndate_study'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div(
                id = 'graph_container_ndate_study',
                children=[]),

        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div("Par groupe ethnique :", style={"font-weight": "bold",
                                                 "font-size":"90%"})
        ], xl=8, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            daq.BooleanSwitch(
                on=False,
                id='BSwitch_ndate_ethnic'
            ),
            html.Br()
        ], xl=7, lg=8, md=8, xs=12)
    ], justify='start', style={"background-color": "#f5f8fc"}),

    dbc.Row([
        dbc.Col([

            html.Div(
                id = 'graph_container_ndate_ethnic',
                children=[])

        ], xl=6, lg=8, md=8, xs=12)
    ], justify='center', style={"background-color": "#f5f8fc"})


], fluid=True)


########################################################
###################### Callbacks #######################
########################################################

# --------------------- Histogram -----------------------------
@app.callback(
    Output('hist', 'figure'),
    Input('study', 'value'),
    Input('ethnic', 'value')
)

def update_hist(study, ethnic):
    if study == 'All':
        data = df
    else:
        data = df[df['field_of_study'] == study]

    if ethnic == 'All':
        data = data
    else:
        data = data[data["ethnic_group"] == ethnic]

    colors = ['rgb(0, 0, 100)', 'rgb(0, 200, 200)']

    fig = px.histogram(
        data, x="age",
        color="gender",
        marginal="box",  # or violin, rug
        hover_data=data.columns,
        barmode='overlay',
        color_discrete_sequence=['#d07670', '#3596b6'],
        opacity=.9
    )

    # Titles, axes
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title_text=None,
        title_x=0.5,
        yaxis_title='Count',
        xaxis_title='Age',
        margin=dict(t=50, b=50, l=0, r=0),
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=1.15
    )
    return fig

@app.callback(
    Output('gender_bar', 'figure'),
    Input('study', 'value'),
    Input('ethnic', 'value')
)

def update_bar(study, ethnic):
    if study == 'All':
        data = df
    else:
        data = df[df['field_of_study'] == study]

    if ethnic == 'All':
        data = data
    else:
        data = data[data["ethnic_group"] == ethnic]

    data = get_proportion(data, 'gender')

    fig = px.bar(data,
                 y='count',
                 x=data.index,
                 color=data.index,
                 text='percentage',
                 color_discrete_sequence=['#d07670', '#3596b6'])

    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=20, r=10),
        title_text=None,
        title_x=0.5,
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
        showlegend=False
    )

    fig.update_traces(texttemplate='%{text} %')

    return fig

@app.callback(
    Output('txt', 'children'),
    Input('BSwitch', 'on')
)

def update_result(value):
    children = [dcc.Markdown([
        "L'histrogramme nous indique que **la grande majorité des participants ont entre 20 et 30 ans.** "
        "Nous observons également que l'âge médian des hommes (27 ans) n'est que **d'une année plus élévé** que celui des femmes (26 ans). "
        "Les femmes sont représentées à hauteur de **49,73%** contre **50,27%** pour les hommes. ",
        
        "\nNous nous attendions à cette distribution des âges puisqu'il nous était indiqué que **les participants "
        "étaient des étudiants d'études supérieures**. Le nombre d'hommes et femmes et quasiment égal, il n'y a eu que des "
        "*dates* entre sexe opposé (nous avions vérifié lors de l'EDA disponible sur GitHub."])
    ]

    if value == True:
        return children
    else:
        return None

@app.callback(
    Output('field_study', 'figure'),
    Input('ageSlider', 'value')
)

def update_hbar(age):
    ages = [i for i in range(age[0], age[1] + 1)]
    data = df[df['age'].isin(ages)]
    data = groupby(data, 'field_of_study', 'gender')

    fig = px.bar(
        data.sort_values(by='field_of_study', ascending=True),
        y='count',
        x='field_of_study',
        color='gender',
        text='percentage',
        color_discrete_sequence=['#d07670', '#3596b6']
    )

    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title_text=None,
        title_x=0.5,
        xaxis_title=None,
        yaxis_title='Count',
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=1.15,
        margin=dict(t=50, b=50, l=10, r=50)
    )

    fig.update_traces(texttemplate='%{text} %')
    fig.update_xaxes(tickangle=50)

    return fig

@app.callback(
    Output('ethnic_bar', 'figure'),
    Input('ageSlider2', 'value')
)

def update_hbar(age):
    ages = [i for i in range(age[0], age[1] + 1)]
    data = df[df['age'].isin(ages)]
    data = groupby(data, 'ethnic_group', 'gender')

    fig = px.bar(
        data.sort_values(by='count', ascending=False),
        y='count',
        x='ethnic_group',
        color='gender',
        text='percentage',
        color_discrete_sequence=['#3596b6', '#d07670']
    )

    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title_text=None,
        title_x=0.5,
        xaxis_title=None,
        yaxis_title='Count',
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=1.15,
        margin=dict(t=50, b=50, l=10, r=10)
    )
    fig.update_xaxes(tickangle=50)

    fig.update_traces(texttemplate='%{text} %')

    return fig

@app.callback(
    Output('txt2', 'children'),
    Input('BSwitch2', 'on')
)

def update_result(value):
    children = [dcc.Markdown([
        "La section *Business* est de loin **la plus représentée avec 130 personnes** et un grande nombre d'hommes **(77%)**\n",
        "La section *Engineering* est elle aussi composée de **77% d'hommes.**" 
        " Les sections *Social Science*, *Education*, *Social Work* et *English* **sont constituée très majoritairement de femmes**.\n",

        "\nOn remarque que les sections les plus représentées sont aussi celles avec le pourcentage d'hommes le plus élevé." ,
        " Mais la part des femmes est rattrapée sur certaines sections atteignant parfois 96% *(Social Work)*, 87% *(Education)*"])
    ]

    if value == True:
        return children
    else:
        return None

@app.callback(
    Output('txt3', 'children'),
    Input('BSwitch3', 'on')
)

def update_result(value):
    children = [
        "Pas grand chose à développer ici, si ce n'est une part importe des Caucasians sur l'ensemble des groupes ethniques.", html.Br(),
        "Pas de difference importante de part entre hommes et femmes parmis tous ces groupes." \
    ]

    if value == True:
        return children
    else:
        return None


@app.callback(
    Output('satis_bar', 'figure'),
    Input('ageSlider3', 'value'),
    Input('ethnic2', 'value'),
    Input('study2', 'value')
)

def update_graph(age, ethnic, study):

    ages = [i for i in range(age[0], age[1] + 1)]
    if study == 'All':
        data = df
    else:
        data = df[df['field_of_study'] == study]

    if ethnic == 'All':
        data = data
    else:
        data = data[data["ethnic_group"] == ethnic]

    #data = data[data['field_of_study'] == study]
    data = data[data['age'].isin(ages)]

    data2 = groupby(data, 'gender', 'satis_2')

    fig = px.bar(
        # Data
        data2.sort_values(by='satis_2', ascending=False),
        hover_data=data2,
        hover_name='count',
        x='percentage',
        y='gender',

        # Legend & annotate
        color='satis_2',
        text='percentage',

        # Colors
        color_discrete_sequence=['lightgrey', 'darkred', 'red', '#fbff89', 'lightgreen', 'green'],
        opacity=.8,
        # Cross shape
        pattern_shape='satis_2',
        pattern_shape_sequence=[
            "x",
            "",
            "",
            "",
            "",
            ""]
    )


    if study in df['field_of_study'].unique() and ethnic in df['ethnic_group'].unique():
        title = f'Satisfaction ({study}, {ethnic})'

    elif study in df['field_of_study'].unique():
        title = f'Satisfaction ({study})'

    elif ethnic in df['ethnic_group'].unique():
        title = f'Satisfaction ({ethnic})'

    else:
        title = "Overall satisfaction"

    if len(title) > 40:
        title_font_size = 12
    else:
        title_font_size = 15


    # Titles, axes
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=10, r=10),
        #template='plotly_dark',
        title_text=title,
        title_font_size=title_font_size,
        title_x=0.5,
        title_y=.9,
        legend_traceorder="reversed",
        yaxis_title=None,
        xaxis_title=None,
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=-0.1
    )

    # Annotate percentage
    fig.update_traces(texttemplate='<b>%{text} %</b>',
                      textposition='inside',
                      textfont_size=10,
                      insidetextanchor="middle")

    return fig

@app.callback(
    Output('graph_container', 'children'),
    Input('BSwitch4', 'on')
    )

def show_graph(value):

    children = [
        dcc.Graph(
            id="study_satis",
            figure=study_func(
                df,
                col='field_of_study',
                col2="satis_2",
                tick_size=9,
                tick_angle=45
            ),
            style={
                "height": "700px",
                "width": "100%"
            },
            config=config
        )
    ]

    if value == True:
        return children
    else:
        return None

@app.callback(
    Output('graph_container2', 'children'),
    Input('BSwitch5', 'on')
    )

def show_graph(value):

    children = [
        dcc.Graph(
            id="ethnic_satis",
            figure=study_func(
                df,
                col='ethnic_group',
                col2="satis_2",
                tick_size=11,
                tick_angle=0
            ),
            style={
                "height": "400px",
                "width": "100%"
            },
            config=config
        )
    ]

    if value == True:
        return children
    else:
        return None


@app.callback(
    Output('duration_bar', 'figure'),
    Input('ageSlider_duration', 'value'),
    Input('ethnic_duration', 'value'),
    Input('study_duration', 'value')
)

def update_graph(age, ethnic, study):

    ages = [i for i in range(age[0], age[1] + 1)]
    if study == 'All':
        data = df
    else:
        data = df[df['field_of_study'] == study]

    if ethnic == 'All':
        data = data
    else:
        data = data[data["ethnic_group"] == ethnic]

    #data = data[data['field_of_study'] == study]
    data = data[data['age'].isin(ages)]

    data2 = groupby(data, 'gender', 'length')

    fig = px.bar(
        # Data
        data2.sort_values(by="length", ascending=False),
        hover_data=data2,
        hover_name='length',
        x='percentage',
        y='gender',

        # Legend & annotate
        color='length',
        text='percentage',

        # Colors
        color_discrete_sequence=['lightgrey', 'darkred', 'red', 'lightgreen'],
        opacity=.8,
        # Cross shape
        pattern_shape='length',
        pattern_shape_sequence=[
            "x",
            "",
            "",
            "",
            "",
            ""]
    )


    if study in df['field_of_study'].unique() and ethnic in df['ethnic_group'].unique():
        title = f'Thought on date duration ({study}, {ethnic})'

    elif study in df['field_of_study'].unique():
        title = f'Thought on date duration ({study})'

    elif ethnic in df['ethnic_group'].unique():
        title = f'Thought on date duration ({ethnic})'

    else:
        title =  "Overall thought on date duration"

    if len(title) > 40:
        title_font_size = 12
    else:
        title_font_size = 15


    # Titles, axes
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=10, r=10),
        #template='plotly_dark',
        title_text=title,
        title_font_size=title_font_size,
        title_x=0.5,
        title_y=.9,
        legend_traceorder="reversed",
        yaxis_title=None,
        xaxis_title=None,
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=-0.1
    )

    # Annotate percentage
    fig.update_traces(texttemplate='<b>%{text} %</b>',
                      textposition='inside',
                      textfont_size=10,
                      insidetextanchor="middle")

    return fig

@app.callback(
    Output('graph_container_duration_study', 'children'),
    Input('BSwitch_duration_study', 'on')
    )

def show_graph(value):

    children = [
        dcc.Graph(
            id="study_duration_graph",
            figure=duration_func(
                df,
                col='field_of_study',
                col2="length",
                tick_size=9,
                tick_angle=45
            ),
            style={
                "height": "700px",
                "width": "100%"
            },
            config=config
        )
    ]

    if value == True:
        return children
    else:
        return None

@app.callback(
    Output('graph_container_duration_ethnic', 'children'),
    Input('BSwitch_duration_ethnic', 'on')
    )

def show_graph(value):

    children = [
        dcc.Graph(
            id="ethnic_duration_graph",
            figure=duration_func(
                df,
                col='ethnic_group',
                col2="length",
                tick_size=11,
                tick_angle=0
            ),
            style={
                "height": "400px",
                "width": "100%"
            },
            config=config
        )
    ]

    if value == True:
        return children
    else:
        return None

#########################################################
################### Number of date ######################
#########################################################

@app.callback(
    Output('ndate_bar', 'figure'),
    Input('ageSlider_ndate', 'value'),
    Input('ethnic_ndate', 'value'),
    Input('study_ndate', 'value')
)

def update_graph(age, ethnic, study):

    ages = [i for i in range(age[0], age[1] + 1)]
    if study == 'All':
        data = df
    else:
        data = df[df['field_of_study'] == study]

    if ethnic == 'All':
        data = data
    else:
        data = data[data["ethnic_group"] == ethnic]

    #data = data[data['field_of_study'] == study]
    data = data[data['age'].isin(ages)]

    data2 = groupby(data, 'gender', 'speed_date_nb')

    fig = px.bar(
        # Data
        data2.sort_values(by="speed_date_nb", ascending=False),
        hover_data=data2,
        hover_name='speed_date_nb',
        x='percentage',
        y='gender',

        # Legend & annotate
        color='speed_date_nb',
        text='percentage',

        # Colors
        color_discrete_sequence=['lightgrey', 'darkred', 'red', 'lightgreen'],
        opacity=.8,
        # Cross shape
        pattern_shape='speed_date_nb',
        pattern_shape_sequence=[
            "x",
            "",
            "",
            "",
            "",
            ""]
    )


    if study in df['field_of_study'].unique() and ethnic in df['ethnic_group'].unique():
        title = f'Thought on number of dates ({study}, {ethnic})'

    elif study in df['field_of_study'].unique():
        title = f'Thought on number of dates ({study})'

    elif ethnic in df['ethnic_group'].unique():
        title = f'Thought on number of dates ({ethnic})'

    else:
        title =  "Overall thought on number of dates"

    if len(title) > 40:
        title_font_size = 12
    else:
        title_font_size = 15


    # Titles, axes
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=10, r=10),
        #template='plotly_dark',
        title_text=title,
        title_font_size=title_font_size,
        title_x=0.5,
        title_y=.9,
        legend_traceorder="reversed",
        yaxis_title=None,
        xaxis_title=None,
        legend_title=None,
        legend_orientation='h',
        legend_valign='middle',
        legend_x=-0.01,
        legend_y=-0.1
    )

    # Annotate percentage
    fig.update_traces(texttemplate='<b>%{text} %</b>',
                      textposition='inside',
                      textfont_size=10,
                      insidetextanchor="middle")

    return fig

@app.callback(
    Output('graph_container_ndate_study', 'children'),
    Input('BSwitch_ndate_study', 'on')
    )

def show_graph(value):

    children = [
        dcc.Graph(
            id="study_ndate_graph",
            figure=duration_func(
                df,
                col='field_of_study',
                col2="speed_date_nb",
                tick_size=9,
                tick_angle=45
            ),
            style={
                "height": "700px",
                "width": "100%"
            },
            config=config
        )
    ]

    if value == True:
        return children
    else:
        return None

@app.callback(
    Output('graph_container_ndate_ethnic', 'children'),
    Input('BSwitch_ndate_ethnic', 'on')
    )

def show_graph(value):

    children = [
        dcc.Graph(
            id="ethnic_ndate_graph",
            figure=duration_func(
                df,
                col='ethnic_group',
                col2="speed_date_nb",
                tick_size=11,
                tick_angle=0
            ),
            style={
                "height": "400px",
                "width": "100%"
            },
            config=config
        )
    ]

    if value == True:
        return children
    else:
        return None


# ------------------- Run server -----------------------

if __name__ == '__main__':
    app.run_server(
        debug=True,
        #port=8000
    )
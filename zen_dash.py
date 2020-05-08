#!/usr/bin/python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

from datetime import datetime

import pandas as pd

# задаём данные для отрисовки
from sqlalchemy import create_engine

if __name__ == "__main__":

    db_config = {'user': 'my_user',
                 'pwd': 'my_user_password',
                 'host': 'localhost',
                 'port': 5432,
                 'db': 'zen'}

    connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                             db_config['pwd'],
                                                             db_config['host'],
                                                             db_config['port'],
                                                             db_config['db'])

    engine = create_engine(connection_string)

    # получаем сырые данные
    query = '''
               SELECT * FROM dash_visits
           '''
    dash_visits = pd.io.sql.read_sql(query, con = engine)
    dash_visits['dt'] = pd.to_datetime(dash_visits['dt'])

    query = '''
               SELECT * FROM dash_engagement
           '''
    dash_engagement = pd.io.sql.read_sql(query, con = engine)
    dash_engagement['dt'] = pd.to_datetime(dash_engagement['dt']).dt.round('min')

note = '''
         Этот дашборд показывает историю событий Яндекс.Дзен по темам карточек, разбивку событий по темам источников и глубину взаимодействия пользователей с карточками.
         Используйте выбор интервала даты и времени истории событий по темам карточек и интервал возрастных категорий для управления дашбордом.
         Используйте выбор тем карточек для анализа графика разбивки событий по темам источников.
      '''

# задаём лейаут
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, compress=False)
app.layout = html.Div(children=[

    # формируем html
    html.H1(children = 'Анализ взаимодействия пользователей с карточками Яндекс.Дзен'),

    html.Br(),

    html.Label(note),

    html.Br(),

    html.Div([
        html.Div([

            # график истории событий по темам карточек
            html.Label('Выберете дату:'),

            dcc.DatePickerRange(
                start_date = dash_visits['dt'].min(),
                end_date = dash_visits['dt'].max(),
                display_format = 'YYYY-MM-DD',
                id = 'dt_selector',
            ),
            html.Br(),
            html.Label('Выберете возрастную группу посетеителей:'),
            dcc.Dropdown(
                options = [{'label': x, 'value': x} for x in dash_visits['age_segment'].unique()],
                value = dash_visits['age_segment'].unique().tolist(),
                multi = True,
                id = 'age-dropdown'
            ),
            html.Br(),
            html.Label('История событий по темам карточек'),
            html.Br(),
            dcc.Graph(
                style = {'height': '50vw'},
                id = 'history-absolute-visits'
            ),
        ], className = 'six columns'),

        html.Div([

            # график разбивки событий по темам источников
            html.Label('Выберете тему источника'),

            dcc.Dropdown(
                options = [{'label': x, 'value': x} for x in dash_visits['item_topic'].unique()],
                value = dash_visits['item_topic'].unique().tolist(),
                multi = True,
                id = 'item-topic-dropdown'
            ),
            html.Br(),
            html.Label('Разбивка событий по темам источников'),
            dcc.Graph(
                style = {'height': '25vw'},
                id = 'pie-visits'
            ),

            # график средней глубины взаимодействия
            html.Label('Средняя глубина взаимодействия:'),

            dcc.Graph(
                style = {'height': '25vw'},
                id = 'engagement-graph'
            ),
        ], className = 'six columns'),

    ], className = 'row'),

  ])

#описываем логику дашборда
@app.callback(
    [Output('history-absolute-visits', 'figure'),
     Output('pie-visits', 'figure'),
     Output('engagement-graph', 'figure'),
    ],
    [Input('dt_selector', 'start_date'),
     Input('dt_selector', 'end_date'),
     Input('item-topic-dropdown', 'value'),
     Input('age-dropdown', 'value')
    ])

def update_figures(start_date, end_date, selected_item_topics, selected_ages):
    #применяем фильтрацию
    filtered = dash_visits.query('dt >= @start_date and dt <= @end_date')
    filtered = filtered.query('item_topic in @selected_item_topics')
    filtered = filtered.query('age_segment in @selected_ages')

    filtered_topic = dash_visits.query('dt >= @start_date and dt <= @end_date')
    filtered_topic = filtered_topic.query('item_topic in @selected_item_topics')
    filtered_topic = filtered_topic.query('age_segment in @selected_ages')

    filtered_interactions = dash_engagement.query('dt >= @start_date and dt <= @end_date')
    filtered_interactions = filtered_interactions.query('item_topic in @selected_item_topics')
    filtered_interactions = filtered_interactions.query('age_segment in @selected_ages')

    history_by_items = (filtered.groupby(['item_topic', 'dt'])
                            .agg({'visits': 'sum'})
                            .reset_index()
                      )

    filtered_topic_1 = (filtered_topic.groupby(['source_topic'])
                               .agg({'visits': 'sum'})
                               .reset_index()
                      )

    filtered_interactions_1 = (filtered_interactions.groupby(['event'])
                               .agg({'unique_users': 'mean'})
                               .reset_index()
                      )

    filtered_interactions_1['avg_unique_users'] = filtered_interactions_1['unique_users'] / filtered_interactions_1['unique_users'].max()
    filtered_interactions_1 = filtered_interactions_1.sort_values(by='avg_unique_users', ascending=False)

  # график истории событий по темам карточек
    data_by_items = []
    for item_topic in history_by_items['item_topic'].unique():
        data_by_items += [go.Scatter(x = history_by_items.query('item_topic == @item_topic')['dt'],
                                   y = history_by_items.query('item_topic == @item_topic')['visits'],
                                   mode = 'lines',
                                   stackgroup = 'one',
                                   name = item_topic)]

  # график разбивки событий по темам источников
    data_by_topic = [go.Pie(labels = filtered_topic_1['source_topic'],
                          values = filtered_topic_1['visits'])]

  # график средней глубины взаимодействия
    sales_by_interactions = [go.Bar(x = filtered_interactions_1['event'],
                                  y = filtered_interactions_1['avg_unique_users']
                                  )]


  #формируем результат для отображения
    return (
            {
                'data': data_by_items,
                'layout': go.Layout(xaxis = {'title': 'Дата'},
                                    yaxis = {'title': 'Количество событий по темам'})
             },
            {
                'data': data_by_topic,
                'layout': go.Layout()
             },
            {
                'data': sales_by_interactions,
                'layout': go.Layout(xaxis = {'title': 'Событие'},
                                    yaxis = {'title': '% событий'})
             },

    )

if __name__ == '__main__':
    app.run_server(debug = True, host='0.0.0.0', port=3000)

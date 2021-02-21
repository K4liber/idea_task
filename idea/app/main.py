from os.path import join

import dash
import dash_core_components as dcc
import dash_html_components as html

from ..data.hdf5.in_memory import InMemory
from ..definitions import ROOT_DIR
from ..utils.logger import logger
from ..visualization.network_data import NetworkData
from ..visualization.style import MIN_CLUSTERS, MAX_CLUSTERS

hdf5_filepath = join(ROOT_DIR, 'data/hdf5/files/task_data.hdf5')
db = InMemory(hdf5_filepath)
network_data = NetworkData(db)
assets_path = join(ROOT_DIR, 'visualization/assets/')
app = dash.Dash(assets_folder=assets_path, title='Energy network')
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Input(id='hour_from', type='number', min=1, max=24),
                dcc.RangeSlider(
                    id='slider',
                    min=1,
                    max=24,
                    marks={x + 1: str(x + 1) for x in range(24)},
                    value=[6, 12],
                    allowCross=True
                ),
                dcc.Input(id='hour_to', type='number', min=1, max=24)
            ],
            id='range',
            style={'display': 'grid', 'grid-template-columns': '5% 90% 5%',
                   'width': '90vw', 'height': '3vh', 'margin': '0 auto', 'margin-bottom': '1vh', 'padding': '1vh'}
        ),
        dcc.Graph(figure=network_data.get_figure(),
                  id='network', style={'width': '90vw', 'height': '88vh', 'margin': '0 auto'}),
        html.Div(
            [
                html.Div(
                    [
                        'Clusters: ',
                        dcc.Input(id='n_clusters', type='number', value=1, min=MIN_CLUSTERS, max=MAX_CLUSTERS),
                    ],
                    id='clusters',
                    style={'display': 'grid', 'grid-template-columns': '5% 5%'}
                ),
            ],
            id='other_settings',
            style={'width': '90vw', 'height': '5vh', 'margin': '0 auto', 'margin-top': '1vh'}
        ),
    ],
    style={'background-color': '#AAF', 'margin': '0px'},
)


@app.callback(
    dash.dependencies.Output('slider', 'value'),
    [dash.dependencies.Input('hour_from', 'value'),
     dash.dependencies.Input('hour_to', 'value')])
def update_slider(new_hour_from, new_hour_to):
    return [new_hour_from, new_hour_to]


@app.callback(
    [
        dash.dependencies.Output('hour_from', 'value'),
        dash.dependencies.Output('hour_to', 'value'),
        dash.dependencies.Output('network', 'figure')
    ],
    [
        dash.dependencies.Input('slider', 'value'),
        dash.dependencies.Input('n_clusters', 'value'),
    ]
)
def update_figure(new_values, n_clusters):
    logger.error(new_values)
    logger.error(n_clusters)
    network_data.set_state(hour_from=new_values[0], hour_to=new_values[1], n_clusters=n_clusters)
    return [new_values[0], new_values[1], network_data.get_figure()]


app.run_server(host='0.0.0.0', debug=False, use_reloader=True)

import dash
from dash import html, dcc
import plotly.graph_objs as go
from collections import deque
import paho.mqtt.client as mqtt
import json

# Almacén de datos
rpm_data = deque(maxlen=50)
vel_data = deque(maxlen=50)

# MQTT
def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    rpm_data.append(data["rpm"])
    vel_data.append(data["vel_lineal"])

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("tractor/outputs")
client.loop_start()

# Dash App
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Tractor Dashboard"),
    dcc.Graph(id='live-graph'),
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # 1 sec
])

@app.callback(
    dash.dependencies.Output('live-graph', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=list(rpm_data), name='RPM'))
    fig.add_trace(go.Scatter(y=list(vel_data), name='Velocidad Lineal'))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

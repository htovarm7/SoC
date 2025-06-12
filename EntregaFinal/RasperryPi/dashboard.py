import dash
from dash import html, dcc, Input, Output
import dash_daq as daq
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
import json
import threading
from datetime import datetime

# === MQTT Setup ===
broker_address = "localhost"
topic_sub = "tractor/data"
topic_pub = "tractor/control"

rpm_data = []
vel_lineal_data = []
gear_data = []
timestamps = []

modo_manual = False

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT con código:", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm = data.get("rpm")
        vl = data.get("spd")
        gear = data.get("gear")
        now = datetime.now().strftime("%H:%M:%S")

        if rpm is not None and vl is not None and gear is not None:
            rpm_data.append(rpm)
            vel_lineal_data.append(vl)
            gear_data.append(gear)
            timestamps.append(now)

    except Exception as e:
        print("Error al procesar el mensaje:", e)

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)

def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True
mqtt_thread.start()

# === Dash App ===
app = dash.Dash(__name__)
app.title = "Tractor Dashboard"

app.layout = html.Div([
    html.H1("Dashboard del Tractor"),
    
    daq.ToggleSwitch(
        id='modo-switch',
        label=['Automático', 'Manual'],
        value=False
    ),

    html.Div([
        html.Label('Acelerador'),
        daq.BooleanSwitch(
            id='btn-acelerador',
            on=False,
            label="Encendido",
            labelPosition="top"
        
        ),
        html.Br(),
        
        html.Label('Freno'),
        daq.BooleanSwitch(
            id='btn-freno',
            on=False,
            label="Presionado",
            labelPosition="top"
        )
    ], id='manual-controls', style={'display': 'none'}),
    
    dcc.Graph(id='rpm-graph'),
    dcc.Graph(id='vel-graph'),
    dcc.Graph(id='gear-graph'),
    
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
    
    html.Div(id='dummy-output', style={'display': 'none'})
])

@app.callback(
    Output('manual-controls', 'style'),
    Input('modo-switch', 'value')
)
def toggle_manual_controls(mode):
    return {'display': 'block'} if mode else {'display': 'none'}

@app.callback(
    Output('dummy-output', 'children'),
    Input('btn-acelerador', 'on'),
    Input('btn-freno', 'on'),
    Input('modo-switch', 'value'),
    prevent_initial_call=True
)

def publish_control(acel_on, freno_on, modo):
    if modo:
        throttle = 100 if acel_on else 0
        brake = 100 if freno_on else 0
        
        payload = json.dumps({"throttle": throttle, "brake": brake})
        client.publish(topic_pub, payload)
    return ""

@app.callback(
    Output('rpm-graph', 'figure'),
    Output('vel-graph', 'figure'),
    Output('gear-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    rpm_fig = go.Figure()
    rpm_fig.add_trace(go.Scatter(x=timestamps, y=rpm_data, mode='lines+markers', name='RPM'))
    rpm_fig.update_layout(title='RPM del Motor', xaxis_title='Tiempo', yaxis_title='RPM', height=300)

    vel_fig = go.Figure()
    vel_fig.add_trace(go.Scatter(x=timestamps, y=vel_lineal_data, mode='lines+markers', name='Velocidad'))
    vel_fig.update_layout(title='Velocidad Lineal', xaxis_title='Tiempo', yaxis_title='km/h', height=300)

    gear_fig = go.Figure()
    gear_fig.add_trace(go.Scatter(x=timestamps, y=gear_data, mode='lines+markers', name='Marcha'))
    gear_fig.update_layout(title='Marcha', xaxis_title='Tiempo', yaxis_title='Gear', height=300)

    return rpm_fig, vel_fig, gear_fig

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
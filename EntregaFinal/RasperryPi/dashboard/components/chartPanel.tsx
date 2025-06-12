"use client"
import { useEffect, useState } from 'react';
import { client, topicSub } from '../mqtt/mqttClient';
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend
} from 'recharts';

export default function ChartPanel() {
  const [data, setData] = useState([]);

  useEffect(() => {
    client.on('connect', () => {
      console.log('MQTT conectado');
      client.subscribe(topicSub);
    });

    client.on('message', (topic, message) => {
      try {
        const json = JSON.parse(message.toString());
        const newData = {
          rpm: json.rpm,
          vel_lineal: json.vel_lineal
        };
        setData((prev) => [...prev.slice(-99), newData]); // limitar a 100 muestras
      } catch (e) {
        console.error('Error procesando mensaje MQTT:', e);
      }
    });

    return () => {
      client.end();
    };
  }, []);

  return (
    <div className="mt-8">
      <h2 className="text-lg font-semibold mb-4">Gráficas en Tiempo Real</h2>
      <LineChart width={600} height={300} data={data}>
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey={(d, idx) => idx} label={{ value: "Muestra", position: "insideBottom", offset: -5 }} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="rpm" stroke="#8884d8" name="RPM" />
        <Line type="monotone" dataKey="vel_lineal" stroke="#82ca9d" name="Vel. Lineal (m/s)" />
      </LineChart>
    </div>
  );
}

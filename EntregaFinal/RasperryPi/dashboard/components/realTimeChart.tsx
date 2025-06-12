"use client"
import React, { useEffect, useRef, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart, TimeScale, LinearScale, LineElement, PointElement, Tooltip } from "chart.js";
import "chartjs-adapter-date-fns";

Chart.register(TimeScale, LinearScale, LineElement, PointElement, Tooltip);

type DataPoint = { x: Date; y: number };

const RealTimeChart = () => {
  const [dataPoints, setDataPoints] = useState<DataPoint[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000/ws/data");

    ws.current.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      const timestamp = new Date();
      // Asegúrate de reemplazar "value" con el campo real que llega por MQTT
      setDataPoints((prev) => [...prev.slice(-50), { x: timestamp, y: data.value }]);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const chartData = {
    datasets: [
      {
        label: "Valor vs Tiempo",
        data: dataPoints,
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        type: "time" as const,
        time: { unit: "second" as const },
        title: { display: true, text: "Tiempo" },
      },
      y: {
        title: { display: true, text: "Valor" },
      },
    },
  };

  return (
    <div>
        <h1> Grafica </h1>
        <Line data={chartData} options={options} />
    </div>
  );
};

export default RealTimeChart;

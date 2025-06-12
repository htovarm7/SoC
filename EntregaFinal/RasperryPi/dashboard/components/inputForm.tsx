"use client"
import { useState } from 'react';
import { client, topicPub } from '../mqtt/mqttClient';

export default function InputForm() {
  const [inputs, setInputs] = useState({
    velocidad_angular: '',
    relacion_transmision: '',
    radio_rueda: ''
  });

  const handleChange = (e) => {
    setInputs({ ...inputs, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {
    const { velocidad_angular, relacion_transmision, radio_rueda } = inputs;

    const data = {
      velocidad_angular: parseFloat(velocidad_angular),
      relacion_transmision: parseFloat(relacion_transmision),
      radio_rueda: parseFloat(radio_rueda)
    };

    if (Object.values(data).some(isNaN)) {
      alert('Por favor ingresa valores numéricos válidos');
      return;
    }

    client.publish(topicPub, JSON.stringify(data));
    console.log("Datos enviados:", data);
  };

  return (
    <div className="p-4 border rounded w-full max-w-md">
      <label className="block mb-2">Velocidad Angular (rad/s)</label>
      <input
        type="number"
        name="velocidad_angular"
        value={inputs.velocidad_angular}
        onChange={handleChange}
        className="input border p-2 w-full mb-4"
      />

      <label className="block mb-2">Relación Transmisión</label>
      <input
        type="number"
        name="relacion_transmision"
        value={inputs.relacion_transmision}
        onChange={handleChange}
        className="input border p-2 w-full mb-4"
      />

      <label className="block mb-2">Radio de Rueda (m)</label>
      <input
        type="number"
        name="radio_rueda"
        value={inputs.radio_rueda}
        onChange={handleChange}
        className="input border p-2 w-full mb-4"
      />

      <button
        onClick={handleSubmit}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Enviar
      </button>
    </div>
  );
}

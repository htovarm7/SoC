import mqtt from 'mqtt';

const brokerUrl = 'ws://192.168.137.214:9001'; // MQTT debe estar en WebSocket (verifica que tu broker soporte esto)
const topicPub = 'tractor/inputs';
const topicSub = 'tractor/outputs';

const client = mqtt.connect(brokerUrl);

export { client, topicPub, topicSub };

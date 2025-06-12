import InputForm from '@/components/inputForm';
import ChartPanel from '@/components/chartPanel';

function App() {
  return (
    <main className="p-6 font-sans">
      <h1 className="text-2xl font-bold mb-6">Control de Tractor</h1>
      <InputForm />
      <ChartPanel />
    </main>
  );
}

export default App;
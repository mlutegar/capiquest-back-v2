import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';

const GraficoLinha = ({ dados }) => {

  if (!dados || dados.length === 0)
    return <p>Nenhum dado disponível</p>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={dados}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="tentativa" />
        <YAxis />
        <Tooltip formatter={(v) => `${v.toFixed(2)}s`} />
        <Legend />
        <Line
          type="monotone"
          dataKey="tempo_reacao"
          stroke="#8884d8"
          strokeWidth={2}
          name="Tempo de Reação"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default GraficoLinha;
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

const GraficoLinha = ({ dados }) => {

  if (!dados || dados.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-500">
        Nenhum dado disponível
      </div>
    );
  }

  const media = (
    dados.reduce((acc, d) => acc + d.tempo_reacao, 0)
    / dados.length
  ).toFixed(2);

  return (
    <div className="bg-white rounded-2xl shadow-md p-4">

      <h2 className="text-lg font-bold mb-4">
        Evolução do Tempo de Reação
      </h2>

      <ResponsiveContainer width="100%" height={320}>

        <LineChart data={dados}>

          <CartesianGrid
            strokeDasharray="3 3"
            opacity={0.3}
          />

          <XAxis dataKey="tentativa" />

          <YAxis />

          <Tooltip
            formatter={(v) => `${v.toFixed(2)}s`}
            contentStyle={{
              borderRadius: '12px',
              border: 'none',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
            }}
          />

          <Legend />

          <ReferenceLine
            y={media}
            stroke="#ef4444"
            strokeDasharray="5 5"
            label="Média"
          />

          <Line
            type="monotone"
            dataKey="tempo_reacao"
            stroke="#8b5cf6"
            strokeWidth={3}
            dot={{ r: 5 }}
            activeDot={{ r: 8 }}
            animationDuration={1200}
            name="Tempo de Reação"
          />

        </LineChart>

      </ResponsiveContainer>

    </div>
  );
};

export default GraficoLinha;
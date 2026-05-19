import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList
} from 'recharts';

const TIPOS = {
  click: 'Clique',
  drag: 'Arrastar',
  type: 'Digitar'
};

const GraficoBarras = ({ dados }) => {

  if (!dados || dados.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-500">
        Nenhum dado disponível
      </div>
    );
  }

  const transformados = dados.map(d => ({
    tipo: TIPOS[d.tipo] || d.tipo,
    pontuacao_media: Number(d.pontuacao_media)
  }));

  return (
    <div className="bg-white rounded-2xl shadow-md p-4">

      <h2 className="text-lg font-bold mb-4">
        Pontuação Média por Tipo
      </h2>

      <ResponsiveContainer width="100%" height={320}>

        <BarChart data={transformados}>

          <CartesianGrid
            strokeDasharray="3 3"
            opacity={0.3}
          />

          <XAxis dataKey="tipo" />

          <YAxis />

          <Tooltip
            formatter={(v) => `${v.toFixed(2)} pts`}
            contentStyle={{
              borderRadius: '12px',
              border: 'none',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
            }}
          />

          <Legend />

          <Bar
            dataKey="pontuacao_media"
            fill="#6366f1"
            radius={[10, 10, 0, 0]}
            animationDuration={1000}
            name="Pontuação Média"
          >

            <LabelList
              dataKey="pontuacao_media"
              position="top"
              formatter={(v) => v.toFixed(1)}
            />

          </Bar>

        </BarChart>

      </ResponsiveContainer>

    </div>
  );
};

export default GraficoBarras;
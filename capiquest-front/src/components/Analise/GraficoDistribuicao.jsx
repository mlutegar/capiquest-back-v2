import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList
} from 'recharts';

const ORDEM = ['0-2s', '2-4s', '4-6s', '6+s'];

const CORES = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444'];

const GraficoDistribuicao = ({ dados }) => {

  if (!dados || dados.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-500">
        Nenhum dado disponível
      </div>
    );
  }

  const ordenados = [...dados].sort(
    (a, b) => ORDEM.indexOf(a.faixa) - ORDEM.indexOf(b.faixa)
  );

  return (
    <div className="bg-white rounded-2xl shadow-md p-4">

      <h2 className="text-lg font-bold mb-4">
        Distribuição por Tempo
      </h2>

      <ResponsiveContainer width="100%" height={320}>

        <BarChart data={ordenados}>

          <CartesianGrid
            strokeDasharray="3 3"
            opacity={0.3}
          />

          <XAxis
            dataKey="faixa"
            tick={{ fontSize: 12 }}
          />

          <YAxis />

          <Tooltip
            contentStyle={{
              borderRadius: '12px',
              border: 'none',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
            }}
          />

          <Bar
            dataKey="quantidade"
            radius={[10, 10, 0, 0]}
            animationDuration={1200}
          >

            {
              ordenados.map((_, index) => (
                <Cell
                  key={index}
                  fill={CORES[index % CORES.length]}
                />
              ))
            }

            <LabelList
              dataKey="quantidade"
              position="top"
            />

          </Bar>

        </BarChart>

      </ResponsiveContainer>

    </div>
  );
};

export default GraficoDistribuicao;
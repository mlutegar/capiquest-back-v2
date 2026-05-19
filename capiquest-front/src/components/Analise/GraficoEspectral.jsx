import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

const GraficoEspectral = ({ dados }) => {

  if (!dados || dados.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-gray-500">
        Nenhum dado disponível
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-md p-4">

      <h2 className="text-lg font-bold mb-4">
        Análise Espectral
      </h2>

      <ResponsiveContainer width="100%" height={350}>

        <AreaChart data={dados}>

          <defs>

            <linearGradient
              id="colorSpectral"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >

              <stop
                offset="0%"
                stopColor="#8b5cf6"
                stopOpacity={0.9}
              />

              <stop
                offset="50%"
                stopColor="#3b82f6"
                stopOpacity={0.5}
              />

              <stop
                offset="100%"
                stopColor="#06b6d4"
                stopOpacity={0.1}
              />

            </linearGradient>

          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            opacity={0.2}
          />

          <XAxis dataKey="tempo" />

          <YAxis />

          <Tooltip
            formatter={(v) => `${v}`}
            contentStyle={{
              borderRadius: '12px',
              border: 'none',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
            }}
          />

          <Area
            type="monotone"
            dataKey="intensidade"
            stroke="#8b5cf6"
            strokeWidth={3}
            fill="url(#colorSpectral)"
            animationDuration={1500}
          />

        </AreaChart>

      </ResponsiveContainer>

    </div>
  );
};

export default GraficoEspectral;
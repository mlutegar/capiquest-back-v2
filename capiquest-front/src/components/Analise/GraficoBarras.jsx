import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const TIPOS = { click: 'Clique', drag: 'Arrastar', type: 'Digitar' };

const GraficoBarras = ({ dados }) => {
  const transformados = dados.map(d => ({
    tipo: TIPOS[d.tipo] || d.tipo,
    pontuacao_media: d.pontuacao_media
  }));

  return (
    <ResponsiveContainer width='100%' height={300}>
      <BarChart data={transformados}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis dataKey='tipo' />
        <YAxis />
        <Tooltip formatter={(v) => v.toFixed(2)} />
        <Legend />
        <Bar
          dataKey='pontuacao_media'
          fill='#884d8'   // ⚠️ ATENÇÃO: provável erro de digitação – o correto seria '#8884d8'
          name='Pontuacao Media'
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default GraficoBarras;
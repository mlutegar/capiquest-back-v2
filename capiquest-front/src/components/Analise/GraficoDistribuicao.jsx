import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const CORES = {
  '0-2s': '#4caf50',
  '2-4s': '#8bc34a',
  '4-6s': '#ff9800',
  '6+s': '#f44336'
};

const ORDEM = ['0-2s', '2-4s', '4-6s', '6+s'];

const GraficoDistribuicao = ({ dados }) => {
  const ordenados = [...dados].sort(
    (a, b) => ORDEM.indexOf(a.faixa) - ORDEM.indexOf(b.faixa)
  );

  return (
    <ResponsiveContainer width='100%' height={300}>
      <BarChart data={ordenados}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis dataKey='faixa' />
        <YAxis label={{ value: 'Quantidade', angle: -90 }} />
        <Tooltip />
        <Bar dataKey='quantidade' fill='#82ca9d' name='Qtd' />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default GraficoDistribuicao;
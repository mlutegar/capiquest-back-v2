import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip,
  ResponsiveContainer
} from 'recharts';

const ORDEM = ['0-2s', '2-4s', '4-6s', '6+s'];

const GraficoDistribuicao = ({ dados }) => {

  const ordenados = [...dados].sort(
    (a, b) => ORDEM.indexOf(a.faixa) - ORDEM.indexOf(b.faixa)
  );

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={ordenados}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="faixa" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="quantidade" name="Quantidade" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default GraficoDistribuicao;
import { useState, useEffect } from 'react';

import GraficoLinha from '../components/Analise/GraficoLinha';
import GraficoBarras from '../components/Analise/GraficoBarras';
import GraficoDistribuicao from '../components/Analise/GraficoDistribuicao';

const Analise = () => {

  const [criancas, setCriancas] = useState([]);
  const [criancaSelecionada, setCriancaSelecionada] = useState(null);
  const [dadosAnalise, setDadosAnalise] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    carregarCriancas();
  }, []);

  useEffect(() => {
    carregarDadosAnalise();
  }, [criancaSelecionada]);

  const carregarCriancas = async () => {
    const response = await fetch('http://127.0.0.1:8075/polls/api/analise/criancas/');
    const data = await response.json();
    setCriancas(data);
  };

  const carregarDadosAnalise = async () => {

    setLoading(true);
    setErro(null);

    try {
      let url = 'http://127.0.0.1:8030/polls/api/analise/dados-gerais/';

      if (criancaSelecionada)
        url += `?crianca_id=${criancaSelecionada}`;

      const response = await fetch(url);

      if (!response.ok)
        throw new Error('Erro na requisição');

      const dados = await response.json();

      setDadosAnalise(dados.total_acoes === 0 ? null : dados);

    } catch (error) {
      setErro('Não foi possível carregar os dados');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>

      <select onChange={e => setCriancaSelecionada(e.target.value || null)}>
        <option value="">Todas</option>
        {criancas.map(c => (
          <option key={c.id} value={c.id}>{c.nome}</option>
        ))}
      </select>

      {erro && <p style={{ color: 'red' }}>{erro}</p>}
      {loading && <p>Carregando...</p>}

      {!loading && dadosAnalise && (
        <>
          <GraficoLinha dados={dadosAnalise.tempo_reacao_serie} />
          <GraficoBarras dados={dadosAnalise.pontuacao_por_tipo} />
          <GraficoDistribuicao dados={dadosAnalise.distribuicao_tempo_resposta} />
        </>
      )}

    </div>
  );
};

export default Analise;
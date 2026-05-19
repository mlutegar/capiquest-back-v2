import { useState, useEffect } from 'react';
import GraficoLinha from '../components/Analise/GraficoLinha';
import GraficoBarras from '../components/Analise/GraficoBarras';
import GraficoDistribuicao from '../components/Analise/GraficoDistribuicao';
import GraficoEspectral from '../components/Analise/GraficoEspectral'; // Adicionar esta importação

const Analise = () => {
  const [criancas, setCriancas] = useState([]);
  const [criancaSelecionada, setCriancaSelecionada] = useState(null);
  const [dadosAnalise, setDadosAnalise] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState(null);

  // URL base - ajuste para a porta correta do seu backend
  const API_BASE_URL = 'http://127.0.0.1:8000'; // ou 8075

  useEffect(() => {
    carregarCriancas();
  }, []);

  useEffect(() => {
    carregarDadosAnalise();
  }, [criancaSelecionada]);

  const carregarCriancas = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/polls/api/analise/criancas/`);
      
      if (!response.ok) {
        throw new Error('Erro ao carregar crianças');
      }
      
      const data = await response.json();
      setCriancas(data);
    } catch (error) {
      setErro('Não foi possível carregar a lista de crianças');
    }
  };

  const carregarDadosAnalise = async () => {
    setLoading(true);
    setErro(null);

    try {
      let url = `${API_BASE_URL}/polls/api/analise/dados-gerais/`;

      if (criancaSelecionada) {
        url += `?crianca_id=${criancaSelecionada}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Erro na requisição');
      }

      const dados = await response.json();

      // Verifica se há dados válidos
      if (dados.total_acoes === 0 || !dados.total_acoes) {
        setDadosAnalise(null);
        setErro('Nenhum dado disponível para análise');
      } else {
        setDadosAnalise(dados);
        setErro(null);
      }

    } catch (error) {
      console.error('Erro:', error);
      setErro('Não foi possível carregar os dados');
      setDadosAnalise(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCriancaChange = (e) => {
    const value = e.target.value;
    setCriancaSelecionada(value || null);
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="crianca-select">Selecionar criança: </label>
        <select 
          id="crianca-select"
          onChange={handleCriancaChange}
          value={criancaSelecionada || ''}
        >
          <option value="">Todas as crianças</option>
          {criancas.map((crianca) => (
            <option key={crianca.id} value={crianca.id}>
              {crianca.nome}
            </option>
          ))}
        </select>
      </div>

      {erro && (
        <div style={{ 
          color: 'red', 
          padding: '10px', 
          marginBottom: '20px',
          backgroundColor: '#ffebee',
          borderRadius: '4px'
        }}>
          {erro}
        </div>
      )}
      
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          Carregando dados...
        </div>
      )}

      {!loading && dadosAnalise && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Gráfico Espectral - adicionado no topo */}
          {dadosAnalise.dados_espectrais && (
            <GraficoEspectral dados={dadosAnalise.dados_espectrais} />
          )}

          {/* Grid para os gráficos existentes */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', 
            gap: '24px' 
          }}>
            {dadosAnalise.tempo_reacao_serie && (
              <GraficoLinha dados={dadosAnalise.tempo_reacao_serie} />
            )}
            
            {dadosAnalise.pontuacao_por_tipo && (
              <GraficoBarras dados={dadosAnalise.pontuacao_por_tipo} />
            )}
            
            {dadosAnalise.distribuicao_tempo_resposta && (
              <GraficoDistribuicao dados={dadosAnalise.distribuicao_tempo_resposta} />
            )}
          </div>

          {(!dadosAnalise.tempo_reacao_serie && 
            !dadosAnalise.pontuacao_por_tipo && 
            !dadosAnalise.distribuicao_tempo_resposta &&
            !dadosAnalise.dados_espectrais) && (
            <p>Nenhum gráfico disponível para os dados selecionados</p>
          )}
        </div>
      )}

      {!loading && !dadosAnalise && !erro && (
        <p>Selecione uma criança para visualizar os dados de análise</p>
      )}
    </div>
  );
};

export default Analise;
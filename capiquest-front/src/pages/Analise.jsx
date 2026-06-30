// frontend/src/Analise.jsx

import { useState, useEffect } from 'react';
import GraficoLinha from '../components/Analise/GraficoLinha';
import GraficoBarras from '../components/Analise/GraficoBarras';
import GraficoDistribuicao from '../components/Analise/GraficoDistribuicao';
import GraficoEspectral from '../components/Analise/GraficoEspectral';
import GraficoJitter from '../components/Analise/GraficoJitter';

const Analise = () => {
  const [criancas, setCriancas] = useState([]);
  const [criancaSelecionada, setCriancaSelecionada] = useState(null);
  const [dadosAnalise, setDadosAnalise] = useState(null);
  const [dadosGrupo, setDadosGrupo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingGrupo, setLoadingGrupo] = useState(false);
  const [erro, setErro] = useState(null);
  const [agruparPor, setAgruparPor] = useState('crianca');
  const [exportando, setExportando] = useState(false);

  const API_BASE_URL = 'http://127.0.0.1:8000';

  useEffect(() => {
    carregarCriancas();
  }, []);

  useEffect(() => {
    carregarDadosAnalise();
    carregarDadosGrupo();
  }, [criancaSelecionada, agruparPor]);

  const carregarCriancas = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/polls/api/analise/criancas/`);
      if (!response.ok) throw new Error('Erro ao carregar crianças');
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
      if (!response.ok) throw new Error('Erro na requisição');

      const dados = await response.json();
      
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

  const carregarDadosGrupo = async () => {
    setLoadingGrupo(true);
    try {
      const url = `${API_BASE_URL}/polls/api/analise/dados-grupo/?agrupar_por=${agruparPor}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Erro ao carregar dados de grupo');
      const dados = await response.json();
      setDadosGrupo(dados.dados || []);
    } catch (error) {
      console.error('Erro ao carregar dados de grupo:', error);
      setDadosGrupo([]);
    } finally {
      setLoadingGrupo(false);
    }
  };

  const handleCriancaChange = (e) => {
    setCriancaSelecionada(e.target.value || null);
  };

  const handleAgruparChange = (e) => {
    setAgruparPor(e.target.value);
  };

  const handleExportar = async (formato) => {
    setExportando(true);
    try {
      const url = `${API_BASE_URL}/polls/api/analise/exportar/${formato}/?crianca_id=${criancaSelecionada || ''}`;
      const response = await fetch(url);
      
      if (!response.ok) throw new Error('Erro na exportação');
      
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      
      // Extrair nome do arquivo do header Content-Disposition
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `analise.${formato}`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/);
        if (match) filename = match[1];
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Erro na exportação:', error);
      alert('Erro ao exportar arquivo');
    } finally {
      setExportando(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '20px' }}>
        📊 Análise de Desempenho
      </h1>
      
      {/* Controles */}
      <div style={{ 
        background: 'white', 
        padding: '20px', 
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center' }}>
          <div>
            <label htmlFor="crianca-select" style={{ display: 'block', marginBottom: '4px', fontWeight: '600' }}>
              👤 Criança
            </label>
            <select 
              id="crianca-select"
              onChange={handleCriancaChange}
              value={criancaSelecionada || ''}
              style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #ddd', minWidth: '150px' }}
            >
              <option value="">Todas</option>
              {criancas.map((crianca) => (
                <option key={crianca.id} value={crianca.id}>
                  {crianca.nome}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="agrupar-select" style={{ display: 'block', marginBottom: '4px', fontWeight: '600' }}>
              📂 Agrupar por
            </label>
            <select 
              id="agrupar-select"
              onChange={handleAgruparChange}
              value={agruparPor}
              style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #ddd', minWidth: '150px' }}
            >
              <option value="crianca">Criança</option>
              <option value="tipo">Tipo de Ação</option>
              <option value="faixa_etaria">Faixa Etária</option>
            </select>
          </div>
          
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
            <button
              onClick={() => handleExportar('excel')}
              disabled={exportando}
              style={{
                padding: '8px 20px',
                borderRadius: '8px',
                border: 'none',
                background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                color: 'white',
                fontWeight: '600',
                cursor: exportando ? 'not-allowed' : 'pointer',
                opacity: exportando ? 0.7 : 1
              }}
            >
              {exportando ? '⏳' : '📊'} Excel
            </button>
            <button
              onClick={() => handleExportar('pdf')}
              disabled={exportando}
              style={{
                padding: '8px 20px',
                borderRadius: '8px',
                border: 'none',
                background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                color: 'white',
                fontWeight: '600',
                cursor: exportando ? 'not-allowed' : 'pointer',
                opacity: exportando ? 0.7 : 1
              }}
            >
              {exportando ? '⏳' : '📄'} PDF
            </button>
          </div>
        </div>
      </div>

      {erro && (
        <div style={{ 
          color: 'red', 
          padding: '12px', 
          marginBottom: '16px',
          backgroundColor: '#ffebee',
          borderRadius: '8px'
        }}>
          {erro}
        </div>
      )}
      
      {loading && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          Carregando dados...
        </div>
      )}

      {/* Gráfico Jitter - Análise em Grupo */}
      <div style={{ marginBottom: '30px' }}>
        {loadingGrupo ? (
          <div style={{ textAlign: 'center', padding: '40px', background: 'white', borderRadius: '16px' }}>
            Carregando dados de grupo...
          </div>
        ) : (
          <GraficoJitter 
            dados={dadosGrupo} 
            grupoPor={agruparPor}
            eixoX="tempo_reacao"
          />
        )}
      </div>

      {/* Gráficos individuais */}
      {!loading && dadosAnalise && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Gráfico Espectral */}
          {dadosAnalise.dados_espectrais && dadosAnalise.dados_espectrais.length > 0 && (
            <GraficoEspectral dados={dadosAnalise.dados_espectrais} />
          )}

          {/* Grid de gráficos */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', 
            gap: '24px' 
          }}>
            {dadosAnalise.tempo_reacao_serie && dadosAnalise.tempo_reacao_serie.length > 0 && (
              <GraficoLinha dados={dadosAnalise.tempo_reacao_serie} />
            )}
            
            {dadosAnalise.pontuacao_por_tipo && dadosAnalise.pontuacao_por_tipo.length > 0 && (
              <GraficoBarras dados={dadosAnalise.pontuacao_por_tipo} />
            )}
            
            {dadosAnalise.distribuicao_tempo_resposta && dadosAnalise.distribuicao_tempo_resposta.length > 0 && (
              <GraficoDistribuicao dados={dadosAnalise.distribuicao_tempo_resposta} />
            )}
          </div>
        </div>
      )}

      {!loading && !dadosAnalise && !erro && (
        <div style={{ 
          textAlign: 'center', 
          padding: '40px', 
          background: 'white', 
          borderRadius: '16px',
          color: '#a0aec0'
        }}>
          <span style={{ fontSize: '48px', display: 'block', marginBottom: '16px' }}>📊</span>
          <p style={{ fontSize: '18px' }}>Selecione uma criança para visualizar os dados de análise</p>
        </div>
      )}
    </div>
  );
};

export default Analise;
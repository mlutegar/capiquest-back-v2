/**
 * GraficoMarcador.jsx
 * Componente React para visualização de análise de desempenho por marcadores
 * Versão: 1.0
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  ScatterController,
  DoughnutController,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Bar, Doughnut, Scatter } from 'react-chartjs-2';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  ScatterController,
  DoughnutController,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// ============================================================
// CONSTANTES
// ============================================================

const NIVEIS = {
  1: { rotulo: 'Ausência', cor: '#ef4444', corClara: '#fca5a5', icone: '🔴', ordem: 1 },
  2: { rotulo: 'Intermediário', cor: '#f59e0b', corClara: '#fcd34d', icone: '🟡', ordem: 2 },
  3: { rotulo: 'Êxito', cor: '#22c55e', corClara: '#86efac', icone: '🟢', ordem: 3 }
};

// ============================================================
// SUBCOMPONENTES
// ============================================================

/**
 * Card de resumo por nível
 */
const CardNivel = ({ nivel, stats, total }) => {
  const info = NIVEIS[nivel] || { rotulo: `Nível ${nivel}`, cor: '#888', icone: '⚪' };
  const pct = total > 0 ? (stats.quantidade / total * 100) : 0;

  return (
    <div className="gm-card" style={{ borderLeftColor: info.cor }}>
      <div className="gm-card-header">
        <span className="gm-card-icon">{info.icone}</span>
        <span className="gm-card-titulo">{info.rotulo}</span>
        <span className="gm-card-badge">{stats.quantidade || 0} ações</span>
      </div>
      <div className="gm-card-body">
        <div className="gm-card-stat">
          <span className="gm-card-label">⏱ Tempo médio</span>
          <span className="gm-card-valor" style={{ color: info.cor }}>
            {(stats.tempo_medio || 0).toFixed(2)}s
          </span>
        </div>
        <div className="gm-card-stat">
          <span className="gm-card-label">📊 Porcentagem</span>
          <span className="gm-card-valor">{pct.toFixed(1)}%</span>
        </div>
        <div className="gm-card-stat">
          <span className="gm-card-label">📉 Min - Max</span>
          <span className="gm-card-valor">
            {(stats.tempo_min || 0).toFixed(2)}s - {(stats.tempo_max || 0).toFixed(2)}s
          </span>
        </div>
        <div className="gm-card-stat">
          <span className="gm-card-label">⭐ Pontuação média</span>
          <span className="gm-card-valor">{(stats.pontuacao_media || 0).toFixed(2)}</span>
        </div>
      </div>
      <div className="gm-card-bar">
        <div className="gm-card-progress" style={{ width: `${pct}%`, background: info.cor }} />
      </div>
    </div>
  );
};

/**
 * Tabela detalhada
 */
const TabelaDetalhada = ({ dadosPorNivel, total }) => {
  let totalQuantidade = 0;
  let totalPontuacao = 0;
  let totalTempo = 0;

  const rows = [1, 2, 3].map(nivel => {
    const info = NIVEIS[nivel];
    const stats = dadosPorNivel.find(d => d.nivel === nivel) || { 
      quantidade: 0, 
      tempo_medio: 0, 
      tempo_min: 0, 
      tempo_max: 0, 
      pontuacao_media: 0 
    };
    
    totalQuantidade += stats.quantidade || 0;
    totalPontuacao += (stats.pontuacao_media || 0) * (stats.quantidade || 0);
    totalTempo += (stats.tempo_medio || 0) * (stats.quantidade || 0);

    const pct = total > 0 ? (stats.quantidade / total * 100) : 0;

    return (
      <tr key={nivel}>
        <td>
          <span className="gm-tabela-nivel" style={{ color: info.cor }}>
            {info.icone} {info.rotulo}
          </span>
        </td>
        <td>{stats.quantidade || 0}</td>
        <td>{pct.toFixed(1)}%</td>
        <td>{(stats.tempo_medio || 0).toFixed(2)}s</td>
        <td>{(stats.tempo_min || 0).toFixed(2)}s</td>
        <td>{(stats.tempo_max || 0).toFixed(2)}s</td>
        <td>{(stats.pontuacao_media || 0).toFixed(2)}</td>
      </tr>
    );
  });

  const mediaGeralPontuacao = totalQuantidade > 0 ? totalPontuacao / totalQuantidade : 0;
  const mediaGeralTempo = totalQuantidade > 0 ? totalTempo / totalQuantidade : 0;

  return (
    <div className="gm-tabela-container">
      <h4>📋 Tabela Detalhada por Nível</h4>
      <table className="gm-tabela">
        <thead>
          <tr>
            <th>Nível</th>
            <th>Quantidade</th>
            <th>Porcentagem</th>
            <th>Tempo Médio</th>
            <th>Tempo Mínimo</th>
            <th>Tempo Máximo</th>
            <th>Pontuação Média</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
        <tfoot>
          <tr className="gm-tabela-total">
            <td><strong>📊 TOTAL</strong></td>
            <td><strong>{totalQuantidade}</strong></td>
            <td>100%</td>
            <td><strong>{mediaGeralTempo.toFixed(2)}s</strong></td>
            <td>-</td>
            <td>-</td>
            <td><strong>{mediaGeralPontuacao.toFixed(2)}</strong></td>
          </tr>
        </tfoot>
      </table>
      <div className="gm-tabela-observacao">
        <small>
          💡 <strong>Interpretação:</strong> Níveis mais altos (Êxito) geralmente apresentam 
          tempos de reação menores e pontuações mais altas, indicando melhor desempenho na tarefa.
        </small>
      </div>
    </div>
  );
};

/**
 * Legenda do gráfico
 */
const Legenda = () => (
  <div className="gm-legend">
    {[1, 2, 3].map(nivel => {
      const info = NIVEIS[nivel];
      return (
        <div key={nivel} className="gm-legend-item">
          <span className="gm-legend-color" style={{ background: info.cor }} />
          <span>
            Nível {nivel} - {info.rotulo}: {nivel === 1 ? 'Baixo desempenho' : nivel === 2 ? 'Em desenvolvimento' : 'Alto desempenho'}
          </span>
        </div>
      );
    })}
  </div>
);

// ============================================================
// COMPONENTE PRINCIPAL
// ============================================================

const GraficoMarcador = ({ 
  dados, 
  loading = false, 
  erro = null, 
  onRefresh,
  mostrarBoxplot = true,
  mostrarTabela = true,
  mostrarDistribuicao = true,
  className = ''
}) => {
  const [dadosProcessados, setDadosProcessados] = useState({
    porNivel: [],
    porMarcador: [],
    brutosPorNivel: { 1: [], 2: [], 3: [] },
    total: 0,
    estatisticas: {}
  });

  // Processar dados quando recebidos
  useEffect(() => {
    if (dados) {
      const porNivel = dados.dados_por_nivel || [];
      const porMarcador = dados.dados_por_marcador || [];
      
      // Agrupar dados brutos por nível
      const brutosPorNivel = { 1: [], 2: [], 3: [] };
      porMarcador.forEach(item => {
        const nivel = item.nivel || 1;
        if (brutosPorNivel[nivel]) {
          brutosPorNivel[nivel].push(item.tempo_reacao || 0);
        }
      });

      // Calcular estatísticas
      const estatisticas = {};
      [1, 2, 3].forEach(nivel => {
        const dadosNivel = porNivel.find(d => d.nivel === nivel);
        estatisticas[nivel] = dadosNivel || { 
          quantidade: 0, 
          tempo_medio: 0, 
          tempo_min: 0, 
          tempo_max: 0, 
          pontuacao_media: 0 
        };
      });

      setDadosProcessados({
        porNivel,
        porMarcador,
        brutosPorNivel,
        total: porMarcador.length,
        estatisticas
      });
    }
  }, [dados]);

  // Configuração do gráfico de barras
  const configBarras = {
    labels: [1, 2, 3]
      .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
      .map(n => NIVEIS[n].rotulo),
    datasets: [{
      label: 'Tempo Médio de Reação (s)',
      data: [1, 2, 3]
        .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
        .map(n => dadosProcessados.estatisticas[n]?.tempo_medio || 0),
      backgroundColor: [1, 2, 3]
        .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
        .map(n => NIVEIS[n].corClara),
      borderColor: [1, 2, 3]
        .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
        .map(n => NIVEIS[n].cor),
      borderWidth: 2,
      borderRadius: 8,
      barPercentage: 0.7,
    }]
  };

  // Configuração do gráfico de distribuição (doughnut)
  const configDistribuicao = {
    labels: [1, 2, 3]
      .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
      .map(n => NIVEIS[n].rotulo),
    datasets: [{
      data: [1, 2, 3]
        .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
        .map(n => dadosProcessados.estatisticas[n]?.pontuacao_media || 0),
      backgroundColor: [1, 2, 3]
        .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
        .map(n => NIVEIS[n].cor + '99'),
      borderColor: [1, 2, 3]
        .filter(n => dadosProcessados.estatisticas[n]?.quantidade > 0)
        .map(n => NIVEIS[n].cor),
      borderWidth: 3,
      hoverOffset: 10,
    }]
  };

  // Configuração do boxplot (scatter com jitter)
  const configBoxplot = {
    datasets: [1, 2, 3]
      .filter(n => (dadosProcessados.brutosPorNivel[n] || []).length > 1)
      .map(n => {
        const valores = dadosProcessados.brutosPorNivel[n] || [];
        const info = NIVEIS[n];
        return {
          label: info.rotulo,
          data: valores.map((v, i) => ({
            x: n + (Math.random() - 0.5) * 0.4,
            y: v
          })),
          backgroundColor: info.cor + '66',
          borderColor: info.cor,
          borderWidth: 1,
          pointRadius: 5,
          pointHoverRadius: 8,
        };
      })
  };

  // Estados de loading e erro
  if (loading) {
    return (
      <div className="gm-loading">
        <div className="gm-spinner" />
        <p>Carregando dados de marcadores...</p>
      </div>
    );
  }

  if (erro) {
    return (
      <div className="gm-erro">
        <p>❌ Erro ao carregar dados: {erro}</p>
        {onRefresh && (
          <button onClick={onRefresh} className="gm-btn-retry">
            🔃 Tentar novamente
          </button>
        )}
      </div>
    );
  }

  if (!dados || dadosProcessados.total === 0) {
    return (
      <div className="gm-sem-dados">
        <p>📭 Nenhum dado com marcador disponível</p>
        <small>Certifique-se de que as ações possuem nível definido no marcador.</small>
      </div>
    );
  }

  // Renderização principal
  return (
    <div className={`grafico-marcador-wrapper ${className}`}>
      {/* Header */}
      <div className="gm-header">
        <h3>📊 Análise de Desempenho por Marcador</h3>
        <p className="gm-subtitle">Relação entre tempo de reação e nível de habilidade</p>
        <div className="gm-total">
          Total de ações com marcador: <strong>{dadosProcessados.total}</strong>
        </div>
      </div>

      {/* Cards */}
      <div className="gm-cards">
        {[1, 2, 3].map(nivel => (
          <CardNivel
            key={nivel}
            nivel={nivel}
            stats={dadosProcessados.estatisticas[nivel] || {}}
            total={dadosProcessados.total}
          />
        ))}
      </div>

      {/* Gráficos em grid */}
      <div className="gm-charts-grid">
        <div className="gm-chart-container">
          <h4>📈 Tempo Médio por Nível</h4>
          <Bar 
            data={configBarras} 
            options={{
              responsive: true,
              maintainAspectRatio: true,
              plugins: {
                legend: { display: true, position: 'top' },
                tooltip: {
                  callbacks: {
                    label: ctx => `Tempo médio: ${ctx.parsed.y.toFixed(2)}s`
                  }
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: { display: true, text: 'Tempo (segundos)' },
                  grid: { color: 'rgba(0,0,0,0.05)' }
                },
                x: { grid: { display: false } }
              }
            }}
          />
        </div>

        {mostrarBoxplot && configBoxplot.datasets.length > 0 && (
          <div className="gm-chart-container">
            <h4>📦 Distribuição dos Tempos</h4>
            <Scatter
              data={configBoxplot}
              options={{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                  legend: { display: true, position: 'top' },
                  tooltip: {
                    callbacks: {
                      label: ctx => `Tempo: ${ctx.parsed.y.toFixed(2)}s`
                    }
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Tempo de Reação (s)' }
                  },
                  x: {
                    type: 'linear',
                    min: 0.5,
                    max: 3.5,
                    title: { display: true, text: 'Nível' },
                    ticks: {
                      callback: val => {
                        const nivel = Math.round(val);
                        return NIVEIS[nivel]?.rotulo || `Nível ${nivel}`;
                      }
                    }
                  }
                }
              }}
            />
          </div>
        )}
      </div>

      {/* Gráfico de distribuição de pontuação */}
      {mostrarDistribuicao && configDistribuicao.datasets[0].data.length > 0 && (
        <div className="gm-chart-container gm-chart-full">
          <h4>🎯 Distribuição de Pontuação por Nível</h4>
          <div style={{ maxWidth: '400px', margin: '0 auto' }}>
            <Doughnut
              data={configDistribuicao}
              options={{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                  legend: { position: 'bottom' },
                  tooltip: {
                    callbacks: {
                      label: ctx => {
                        const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                        const pct = total > 0 ? (ctx.parsed / total * 100).toFixed(1) : 0;
                        return `Pontuação: ${ctx.parsed.toFixed(2)} (${pct}%)`;
                      }
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      )}

      {/* Tabela detalhada */}
      {mostrarTabela && (
        <TabelaDetalhada 
          dadosPorNivel={dadosProcessados.porNivel} 
          total={dadosProcessados.total} 
        />
      )}

      {/* Legenda */}
      <Legenda />
    </div>
  );
};

// ============================================================
// HOOK PARA CARREGAR DADOS
// ============================================================

export const useDadosMarcador = (criancaId = null) => {
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState(null);

  const carregarDados = useCallback(async () => {
    setLoading(true);
    setErro(null);
    
    try {
      const url = criancaId 
        ? `/api/dados-marcadores/?crianca_id=${criancaId}`
        : '/api/dados-marcadores/';
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setDados(data);
    } catch (error) {
      setErro(error.message);
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  }, [criancaId]);

  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  return { dados, loading, erro, recarregar: carregarDados };
};

// ============================================================
// COMPONENTE COM FILTRO DE CRIANÇA
// ============================================================

export const GraficoMarcadorComFiltro = ({ 
  criancaId, 
  onCriancaChange,
  criancas = [],
  ...props 
}) => {
  const { dados, loading, erro, recarregar } = useDadosMarcador(criancaId);

  return (
    <div>
      {criancas.length > 0 && (
        <div className="gm-filtros">
          <label htmlFor="criancaSelect">Filtrar por criança:</label>
          <select
            id="criancaSelect"
            value={criancaId || ''}
            onChange={(e) => {
              const val = e.target.value;
              if (onCriancaChange) onCriancaChange(val || null);
            }}
          >
            <option value="">Todas as crianças</option>
            {criancas.map(c => (
              <option key={c.id} value={c.id}>{c.nome}</option>
            ))}
          </select>
          <button onClick={recarregar} className="gm-btn-refresh">
            🔃 Atualizar
          </button>
        </div>
      )}
      
      <GraficoMarcador
        dados={dados}
        loading={loading}
        erro={erro}
        onRefresh={recarregar}
        {...props}
      />
    </div>
  );
};

// ============================================================
// ESTILOS (CSS-in-JS)
// ============================================================

export const estilosGraficoMarcador = `
  .grafico-marcador-wrapper {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 20px;
    background: #f8fafc;
    border-radius: 16px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .gm-header {
    text-align: center;
    margin-bottom: 24px;
  }

  .gm-header h3 {
    font-size: 1.6em;
    color: #1e293b;
    margin: 0;
  }

  .gm-subtitle {
    color: #64748b;
    margin: 4px 0 8px;
  }

  .gm-total {
    font-size: 0.95em;
    color: #475569;
  }

  .gm-total strong {
    color: #667eea;
    font-size: 1.1em;
  }

  /* Filtros */
  .gm-filtros {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    align-items: center;
    background: white;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

  .gm-filtros label {
    font-weight: 500;
    color: #475569;
  }

  .gm-filtros select {
    padding: 6px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.95em;
    background: white;
    min-width: 160px;
  }

  .gm-filtros select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .gm-btn-refresh, .gm-btn-retry {
    padding: 6px 16px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.95em;
    transition: background 0.2s;
  }

  .gm-btn-refresh:hover, .gm-btn-retry:hover {
    background: #5a67d8;
  }

  /* Cards */
  .gm-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .gm-card {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-left: 4px solid #667eea;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .gm-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }

  .gm-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }

  .gm-card-icon {
    font-size: 1.4em;
  }

  .gm-card-titulo {
    font-weight: 600;
    font-size: 1.05em;
    color: #1e293b;
  }

  .gm-card-badge {
    margin-left: auto;
    background: #f1f5f9;
    padding: 2px 12px;
    border-radius: 20px;
    font-size: 0.8em;
    color: #475569;
  }

  .gm-card-body {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px 16px;
  }

  .gm-card-stat {
    display: flex;
    flex-direction: column;
  }

  .gm-card-label {
    font-size: 0.75em;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .gm-card-valor {
    font-size: 1.1em;
    font-weight: 600;
    color: #1e293b;
  }

  .gm-card-bar {
    margin-top: 12px;
    height: 4px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
  }

  .gm-card-progress {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
    background: #667eea;
  }

  /* Gráficos */
  .gm-charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  .gm-chart-container {
    background: white;
    border-radius: 12px;
    padding: 16px 20px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

  .gm-chart-full {
    grid-column: 1 / -1;
  }

  .gm-chart-container h4 {
    margin: 0 0 12px 0;
    color: #1e293b;
    font-size: 1em;
  }

  .gm-chart-container canvas {
    width: 100% !important;
    height: auto !important;
    max-height: 300px;
  }

  /* Tabela */
  .gm-tabela-container {
    background: white;
    border-radius: 12px;
    padding: 16px 20px 20px;
    margin-top: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

  .gm-tabela-container h4 {
    margin: 0 0 12px 0;
    color: #1e293b;
  }

  .gm-tabela {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9em;
  }

  .gm-tabela thead th {
    background: #f1f5f9;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    color: #475569;
    border-bottom: 2px solid #e2e8f0;
  }

  .gm-tabela tbody td {
    padding: 10px 12px;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
  }

  .gm-tabela tbody tr:hover td {
    background: #f8fafc;
  }

  .gm-tabela-nivel {
    font-weight: 500;
  }

  .gm-tabela-total {
    background: #f1f5f9 !important;
    font-weight: 600;
  }

  .gm-tabela-total td {
    border-top: 2px solid #e2e8f0;
    padding: 10px 12px;
  }

  .gm-tabela-observacao {
    margin-top: 12px;
    padding: 12px 16px;
    background: #f0f9ff;
    border-radius: 8px;
    color: #0369a1;
    font-size: 0.9em;
  }

  /* Legendas */
  .gm-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 16px 24px;
    margin-top: 16px;
    padding: 12px 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

  .gm-legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85em;
    color: #475569;
  }

  .gm-legend-color {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }

  /* Estados */
  .gm-loading {
    text-align: center;
    padding: 40px 20px;
    color: #64748b;
  }

  .gm-spinner {
    width: 40px;
    height: 40px;
    margin: 0 auto 16px;
    border: 4px solid #e2e8f0;
    border-top-color: #667eea;
    border-radius: 50%;
    animation: gm-spin 0.8s linear infinite;
  }

  @keyframes gm-spin {
    to { transform: rotate(360deg); }
  }

  .gm-sem-dados, .gm-erro {
    text-align: center;
    padding: 40px 20px;
    background: white;
    border-radius: 12px;
    color: #64748b;
  }

  .gm-erro {
    color: #dc2626;
  }

  .gm-erro button {
    margin-top: 12px;
  }

  /* Responsivo */
  @media (max-width: 768px) {
    .gm-cards {
      grid-template-columns: 1fr;
    }

    .gm-charts-grid {
      grid-template-columns: 1fr;
    }

    .gm-card-body {
      grid-template-columns: 1fr 1fr;
    }

    .gm-tabela {
      font-size: 0.8em;
    }

    .gm-tabela thead th,
    .gm-tabela tbody td {
      padding: 6px 8px;
    }

    .gm-filtros {
      flex-direction: column;
      align-items: stretch;
    }

    .gm-filtros select {
      width: 100%;
    }
  }

  @media (max-width: 480px) {
    .grafico-marcador-wrapper {
      padding: 12px;
    }

    .gm-card {
      padding: 12px 16px;
    }

    .gm-card-body {
      grid-template-columns: 1fr;
    }
  }
`;

// ============================================================
// EXPORTAÇÃO PADRÃO
// ============================================================

export default GraficoMarcador;
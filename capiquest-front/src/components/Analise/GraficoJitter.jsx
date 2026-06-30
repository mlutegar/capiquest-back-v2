// frontend/src/components/Analise/GraficoJitter.jsx

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Label
} from 'recharts';
import { useMemo } from 'react';

const GraficoJitter = ({ dados, grupoPor = 'crianca', eixoX = 'tempo_reacao' }) => {
  
  const dadosProcessados = useMemo(() => {
    if (!dados || dados.length === 0) return [];

    const grupos = {};
    dados.forEach(item => {
      let chave;
      if (grupoPor === 'crianca') {
        chave = item.crianca_nome || item.crianca_id || 'Desconhecido';
      } else if (grupoPor === 'tipo') {
        const tipoMap = {
          'click': 'Clique', 'drag': 'Arrastar', 'type': 'Digitar',
          'select': 'Selecionar', 'submit': 'Enviar', 'next': 'Avançar',
          'back': 'Voltar', 'hint': 'Pedir Dica', 'skip': 'Pular',
        };
        chave = tipoMap[item.tipo] || item.tipo || 'Desconhecido';
      } else if (grupoPor === 'faixa_etaria') {
        chave = item.faixa_etaria || 'Não informada';
      } else {
        chave = 'Todos';
      }
      
      if (!grupos[chave]) {
        grupos[chave] = [];
      }
      grupos[chave].push({
        valor: item[eixoX] || 0,
        pontuacao: item.pontuacao || 0,
        id: item.id,
        marcador: item.marcador || null,
        original: item
      });
    });

    const resultado = [];
    Object.keys(grupos).forEach((nomeGrupo, idx) => {
      const valores = grupos[nomeGrupo];
      const xPos = idx + 1;
      
      valores.forEach(item => {
        const xJittered = xPos + (Math.random() - 0.5) * 0.4;
        const yJittered = item.valor + (Math.random() - 0.5) * 0.05;
        
        resultado.push({
          x: xJittered,
          y: yJittered,
          grupo: nomeGrupo,
          valor_original: item.valor,
          pontuacao: item.pontuacao,
          marcador: item.marcador,
          id: item.id,
          xCategoria: nomeGrupo
        });
      });
    });

    return resultado;
  }, [dados, grupoPor, eixoX]);

  const estatisticasGrupo = useMemo(() => {
    const stats = {};
    dadosProcessados.forEach(item => {
      if (!stats[item.grupo]) {
        stats[item.grupo] = { valores: [], pontuacoes: [], marcadores: {} };
      }
      stats[item.grupo].valores.push(item.valor_original);
      if (item.pontuacao) stats[item.grupo].pontuacoes.push(item.pontuacao);
      if (item.marcador) {
        stats[item.grupo].marcadores[item.marcador] = (stats[item.grupo].marcadores[item.marcador] || 0) + 1;
      }
    });
    
    Object.keys(stats).forEach(grupo => {
      const vals = stats[grupo].valores;
      stats[grupo].media = vals.reduce((a, b) => a + b, 0) / vals.length;
      stats[grupo].mediana = vals.sort((a, b) => a - b)[Math.floor(vals.length / 2)];
      stats[grupo].count = vals.length;
      stats[grupo].desvio = Math.sqrt(
        vals.reduce((a, b) => a + Math.pow(b - stats[grupo].media, 2), 0) / vals.length
      );
    });
    
    return stats;
  }, [dadosProcessados]);

  const maxValor = useMemo(() => {
    if (dadosProcessados.length === 0) return 10;
    const max = Math.max(...dadosProcessados.map(d => d.y));
    return max + 2;
  }, [dadosProcessados]);

  const cores = [
    '#8b5cf6', '#3b82f6', '#22c55e', '#f59e0b', 
    '#ef4444', '#ec4899', '#06b6d4', '#84cc16',
    '#f97316', '#8b5cf6', '#14b8a6', '#d946ef'
  ];

  const getCorGrupo = (grupo, index) => {
    const grupos = Object.keys(estatisticasGrupo);
    const idx = grupos.indexOf(grupo);
    return cores[idx % cores.length];
  };

  const scatterData = dadosProcessados.map(item => ({
    ...item,
    cor: getCorGrupo(item.grupo, 0)
  }));

  const mediaData = Object.keys(estatisticasGrupo).map((grupo, idx) => ({
    nome: grupo,
    media: estatisticasGrupo[grupo].media,
    x: idx + 1
  }));

  if (!dados || dados.length === 0) {
    return (
      <div className="flex items-center justify-center h-[400px] bg-white rounded-2xl shadow-md p-4">
        <div className="text-center text-gray-500">
          <span className="text-4xl block mb-2">📊</span>
          <p>Selecione uma opção para visualizar o Jitter Plot</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-md p-4">
      <h2 className="text-lg font-bold mb-2">
        📊 Análise em Grupo - Jitter Plot
      </h2>
      
      <div className="text-sm text-gray-500 mb-4">
        <span className="mr-4">👥 Grupos: {Object.keys(estatisticasGrupo).length}</span>
        <span>📦 Total de pontos: {dadosProcessados.length}</span>
      </div>
      
      <ResponsiveContainer width="100%" height={420}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          
          <XAxis 
            type="number" 
            dataKey="x" 
            domain={[0, Object.keys(estatisticasGrupo).length + 1]}
            tick={false}
            label={{ 
              value: grupoPor === 'crianca' ? 'Crianças' : 
                     grupoPor === 'tipo' ? 'Tipo de Ação' : 
                     grupoPor === 'faixa_etaria' ? 'Faixa Etária' : 'Grupos',
              position: 'bottom',
              offset: 10
            }}
          />
          
          <YAxis 
            domain={[0, maxValor]}
            label={{ 
              value: 'Tempo de Reação (s)', 
              angle: -90, 
              position: 'left',
              offset: 10
            }}
          />
          
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
                    <p className="font-semibold">{data.grupo}</p>
                    <p>Tempo: {data.valor_original.toFixed(2)}s</p>
                    {data.pontuacao && <p>Pontuação: {data.pontuacao.toFixed(1)}</p>}
                    {data.marcador && <p className="text-xs text-blue-600">🏷️ {data.marcador}</p>}
                    <p className="text-xs text-gray-400">ID: {data.id}</p>
                  </div>
                );
              }
              return null;
            }}
          />
          
          <Legend 
            wrapperStyle={{ paddingTop: 10 }}
            formatter={(value) => {
              const stat = estatisticasGrupo[value];
              return `${value} (n=${stat?.count || 0})`;
            }}
          />
          
          {Object.keys(estatisticasGrupo).map((grupo, idx) => {
            const dadosGrupo = scatterData.filter(d => d.grupo === grupo);
            const cor = getCorGrupo(grupo, idx);
            const stat = estatisticasGrupo[grupo];
            
            return (
              <Scatter
                key={grupo}
                name={grupo}
                data={dadosGrupo}
                fill={cor}
                stroke={cor}
                strokeWidth={1}
                shape="circle"
                legendType="circle"
              >
                {dadosGrupo.map((entry, index) => (
                  <circle
                    key={index}
                    cx={entry.x * 30}
                    cy={entry.y * 30}
                    r={6}
                    fill={cor}
                    opacity={0.7}
                  />
                ))}
              </Scatter>
            );
          })}
          
          {mediaData.map((item) => (
            <ReferenceLine
              key={item.nome}
              x={item.x - 0.5}
              y={item.media}
              stroke={getCorGrupo(item.nome, 0)}
              strokeDasharray="3 3"
              strokeWidth={2}
              label={{
                value: `μ=${item.media.toFixed(2)}s`,
                position: 'right',
                fill: getCorGrupo(item.nome, 0),
                fontSize: 10
              }}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4 text-sm">
        {Object.keys(estatisticasGrupo).map((grupo, idx) => {
          const stat = estatisticasGrupo[grupo];
          const cor = getCorGrupo(grupo, idx);
          const marcadoresMaisComuns = Object.entries(stat.marcadores || {})
            .sort((a, b) => b[1] - a[1])
            .slice(0, 2)
            .map(([nome, qtd]) => `${nome} (${qtd}x)`)
            .join(', ');
          
          return (
            <div key={grupo} className="p-2 rounded border" style={{ borderColor: cor }}>
              <div className="font-semibold" style={{ color: cor }}>
                {grupo}
              </div>
              <div className="text-gray-600 text-xs">
                <div>Média: {stat.media.toFixed(2)}s</div>
                <div>n: {stat.count}</div>
                {stat.desvio && <div>DP: {stat.desvio.toFixed(2)}s</div>}
                {marcadoresMaisComuns && (
                  <div className="text-blue-500 mt-1">🏷️ {marcadoresMaisComuns}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default GraficoJitter;
from django.shortcuts import render
from django.db.models import Avg, Count, F, Q, Max, Min
from django.utils import timezone
from datetime import timedelta
from .models import Crianca, Acao
import json
import numpy as np
from scipy.fft import fft, fftfreq
import math
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# Função helper para converter Decimal para float
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Custom JSON encoder para Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def analise(request):
    criancas = Crianca.objects.all()
    crianca_id = request.GET.get("crianca")
    
    # Dados principais
    tempo_reacao_serie = []
    pontuacao_por_tipo = []
    distribuicao = []
    dados_espectrais = []
    estatisticas_gerais = {}
    crianca = None
    
    if crianca_id:
        try:
            crianca = Crianca.objects.get(id=crianca_id)
            # Filtrar apenas registros com tempo_reacao não nulo
            resultados = Acao.objects.filter(
                crianca_id=crianca_id,
                tempo_reacao__isnull=False
            ).order_by("created_at")  # Mudado de "id" para "created_at"
            
            if resultados.exists():
                # 1. Gráfico de linha - Tempo de Reação por Tentativa
                tempo_reacao_serie = []
                for i, r in enumerate(resultados):
                    if r.tempo_reacao is not None:
                        tempo_reacao_serie.append({
                            "tentativa": i + 1,
                            "tempo_reacao": round(float(r.tempo_reacao), 3)
                        })
                
                # 2. Gráfico de barras - Pontuação por Tipo de Ação
                pontuacao_por_tipo = list(
                    resultados.values(tipo_acao=F("tipo"))
                    .annotate(
                        pontuacao_media=Avg("pontuacao"),
                        quantidade=Count("id")
                    )
                    .order_by("-pontuacao_media")
                )
                
                # Mapeamento dos tipos para português
                tipo_map = {
                    'click': 'Clique',
                    'drag': 'Arrastar', 
                    'type': 'Digitar',
                    'select': 'Selecionar',
                    'submit': 'Enviar',
                    'next': 'Avançar',
                    'back': 'Voltar',
                    'hint': 'Pedir Dica',
                    'skip': 'Pular',
                }
                
                for item in pontuacao_por_tipo:
                    if item['tipo_acao'] in tipo_map:
                        item['tipo_acao'] = tipo_map[item['tipo_acao']]
                    # Converter Decimal para float
                    if item['pontuacao_media'] is not None:
                        item['pontuacao_media'] = round(float(item['pontuacao_media']), 2)
                    else:
                        item['pontuacao_media'] = 0
                
                # 3. Distribuição por Faixa de Tempo
                total = resultados.count()
                distribuicao = [
                    {
                        "faixa": "0-2s",
                        "quantidade": resultados.filter(tempo_reacao__lt=2).count(),
                        "cor": "#22c55e",
                        "porcentagem": 0
                    },
                    {
                        "faixa": "2-4s", 
                        "quantidade": resultados.filter(tempo_reacao__gte=2, tempo_reacao__lt=4).count(),
                        "cor": "#3b82f6",
                        "porcentagem": 0
                    },
                    {
                        "faixa": "4-6s",
                        "quantidade": resultados.filter(tempo_reacao__gte=4, tempo_reacao__lt=6).count(),
                        "cor": "#f59e0b",
                        "porcentagem": 0
                    },
                    {
                        "faixa": "6+s",
                        "quantidade": resultados.filter(tempo_reacao__gte=6).count(),
                        "cor": "#ef4444",
                        "porcentagem": 0
                    },
                ]
                
                # Calcular porcentagens
                for item in distribuicao:
                    item["porcentagem"] = round((item["quantidade"] / total) * 100, 1) if total > 0 else 0
                
                # 4. Dados Espectrais (Análise de Fourier)
                tempos_reacao = list(resultados.filter(tempo_reacao__isnull=False).values_list('tempo_reacao', flat=True))
                tempos_reacao = [float(t) for t in tempos_reacao if t is not None]
                
                if len(tempos_reacao) > 3:
                    dados_espectrais = calcular_analise_espectral(tempos_reacao)
                
                # 5. Estatísticas Gerais
                tempo_medio = resultados.aggregate(Avg('tempo_reacao'))['tempo_reacao__avg']
                tempo_minimo = resultados.aggregate(Min('tempo_reacao'))['tempo_reacao__min']
                tempo_maximo = resultados.aggregate(Max('tempo_reacao'))['tempo_reacao__max']
                pontuacao_media = resultados.aggregate(Avg('pontuacao'))['pontuacao__avg']
                
                estatisticas_gerais = {
                    "total_acoes": total,
                    "tempo_medio": round(float(tempo_medio), 3) if tempo_medio is not None else 0,
                    "tempo_minimo": round(float(tempo_minimo), 3) if tempo_minimo is not None else 0,
                    "tempo_maximo": round(float(tempo_maximo), 3) if tempo_maximo is not None else 0,
                    "pontuacao_media": round(float(pontuacao_media), 2) if pontuacao_media is not None else 0,
                    "taxa_acertos": calcular_taxa_acertos(resultados),
                    "desvio_padrao": round(calcular_desvio_padrao(tempos_reacao), 3) if tempos_reacao else 0,
                    "data_inicio": resultados.first().created_at.strftime("%d/%m/%Y %H:%M") if resultados.first() else None,
                    "data_fim": resultados.last().created_at.strftime("%d/%m/%Y %H:%M") if resultados.last() else None,
                }
            else:
                # Nenhum resultado com tempo_reacao válido
                estatisticas_gerais = {
                    "total_acoes": 0,
                    "tempo_medio": 0,
                    "tempo_minimo": 0,
                    "tempo_maximo": 0,
                    "pontuacao_media": 0,
                    "taxa_acertos": 0,
                    "desvio_padrao": 0,
                    "data_inicio": None,
                    "data_fim": None,
                }
                
        except Crianca.DoesNotExist:
            logger.warning("Crianca id=%s nao encontrada", crianca_id)
            crianca = None
            estatisticas_gerais = {}
        except Exception as e:
            logger.exception("Erro ao gerar analise para crianca_id=%s: %s", crianca_id, str(e))
            crianca = None
            estatisticas_gerais = {}
    
    # Usar o encoder personalizado para Decimal
    contexto = {
        "criancas": criancas,
        "crianca_id_selecionada": crianca_id or "",
        "crianca_nome": crianca.nome if crianca else "",
        "tempo_reacao_serie_json": json.dumps(tempo_reacao_serie, cls=DecimalEncoder),
        "pontuacao_por_tipo_json": json.dumps(pontuacao_por_tipo, cls=DecimalEncoder),
        "distribuicao_json": json.dumps(distribuicao, cls=DecimalEncoder),
        "dados_espectrais_json": json.dumps(dados_espectrais, cls=DecimalEncoder),
        "estatisticas_gerais": estatisticas_gerais,
        "has_data": bool(tempo_reacao_serie),
    }
    
    return render(request, "polls/analise.html", contexto)


def calcular_analise_espectral(tempos_reacao):
    """
    Calcula a análise espectral usando FFT
    """
    try:
        # Filtrar valores None e converter para float
        tempos_limpos = [float(t) for t in tempos_reacao if t is not None]
        n = len(tempos_limpos)
        
        if n < 10:
            # Para poucos dados, retornar dados simplificados
            return [
                {"tempo": i, "intensidade": min(100, t * 10), "frequencia": 0} 
                for i, t in enumerate(tempos_limpos[:30])
            ]
        
        # Aplicar FFT
        yf = fft(tempos_limpos)
        xf = fftfreq(n, 1)[:n//2]
        
        # Calcular magnitude espectral
        magnitude = 2.0/n * np.abs(yf[:n//2])
        
        # Normalizar para escala 0-100
        if len(magnitude) > 0 and np.max(magnitude) > 0:
            magnitude = (magnitude / np.max(magnitude)) * 100
        
        # Pegar apenas as frequências mais relevantes (primeiros 30 pontos)
        dados_espectrais = []
        for i in range(min(30, len(xf))):
            if i < len(magnitude):
                dados_espectrais.append({
                    "tempo": i,
                    "intensidade": round(float(magnitude[i]), 2),
                    "frequencia": round(float(xf[i]), 4)
                })
        
        return dados_espectrais
        
    except Exception as e:
        logger.exception("Erro na análise espectral: %s", str(e))
        # Em caso de erro, retornar dados de fallback
        tempos_limpos = [float(t) for t in tempos_reacao if t is not None]
        return [
            {"tempo": i, "intensidade": min(100, t * 10), "frequencia": 0} 
            for i, t in enumerate(tempos_limpos[:30])
        ]


def calcular_taxa_acertos(resultados):
    """
    Calcula a taxa de acertos baseada na pontuação
    """
    try:
        acertos = resultados.filter(pontuacao__gt=0).count()
        total = resultados.count()
        if total > 0:
            return round((acertos / total) * 100, 1)
        return 0
    except:
        return 0


def calcular_desvio_padrao(dados):
    """
    Calcula o desvio padrão de uma lista de dados
    """
    try:
        # Filtrar valores None
        dados_limpos = [float(d) for d in dados if d is not None]
        if len(dados_limpos) < 2:
            return 0
        media = sum(dados_limpos) / len(dados_limpos)
        variancia = sum((x - media) ** 2 for x in dados_limpos) / len(dados_limpos)
        return math.sqrt(variancia)
    except:
        return 0


def api_dados_analise(request):
    """
    API endpoint para os componentes React obterem dados de análise
    """
    from django.http import JsonResponse
    
    crianca_id = request.GET.get("crianca_id")
    
    response_data = {
        "tempo_reacao_serie": [],
        "pontuacao_por_tipo": [],
        "distribuicao_tempo_resposta": [],
        "dados_espectrais": [],
        "total_acoes": 0
    }
    
    if crianca_id:
        try:
            # Filtrar apenas registros com tempo_reacao não nulo
            resultados = Acao.objects.filter(
                crianca_id=crianca_id,
                tempo_reacao__isnull=False
            ).order_by("created_at")
            
            if resultados.exists():
                # Dados da série temporal
                tempo_reacao_serie = []
                for i, r in enumerate(resultados):
                    if r.tempo_reacao is not None:
                        tempo_reacao_serie.append({
                            "tentativa": i + 1, 
                            "tempo_reacao": round(float(r.tempo_reacao), 3)
                        })
                response_data["tempo_reacao_serie"] = tempo_reacao_serie
                
                # Dados por tipo
                tipo_map = {
                    'click': 'Clique', 
                    'drag': 'Arrastar', 
                    'type': 'Digitar',
                    'select': 'Selecionar',
                    'submit': 'Enviar',
                    'next': 'Avançar',
                    'back': 'Voltar',
                    'hint': 'Pedir Dica',
                    'skip': 'Pular',
                }
                pontuacao_por_tipo = list(
                    resultados.values(tipo_acao=F("tipo"))
                    .annotate(pontuacao_media=Avg("pontuacao"))
                )
                
                for item in pontuacao_por_tipo:
                    item["pontuacao_media"] = round(float(item["pontuacao_media"]), 2) if item["pontuacao_media"] is not None else 0
                    if item["tipo_acao"] in tipo_map:
                        item["tipo_acao"] = tipo_map[item["tipo_acao"]]
                
                response_data["pontuacao_por_tipo"] = pontuacao_por_tipo
                
                # Dados de distribuição
                total = resultados.count()
                response_data["distribuicao_tempo_resposta"] = [
                    {"faixa": "0-2s", "quantidade": resultados.filter(tempo_reacao__lt=2).count()},
                    {"faixa": "2-4s", "quantidade": resultados.filter(tempo_reacao__gte=2, tempo_reacao__lt=4).count()},
                    {"faixa": "4-6s", "quantidade": resultados.filter(tempo_reacao__gte=4, tempo_reacao__lt=6).count()},
                    {"faixa": "6+s", "quantidade": resultados.filter(tempo_reacao__gte=6).count()},
                ]
                
                # Dados espectrais
                tempos = list(resultados.filter(tempo_reacao__isnull=False).values_list('tempo_reacao', flat=True))
                tempos = [float(t) for t in tempos if t is not None]
                if tempos:
                    response_data["dados_espectrais"] = calcular_analise_espectral(tempos)
                
                response_data["total_acoes"] = total
                
        except Exception as e:
            logger.exception("Erro na API de análise: %s", str(e))
            response_data["erro"] = str(e)
    
    return JsonResponse(response_data)
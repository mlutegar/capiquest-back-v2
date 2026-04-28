# polls/views_analise.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from django.db.models.functions import Round
from .models import Acao, Crianca

class ListaCriancasParaAnalise(APIView):
    """GET /api/analise/criancas/"""
    def get(self, request):
        criancas = Crianca.objects.all().values('id', 'nome')
        return Response(list(criancas))

class AnaliseDadosGerais(APIView):
    """GET /api/analise/dados-gerais/?crianca_id={id}"""
    def get(self, request):
        crianca_id = request.query_params.get('crianca_id')
        queryset = Acao.objects.all()
        
        if crianca_id:
            queryset = queryset.filter(crianca_id=crianca_id)
        
        # Gráfico 1: Série temporal
        acoes_ordenadas = queryset.order_by('created_at')
        tempo_reacao_serie = []
        for idx, acao in enumerate(acoes_ordenadas, start=1):
            if acao.tempo_reacao is not None:
                tempo_reacao_serie.append({
                    'tentativa': idx,
                    'tempo_reacao': float(acao.tempo_reacao),
                    'fase': acao.fase
                })
        
        # Gráfico 2: Pontuação média por tipo
        pontuacao_por_tipo = (
            queryset
            .values('tipo')
            .annotate(pontuacao_media=Round(Avg('pontuacao'), precision=2))
            .order_by('-pontuacao_media')
        )
        pontuacao_por_tipo = [
            {
                'tipo': item['tipo'],
                'pontuacao_media': float(item['pontuacao_media'] or 0)
            }
            for item in pontuacao_por_tipo
        ]
        
        # Gráfico 3: Distribuição de tempo de resposta
        faixas = [
            {'faixa': '0-2s', 'min': 0, 'max': 2},
            {'faixa': '2-4s', 'min': 2, 'max': 4},
            {'faixa': '4-6s', 'min': 4, 'max': 6},
            {'faixa': '6+s', 'min': 6, 'max': None},
        ]
        
        distribuicao = []
        for faixa in faixas:
            query = Q(tempo_resposta__gte=faixa['min'])
            if faixa['max']:
                query &= Q(tempo_resposta__lt=faixa['max'])
            quantidade = queryset.filter(query).count()
            distribuicao.append({
                'faixa': faixa['faixa'],
                'quantidade': quantidade
            })
        
        return Response({
            'total_acoes': queryset.count(),
            'tempo_reacao_serie': tempo_reacao_serie,
            'pontuacao_por_tipo': pontuacao_por_tipo,
            'distribuicao_tempo_resposta': distribuicao
        })
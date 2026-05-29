# polls/views_analise.py

import json

from django.shortcuts import render
from django.db.models import Avg, Q
from django.db.models.functions import Round

from .models import Acao, Crianca


def pagina_analise(request):
    crianca_id = request.GET.get('crianca_id')

    criancas = Crianca.objects.all().order_by('nome')

    tempo_reacao_serie = []
    pontuacao_por_tipo = []
    distribuicao = []

    if crianca_id:
        queryset = Acao.objects.filter(
            crianca_id=crianca_id
        )

        # -----------------------------
        # Gráfico 1 - Série temporal
        # -----------------------------
        acoes_ordenadas = queryset.order_by('created_at')

        for idx, acao in enumerate(acoes_ordenadas, start=1):
            if acao.tempo_reacao is not None:
                tempo_reacao_serie.append({
                    'tentativa': idx,
                    'tempo_reacao': float(acao.tempo_reacao),
                })

        # -----------------------------
        # Gráfico 2 - Pontuação média por tipo
        # -----------------------------
        pontuacao_por_tipo = (
            queryset
            .values('tipo')
            .annotate(
                pontuacao_media=Round(
                    Avg('pontuacao'),
                    precision=2
                )
            )
            .order_by('-pontuacao_media')
        )

        pontuacao_por_tipo = list(pontuacao_por_tipo)

        # -----------------------------
        # Gráfico 3 - Distribuição do tempo de reação
        # -----------------------------
        faixas = [
            {'faixa': '0-2s', 'min': 0, 'max': 2},
            {'faixa': '2-4s', 'min': 2, 'max': 4},
            {'faixa': '4-6s', 'min': 4, 'max': 6},
            {'faixa': '6+s', 'min': 6, 'max': None},
        ]

        for faixa in faixas:
            query = Q(
                tempo_reacao__gte=faixa['min']
            )

            if faixa['max'] is not None:
                query &= Q(
                    tempo_reacao__lt=faixa['max']
                )

            distribuicao.append({
                'faixa': faixa['faixa'],
                'quantidade': queryset.filter(query).count()
            })

    context = {
        'criancas': criancas,
        'crianca_id': crianca_id,

        'tempo_reacao_serie_json': json.dumps(tempo_reacao_serie),
        'pontuacao_por_tipo_json': json.dumps(pontuacao_por_tipo),
        'distribuicao_json': json.dumps(distribuicao),
    }

    return render(
        request,
        'polls/analise.html',
        context
    )
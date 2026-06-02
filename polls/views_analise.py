from django.shortcuts import render
from django.db.models import Avg, Count
from .models import Crianca, Resultado


def analise(request):
    criancas = Crianca.objects.all()

    crianca_id = request.GET.get("crianca_id")

    tempo_reacao_serie = []
    pontuacao_por_tipo = []
    distribuicao = []

    if crianca_id:
        resultados = Resultado.objects.filter(
            crianca_id=crianca_id
        ).order_by("id")

        tempo_reacao_serie = [
            {
                "tentativa": i + 1,
                "tempo_reacao": r.tempo_reacao
            }
            for i, r in enumerate(resultados)
        ]

        pontuacao_por_tipo = list(
            resultados.values("tipo_acao")
            .annotate(
                pontuacao_media=Avg("pontuacao")
            )
        )

        distribuicao = [
            {
                "faixa": "0–1s",
                "quantidade": resultados.filter(
                    tempo_reacao__lt=1
                ).count(),
            },
            {
                "faixa": "1–2s",
                "quantidade": resultados.filter(
                    tempo_reacao__gte=1,
                    tempo_reacao__lt=2
                ).count(),
            },
            {
                "faixa": "2s+",
                "quantidade": resultados.filter(
                    tempo_reacao__gte=2
                ).count(),
            },
        ]

    contexto = {
        "criancas": criancas,
        "tempo_reacao_serie_json": tempo_reacao_serie,
        "pontuacao_por_tipo_json": pontuacao_por_tipo,
        "distribuicao_json": distribuicao,
    }

    return render(
        request,
        "polls/analise.html",
        contexto
    )
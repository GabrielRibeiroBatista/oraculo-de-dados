from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count
from django.core.paginator import Paginator
from scraper.models import Fonte, PalavraChave, EntradaColetada
import json
from datetime import datetime, timedelta

def index(request):
    """Página inicial do dashboard público"""
    # Estatísticas gerais
    total_fontes = Fonte.objects.filter(ativo=True).count()
    total_palavras = PalavraChave.objects.filter(ativo=True).count()
    total_entradas = EntradaColetada.objects.count()
    
    # Entradas mais recentes
    entradas_recentes = EntradaColetada.objects.order_by('-data_coleta')[:5]
    
    # Fontes mais produtivas
    fontes_produtivas = Fonte.objects.annotate(
        total_entradas=Count('entradas')
    ).order_by('-total_entradas')[:5]
    
    # Palavras-chave mais mencionadas
    palavras_populares = PalavraChave.objects.annotate(
        total_entradas=Count('entradas')
    ).order_by('-total_entradas')[:5]
    
    # Dados para gráfico de tendência (últimos 7 dias)
    hoje = datetime.now().date()
    data_inicio = hoje - timedelta(days=6)
    
    # Preparar dados para o gráfico de tendência
    dados_tendencia = []
    for i in range(7):
        data = data_inicio + timedelta(days=i)
        data_seguinte = data + timedelta(days=1)
        
        contagem = EntradaColetada.objects.filter(
            data_coleta__gte=data,
            data_coleta__lt=data_seguinte
        ).count()
        
        dados_tendencia.append({
            'data': data.strftime('%d/%m'),
            'contagem': contagem
        })
    
    context = {
        'total_fontes': total_fontes,
        'total_palavras': total_palavras,
        'total_entradas': total_entradas,
        'entradas_recentes': entradas_recentes,
        'fontes_produtivas': fontes_produtivas,
        'palavras_populares': palavras_populares,
        'dados_tendencia': json.dumps(dados_tendencia),
    }
    
    return render(request, 'dashboard/index.html', context)

def dados(request):
    """Página de visualização de dados com filtros"""
    # Obter parâmetros de filtro
    fonte_id = request.GET.get('fonte')
    palavra_chave_id = request.GET.get('palavra_chave')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Iniciar queryset
    entradas = EntradaColetada.objects.all().order_by('-data_coleta')
    
    # Aplicar filtros
    if fonte_id:
        entradas = entradas.filter(fonte_id=fonte_id)
    
    if palavra_chave_id:
        entradas = entradas.filter(palavras_chave__id=palavra_chave_id)
    
    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            entradas = entradas.filter(data_coleta__gte=data_inicio)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim = data_fim + timedelta(days=1)  # Incluir o dia inteiro
            entradas = entradas.filter(data_coleta__lt=data_fim)
        except ValueError:
            pass
    
    # Paginação
    paginator = Paginator(entradas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    fontes = Fonte.objects.filter(ativo=True).order_by('nome')
    palavras_chave = PalavraChave.objects.filter(ativo=True).order_by('string')
    
    context = {
        'page_obj': page_obj,
        'fontes': fontes,
        'palavras_chave': palavras_chave,
        'fonte_selecionada': fonte_id,
        'palavra_chave_selecionada': palavra_chave_id,
        'data_inicio': data_inicio.strftime('%Y-%m-%d') if data_inicio and not isinstance(data_inicio, str) else data_inicio,
        'data_fim': data_fim.strftime('%Y-%m-%d') if data_fim and not isinstance(data_fim, str) else data_fim,
    }
    
    return render(request, 'dashboard/dados.html', context)

def dados_json(request):
    """Endpoint JSON para obter dados para gráficos dinâmicos"""
    # Obter parâmetros
    tipo = request.GET.get('tipo', 'fontes')
    fonte_id = request.GET.get('fonte')
    palavra_chave_id = request.GET.get('palavra_chave')
    periodo = request.GET.get('periodo', '7')  # Padrão: 7 dias
    
    try:
        dias = int(periodo)
    except ValueError:
        dias = 7
    
    # Calcular data de início com base no período
    data_inicio = datetime.now() - timedelta(days=dias)
    
    # Filtrar entradas pelo período
    entradas = EntradaColetada.objects.filter(data_coleta__gte=data_inicio)
    
    # Aplicar filtros adicionais
    if fonte_id:
        entradas = entradas.filter(fonte_id=fonte_id)
    
    if palavra_chave_id:
        entradas = entradas.filter(palavras_chave__id=palavra_chave_id)
    
    # Preparar dados com base no tipo solicitado
    if tipo == 'fontes':
        # Contagem por fonte
        dados = list(entradas.values('fonte__nome')
                    .annotate(total=Count('id'))
                    .order_by('-total')[:10])
        
        return JsonResponse({
            'labels': [item['fonte__nome'] for item in dados],
            'data': [item['total'] for item in dados],
        })
    
    elif tipo == 'palavras':
        # Contagem por palavra-chave
        dados = list(PalavraChave.objects.filter(entradas__in=entradas)
                    .annotate(total=Count('entradas'))
                    .order_by('-total')[:10]
                    .values('string', 'total'))
        
        return JsonResponse({
            'labels': [item['string'] for item in dados],
            'data': [item['total'] for item in dados],
        })
    
    elif tipo == 'tendencia':
        # Dados de tendência diária
        dados = []
        for i in range(dias):
            data = data_inicio + timedelta(days=i)
            data_seguinte = data + timedelta(days=1)
            
            contagem = entradas.filter(
                data_coleta__gte=data,
                data_coleta__lt=data_seguinte
            ).count()
            
            dados.append({
                'data': data.strftime('%d/%m'),
                'contagem': contagem
            })
        
        return JsonResponse({
            'labels': [item['data'] for item in dados],
            'data': [item['contagem'] for item in dados],
        })
    
    # Tipo desconhecido
    return JsonResponse({'error': 'Tipo de dados não reconhecido'}, status=400)

def detalhe_fonte(request, fonte_id):
    """Página de detalhes de uma fonte específica"""
    fonte = get_object_or_404(Fonte, id=fonte_id)
    
    # Entradas desta fonte
    entradas = EntradaColetada.objects.filter(fonte=fonte).order_by('-data_coleta')
    
    # Paginação
    paginator = Paginator(entradas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Palavras-chave mais encontradas nesta fonte
    palavras_chave = PalavraChave.objects.filter(
        entradas__fonte=fonte
    ).annotate(
        total=Count('entradas')
    ).order_by('-total')[:10]
    
    context = {
        'fonte': fonte,
        'page_obj': page_obj,
        'palavras_chave': palavras_chave,
    }
    
    return render(request, 'dashboard/detalhe_fonte.html', context)

def detalhe_palavra_chave(request, palavra_chave_id):
    """Página de detalhes de uma palavra-chave específica"""
    palavra_chave = get_object_or_404(PalavraChave, id=palavra_chave_id)
    
    # Entradas com esta palavra-chave
    entradas = EntradaColetada.objects.filter(
        palavras_chave=palavra_chave
    ).order_by('-data_coleta')
    
    # Paginação
    paginator = Paginator(entradas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Fontes mais frequentes para esta palavra-chave
    fontes = Fonte.objects.filter(
        entradas__palavras_chave=palavra_chave
    ).annotate(
        total=Count('entradas')
    ).order_by('-total')[:10]
    
    context = {
        'palavra_chave': palavra_chave,
        'page_obj': page_obj,
        'fontes': fontes,
    }
    
    return render(request, 'dashboard/detalhe_palavra_chave.html', context)

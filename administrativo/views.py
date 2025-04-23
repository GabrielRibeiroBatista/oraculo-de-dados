from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.core.paginator import Paginator
from django.core.management import call_command
from django.db.models import Count
from django.core.cache import cache
from scraper.models import Fonte, PalavraChave, EntradaColetada
from .forms import FonteForm, PalavraChaveForm
import logging
import os

# Configuração de logging
logger = logging.getLogger(__name__)

@login_required
def painel_controle(request):
    """Painel de controle principal do sistema administrativo"""
    # Estatísticas para o dashboard
    total_fontes = Fonte.objects.count()
    fontes_ativas = Fonte.objects.filter(ativo=True).count()
    
    total_palavras = PalavraChave.objects.count()
    palavras_ativas = PalavraChave.objects.filter(ativo=True).count()
    
    total_entradas = EntradaColetada.objects.count()
    entradas_recentes = EntradaColetada.objects.order_by('-data_coleta')[:5]
    
    # Contagem de entradas por fonte
    entradas_por_fonte = Fonte.objects.annotate(total_entradas=Count('entradas')).order_by('-total_entradas')[:5]
    
    # Contagem de entradas por palavra-chave
    entradas_por_palavra = PalavraChave.objects.annotate(total_entradas=Count('entradas')).order_by('-total_entradas')[:5]
    
    context = {
        'total_fontes': total_fontes,
        'fontes_ativas': fontes_ativas,
        'total_palavras': total_palavras,
        'palavras_ativas': palavras_ativas,
        'total_entradas': total_entradas,
        'entradas_recentes': entradas_recentes,
        'entradas_por_fonte': entradas_por_fonte,
        'entradas_por_palavra': entradas_por_palavra,
    }
    
    return  render(request, 'administrativo/painel_controle.html', context)

@login_required
def lista_fontes(request):
    """Lista todas as fontes cadastradas"""
    fontes = Fonte.objects.all().order_by('nome')
    
    # Paginação
    paginator = Paginator(fontes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return  render(request, 'administrativo/lista_fontes.html', {'page_obj': page_obj})

@login_required
def adicionar_fonte(request):
    """Adiciona uma nova fonte"""
    if request.method == 'POST':
        form = FonteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fonte adicionada com sucesso!')
            return redirect('administrativo:lista_fontes')
    else:
        form = FonteForm()
    
    return  render(request, 'administrativo/form_fonte.html', {'form': form, 'titulo': 'Adicionar Fonte'})

@login_required
def editar_fonte(request, fonte_id):
    """Edita uma fonte existente"""
    fonte = get_object_or_404(Fonte, id=fonte_id)
    
    if request.method == 'POST':
        form = FonteForm(request.POST, instance=fonte)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fonte atualizada com sucesso!')
            return redirect('administrativo:lista_fontes')
    else:
        form = FonteForm(instance=fonte)
    
    return  render(request, 'administrativo/form_fonte.html', {'form': form, 'titulo': 'Editar Fonte'})

@login_required
def excluir_fonte(request, fonte_id):
    """Exclui uma fonte"""
    fonte = get_object_or_404(Fonte, id=fonte_id)
    
    if request.method == 'POST':
        fonte.delete()
        messages.success(request, 'Fonte excluída com sucesso!')
        return redirect('administrativo:lista_fontes')
    
    return  render(request, 'administrativo/confirmar_exclusao.html', {'objeto': fonte, 'tipo': 'fonte'})

@login_required
def lista_palavras_chave(request):
    """Lista todas as palavras-chave cadastradas"""
    palavras_chave = PalavraChave.objects.all().order_by('string')
    
    # Paginação
    paginator = Paginator(palavras_chave, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return  render(request, 'administrativo/lista_palavras_chave.html', {'page_obj': page_obj})

@login_required
def adicionar_palavra_chave(request):
    """Adiciona uma nova palavra-chave"""
    if request.method == 'POST':
        form = PalavraChaveForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Palavra-chave adicionada com sucesso!')
            return redirect('administrativo:lista_palavras_chave')
    else:
        form = PalavraChaveForm()
    
    return  render(request, 'administrativo/form_palavra_chave.html', {'form': form, 'titulo': 'Adicionar Palavra-chave'})

@login_required
def editar_palavra_chave(request, palavra_chave_id):
    """Edita uma palavra-chave existente"""
    palavra_chave = get_object_or_404(PalavraChave, id=palavra_chave_id)
    
    if request.method == 'POST':
        form = PalavraChaveForm(request.POST, instance=palavra_chave)
        if form.is_valid():
            form.save()
            messages.success(request, 'Palavra-chave atualizada com sucesso!')
            return redirect('administrativo:lista_palavras_chave')
    else:
        form = PalavraChaveForm(instance=palavra_chave)
    
    return  render(request, 'administrativo/form_palavra_chave.html', {'form': form, 'titulo': 'Editar Palavra-chave'})

@login_required
def excluir_palavra_chave(request, palavra_chave_id):
    """Exclui uma palavra-chave"""
    palavra_chave = get_object_or_404(PalavraChave, id=palavra_chave_id)
    
    if request.method == 'POST':
        palavra_chave.delete()
        messages.success(request, 'Palavra-chave excluída com sucesso!')
        return redirect('administrativo:lista_palavras_chave')
    
    return  render(request, 'administrativo/confirmar_exclusao.html', {'objeto': palavra_chave, 'tipo': 'palavra-chave'})

@login_required
def logs_coleta(request):
    """Exibe logs de coleta e histórico de scraping"""
    # Obter entradas coletadas com paginação
    entradas = EntradaColetada.objects.all().order_by('-data_coleta')
    
    # Filtros
    fonte_id = request.GET.get('fonte')
    palavra_chave_id = request.GET.get('palavra_chave')
    
    if fonte_id:
        entradas = entradas.filter(fonte_id=fonte_id)
    
    if palavra_chave_id:
        entradas = entradas.filter(palavras_chave__id=palavra_chave_id)
    
    # Paginação
    paginator = Paginator(entradas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    fontes = Fonte.objects.all().order_by('nome')
    palavras_chave = PalavraChave.objects.all().order_by('string')
    
    context = {
        'page_obj': page_obj,
        'fontes': fontes,
        'palavras_chave': palavras_chave,
        'fonte_selecionada': fonte_id,
        'palavra_chave_selecionada': palavra_chave_id,
    }
    
    return  render(request, 'administrativo/logs_coleta.html', context)

@login_required
def executar_scraping(request):
    """Executa o scraping manualmente"""
    try:
        # Verificar se foi especificada uma fonte
        fonte_id = request.GET.get('fonte_id')
        
        if fonte_id:
            # Executar scraping para uma fonte específica
            call_command('executar_scraping', fonte_id=fonte_id)
            messages.success(request, f'Scraping iniciado para a fonte selecionada.')
        else:
            # Executar scraping para todas as fontes ativas
            call_command('executar_scraping', todas=True)
            messages.success(request, 'Scraping iniciado para todas as fontes ativas.')
        
    except Exception as e:
        logger.error(f"Erro ao executar scraping: {str(e)}")
        messages.error(request, f'Erro ao executar scraping: {str(e)}')
    
    # Redirecionar para a página anterior ou para o painel
    return redirect(request.META.get('HTTP_REFERER', 'administrativo:painel_controle'))

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = auth.authenticate(
            request,
            username = username,
            password = password
        )

        if usuario is not None:
            auth.login(request, usuario)
            return redirect('administrativo:painel_controle')
        else:
            messages.error(request, 'Credenciais inválidas. Por favor, tente novamente.')

    return render(request, 'administrativo/login.html')

def logout(request):
    auth.logout(request)
    cache.clear()
    return redirect('administrativo:login')
from django.contrib import admin
from .models import Fonte, PalavraChave, EntradaColetada

@admin.register(Fonte)
class FonteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'url', 'ativo', 'data_cadastro')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome', 'url')
    date_hierarchy = 'data_cadastro'
    list_editable = ('ativo',)

@admin.register(PalavraChave)
class PalavraChaveAdmin(admin.ModelAdmin):
    list_display = ('string', 'categoria', 'prioridade', 'ativo', 'data_cadastro')
    list_filter = ('categoria', 'prioridade', 'ativo')
    search_fields = ('string',)
    date_hierarchy = 'data_cadastro'
    list_editable = ('prioridade', 'ativo')

@admin.register(EntradaColetada)
class EntradaColetadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fonte', 'data_publicacao', 'data_coleta', 'processado')
    list_filter = ('fonte', 'processado', 'data_coleta')
    search_fields = ('titulo', 'conteudo')
    date_hierarchy = 'data_coleta'
    filter_horizontal = ('palavras_chave',)
    readonly_fields = ('data_coleta',)
    list_per_page = 20

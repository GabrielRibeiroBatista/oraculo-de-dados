from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'administrativo'

urlpatterns = [
    # URLs de autenticação
    path('login/', views.login, name='login'),
    # path('login/', auth_views.LoginView.as_view(template_name='administrativo/login.html'), name='login'),
    path('logout/', views.logout, name='logout'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='administrativo:login'), name='logout'),
    
    # URLs do painel administrativo
    path('', views.painel_controle, name='painel_controle'),
    path('fontes/', views.lista_fontes, name='lista_fontes'),
    path('fontes/adicionar/', views.adicionar_fonte, name='adicionar_fonte'),
    path('fontes/editar/<int:fonte_id>/', views.editar_fonte, name='editar_fonte'),
    path('fontes/excluir/<int:fonte_id>/', views.excluir_fonte, name='excluir_fonte'),
    
    path('palavras-chave/', views.lista_palavras_chave, name='lista_palavras_chave'),
    path('palavras-chave/adicionar/', views.adicionar_palavra_chave, name='adicionar_palavra_chave'),
    path('palavras-chave/editar/<int:palavra_chave_id>/', views.editar_palavra_chave, name='editar_palavra_chave'),
    path('palavras-chave/excluir/<int:palavra_chave_id>/', views.excluir_palavra_chave, name='excluir_palavra_chave'),
    
    path('logs/', views.logs_coleta, name='logs_coleta'),
    path('executar-scraping/', views.executar_scraping, name='executar_scraping'),
]

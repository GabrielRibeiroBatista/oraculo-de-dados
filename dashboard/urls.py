from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('dados/', views.dados, name='dados'),
    path('dados/json/', views.dados_json, name='dados_json'),
    path('fonte/<int:fonte_id>/', views.detalhe_fonte, name='detalhe_fonte'),
    path('palavra-chave/<int:palavra_chave_id>/', views.detalhe_palavra_chave, name='detalhe_palavra_chave'),
]

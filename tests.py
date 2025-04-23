import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from scraper.models import Fonte, PalavraChave, EntradaColetada
from datetime import datetime, timedelta

class ModelTestCase(TestCase):
    """Testes para os modelos do sistema"""
    
    def setUp(self):
        # Criar objetos de teste
        self.fonte = Fonte.objects.create(
            nome="Site de Teste",
            url="https://exemplo.com.br",
            tipo="noticia"
        )
        
        self.palavra_chave = PalavraChave.objects.create(
            string="teste",
            categoria="principal",
            prioridade=2
        )
        
        self.entrada = EntradaColetada.objects.create(
            fonte=self.fonte,
            titulo="Notícia de Teste",
            conteudo="Este é um conteúdo de teste para verificar o funcionamento do modelo.",
            data_publicacao=datetime.now(),
            link_relacionado="https://exemplo.com.br/noticia/1"
        )
        self.entrada.palavras_chave.add(self.palavra_chave)
    
    def test_fonte_criacao(self):
        """Teste de criação de Fonte"""
        self.assertEqual(self.fonte.nome, "Site de Teste")
        self.assertEqual(self.fonte.url, "https://exemplo.com.br")
        self.assertEqual(self.fonte.tipo, "noticia")
        self.assertTrue(self.fonte.ativo)
    
    def test_palavra_chave_criacao(self):
        """Teste de criação de PalavraChave"""
        self.assertEqual(self.palavra_chave.string, "teste")
        self.assertEqual(self.palavra_chave.categoria, "principal")
        self.assertEqual(self.palavra_chave.prioridade, 2)
        self.assertTrue(self.palavra_chave.ativo)
    
    def test_entrada_coletada_criacao(self):
        """Teste de criação de EntradaColetada"""
        self.assertEqual(self.entrada.fonte, self.fonte)
        self.assertEqual(self.entrada.titulo, "Notícia de Teste")
        self.assertIn("conteúdo de teste", self.entrada.conteudo)
        self.assertEqual(self.entrada.link_relacionado, "https://exemplo.com.br/noticia/1")
        self.assertIn(self.palavra_chave, self.entrada.palavras_chave.all())

class ViewsTestCase(TestCase):
    """Testes para as views do sistema"""
    
    def setUp(self):
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        
        # Criar cliente de teste
        self.client = Client()
        
        # Criar objetos de teste
        self.fonte = Fonte.objects.create(
            nome="Site de Teste",
            url="https://exemplo.com.br",
            tipo="noticia"
        )
        
        self.palavra_chave = PalavraChave.objects.create(
            string="teste",
            categoria="principal",
            prioridade=2
        )
        
        # Criar algumas entradas para teste
        for i in range(5):
            entrada = EntradaColetada.objects.create(
                fonte=self.fonte,
                titulo=f"Notícia de Teste {i+1}",
                conteudo=f"Este é o conteúdo da notícia de teste {i+1}.",
                data_publicacao=datetime.now() - timedelta(days=i),
                link_relacionado=f"https://exemplo.com.br/noticia/{i+1}"
            )
            entrada.palavras_chave.add(self.palavra_chave)
    
    def test_dashboard_index(self):
        """Teste da página inicial do dashboard"""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "Entradas Coletadas")
    
    def test_dashboard_dados(self):
        """Teste da página de dados do dashboard"""
        response = self.client.get(reverse('dashboard:dados'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dados.html')
        self.assertContains(response, "Visualização de Dados")
    
    def test_dashboard_detalhe_fonte(self):
        """Teste da página de detalhes de fonte"""
        response = self.client.get(reverse('dashboard:detalhe_fonte', args=[self.fonte.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/detalhe_fonte.html')
        self.assertContains(response, self.fonte.nome)
    
    def test_dashboard_detalhe_palavra_chave(self):
        """Teste da página de detalhes de palavra-chave"""
        response = self.client.get(reverse('dashboard:detalhe_palavra_chave', args=[self.palavra_chave.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/detalhe_palavra_chave.html')
        self.assertContains(response, self.palavra_chave.string)
    
    def test_admin_login_required(self):
        """Teste de redirecionamento para login em páginas administrativas"""
        response = self.client.get(reverse('administrativo:painel_controle'))
        self.assertRedirects(response, '/administrativo/login/?next=/administrativo/')
    
    def test_admin_login(self):
        """Teste de login no painel administrativo"""
        response = self.client.post(reverse('administrativo:login'), {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('administrativo:painel_controle'))
    
    def test_admin_painel_controle(self):
        """Teste do painel de controle administrativo"""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('administrativo:painel_controle'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administrativo/painel_controle.html')
        self.assertContains(response, "Painel de Controle")

class WindowsCompatibilityTests(unittest.TestCase):
    """Testes de compatibilidade com Windows"""
    
    def test_path_compatibility(self):
        """Teste de compatibilidade de caminhos"""
        # Verificar se não há caminhos absolutos do Linux
        with open('README.md', 'r') as f:
            readme_content = f.read()
            self.assertNotIn('/home/', readme_content)
            self.assertNotIn('/usr/', readme_content)
            self.assertNotIn('/var/', readme_content)
    
    def test_script_compatibility(self):
        """Teste de compatibilidade de scripts"""
        # Verificar se existem scripts para Windows
        import os
        self.assertTrue(os.path.exists('configurar_windows.bat'))
        self.assertTrue(os.path.exists('executar_scraping.bat'))
    
    def test_scheduler_compatibility(self):
        """Teste de compatibilidade do agendador"""
        # Verificar se não há referências ao cron do Linux
        import os
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        self.assertNotIn('crontab', content)
                        self.assertNotIn('cron.', content)

if __name__ == '__main__':
    unittest.main()

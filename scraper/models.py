from django.db import models

class Fonte(models.Model):
    TIPO_CHOICES = [
        ('noticia', 'Site de Notícias'),
        ('blog', 'Blog'),
        ('forum', 'Fórum'),
        ('rede_social', 'Rede Social'),
        ('outro', 'Outro'),
    ]
    
    nome = models.CharField(max_length=100)
    url = models.URLField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Fonte'
        verbose_name_plural = 'Fontes'
        ordering = ['nome']


class PalavraChave(models.Model):
    CATEGORIA_CHOICES = [
        ('principal', 'Principal'),
        ('secundaria', 'Secundária'),
        ('monitoramento', 'Monitoramento'),
        ('alerta', 'Alerta'),
    ]
    
    PRIORIDADE_CHOICES = [
        (1, 'Baixa'),
        (2, 'Média'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]
    
    string = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    prioridade = models.IntegerField(choices=PRIORIDADE_CHOICES, default=2)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.string
    
    class Meta:
        verbose_name = 'Palavra-chave'
        verbose_name_plural = 'Palavras-chave'
        ordering = ['-prioridade', 'string']


class EntradaColetada(models.Model):
    fonte = models.ForeignKey(Fonte, on_delete=models.CASCADE, related_name='entradas')
    palavras_chave = models.ManyToManyField(PalavraChave, related_name='entradas')
    titulo = models.CharField(max_length=255)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(null=True, blank=True)
    data_coleta = models.DateTimeField(auto_now_add=True)
    link_relacionado = models.URLField(max_length=255)
    processado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = 'Entrada Coletada'
        verbose_name_plural = 'Entradas Coletadas'
        ordering = ['-data_coleta']
        indexes = [
            models.Index(fields=['-data_coleta']),
            models.Index(fields=['processado']),
        ]

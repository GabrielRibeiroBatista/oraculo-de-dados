from django import forms
from scraper.models import Fonte, PalavraChave

class FonteForm(forms.ModelForm):
    class Meta:
        model = Fonte
        fields = ['nome', 'url', 'tipo', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PalavraChaveForm(forms.ModelForm):
    class Meta:
        model = PalavraChave
        fields = ['string', 'categoria', 'prioridade', 'ativo']
        widgets = {
            'string': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

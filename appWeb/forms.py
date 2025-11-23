from django import forms
from .models import Vendedor, Produto, ImagemProduto


class VendedorForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Vendedor
        fields = [
            "email", "senha", "nome_completo",
            "nome_venda", "celular", "local_principal_venda",
            "status_disponivel"
        ]


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "imagem", "preco", "descricao", "status_disponivel"]

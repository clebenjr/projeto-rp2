from django import forms
from .models import Vendedor, Produto, ImagemProduto


class VendedorForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Vendedor
        fields = [
            "email", "senha", "nome_completo",
            "nome_venda", "celular", "local_principal_venda",
            "status_disponivel",
            "foto_perfil"
        ]


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "imagem", "preco", "descricao", "status_disponivel"]



class AlterarSenhaVendedorForm(forms.Form):
    senha_atual = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={"class": "input-field"}),
    )
    senha_nova = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={"class": "input-field"}),
    )
    confirmar_senha_nova = forms.CharField(
        label="Confirmar nova senha",
        widget=forms.PasswordInput(attrs={"class": "input-field"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        senha_nova = cleaned_data.get("senha_nova")
        confirmar_senha_nova = cleaned_data.get("confirmar_senha_nova")

        if senha_nova and confirmar_senha_nova and senha_nova != confirmar_senha_nova:
            raise forms.ValidationError("A nova senha e a confirmação não conferem.")

        return cleaned_data
    

class VendedorPerfilForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = [
            "email",
            "nome_completo",
            "nome_venda",
            "celular",
            "local_principal_venda",
            "status_disponivel",
            "foto_perfil",
        ]
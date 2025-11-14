from django.db import models


class Vendedor(models.Model):
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)  # pode guardar hash depois
    nome_completo = models.CharField(max_length=150)
    nome_venda = models.CharField(max_length=100)
    celular = models.CharField(max_length=20)
    local_principal_venda = models.CharField(
        max_length=100,
        help_text="Ex.: Saída do bandejão, prainha, etc."
    )
    status_disponivel = models.BooleanField(
        default=False,
        help_text="Toggle Disponível / Indisponível do perfil"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_venda or self.nome_completo
    

class Produto(models.Model):
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name="produtos"
    )
    nome = models.CharField(max_length=100)
    imagem = models.ImageField(
        upload_to="produtos/",
        null=True,
        blank=True,
        help_text="Arquivo da figura (brigadeiro, brownie, etc.)"
    )
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    descricao = models.TextField(blank=True)
    status_disponivel = models.BooleanField(
        default=True,
        help_text="Disponível / Indisponível na tela de produto"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.vendedor.nome_venda})"

    class Meta:
        ordering = ["nome"]

from django.db import models


class Vendedor(models.Model):
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)  # pode guardar hash depois
    is_active = models.BooleanField(
        default=False,
        help_text="Conta ativa após confirmação por e-mail"
    )
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
    
    foto_perfil = models.ImageField(
        upload_to="vendedores/perfis/",
        null=True,
        blank=True
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
        help_text="Imagem principal (aparece nas listas)"
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


class ImagemProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="imagens_catalogo"
    )
    imagem = models.ImageField(upload_to="produtos/catalogo/")

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagem de {self.produto.nome} ({self.id})"


# If Cloudinary storage is available at runtime, attach it to the ImageField
# instances so uploads always use Cloudinary even if the default_storage
# instance was created earlier as a filesystem storage.
try:
    from cloudinary_storage.storage import MediaCloudinaryStorage
    _cloud_storage = MediaCloudinaryStorage()
except Exception:
    _cloud_storage = None

if _cloud_storage:
    try:
        Vendedor._meta.get_field('foto_perfil').storage = _cloud_storage
    except Exception:
        pass
    try:
        Produto._meta.get_field('imagem').storage = _cloud_storage
    except Exception:
        pass
    try:
        ImagemProduto._meta.get_field('imagem').storage = _cloud_storage
    except Exception:
        pass
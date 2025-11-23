from django.contrib import admin
from .models import Vendedor, Produto, ImagemProduto  # ajuste os nomes que você tiver

admin.site.register(Vendedor)
admin.site.register(Produto)
admin.site.register(ImagemProduto)


from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_vendedor, name="login"),
    path("logout/", views.logout_vendedor, name="logout"),
    path("cadastro/", views.cadastro_vendedor, name="cadastro"),
    path("painel/", views.painel_vendedor, name="painel_vendedor"),

    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),

    path("produtos/", views.listar_produtos, name="listar_produtos"),
    path("produtos/novo/", views.criar_produto, name="criar_produto"),
    path("produtos/<int:produto_id>/editar/", views.editar_produto, name="editar_produto"),
    path("produtos/<int:produto_id>/excluir/", views.excluir_produto, name="excluir_produto"),
]

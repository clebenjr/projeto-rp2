from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from .models import Vendedor, Produto
from .models import Vendedor, Produto, ImagemProduto
from .forms import VendedorForm, ProdutoForm

def home(request):
    return render(request, 'appWeb/index.html')


def login_vendedor(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        try:
            vendedor = Vendedor.objects.get(email=email)
        except Vendedor.DoesNotExist:
            messages.error(request, "E-mail não encontrado.")
            return redirect("login")

        if check_password(senha, vendedor.senha):
            request.session["vendedor_id"] = vendedor.id
            return redirect("painel_vendedor")

        messages.error(request, "Senha incorreta.")
        return redirect("login")

    return render(request, "appWeb/vendedor/login.html")



def logout_vendedor(request):
    request.session.flush()
    django_logout(request)
    return render(request, "appWeb/inicial.html")



def cadastro_vendedor(request):
    if request.method == "POST":
        form = VendedorForm(request.POST)

        if form.is_valid():
            vendedor = form.save(commit=False)
            vendedor.senha = make_password(form.cleaned_data["senha"])
            vendedor.save()
            messages.success(request, "Conta criada com sucesso!")
            return redirect("login")

    else:
        form = VendedorForm()

    return render(request, "appWeb/vendedor/cadastro.html", {"form": form})


def painel_vendedor(request):
    vendedor_id = request.session.get("vendedor_id")
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)

    produtos = vendedor.produtos.all()

    return render(request, "appWeb/vendedor/painel.html", {
        "vendedor": vendedor,
        "produtos": produtos
    })

def editar_perfil(request):
    vendedor_id = request.session.get("vendedor_id")
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)

    if request.method == "POST":
        form = VendedorForm(request.POST, instance=vendedor)

        if form.is_valid():
            novo = form.save(commit=False)

            # Atualizar senha se for informada
            senha_nova = request.POST.get("senha_nova")
            if senha_nova:
                novo.senha = make_password(senha_nova)

            novo.save()
            messages.success(request, "Perfil atualizado!")
            return redirect("painel_vendedor")

    else:
        form = VendedorForm(instance=vendedor)

    return render(request, "appWeb/vendedor/editar_perfil.html", {"form": form})


def listar_produtos(request):
    vendedor_id = request.session.get("vendedor_id")
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)

    produtos = vendedor.produtos.all()

    return render(request, "appWeb/produto/listar.html", {"produtos": produtos})


def criar_produto(request):
    vendedor_id = request.session.get("vendedor_id")
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)

    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES)

        if form.is_valid():
            produto = form.save(commit=False)
            produto.vendedor = vendedor
            produto.save()

            # IMAGENS DE CATÁLOGO (várias)
            imagens_catalogo = request.FILES.getlist("imagens_catalogo")
            for img in imagens_catalogo:
                ImagemProduto.objects.create(produto=produto, imagem=img)

            messages.success(request, "Produto cadastrado!")
            return redirect("listar_produtos")

    else:
        form = ProdutoForm()

    return render(request, "appWeb/produto/criar.html", {"form": form})


def editar_produto(request, produto_id):
    vendedor_id = request.session.get("vendedor_id")
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)

    produto = get_object_or_404(Produto, id=produto_id, vendedor=vendedor)

    if request.method == "POST":
        form = ProdutoForm(request.POST, request.FILES, instance=produto)

        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado!")
            return redirect("listar_produtos")

    else:
        form = ProdutoForm(instance=produto)

    return render(request, "appWeb/produto/editar.html", {"form": form, "produto": produto})


def excluir_produto(request, produto_id):
    vendedor_id = request.session.get("vendedor_id")
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)

    produto = get_object_or_404(Produto, id=produto_id, vendedor=vendedor)

    produto.delete()
    messages.success(request, "Produto removido!")
    return redirect("listar_produtos")

# ==========================
# TRILHA INICIAL
# ==========================
def pagina_inicial(request):
    """
    Tela inicial: escolher Vendedor ou Comprador.
    """
    return render(request, "appWeb/inicial.html")

# ==========================
# TRILHA DO COMPRADOR (visitante)

def home_cliente(request):
    """
    Lista de produtos para o comprador (sem login).
    Permite busca simples por nome do produto ou nome do vendedor.
    """
    busca = request.GET.get("q", "").strip()

    produtos = Produto.objects.select_related("vendedor").filter(
        status_disponivel=True,
        vendedor__status_disponivel=True,
    )

    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) |
            Q(vendedor__nome_venda__icontains=busca)
        )

    context = {
        "produtos": produtos,
        "busca": busca,
    }
    return render(request, "appWeb/cliente/home_cliente.html", context)


def info_vendedores(request):
    """
    Tela 'Login/Cadastro para vendedores' (3 pontinhos / menu).
    Apenas informativa, não mexe em nada no BD.
    """
    return render(request, "appWeb/cliente/info_vendedores.html")


def detalhe_produto_cliente(request, produto_id):
    """
    Tela de detalhes do produto para o comprador.
    Mostra imagem grande, nome, preço, vendedor e descrição.
    Botão 'Entre em contato' pode abrir um link de WhatsApp.
    """
    produto = get_object_or_404(
        Produto.objects.select_related("vendedor"),
        id=produto_id,
        status_disponivel=True,
        vendedor__status_disponivel=True,
    )

    # se quiser usar link de WhatsApp:
    whatsapp_link = ""
    if produto.vendedor.celular:
        numero = produto.vendedor.celular
        numero = "".join(filter(str.isdigit, numero))
        whatsapp_link = f"https://wa.me/55{numero}"

    context = {
        "produto": produto,
        "whatsapp_link": whatsapp_link,
    }
    return render(request, "appWeb/cliente/detalhe_produto.html", context)


def detalhe_vendedor_cliente(request, vendedor_id):
    """
    Tela de perfil do vendedor na visão do comprador.
    Mostra dados do vendedor + lista de produtos disponíveis dele.
    """
    vendedor = get_object_or_404(Vendedor, id=vendedor_id, status_disponivel=True)

    produtos = vendedor.produtos.filter(status_disponivel=True)

    whatsapp_link = ""
    if vendedor.celular:
        numero = "".join(filter(str.isdigit, vendedor.celular))
        whatsapp_link = f"https://wa.me/55{numero}"

    context = {
        "vendedor": vendedor,
        "produtos": produtos,
        "whatsapp_link": whatsapp_link,
    }
    return render(request, "appWeb/cliente/detalhe_vendedor.html", context)
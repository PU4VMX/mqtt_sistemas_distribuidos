import os
from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.database import conexao

# Definindo o caminho do arquivo HTML
HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")

router = APIRouter()

# Definindo as rotas
@router.get("/status")
async def get_status():
    """Função para retornar o status do sistema."""
    return {"status": "OK"}


@router.get("/instance")
async def get_instance():
    """Função para retornar a instância do sistema."""
    return {"instance": os.getenv("INSTANCE")}


@router.get("/umidade")
async def get_umidade():
    """Função para retornar os dados de umidade."""
    dados = conexao.get_umidade()
    dados_ordenados = sorted(dados, key=lambda x: x.data)
    return [{"data": str(d.data), "valor": d.valor} for d in dados_ordenados]


@router.get("/acionamentos")
async def get_acionamentos():
    """Função para retornar os dados de acionamentos."""
    dados = conexao.get_acionamentos()
    dados_ordenados = sorted(dados, key=lambda x: x.timestamp)
    return [
        {"timestamp": str(d.timestamp), "estado": d.estado, "gatilho": d.gatilho}
        for d in dados_ordenados
    ]

@router.get("/home")
async def get_html():
    return FileResponse(HTML_PATH)



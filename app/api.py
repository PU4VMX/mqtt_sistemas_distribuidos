import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

# Definindo o caminho do arquivo HTML
HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")

router = APIRouter()

# Definindo as rotas
@router.get("/status")
async def get_status():
    """Função para retornar o status do sistema."""
    return {"status": "OK"}


@router.get("/umidade")
async def get_umidade():
    """Função para retornar os dados de umidade."""
    return {"umidade": 'ok'}

@router.get("/")
async def get_html():
    return FileResponse(HTML_PATH)



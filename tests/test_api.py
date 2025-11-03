"""
Testes para a API de Briefings
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health_check():
    """Testa endpoint de health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "EnsinaLab" in response.json()["message"]

# TODO: Adicionar mais testes quando banco estiver configurado
# def test_create_briefing():
#     """Testa criação de briefing"""
#     briefing_data = {
#         "title": "Teste de Vídeo",
#         "description": "Descrição de teste",
#         "target_grade": "6º ano",
#         "duration_minutes": 3
#     }
#     response = client.post("/api/v1/briefings", json=briefing_data)
#     assert response.status_code == 201

#!/usr/bin/env python3
"""
Teste de sanitização de metadados no upload para R2
"""
import sys
import os
import tempfile

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.storage import VideoStorage

def test_sanitize_metadata():
    """Testa sanitização de metadados"""
    
    storage = VideoStorage()
    
    # Teste 1: Título com acentos
    metadata = {
        "title": "Passo a Passo: Implementando a Metodologia Reggio Emilia na Educação Infantil",
        "duration": "137.25",
        "video_id": "3"
    }
    
    print("=" * 60)
    print("TESTE 1: Título com acentos e caracteres especiais")
    print("=" * 60)
    
    print("\nMETADATA ORIGINAL:")
    for k, v in metadata.items():
        print(f"  {k}: {v}")
    
    sanitized = storage._sanitize_metadata(metadata)
    
    print("\nMETADATA SANITIZADA:")
    for k, v in sanitized.items():
        print(f"  {k}: {v}")
    
    # Verificar se é ASCII puro
    for key, value in sanitized.items():
        try:
            value.encode('ascii')
            print(f"  ✅ {key}: Válido (apenas ASCII)")
        except UnicodeEncodeError:
            print(f"  ❌ {key}: INVÁLIDO (contém não-ASCII)")
            return False
    
    # Teste 2: Metadata sem acentos
    metadata2 = {
        "title": "Introduction to Python Programming",
        "duration": "120.5",
        "video_id": "5"
    }
    
    print("\n" + "=" * 60)
    print("TESTE 2: Título sem acentos")
    print("=" * 60)
    
    print("\nMETADATA ORIGINAL:")
    for k, v in metadata2.items():
        print(f"  {k}: {v}")
    
    sanitized2 = storage._sanitize_metadata(metadata2)
    
    print("\nMETADATA SANITIZADA:")
    for k, v in sanitized2.items():
        print(f"  {k}: {v}")
    
    # Verificar se permanece igual
    if sanitized2 == {k: str(v) for k, v in metadata2.items()}:
        print("  ✅ Metadata sem acentos permanece inalterada")
    else:
        print("  ⚠️  Metadata foi modificada (não esperado)")
    
    # Teste 3: Caracteres especiais diversos
    metadata3 = {
        "title": "Español: ñ, ü, ¿cómo? ¡excelente!",
        "description": "Português: ç, ã, õ, á, é, í, ó, ú",
        "author": "François Müller"
    }
    
    print("\n" + "=" * 60)
    print("TESTE 3: Caracteres especiais diversos")
    print("=" * 60)
    
    print("\nMETADATA ORIGINAL:")
    for k, v in metadata3.items():
        print(f"  {k}: {v}")
    
    sanitized3 = storage._sanitize_metadata(metadata3)
    
    print("\nMETADATA SANITIZADA:")
    for k, v in sanitized3.items():
        print(f"  {k}: {v}")
    
    # Verificar ASCII
    all_valid = True
    for key, value in sanitized3.items():
        try:
            value.encode('ascii')
            print(f"  ✅ {key}: Válido")
        except UnicodeEncodeError:
            print(f"  ❌ {key}: INVÁLIDO")
            all_valid = False
    
    print("\n" + "=" * 60)
    if all_valid:
        print("✅ TODOS OS TESTES PASSARAM")
        print("=" * 60)
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_sanitize_metadata()
    sys.exit(0 if success else 1)

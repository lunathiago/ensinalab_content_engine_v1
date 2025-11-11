#!/usr/bin/env python3
"""
Script de diagnóstico: Verifica se Celery Worker está funcionando
"""
import os
import sys
import time


def check_redis_connection():
    """Verifica conexão com Redis"""
    import redis
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    try:
        client = redis.from_url(redis_url)
        client.ping()
        print(f"✅ Redis conectado: {redis_url[:40]}...")
        return True
    except Exception as e:
        print(f"❌ Redis não acessível: {e}")
        print(f"   URL: {redis_url}")
        return False


def check_celery_app():
    """Verifica se Celery app está configurado"""
    try:
        from src.workers.celery_config import celery_app
        
        print(f"✅ Celery app importado")
        print(f"   Broker: {celery_app.conf.broker_url[:40]}...")
        print(f"   Backend: {celery_app.conf.result_backend[:40]}...")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar Celery: {e}")
        return False


def check_tasks():
    """Verifica se tasks estão registradas"""
    try:
        from src.workers.celery_config import celery_app
        
        registered_tasks = list(celery_app.tasks.keys())
        
        expected_tasks = [
            'src.workers.tasks.generate_options',
            'src.workers.tasks.generate_video',
            'src.workers.tasks.resume_video_generation'
        ]
        
        print(f"\n📋 Tasks registradas: {len(registered_tasks)}")
        
        for task in expected_tasks:
            if task in registered_tasks:
                print(f"   ✅ {task}")
            else:
                print(f"   ❌ {task} NÃO ENCONTRADA!")
        
        return all(task in registered_tasks for task in expected_tasks)
        
    except Exception as e:
        print(f"❌ Erro ao verificar tasks: {e}")
        return False


def check_worker_active():
    """Verifica se há workers ativos"""
    try:
        from src.workers.celery_config import celery_app
        
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if not active_workers:
            print(f"\n⚠️  NENHUM WORKER ATIVO!")
            print(f"   Workers precisam ser iniciados com:")
            print(f"   celery -A src.workers.celery_config worker --loglevel=info")
            return False
        
        print(f"\n✅ Workers ativos: {len(active_workers)}")
        for worker_name in active_workers.keys():
            print(f"   → {worker_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar workers: {e}")
        return False


def test_task_dispatch():
    """Testa disparo de task"""
    try:
        from src.workers.tasks import generate_options
        
        print(f"\n🧪 Testando disparo de task...")
        
        # Dispatchar task de teste (briefing_id fictício)
        result = generate_options.delay(999999)
        
        print(f"   ✅ Task disparada com sucesso!")
        print(f"   Task ID: {result.id}")
        print(f"   Status inicial: {result.state}")
        
        # Aguardar um pouco
        print(f"   ⏳ Aguardando 3s...")
        time.sleep(3)
        
        print(f"   Status após 3s: {result.state}")
        
        if result.state == 'PENDING':
            print(f"   ⚠️  Task ainda PENDING - worker pode não estar processando")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar dispatch: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO: Celery Worker")
    print("="*60 + "\n")
    
    checks = {
        "Redis": check_redis_connection(),
        "Celery App": check_celery_app(),
        "Tasks": check_tasks(),
        "Workers Ativos": check_worker_active(),
        "Dispatch Test": test_task_dispatch()
    }
    
    print("\n" + "="*60)
    print("📊 RESUMO")
    print("="*60)
    
    for check, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    all_ok = all(checks.values())
    
    if not all_ok:
        print("\n" + "="*60)
        print("🔧 AÇÕES NECESSÁRIAS")
        print("="*60)
        
        if not checks["Redis"]:
            print("\n1. Verificar REDIS_URL no .env ou Render:")
            print("   Deve apontar para Redis válido")
            print("   Ex: redis://red-xxx:6379/0")
        
        if not checks["Workers Ativos"]:
            print("\n2. Iniciar Worker no Render:")
            print("   Verificar se serviço 'ensinalab-worker' está rodando")
            print("   Logs: https://dashboard.render.com → ensinalab-worker → Logs")
        
        if not checks["Tasks"]:
            print("\n3. Verificar imports em tasks.py:")
            print("   Pode haver erro de importação circular")
        
        if not checks["Dispatch Test"]:
            print("\n4. Worker pode estar com erro:")
            print("   Verificar logs para exceções")
    
    else:
        print("\n✅ TUDO OK! Worker está funcionando corretamente.")
    
    print("="*60 + "\n")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

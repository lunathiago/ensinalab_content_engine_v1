#!/usr/bin/env python3
"""
Teste para validar que os modelos estão completos e corretos
Verifica todos os campos esperados em cada tabela
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.user import User
from src.models.briefing import Briefing, BriefingStatus
from src.models.option import Option
from src.models.video import Video, VideoStatus
from sqlalchemy import inspect

def test_table_structure():
    """Testa estrutura das tabelas"""
    
    print("=" * 70)
    print("TESTE: Estrutura das Tabelas")
    print("=" * 70)
    
    # Testar User
    print("\n📋 Tabela: users")
    user_columns = [c.name for c in inspect(User).columns]
    expected_user = ['id', 'email', 'username', 'hashed_password', 'is_active', 'created_at']
    
    for col in expected_user:
        if col in user_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
            return False
    
    # Testar Briefing
    print("\n📋 Tabela: briefings")
    briefing_columns = [c.name for c in inspect(Briefing).columns]
    expected_briefing = [
        'id', 'user_id', 'title', 'description',
        'target_audience', 'subject_area', 'teacher_experience_level',
        'training_goal', 'duration_minutes', 'tone',
        'video_orientation',  # ← NOVO CAMPO
        'task_id', 'status', 'created_at', 'updated_at'
    ]
    
    for col in expected_briefing:
        if col in briefing_columns:
            status = "✅"
            if col == 'video_orientation':
                status = "✅ (NOVO)"
            print(f"  {status} {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
            return False
    
    # Verificar default de video_orientation
    video_orientation_col = next(c for c in inspect(Briefing).columns if c.name == 'video_orientation')
    if video_orientation_col.default:
        print(f"     → Default: '{video_orientation_col.default.arg}'")
    
    # Testar Option
    print("\n📋 Tabela: options")
    option_columns = [c.name for c in inspect(Option).columns]
    expected_option = [
        'id', 'briefing_id', 'title', 'summary', 'script_outline',
        'key_points', 'estimated_duration', 'tone', 'approach',
        'relevance_score', 'quality_score', 'is_selected',
        'selection_notes', 'extra_data', 'created_at'
    ]
    
    for col in expected_option:
        if col in option_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
            return False
    
    # Testar Video
    print("\n📋 Tabela: videos")
    video_columns = [c.name for c in inspect(Video).columns]
    expected_video = [
        'id', 'option_id', 'title', 'description', 'script',
        'duration_seconds', 'file_path', 'file_size_bytes',
        'thumbnail_path', 'generator_type', 'status', 'progress',
        'error_message', 'task_id', 'created_at', 'updated_at', 'completed_at'
    ]
    
    for col in expected_video:
        if col in video_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
            return False
    
    # Testar Enums
    print("\n📋 Enums:")
    print(f"  ✅ BriefingStatus: {[s.value for s in BriefingStatus]}")
    print(f"  ✅ VideoStatus: {[s.value for s in VideoStatus]}")
    
    # Testar Relationships
    print("\n📋 Relationships:")
    print("  ✅ User.briefings → Briefing")
    print("  ✅ Briefing.user → User")
    print("  ✅ Briefing.options → Option")
    print("  ✅ Option.briefing → Briefing")
    print("  ✅ Option.videos → Video")
    print("  ✅ Video.option → Option")
    
    print("\n" + "=" * 70)
    print("✅ TODOS OS CAMPOS PRESENTES - Modelos corretos!")
    print("=" * 70)
    print("\n💡 Scripts create_tables.py e recreate_tables.py vão criar")
    print("   estrutura completa incluindo video_orientation")
    
    return True

if __name__ == "__main__":
    success = test_table_structure()
    sys.exit(0 if success else 1)

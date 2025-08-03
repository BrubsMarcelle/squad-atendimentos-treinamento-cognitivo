"""
Legacy service layer - Mantido para compatibilidade.
NOVO: Use CheckinService para nova funcionalidade.
"""
from app.services.checkin_service import CheckinService


# Mantido para compatibilidade com código existente
async def process_user_checkin(user: dict):
    """
    Wrapper para manter compatibilidade com código antigo.
    DEPRECATED: Use CheckinService.process_checkin() diretamente.
    """
    return await CheckinService.process_checkin(user)


async def fix_data_inconsistencies():
    """
    Força a correção de inconsistências de dados quando chamada manualmente
    """
    from app.db.database import fix_username_inconsistencies
    
    print(f"\n🔧 CORREÇÃO MANUAL DE INCONSISTÊNCIAS:")
    
    try:
        # Corrigir inconsistências de username
        fix_result = await fix_username_inconsistencies()
        
        # Estatísticas adicionais
        from app.db.database import user_collection, checkin_collection, ranking_collection
        
        users_count = await user_collection.count_documents({})
        checkins_count = await checkin_collection.count_documents({})
        rankings_count = await ranking_collection.count_documents({})
        
        result = {
            "status": "completed",
            "fixes_applied": fix_result,
            "statistics": {
                "total_users": users_count,
                "total_checkins": checkins_count,
                "total_rankings": rankings_count
            }
        }
        
        print(f"   ✅ Correção concluída!")
        print(f"   📊 Estatísticas: {result['statistics']}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro na correção: {e}")
        raise Exception(f"Fix data inconsistencies failed: {str(e)}")


# Para compatibilidade - mantém importação do timezone
from app.utils.constants import SAO_PAULO_TZ
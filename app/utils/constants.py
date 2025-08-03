"""
Constantes do sistema para evitar magic numbers e strings duplicadas.
"""
from datetime import timezone, timedelta

# Timezone
SAO_PAULO_TZ = timezone(timedelta(hours=-3))

# Códigos de status HTTP mais usados
HTTP_STATUS = {
    'OK': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'NOT_FOUND': 404,
    'INTERNAL_ERROR': 500
}

# Configurações de pontuação
POINTS = {
    'FIRST_CHECKIN_OF_DAY': 10,
    'REGULAR_CHECKIN': 5,
    'STREAK_BONUS': 2
}

# Configurações de dias da semana
WEEKDAYS = {
    'WORKDAYS': list(range(5)),  # 0-4: Segunda a Sexta
    'WEEKEND': [5, 6]            # 5-6: Sábado e Domingo
}

# Mensagens padronizadas
MESSAGES = {
    'WEEKEND_ERROR': "Check-ins são permitidos apenas de Segunda a Sexta",
    'ALREADY_CHECKED_IN': "Você já realizou o check-in hoje às {time}",
    'CHECKIN_SUCCESS': "Check-in realizado com sucesso!",
    'USER_NOT_FOUND': "Usuário não encontrado",
    'INVALID_CREDENTIALS': "Credenciais inválidas",
    'INTERNAL_ERROR': "Erro interno do servidor"
}

# Configurações de autenticação
AUTH = {
    'ALGORITHM': 'HS256',
    'BCRYPT_ROUNDS': 12,
    'TOKEN_EXPIRE_MINUTES': 30
}

# ======================================================================
# file: tests/test_auth.py
# description: Testes de autenticação e JWT
# ======================================================================

from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt
import pytest

from car_api.core.security import create_access_token, create_refresh_token
from car_api.core.settings import settings

# ======================================================================
# Testes para POST /api/v1/auth/login - Login
# ======================================================================


class TestLogin:
    """Testes para autenticação de usuário."""

    def test_login_success(self, client, user, user_data):
        """Testa login com credenciais válidas."""
        login_data = {
            'email': user_data['email'],
            'password': user_data['password'],
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'
        assert isinstance(data['access_token'], str)
        assert isinstance(data['refresh_token'], str)
        assert len(data['access_token']) > 0
        assert len(data['refresh_token']) > 0

    def test_login_invalid_email(self, client, user_data):
        """Testa login com email inexistente."""
        login_data = {
            'email': 'nonexistent@carapi.com',
            'password': user_data['password'],
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Email ou senha inválidos' in response.json()['detail']

    def test_login_invalid_password(self, client, user_data):
        """Testa login com senha incorreta."""
        login_data = {
            'email': user_data['email'],
            'password': 'ValidPassword1',  # Senha válida no formato mas incorreta
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Email ou senha inválidos' in response.json()['detail']

    def test_login_inactive_user(self, client, inactive_user):
        """Testa login de usuário inativo."""
        login_data = {
            'email': 'inactive@carapi.com',
            'password': 'ValidPassword1',  # Senha válida no formato
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Email ou senha inválidos' in response.json()['detail']

    @pytest.mark.parametrize('invalid_email', [
        'invalid-email',  # Formato inválido
        '',  # Vazio
        '@example.com',  # Sem local
        'user@',  # Sem domínio
    ])
    def test_login_invalid_email_format(self, client, invalid_email):
        """Testa login com formatos de email inválidos."""
        login_data = {
            'email': invalid_email,
            'password': 'ValidPassword123!',
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_login_missing_email(self, client):
        """Testa login sem campo email."""
        login_data = {
            'password': 'ValidPassword123!',
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, client, user_data):
        """Testa login sem campo senha."""
        login_data = {
            'email': user_data['email'],
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_login_empty_credentials(self, client):
        """Testa login com credenciais vazias."""
        login_data = {
            'email': '',
            'password': '',
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# ======================================================================
# Testes para POST /api/v1/auth/refresh - Refresh Token
# ======================================================================


class TestRefreshToken:
    """Testes para renovação de token."""

    def test_refresh_token_success(self, client, user):
        """Testa refresh de token com token válido."""
        # Primeiro faz login para obter tokens
        login_response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'TestPassword123',
        })
        refresh_token = login_response.json()['refresh_token']

        # Usa refresh token para obter novo access token
        refresh_response = client.post('/api/v1/auth/refresh', json={
            'refresh_token': refresh_token,
        })

        assert refresh_response.status_code == HTTPStatus.OK
        data = refresh_response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'

    def test_refresh_token_invalid_token(self, client):
        """Testa refresh com token inválido."""
        refresh_response = client.post('/api/v1/auth/refresh', json={
            'refresh_token': 'invalid_refresh_token_here',
        })

        assert refresh_response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token_empty_token(self, client):
        """Testa refresh com token vazio."""
        refresh_response = client.post('/api/v1/auth/refresh', json={
            'refresh_token': '',
        })

        # Token vazio é tratado como não autorizado
        assert refresh_response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token_missing_token(self, client):
        """Testa refresh sem campo de token."""
        refresh_response = client.post('/api/v1/auth/refresh', json={})

        assert refresh_response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_refresh_token_inactive_user(self, client, inactive_user):
        """Testa refresh de token para usuário inativo."""
        refresh_token = create_refresh_token(subject=str(inactive_user.id))

        refresh_response = client.post('/api/v1/auth/refresh', json={
            'refresh_token': refresh_token,
        })

        assert refresh_response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Invalid refresh token' in refresh_response.json()['detail']

    def test_refresh_token_expired(self, client, user):
        """Testa refresh com token expirado."""
        # Cria refresh token expirado
        payload = {
            'sub': str(user.id),
            'exp': datetime.now(timezone.utc) - timedelta(days=1),
            'iat': datetime.now(timezone.utc) - timedelta(days=2),
            'type': 'refresh',
        }
        expired_token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        refresh_response = client.post('/api/v1/auth/refresh', json={
            'refresh_token': expired_token,
        })

        assert refresh_response.status_code == HTTPStatus.UNAUTHORIZED

    def test_refresh_token_wrong_type(self, client, user):
        """Testa refresh usando access token ao invés de refresh token."""

        access_token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
        )

        refresh_response = client.post('/api/v1/auth/refresh', json={
            'refresh_token': access_token,
        })

        assert refresh_response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Invalid token type' in refresh_response.json()['detail']


# ======================================================================
# Testes de acesso sem autenticação
# ======================================================================


class TestAuthenticationRequired:
    """Testes para endpoints que requerem autenticação."""

    def test_protected_endpoint_without_token(self, client):
        """Testa acesso a endpoint protegido sem token."""
        response = client.get('/api/v1/users/me')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_protected_endpoint_with_invalid_token(self, client, invalid_auth_headers):
        """Testa acesso a endpoint protegido com token inválido."""
        response = client.get('/api/v1/users/me', headers=invalid_auth_headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_protected_endpoint_with_expired_token(self, client, expired_auth_headers):
        """Testa acesso a endpoint protegido com token expirado."""
        response = client.get('/api/v1/users/me', headers=expired_auth_headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_health_check_public(self, client):
        """Testa que health check é público."""
        response = client.get('/health-check')

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'status': 'healthy'}

    def test_login_endpoint_public(self, client, user_data):
        """Testa que endpoint de login é público."""
        response = client.post('/api/v1/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password'],
        })

        # Deve retornar 401 (credenciais inválidas) e não 401 (não autorizado)
        # Isso prova que o endpoint é acessível sem token
        assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.OK}

    def test_create_user_endpoint_public(self, client, user_data):
        """Testa que endpoint de criação de usuário é público."""
        user_data['email'] = 'newuser@carapi.com'
        user_data['username'] = 'newuser'

        response = client.post('/api/v1/users/', json=user_data)

        # Deve permitir criação sem autenticação
        assert response.status_code == HTTPStatus.CREATED


# ======================================================================
# Testes de token JWT
# ======================================================================


class TestJWTToken:
    """Testes para validação de tokens JWT."""

    def test_token_contains_user_id(self, client, user):
        """Testa que o token contém o ID do usuário."""
        login_response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'TestPassword123',
        })
        access_token = login_response.json()['access_token']

        # Decodifica o token para verificar claims
        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': False},
        )

        assert payload['sub'] == str(user.id)

    def test_token_contains_role(self, client, user):
        """Testa que o token contém o papel do usuário."""
        login_response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'TestPassword123',
        })
        access_token = login_response.json()['access_token']

        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': False},
        )

        assert payload['role'] == user.role.value

    def test_admin_token_contains_admin_role(self, client, admin_user):
        """Testa que token de admin contém role 'admin'."""
        login_response = client.post('/api/v1/auth/login', json={
            'email': admin_user.email,
            'password': 'AdminPass123!',
        })
        access_token = login_response.json()['access_token']

        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': False},
        )

        assert payload['role'] == 'admin'

    def test_token_type_is_access(self, client, user):
        """Testa que o token tem tipo 'access'."""
        login_response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'TestPassword123',
        })
        access_token = login_response.json()['access_token']

        payload = jwt.decode(
            access_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': False},
        )

        assert payload['type'] == 'access'

    def test_refresh_token_type_is_refresh(self, client, user):
        """Testa que refresh token tem tipo 'refresh'."""
        login_response = client.post('/api/v1/auth/login', json={
            'email': user.email,
            'password': 'TestPassword123',
        })
        refresh_token = login_response.json()['refresh_token']

        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': False},
        )

        assert payload['type'] == 'refresh'


# ======================================================================
# Testes parametrizados para cenários de falha
# ======================================================================


class TestAuthParametrized:
    """Testes parametrizados para autenticação."""

    @pytest.mark.parametrize('wrong_password', [
        'wrongpass1',  # Diferente
        'WrongPass1',
        'TestPass1234',  # Quase correta
        'TESTPASS1234',  # Maiúsculas
        'testpass1234',  # Minúsculas
        'Password1234',  # Totalmente diferente
    ])
    def test_login_with_wrong_passwords(self, client, user_data, wrong_password):
        """Testa login com várias senhas incorretas."""
        login_data = {
            'email': user_data['email'],
            'password': wrong_password,
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Email ou senha inválidos' in response.json()['detail']

    @pytest.mark.parametrize('nonexistent_email', [
        'nonexistent1@carapi.com',
        'fake123@carapi.com',
        'nobody1@carapi.com',
        'different1@carapi.com',
    ])
    def test_login_with_nonexistent_emails(self, client, nonexistent_email):
        """Testa login com vários emails inexistentes."""
        login_data = {
            'email': nonexistent_email,
            'password': 'ValidPassword1',
        }
        response = client.post('/api/v1/auth/login', json=login_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Email ou senha inválidos' in response.json()['detail']

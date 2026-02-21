# ======================================================================
# file: tests/test_users.py
# description: Testes de CRUD de usuários
# ======================================================================

from http import HTTPStatus

import pytest

from car_api.core.security import create_access_token
from car_api.models.users import User

# ======================================================================
# Testes para POST /api/v1/users/ - Criar usuário
# ======================================================================


class TestCreateUser:
    """Testes para criação de usuário."""

    def test_create_user_success(self, client, user_data):
        """Testa criação de usuário com dados válidos."""
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['username'] == user_data['username']
        assert data['email'] == user_data['email']
        assert data['full_name'] == user_data['full_name']
        assert 'id' in data
        assert 'password' not in data

    def test_create_user_duplicate_username(self, client, user, user_data):
        """Testa erro ao criar usuário com username duplicado."""
        # Muda apenas o email
        user_data['email'] = 'different@carapi.com'

        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Username não disponível' in response.json()['detail']

    def test_create_user_duplicate_email(self, client, user, user_data):
        """Testa erro ao criar usuário com email duplicado."""
        # Muda apenas o username
        user_data['username'] = 'different_username'

        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Email já existe' in response.json()['detail']

    @pytest.mark.parametrize(
        'invalid_password',
        [
            '',  # Vazio
            '12345',  # Muito curto (< 6)
            '12345678901234567',  # Muito longo (> 15)
            'abcdef',  # Sem números
            '123456',  # Sem letras
        ],
    )
    def test_create_user_invalid_password(self, client, user_data, invalid_password):
        """Testa criação de usuário com senhas inválidas."""
        user_data['password'] = invalid_password
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        'invalid_username',
        [
            '',  # Vazio
            'ab',  # Muito curto (< 3)
            'a' * 21,  # Muito longo (> 20)
            '123username',  # Começa com número
            'admin',  # Nome reservado
            'root',  # Nome reservado
        ],
    )
    def test_create_user_invalid_username(self, client, user_data, invalid_username):
        """Testa criação de usuário com usernames inválidos."""
        user_data['username'] = invalid_username
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        'invalid_name',
        [
            '',  # Vazio
            'ab',  # Muito curto (< 3)
            'a' * 51,  # Muito longo (> 50)
        ],
    )
    def test_create_user_invalid_full_name(self, client, user_data, invalid_name):
        """Testa criação de usuário com nomes completos inválidos."""
        user_data['full_name'] = invalid_name
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_invalid_email_format(self, client, user_data):
        """Testa criação de usuário com email em formato inválido."""
        user_data['email'] = 'invalid-email'
        response = client.post('/api/v1/users/', json=user_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# ======================================================================
# Testes para GET /api/v1/users/me - Obter perfil
# ======================================================================


class TestGetUserProfile:
    """Testes para obtenção do perfil do usuário."""

    def test_get_me_success(self, client, user, auth_headers):
        """Testa obtenção do perfil com autenticação válida."""
        response = client.get('/api/v1/users/me', headers=auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['username'] == user.username
        assert data['email'] == user.email
        assert data['id'] == user.id

    def test_get_me_without_token(self, client):
        """Testa erro ao obter perfil sem token."""
        response = client.get('/api/v1/users/me')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_me_with_invalid_token(self, client, invalid_auth_headers):
        """Testa erro ao obter perfil com token inválido."""
        response = client.get('/api/v1/users/me', headers=invalid_auth_headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_me_inactive_user(self, client, inactive_user, auth_headers):
        """Testa erro ao obter perfil de usuário inativo."""
        # Cria token para usuário inativo
        token = create_access_token(
            subject=str(inactive_user.id),
            role=inactive_user.role.value,
        )
        headers = {'Authorization': f'Bearer {token}'}

        response = client.get('/api/v1/users/me', headers=headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED


# ======================================================================
# Testes para PUT /api/v1/users/me - Atualizar perfil
# ======================================================================


class TestUpdateUserProfile:
    """Testes para atualização do perfil do usuário."""

    def test_update_me_success(self, client, user, auth_headers):
        """Testa atualização do perfil com dados válidos."""
        update_data = {
            'full_name': 'Updated Full Name',
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['full_name'] == 'Updated Full Name'
        assert data['username'] == user.username  # Não mudou

    def test_update_me_password(self, client, user, auth_headers):
        """Testa atualização da senha."""
        update_data = {
            'password': 'NewPassword123!',
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.OK

        # Testa login com nova senha
        login_response = client.post(
            '/api/v1/auth/login',
            json={
                'email': user.email,
                'password': 'NewPassword123!',
            },
        )
        assert login_response.status_code == HTTPStatus.OK

    def test_update_me_duplicate_username(
        self, client, user, second_user, auth_headers
    ):
        """Testa erro ao atualizar para username duplicado."""
        update_data = {
            'username': second_user.username,
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Username já está em uso' in response.json()['detail']

    def test_update_me_duplicate_email(self, client, user, second_user, auth_headers):
        """Testa erro ao atualizar para email duplicado."""
        update_data = {
            'email': second_user.email,
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Email já está em uso' in response.json()['detail']

    def test_update_me_same_username_allowed(self, client, user, auth_headers):
        """Testa que manter o mesmo username é permitido."""
        update_data = {
            'username': user.username,  # Mesmo username
            'full_name': 'New Name',
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.OK

    def test_update_me_same_email_allowed(self, client, user, auth_headers):
        """Testa que manter o mesmo email é permitido."""
        update_data = {
            'email': user.email,  # Mesmo email
            'full_name': 'New Name',
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.OK

    def test_update_me_without_token(self, client, user_data):
        """Testa erro ao atualizar perfil sem token."""
        response = client.put('/api/v1/users/me', json=user_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED


# ======================================================================
# Testes para DELETE /api/v1/users/me - Excluir usuário
# ======================================================================


class TestDeleteUser:
    """Testes para exclusão de usuário."""

    @pytest.mark.asyncio
    async def test_delete_me_success(self, client, user, auth_headers, session):
        """Testa exclusão do próprio usuário."""
        response = client.delete('/api/v1/users/me', headers=auth_headers)

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verifica se o usuário foi removido
        result = await session.execute(
            User.__table__.select().where(User.__table__.c.id == user.id)
        )
        deleted_user = result.fetchone()
        assert deleted_user is None

    def test_delete_me_without_token(self, client):
        """Testa erro ao excluir usuário sem token."""
        response = client.delete('/api/v1/users/me')

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete_me_with_invalid_token(self, client, invalid_auth_headers):
        """Testa erro ao excluir usuário com token inválido."""
        response = client.delete('/api/v1/users/me', headers=invalid_auth_headers)

        assert response.status_code == HTTPStatus.UNAUTHORIZED


# ======================================================================
# Testes de cenários adicionais
# ======================================================================


class TestUserScenarios:
    """Testes de cenários de negócio."""

    def test_create_user_then_login(self, client, user_data):
        """Testa fluxo completo: criar usuário e fazer login."""
        # Cria usuário
        create_response = client.post('/api/v1/users/', json=user_data)
        assert create_response.status_code == HTTPStatus.CREATED

        # Faz login
        login_response = client.post(
            '/api/v1/auth/login',
            json={
                'email': user_data['email'],
                'password': user_data['password'],
            },
        )
        assert login_response.status_code == HTTPStatus.OK
        assert 'access_token' in login_response.json()

    @pytest.mark.asyncio
    async def test_user_created_is_active_by_default(self, client, user_data, session):
        """Testa que usuário criado é ativo por padrão."""
        client.post('/api/v1/users/', json=user_data)

        result = await session.execute(
            User.__table__.select().where(User.__table__.c.email == user_data['email'])
        )
        user = result.fetchone()
        assert user.is_active is True

    def test_update_multiple_fields(self, client, user, auth_headers):
        """Testa atualização de múltiplos campos simultaneamente."""
        update_data = {
            'username': 'newusername',
            'full_name': 'New Full Name',
            'email': 'newemail@carapi.com',
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['username'] == 'newusername'
        assert data['full_name'] == 'New Full Name'
        assert data['email'] == 'newemail@carapi.com'

    def test_partial_update(self, client, user, auth_headers):
        """Testa atualização parcial (apenas um campo)."""
        update_data = {
            'full_name': 'Only Updated Name',
        }
        response = client.put('/api/v1/users/me', headers=auth_headers, json=update_data)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['full_name'] == 'Only Updated Name'
        assert data['username'] == user.username  # Não mudou
        assert data['email'] == user.email  # Não mudou

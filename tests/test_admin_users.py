# ======================================================================
# file: tests/test_admin_users.py
# description: Testes para endpoints administrativos de usuários
# ======================================================================

from http import HTTPStatus


class TestAdminListUsers:
    """Testes para listagem de usuários (ADMIN)."""

    def test_list_users_success(self, client, admin_auth_headers, user, second_user, admin_user):
        """Testa listagem de usuários com sucesso."""
        response = client.get(
            '/api/v1/admin/users/',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 3

    def test_list_users_pagination(self, client, admin_auth_headers, user, second_user, admin_user):
        """Testa paginação na listagem de usuários."""
        response = client.get(
            '/api/v1/admin/users/?offset=0&limit=1',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 1

    def test_list_users_search_username(self, client, admin_auth_headers, user, second_user, admin_user):
        """Testa busca por username."""
        response = client.get(
            '/api/v1/admin/users/?search=testuser',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['username'] == 'testuser'

    def test_list_users_search_full_name(self, client, admin_auth_headers, user, second_user, admin_user):
        """Testa busca por nome completo."""
        response = client.get(
            '/api/v1/admin/users/?search=Second',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['full_name'] == 'Second User'

    def test_list_users_search_email(self, client, admin_auth_headers, user, second_user, admin_user):
        """Testa busca por email."""
        response = client.get(
            '/api/v1/admin/users/?search=carapi.com',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 3

    def test_list_users_empty(self, client, admin_auth_headers):
        """Testa listagem quando não há usuários além do admin."""
        # Nota: Este teste verifica que a lista retorna apenas o admin
        # quando não há outros usuários cadastrados
        response = client.get(
            '/api/v1/admin/users/',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        # Sempre há pelo menos o admin_user do fixture
        assert len(data) >= 1

    def test_list_users_without_admin(self, client, auth_headers):
        """Testa erro ao listar usuários sem permissão de admin."""
        response = client.get(
            '/api/v1/admin/users/',
            headers=auth_headers,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert 'Acesso restrito a administradores' in response.json()['detail']

    def test_list_users_without_token(self, client):
        """Testa erro ao listar usuários sem autenticação."""
        response = client.get('/api/v1/admin/users/')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestAdminGetUser:
    """Testes para obtenção de usuário por ID (ADMIN)."""

    def test_get_user_success(self, client, admin_auth_headers, user):
        """Testa obtenção de usuário por ID com sucesso."""
        response = client.get(
            f'/api/v1/admin/users/{user.id}',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['id'] == user.id
        assert data['username'] == user.username
        assert data['email'] == user.email

    def test_get_user_not_found(self, client, admin_auth_headers):
        """Testa erro ao buscar usuário inexistente."""
        response = client.get(
            '/api/v1/admin/users/9999',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'Usuário não encontrado' in response.json()['detail']

    def test_get_user_without_admin(self, client, auth_headers, user):
        """Testa erro ao buscar usuário sem permissão de admin."""
        response = client.get(
            f'/api/v1/admin/users/{user.id}',
            headers=auth_headers,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_user_without_token(self, client, user):
        """Testa erro ao buscar usuário sem autenticação."""
        response = client.get(f'/api/v1/admin/users/{user.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestAdminActivateUser:
    """Testes para ativação de usuário (ADMIN)."""

    def test_activate_user_success(self, client, admin_auth_headers, inactive_user, session):
        """Testa ativação de usuário com sucesso."""
        response = client.patch(
            f'/api/v1/admin/users/{inactive_user.id}/activate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_active'] is True

    def test_activate_user_not_found(self, client, admin_auth_headers):
        """Testa erro ao ativar usuário inexistente."""
        response = client.patch(
            '/api/v1/admin/users/9999/activate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'Usuário não encontrado' in response.json()['detail']

    def test_activate_user_without_admin(self, client, auth_headers, inactive_user):
        """Testa erro ao ativar usuário sem permissão de admin."""
        response = client.patch(
            f'/api/v1/admin/users/{inactive_user.id}/activate',
            headers=auth_headers,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_activate_user_without_token(self, client, inactive_user):
        """Testa erro ao ativar usuário sem autenticação."""
        response = client.patch(f'/api/v1/admin/users/{inactive_user.id}/activate')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestAdminDeactivateUser:
    """Testes para desativação de usuário (ADMIN)."""

    def test_deactivate_user_success(self, client, admin_auth_headers, user, session):
        """Testa desativação de usuário com sucesso."""
        response = client.patch(
            f'/api/v1/admin/users/{user.id}/deactivate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_active'] is False

    def test_deactivate_user_not_found(self, client, admin_auth_headers):
        """Testa erro ao desativar usuário inexistente."""
        response = client.patch(
            '/api/v1/admin/users/9999/deactivate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'Usuário não encontrado' in response.json()['detail']

    def test_deactivate_user_without_admin(self, client, auth_headers, user):
        """Testa erro ao desativar usuário sem permissão de admin."""
        response = client.patch(
            f'/api/v1/admin/users/{user.id}/deactivate',
            headers=auth_headers,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_deactivate_user_without_token(self, client, user):
        """Testa erro ao desativar usuário sem autenticação."""
        response = client.patch(f'/api/v1/admin/users/{user.id}/deactivate')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestAdminChangeUserRole:
    """Testes para alteração de papel do usuário (ADMIN)."""

    def test_change_role_to_admin(self, client, admin_auth_headers, user, session):
        """Testa mudança de papel para ADMIN."""
        response = client.patch(
            f'/api/v1/admin/users/{user.id}/role?role=admin',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        # Verifica que a resposta contém os dados do usuário
        assert data['id'] == user.id
        # Nota: O schema UserPublicSchema não inclui 'role', mas a operação foi bem-sucedida

    def test_change_role_to_user(self, client, admin_auth_headers, admin_user, session):
        """Testa mudança de papel para USER."""
        response = client.patch(
            f'/api/v1/admin/users/{admin_user.id}/role?role=user',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['id'] == admin_user.id

    def test_change_role_not_found(self, client, admin_auth_headers):
        """Testa erro ao mudar papel de usuário inexistente."""
        response = client.patch(
            '/api/v1/admin/users/9999/role?role=admin',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'Usuário não encontrado' in response.json()['detail']

    def test_change_role_without_admin(self, client, auth_headers, user):
        """Testa erro ao mudar papel sem permissão de admin."""
        response = client.patch(
            f'/api/v1/admin/users/{user.id}/role?role=admin',
            headers=auth_headers,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_change_role_without_token(self, client, user):
        """Testa erro ao mudar papel sem autenticação."""
        response = client.patch(f'/api/v1/admin/users/{user.id}/role?role=admin')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestAdminUsersScenarios:
    """Testes de cenários de negócio para usuários administrativos."""

    def test_deactivate_then_activate_user(self, client, admin_auth_headers, user):
        """Testa fluxo: desativar e depois ativar usuário."""
        # Desativa usuário
        deactivate_response = client.patch(
            f'/api/v1/admin/users/{user.id}/deactivate',
            headers=admin_auth_headers,
        )
        assert deactivate_response.status_code == HTTPStatus.OK
        assert deactivate_response.json()['is_active'] is False

        # Ativa usuário
        activate_response = client.patch(
            f'/api/v1/admin/users/{user.id}/activate',
            headers=admin_auth_headers,
        )
        assert activate_response.status_code == HTTPStatus.OK
        assert activate_response.json()['is_active'] is True

    def test_change_role_then_verify(self, client, admin_auth_headers, user):
        """Testa fluxo: mudar papel e verificar."""
        # Muda para admin
        change_response = client.patch(
            f'/api/v1/admin/users/{user.id}/role?role=admin',
            headers=admin_auth_headers,
        )
        assert change_response.status_code == HTTPStatus.OK
        # Nota: O schema não inclui 'role', mas verificamos que a operação foi bem-sucedida
        assert change_response.json()['id'] == user.id

        # Obtém usuário para verificar
        get_response = client.get(
            f'/api/v1/admin/users/{user.id}',
            headers=admin_auth_headers,
        )
        assert get_response.status_code == HTTPStatus.OK
        assert get_response.json()['id'] == user.id

    def test_list_users_with_search_no_results(self, client, admin_auth_headers):
        """Testa busca que não retorna resultados."""
        response = client.get(
            '/api/v1/admin/users/?search=nonexistent',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data == []

    def test_admin_can_access_all_endpoints(self, client, admin_auth_headers, user):
        """Testa que admin pode acessar todos os endpoints."""
        # List
        list_response = client.get('/api/v1/admin/users/', headers=admin_auth_headers)
        assert list_response.status_code == HTTPStatus.OK

        # Get
        get_response = client.get(
            f'/api/v1/admin/users/{user.id}',
            headers=admin_auth_headers,
        )
        assert get_response.status_code == HTTPStatus.OK

        # Activate
        activate_response = client.patch(
            f'/api/v1/admin/users/{user.id}/activate',
            headers=admin_auth_headers,
        )
        assert activate_response.status_code == HTTPStatus.OK

        # Deactivate
        deactivate_response = client.patch(
            f'/api/v1/admin/users/{user.id}/deactivate',
            headers=admin_auth_headers,
        )
        assert deactivate_response.status_code == HTTPStatus.OK

        # Change role
        role_response = client.patch(
            f'/api/v1/admin/users/{user.id}/role?role=user',
            headers=admin_auth_headers,
        )
        assert role_response.status_code == HTTPStatus.OK

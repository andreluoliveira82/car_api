# ======================================================================
# file: tests/test_brands.py
# description: Testes de CRUD de marcas
# ======================================================================

from http import HTTPStatus

import pytest

from car_api.models.cars import Brand

# ======================================================================
# Testes para endpoints públicos de marcas
# ======================================================================


class TestListBrands:
    """Testes para listagem de marcas (público)."""

    def test_list_brands_success(self, client, brand, second_brand):
        """Testa listagem de marcas com sucesso."""
        response = client.get('/api/v1/brands/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'brands' in data
        assert 'offset' in data
        assert 'limit' in data
        assert 'total' in data
        assert data['total'] == 2
        assert len(data['brands']) == 2

    def test_list_brands_empty(self, client):
        """Testa listagem quando não há marcas."""
        response = client.get('/api/v1/brands/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['brands'] == []
        assert data['total'] == 0

    def test_list_brands_pagination(self, client, brand, second_brand):
        """Testa paginação na listagem de marcas."""
        response = client.get('/api/v1/brands/?offset=0&limit=1')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data['brands']) == 1
        assert data['offset'] == 0
        assert data['limit'] == 1
        assert data['total'] == 2

    def test_list_brands_search(self, client, brand, second_brand):
        """Testa filtro de busca na listagem de marcas."""
        response = client.get('/api/v1/brands/?search=Toyota')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['brands'][0]['name'] == 'Toyota'

    def test_list_brands_filter_active(self, client, brand, inactive_brand):
        """Testa filtro por status ativo."""
        response = client.get('/api/v1/brands/?is_active=true')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['brands'][0]['name'] == 'Toyota'

    def test_list_brands_filter_inactive(self, client, brand, inactive_brand):
        """Testa filtro por status inativo."""
        response = client.get('/api/v1/brands/?is_active=false')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['brands'][0]['name'] == 'Inactive Brand'

    def test_list_brands_max_limit(self, client):
        """Testa que limite máximo é respeitado."""
        response = client.get('/api/v1/brands/?limit=101')

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestGetBrand:
    """Testes para obtenção de marca por ID."""

    def test_get_brand_success(self, client, brand):
        """Testa obtenção de marca por ID com sucesso."""
        response = client.get(f'/api/v1/brands/{brand.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['id'] == brand.id
        assert data['name'] == brand.name
        assert data['description'] == brand.description

    def test_get_brand_not_found(self, client):
        """Testa erro ao buscar marca inexistente."""
        response = client.get('/api/v1/brands/9999')

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'Marca não encontrada' in response.json()['detail']

    def test_get_brand_inactive(self, client, inactive_brand):
        """Testa obtenção de marca inativa (deve retornar normalmente)."""
        response = client.get(f'/api/v1/brands/{inactive_brand.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_active'] is False


# ======================================================================
# Testes para endpoints administrativos de marcas
# ======================================================================


class TestAdminCreateBrand:
    """Testes para criação de marcas (ADMIN)."""

    def test_admin_create_brand_success(self, client, admin_auth_headers, brand_data):
        """Testa criação de marca por administrador."""
        response = client.post(
            '/api/v1/admin/brands/',
            headers=admin_auth_headers,
            json=brand_data,
        )

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['name'] == brand_data['name']
        assert data['description'] == brand_data['description']
        assert data['is_active'] is True

    def test_admin_create_brand_duplicate_name(self, client, admin_auth_headers, brand, brand_data):
        """Testa erro ao criar marca com nome duplicado."""
        response = client.post(
            '/api/v1/admin/brands/',
            headers=admin_auth_headers,
            json=brand_data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Já existe uma marca cadastrada com esse nome' in response.json()['detail']

    def test_create_brand_without_admin(self, client, auth_headers, brand_data):
        """Testa erro ao criar marca sem permissão de admin."""
        response = client.post(
            '/api/v1/admin/brands/',
            headers=auth_headers,
            json=brand_data,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert 'Acesso restrito a administradores' in response.json()['detail']

    def test_create_brand_without_token(self, client, brand_data):
        """Testa erro ao criar marca sem autenticação."""
        response = client.post('/api/v1/admin/brands/', json=brand_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize('invalid_name', [
        '',  # Vazio
        'a',  # Muito curto (< 2)
        'a' * 51,  # Muito longo (> 50)
    ])
    def test_admin_create_brand_invalid_name(self, client, admin_auth_headers, invalid_name):
        """Testa criação de marca com nome inválido."""
        brand_data = {
            'name': invalid_name,
            'description': 'Descrição válida',
        }
        response = client.post(
            '/api/v1/admin/brands/',
            headers=admin_auth_headers,
            json=brand_data,
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestAdminUpdateBrand:
    """Testes para atualização de marcas (ADMIN)."""

    def test_admin_update_brand_success(self, client, admin_auth_headers, brand):
        """Testa atualização de marca por administrador."""
        update_data = {
            'name': 'Updated Toyota',
            'description': 'Descrição atualizada',
        }
        response = client.put(
            f'/api/v1/admin/brands/{brand.id}',
            headers=admin_auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['name'] == 'Updated Toyota'
        assert data['description'] == 'Descrição atualizada'

    def test_admin_update_brand_partial(self, client, admin_auth_headers, brand):
        """Testa atualização parcial de marca."""
        update_data = {
            'description': 'Only description updated',
        }
        response = client.put(
            f'/api/v1/admin/brands/{brand.id}',
            headers=admin_auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['name'] == 'Toyota'  # Não mudou
        assert data['description'] == 'Only description updated'

    def test_admin_update_brand_duplicate_name(self, client, admin_auth_headers, brand, second_brand):
        """Testa erro ao atualizar para nome duplicado."""
        update_data = {
            'name': second_brand.name,
        }
        response = client.put(
            f'/api/v1/admin/brands/{brand.id}',
            headers=admin_auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Já existe outra marca com esse nome' in response.json()['detail']

    def test_admin_update_brand_not_found(self, client, admin_auth_headers):
        """Testa erro ao atualizar marca inexistente."""
        response = client.put(
            '/api/v1/admin/brands/9999',
            headers=admin_auth_headers,
            json={'name': 'New Name'},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_brand_without_admin(self, client, auth_headers, brand):
        """Testa erro ao atualizar marca sem permissão de admin."""
        response = client.put(
            f'/api/v1/admin/brands/{brand.id}',
            headers=auth_headers,
            json={'name': 'Updated'},
        )

        assert response.status_code == HTTPStatus.FORBIDDEN


class TestAdminActivateDeactivateBrand:
    """Testes para ativar/desativar marcas (ADMIN)."""

    def test_admin_activate_brand(self, client, admin_auth_headers, inactive_brand):
        """Testa ativação de marca inativa."""
        response = client.patch(
            f'/api/v1/admin/brands/{inactive_brand.id}/activate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_active'] is True

    def test_admin_deactivate_brand(self, client, admin_auth_headers, brand):
        """Testa desativação de marca ativa."""
        response = client.patch(
            f'/api/v1/admin/brands/{brand.id}/deactivate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['is_active'] is False

    def test_admin_activate_brand_not_found(self, client, admin_auth_headers):
        """Testa erro ao ativar marca inexistente."""
        response = client.patch(
            '/api/v1/admin/brands/9999/activate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_admin_deactivate_brand_not_found(self, client, admin_auth_headers):
        """Testa erro ao desativar marca inexistente."""
        response = client.patch(
            '/api/v1/admin/brands/9999/deactivate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestAdminDeleteBrand:
    """Testes para exclusão de marcas (ADMIN)."""

    @pytest.mark.asyncio
    async def test_admin_delete_brand_success(self, client, admin_auth_headers, brand, session):
        """Testa exclusão de marca sem carros associados."""
        response = client.delete(
            f'/api/v1/admin/brands/{brand.id}',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verifica se a marca foi removida
        result = await session.execute(
            Brand.__table__.select().where(Brand.__table__.c.id == brand.id)
        )
        deleted_brand = result.fetchone()
        assert deleted_brand is None

    def test_admin_delete_brand_with_cars(self, client, admin_auth_headers, brand, car):
        """Testa erro ao excluir marca com carros associados."""
        response = client.delete(
            f'/api/v1/admin/brands/{brand.id}',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'existem carros associados' in response.json()['detail']

    def test_admin_delete_brand_not_found(self, client, admin_auth_headers):
        """Testa erro ao excluir marca inexistente."""
        response = client.delete(
            '/api/v1/admin/brands/9999',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_brand_without_admin(self, client, auth_headers, brand):
        """Testa erro ao excluir marca sem permissão de admin."""
        response = client.delete(
            f'/api/v1/admin/brands/{brand.id}',
            headers=auth_headers,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN


# ======================================================================
# Testes de cenários adicionais
# ======================================================================


class TestBrandScenarios:
    """Testes de cenários de negócio para marcas."""

    def test_create_then_get_brand(self, client, admin_auth_headers):
        """Testa fluxo: criar marca e depois obtê-la."""
        brand_data = {
            'name': 'New Brand',
            'description': 'Brand created for testing',
        }

        # Cria marca
        create_response = client.post(
            '/api/v1/admin/brands/',
            headers=admin_auth_headers,
            json=brand_data,
        )
        assert create_response.status_code == HTTPStatus.CREATED
        brand_id = create_response.json()['id']

        # Obtém marca
        get_response = client.get(f'/api/v1/brands/{brand_id}')
        assert get_response.status_code == HTTPStatus.OK
        assert get_response.json()['name'] == 'New Brand'

    def test_deactivate_then_list_filtered(self, client, admin_auth_headers, brand):
        """Testa desativar marca e listar com filtro."""
        # Desativa marca
        client.patch(
            f'/api/v1/admin/brands/{brand.id}/deactivate',
            headers=admin_auth_headers,
        )

        # Lista apenas ativas
        active_response = client.get('/api/v1/brands/?is_active=true')
        assert active_response.json()['total'] == 0

        # Lista apenas inativas
        inactive_response = client.get('/api/v1/brands/?is_active=false')
        assert inactive_response.json()['total'] == 1

    def test_update_brand_same_name_allowed(self, client, admin_auth_headers, brand):
        """Testa que atualizar para o mesmo nome é permitido."""
        update_data = {
            'name': brand.name,  # Mesmo nome
            'description': 'Updated description',
        }
        response = client.put(
            f'/api/v1/admin/brands/{brand.id}',
            headers=admin_auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.OK

# ======================================================================
# file: tests/test_cars.py
# description: Testes de CRUD de carros
# ======================================================================

from http import HTTPStatus

import pytest

from car_api.models.cars import Car

# ======================================================================
# Testes para POST /api/v1/cars/ - Criar carro
# ======================================================================


class TestCreateCar:
    """Testes para criação de carros."""

    def test_create_car_success(self, client, auth_headers, brand, user):
        """Testa criação de carro com dados válidos."""
        car_data = {
            'car_type': 'suv',
            'model': 'Corolla Cross',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'ABC1D23',
            'price': 150000.00,
            'description': 'Carro zero km, muito confortável.',
            'brand_id': brand.id,
        }
        response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['model'] == car_data['model']
        assert data['plate'] == car_data['plate']
        assert data['brand_id'] == brand.id
        assert 'id' in data
        assert 'owner_id' in data

    def test_create_car_duplicate_plate(self, client, auth_headers, car, brand, user):
        """Testa erro ao criar carro com placa duplicada."""
        car_data = {
            'car_type': 'suv',
            'model': 'Different Model',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': car.plate,  # Mesma placa do carro existente
            'price': 150000.00,
            'description': 'Outro carro',
            'brand_id': brand.id,
        }
        response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Já existe um carro cadastrado com esta placa' in response.json()['detail']

    def test_create_car_nonexistent_brand(self, client, auth_headers, user):
        """Testa erro ao criar carro com marca inexistente."""
        car_data = {
            'car_type': 'suv',
            'model': 'Corolla Cross',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'XYZ9A87',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': 9999,
        }
        response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'A marca informada não existe' in response.json()['detail']

    def test_create_car_without_token(self, client, brand):
        """Testa erro ao criar carro sem autenticação."""
        car_data = {
            'car_type': 'suv',
            'model': 'Corolla Cross',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'DEF2G34',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
        }
        response = client.post('/api/v1/cars/', json=car_data)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize('invalid_plate', [
        '',  # Vazio
        'ABC',  # Muito curto
        'INVALID',  # Formato inválido
        '1234567',  # Apenas números
    ])
    def test_create_car_invalid_plate(self, client, auth_headers, brand, invalid_plate):
        """Testa criação de carro com placa inválida."""
        car_data = {
            'car_type': 'suv',
            'model': 'Corolla Cross',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': invalid_plate,
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
        }
        response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize('invalid_price', [
        -100,  # Negativo
    ])
    def test_create_car_invalid_price(self, client, auth_headers, brand, invalid_price):
        """Testa criação de carro com preço inválido."""
        car_data = {
            'car_type': 'suv',
            'model': 'Corolla Cross',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'GHI3J45',
            'price': invalid_price,
            'description': 'Carro',
            'brand_id': brand.id,
        }
        response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize('invalid_mileage', [
        -100,  # Negativo
    ])
    def test_create_car_invalid_mileage(self, client, auth_headers, brand, invalid_mileage):
        """Testa criação de carro com quilometragem inválida."""
        car_data = {
            'car_type': 'suv',
            'model': 'Corolla Cross',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': invalid_mileage,
            'plate': 'JKL4M56',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
        }
        response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_car_model_year_before_factory_year(self, client, auth_headers, brand):
        """Testa erro quando ano do modelo é anterior ao de fabricação."""
        car_data = {
            'car_type': 'suv',
            'model': 'Corolla Cross',
            'factory_year': 2024,
            'model_year': 2023,  # Anterior ao factory_year
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'MNO5P67',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
        }
        response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# ======================================================================
# Testes para GET /api/v1/cars/ - Listar carros
# ======================================================================


class TestListCars:
    """Testes para listagem de carros."""

    def test_list_cars_success(self, client, car, second_car):
        """Testa listagem de carros com sucesso."""
        response = client.get('/api/v1/cars/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'cars' in data
        assert 'offset' in data
        assert 'limit' in data
        assert 'total' in data
        assert data['total'] == 2
        assert len(data['cars']) == 2

    def test_list_cars_empty(self, client):
        """Testa listagem quando não há carros."""
        response = client.get('/api/v1/cars/')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['cars'] == []
        assert data['total'] == 0

    def test_list_cars_pagination(self, client, car, second_car):
        """Testa paginação na listagem de carros."""
        response = client.get('/api/v1/cars/?offset=0&limit=1')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data['cars']) == 1
        assert data['offset'] == 0
        assert data['limit'] == 1
        assert data['total'] == 2

    def test_list_cars_filter_by_search(self, client, car, second_car):
        """Testa filtro por busca (modelo, cor ou placa)."""
        response = client.get('/api/v1/cars/?search=Corolla')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['cars'][0]['model'] == 'Corolla Cross'

    def test_list_cars_filter_by_type(self, client, car, second_car):
        """Testa filtro por tipo de carro."""
        response = client.get('/api/v1/cars/?car_type=suv')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['cars'][0]['model'] == 'Corolla Cross'

    def test_list_cars_filter_by_color(self, client, car, second_car):
        """Testa filtro por cor."""
        response = client.get('/api/v1/cars/?color=white')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['cars'][0]['color'] == 'white'

    def test_list_cars_filter_by_fuel_type(self, client, car, second_car):
        """Testa filtro por tipo de combustível."""
        response = client.get('/api/v1/cars/?fuel_type=gasoline')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['cars'][0]['fuel_type'] == 'gasoline'

    def test_list_cars_filter_by_status(self, client, car, second_car):
        """Testa filtro por status."""
        response = client.get('/api/v1/cars/?status=available')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 2

    def test_list_cars_filter_by_brand_id(self, client, car, second_car, brand):
        """Testa filtro por ID da marca."""
        response = client.get(f'/api/v1/cars/?brand_id={brand.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 2

    def test_list_cars_filter_by_owner_id(self, client, car, second_car, user):
        """Testa filtro por ID do proprietário."""
        response = client.get(f'/api/v1/cars/?owner_id={user.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 1
        assert data['cars'][0]['owner_id'] == user.id

    def test_list_cars_filter_by_year_range(self, client, car, second_car):
        """Testa filtro por faixa de ano."""
        response = client.get('/api/v1/cars/?min_year=2024&max_year=2025')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        # Ambos os carros devem estar na faixa
        assert data['total'] >= 1

    def test_list_cars_filter_by_price_range(self, client, car, second_car):
        """Testa filtro por faixa de preço."""
        # Ajusta faixa para incluir ambos os carros
        response = client.get('/api/v1/cars/?min_price=100000&max_price=200000')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        # Ambos os carros estão nesta faixa (120000 e 150000)
        assert data['total'] == 2


# ======================================================================
# Testes para GET /api/v1/cars/{car_id} - Obter carro por ID
# ======================================================================


class TestGetCar:
    """Testes para obtenção de carro por ID."""

    def test_get_car_success(self, client, car):
        """Testa obtenção de carro por ID com sucesso."""
        response = client.get(f'/api/v1/cars/{car.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['id'] == car.id
        assert data['model'] == car.model
        assert 'brand' in data
        assert 'owner' in data

    def test_get_car_not_found(self, client):
        """Testa erro ao buscar carro inexistente."""
        response = client.get('/api/v1/cars/9999')

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert 'não encontrado' in response.json()['detail']

    def test_get_car_public_access(self, client, car):
        """Testa que qualquer um pode ver detalhes de um carro."""
        # Não requer autenticação
        response = client.get(f'/api/v1/cars/{car.id}')

        assert response.status_code == HTTPStatus.OK


# ======================================================================
# Testes para PUT /api/v1/cars/{car_id} - Atualizar carro
# ======================================================================


class TestUpdateCar:
    """Testes para atualização de carros."""

    def test_update_car_owner_success(self, client, auth_headers, car):
        """Testa atualização de carro pelo proprietário."""
        update_data = {
            'model': 'Updated Model',
            'price': 160000.00,
        }
        response = client.put(
            f'/api/v1/cars/{car.id}',
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['model'] == 'Updated Model'
        assert float(data['price']) == 160000.00

    def test_update_car_not_owner_forbidden(self, client, auth_headers, second_car):
        """Testa erro ao atualizar carro de outro usuário."""
        update_data = {
            'model': 'Trying to update',
        }
        response = client.put(
            f'/api/v1/cars/{second_car.id}',
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert 'Not enough permissions' in response.json()['detail']

    def test_update_car_duplicate_plate(self, client, auth_headers, car, second_car):
        """Testa erro ao atualizar para placa duplicada."""
        update_data = {
            'plate': second_car.plate,
        }
        response = client.put(
            f'/api/v1/cars/{car.id}',
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'Já existe um carro cadastrado com esta placa' in response.json()['detail']

    def test_update_car_not_found(self, client, auth_headers):
        """Testa erro ao atualizar carro inexistente."""
        response = client.put(
            '/api/v1/cars/9999',
            headers=auth_headers,
            json={'model': 'Updated'},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_car_without_token(self, client, car):
        """Testa erro ao atualizar carro sem autenticação."""
        response = client.put(
            f'/api/v1/cars/{car.id}',
            json={'model': 'Updated'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_update_car_same_plate_allowed(self, client, auth_headers, car):
        """Testa que manter a mesma placa é permitido."""
        update_data = {
            'model': 'Updated Model',
            'plate': car.plate,  # Mesma placa
        }
        response = client.put(
            f'/api/v1/cars/{car.id}',
            headers=auth_headers,
            json=update_data,
        )

        assert response.status_code == HTTPStatus.OK


# ======================================================================
# Testes para DELETE /api/v1/cars/{car_id} - Excluir carro
# ======================================================================


class TestDeleteCar:
    """Testes para exclusão de carros."""

    @pytest.mark.asyncio
    async def test_delete_car_owner_success(self, client, auth_headers, car, session):
        """Testa exclusão de carro pelo proprietário."""
        response = client.delete(f'/api/v1/cars/{car.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.NO_CONTENT

        # Verifica se o carro foi removido
        result = await session.execute(
            Car.__table__.select().where(Car.__table__.c.id == car.id)
        )
        deleted_car = result.fetchone()
        assert deleted_car is None

    def test_delete_car_not_owner_forbidden(self, client, auth_headers, second_car):
        """Testa erro ao excluir carro de outro usuário."""
        response = client.delete(f'/api/v1/cars/{second_car.id}', headers=auth_headers)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert 'Not enough permissions' in response.json()['detail']

    def test_delete_car_not_found(self, client, auth_headers):
        """Testa erro ao excluir carro inexistente."""
        response = client.delete('/api/v1/cars/9999', headers=auth_headers)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_car_without_token(self, client, car):
        """Testa erro ao excluir carro sem autenticação."""
        response = client.delete(f'/api/v1/cars/{car.id}')

        assert response.status_code == HTTPStatus.UNAUTHORIZED


# ======================================================================
# Testes para endpoints administrativos de carros
# ======================================================================


class TestAdminCars:
    """Testes para endpoints administrativos de carros."""

    def test_admin_create_car_for_user(self, client, admin_auth_headers, second_user, brand):
        """Testa admin criando carro para outro usuário."""
        car_data = {
            'car_type': 'suv',
            'model': 'Admin Created Car',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'ADM1N23',
            'price': 150000.00,
            'description': 'Carro criado por admin',
            'brand_id': brand.id,
            'owner_id': second_user.id,
        }
        response = client.post(
            '/api/v1/admin/cars/',
            headers=admin_auth_headers,
            json=car_data,
        )

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data['owner_id'] == second_user.id

    def test_admin_create_car_nonexistent_owner(self, client, admin_auth_headers, brand):
        """Testa erro ao criar carro para proprietário inexistente."""
        car_data = {
            'car_type': 'suv',
            'model': 'Admin Created Car',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'ADM2N34',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
            'owner_id': 9999,
        }
        response = client.post(
            '/api/v1/admin/cars/',
            headers=admin_auth_headers,
            json=car_data,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert 'usuário proprietário informado não existe' in response.json()['detail']

    def test_admin_list_all_cars(self, client, admin_auth_headers, car, second_car):
        """Testa listagem administrativa de todos os carros."""
        response = client.get('/api/v1/admin/cars/', headers=admin_auth_headers)

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] == 2

    def test_admin_change_car_status(self, client, admin_auth_headers, car):
        """Testa admin alterando status de carro."""
        response = client.patch(
            f'/api/v1/admin/cars/{car.id}/status?status=sold',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['status'] == 'sold'

    def test_admin_deactivate_car(self, client, admin_auth_headers, car):
        """Testa admin desativando carro."""
        response = client.patch(
            f'/api/v1/admin/cars/{car.id}/deactivate',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.OK

    def test_admin_delete_car(self, client, admin_auth_headers, car, session):
        """Testa admin excluindo carro."""
        response = client.delete(
            f'/api/v1/admin/cars/{car.id}',
            headers=admin_auth_headers,
        )

        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_admin_car_operations_without_admin(self, client, auth_headers, brand):
        """Testa erro ao operar carros sem permissão de admin."""
        car_data = {
            'car_type': 'suv',
            'model': 'Test Car',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'USR1A23',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
            'owner_id': 1,
        }
        # Criar carro admin
        response = client.post(
            '/api/v1/admin/cars/',
            headers=auth_headers,
            json=car_data,
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_admin_car_operations_without_token(self, client, brand):
        """Testa erro ao operar carros sem autenticação."""
        car_data = {
            'car_type': 'suv',
            'model': 'Test Car',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'USR2B34',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
            'owner_id': 1,
        }
        response = client.post('/api/v1/admin/cars/', json=car_data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED


# ======================================================================
# Testes de cenários adicionais
# ======================================================================


class TestCarScenarios:
    """Testes de cenários de negócio para carros."""

    def test_create_then_get_car(self, client, auth_headers, brand):
        """Testa fluxo: criar carro e depois obtê-lo."""
        car_data = {
            'car_type': 'suv',
            'model': 'Flow Test Car',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'FLW1A23',
            'price': 150000.00,
            'description': 'Carro de teste de fluxo',
            'brand_id': brand.id,
        }
        # Cria carro
        create_response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)
        assert create_response.status_code == HTTPStatus.CREATED
        car_id = create_response.json()['id']

        # Obtém carro
        get_response = client.get(f'/api/v1/cars/{car_id}')
        assert get_response.status_code == HTTPStatus.OK
        assert get_response.json()['id'] == car_id

    def test_create_then_update_car(self, client, auth_headers, brand):
        """Testa fluxo: criar e depois atualizar carro."""
        car_data = {
            'car_type': 'suv',
            'model': 'Update Flow Car',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'UPD1B34',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
        }
        # Cria carro
        create_response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)
        car_id = create_response.json()['id']

        # Atualiza carro
        update_response = client.put(
            f'/api/v1/cars/{car_id}',
            headers=auth_headers,
            json={'price': 160000.00},
        )
        assert update_response.status_code == HTTPStatus.OK
        assert float(update_response.json()['price']) == 160000.00

    def test_create_then_delete_car(self, client, auth_headers, brand):
        """Testa fluxo: criar e depois excluir carro."""
        car_data = {
            'car_type': 'suv',
            'model': 'Delete Flow Car',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'DEL1C45',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
        }
        # Cria carro
        create_response = client.post('/api/v1/cars/', headers=auth_headers, json=car_data)
        car_id = create_response.json()['id']

        # Exclui carro
        delete_response = client.delete(f'/api/v1/cars/{car_id}', headers=auth_headers)
        assert delete_response.status_code == HTTPStatus.NO_CONTENT

    def test_list_cars_with_multiple_filters(self, client, car, second_car):
        """Testa listagem com múltiplos filtros."""
        response = client.get('/api/v1/cars/?car_type=suv&color=white&status=available')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data['total'] >= 1

    def test_car_with_brand_and_owner_relationships(self, client, car):
        """Testa que carro retorna relações de marca e proprietário."""
        response = client.get(f'/api/v1/cars/{car.id}')

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert 'brand' in data
        assert 'owner' in data
        assert data['brand']['name'] == 'Toyota'
        assert 'username' in data['owner']

    def test_admin_create_then_user_can_update(self, client, admin_auth_headers, auth_headers, user, brand):
        """Testa fluxo: admin cria, usuário atualiza seu carro."""
        car_data = {
            'car_type': 'suv',
            'model': 'Admin Create Flow',
            'factory_year': 2024,
            'model_year': 2025,
            'color': 'white',
            'fuel_type': 'flex',
            'transmission': 'automatic',
            'condition': 'new',
            'status': 'available',
            'mileage': 0,
            'plate': 'ADM3C56',
            'price': 150000.00,
            'description': 'Carro',
            'brand_id': brand.id,
            'owner_id': user.id,
        }
        # Admin cria carro para usuário
        create_response = client.post(
            '/api/v1/admin/cars/',
            headers=admin_auth_headers,
            json=car_data,
        )
        car_id = create_response.json()['id']

        # Usuário atualiza seu carro
        update_response = client.put(
            f'/api/v1/cars/{car_id}',
            headers=auth_headers,
            json={'model': 'User Updated Model'},
        )
        assert update_response.status_code == HTTPStatus.OK
        assert update_response.json()['model'] == 'User Updated Model'

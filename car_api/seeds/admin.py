# ==============================================================================
# File: car_api/seeds/admin.py
# Description: ... operations in the Car API.
# ==============================================================================


from sqlalchemy import select

from car_api.core.database import AsyncSessionLocal
from car_api.core.security import get_password_hash
from car_api.models.users import User, UserRole


async def create_initial_admin():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.role == UserRole.ADMIN))
        admin_exists = result.scalar_one_or_none()

        if admin_exists:
            print('Admin já existe.')
            return

        admin = User(
            username='admin',
            full_name='Administrador',
            email='admin@carapi.com',
            password=get_password_hash('Admin123!'),
            role=UserRole.ADMIN,
            is_active=True,
        )

        session.add(admin)
        await session.commit()

        print('Admin criado com sucesso.')

"""
Modelos ORM para autenticación y autorización.
Schema: app (separado del schema gold de datos).
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from flask_login import UserMixin

Base = declarative_base()


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))

    users = relationship('User', back_populates='role')


class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    role = relationship('Role', back_populates='users')
    sucursales = relationship('UserSucursal', back_populates='user', cascade='all, delete-orphan')

    @property
    def is_admin(self):
        return self.role.name == 'admin'

    @property
    def is_gerente(self):
        return self.role.name == 'gerente'

    @property
    def sucursales_ids(self):
        """Retorna lista de id_sucursal asignados al usuario."""
        return [us.id_sucursal for us in self.sucursales]


class UserSucursal(Base):
    __tablename__ = 'user_sucursales'
    __table_args__ = (
        UniqueConstraint('user_id', 'id_sucursal', name='uq_user_sucursal'),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    id_sucursal = Column(Integer, nullable=False)

    user = relationship('User', back_populates='sucursales')

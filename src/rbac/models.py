from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

class Role(Base):
    __tablename__ = "rbac_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    permissions: Mapped[list["Permission"]] = relationship(
        back_populates="role_permission",
        secondary="rbac_role_permission",
    )

class Permission(Base):
    __tablename__ = "rbac_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[str] = mapped_column(String(255), nullable=False)
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

class RolePermission(Base):
    __tablename__ = "rbac_role_permission"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("rbac_roles.id"),
        primary_key=True,
        # ondelete="CASCADE",
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("rbac_permissions.id"),
        primary_key=True,
        # ondelete="CASCADE",
    )

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


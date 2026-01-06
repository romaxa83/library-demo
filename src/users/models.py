from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, LargeBinary, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.rbac.models import Role

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_verify_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("rbac_roles.id"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    role: Mapped["Role"] = relationship("Role")

    def has_permission(self, permission_alias: str) -> bool:
        """Проверка прав: если superadmin или есть нужный алиас в правах роли"""
        if self.role.is_superadmin:
            return True
        return any(p.alias == permission_alias for p in self.role.permissions)

    @property
    def is_deleted(self) -> bool:
        """Проверить, удалена ли запись"""
        return self.deleted_at is not None
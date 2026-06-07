"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlmodel import Session, func, select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, session: Session):
                super().__init__(session, User)
    """

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, id: UUID) -> ModelType | None:
        """Get a single record by ID."""
        return self.session.get(self.model, id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get all records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def count(self) -> int:
        """Count all records."""
        statement = select(func.count()).select_from(self.model)
        return self.session.exec(statement).one()

    def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def create_many(self, objects: list[ModelType]) -> list[ModelType]:
        """Create multiple records."""
        self.session.add_all(objects)
        self.session.commit()
        for obj in objects:
            self.session.refresh(obj)
        return objects

    def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Delete a record."""
        self.session.delete(obj)
        self.session.commit()

    def delete_by_id(self, id: UUID) -> bool:
        """Delete a record by ID. Returns True if deleted, False if not found."""
        obj = self.get_by_id(id=id)
        if obj:
            self.delete(obj=obj)
            return True
        return False

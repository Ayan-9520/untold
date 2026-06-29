from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Category
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest


class CategoryService:
    @staticmethod
    def list_all(db: Session) -> list[Category]:
        return db.query(Category).order_by(Category.name).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Category:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise NotFoundError("Category")
        return category

    @staticmethod
    def create(db: Session, data: CategoryCreateRequest) -> Category:
        existing = db.query(Category).filter(
            (Category.slug == data.slug) | (Category.name == data.name)
        ).first()
        if existing:
            raise ConflictError("Category already exists")

        category = Category(name=data.name, slug=data.slug, description=data.description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def update(db: Session, category_id: int, data: CategoryUpdateRequest) -> Category:
        category = CategoryService.get_by_id(db, category_id)
        if data.name:
            category.name = data.name
        if data.description is not None:
            category.description = data.description
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category_id: int) -> None:
        category = CategoryService.get_by_id(db, category_id)
        db.delete(category)
        db.commit()

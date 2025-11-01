# models.py
from sqlalchemy import Column, String, Text, DateTime, func, Integer, Index, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(90), nullable=False, unique=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

class RecipeSlugHistory(Base):
    __tablename__ = "recipe_slug_history"
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    old_slug = Column(String(90), index=True, nullable=False)
    changed_at = Column(DateTime, server_default=func.now())

# services/recipes.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utilities.slug import basic_slugify, uniquify_slug
from models import Recipe

def slug_exists(session: Session, slug: str) -> bool:
    return session.query(Recipe.id).filter_by(slug=slug).first() is not None

def create_recipe(session: Session, title: str, author_id: int, content: str = "") -> Recipe:
    base = basic_slugify(title)
    slug = uniquify_slug(base, lambda s: slug_exists(session, s))
    recipe = Recipe(title=title, slug=slug, author_id=author_id, content=content)
    session.add(recipe)
    session.commit()
    return recipe

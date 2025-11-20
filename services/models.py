# services/models.py
from datetime import datetime
from sqlalchemy import event
from flask_login import UserMixin
from services.db import db
from utilities.slug import base_slug, uniquify_slug

class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(90), unique=True, index=True, nullable=False)
    content = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class RecipeSlugHistory(db.Model):
    __tablename__ = "recipe_slug_history"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    old_slug = db.Column(db.String(90), index=True, nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# --- Auto-generate slug on insert ---
@event.listens_for(Recipe, "before_insert")
def recipe_before_insert(mapper, connection, target: Recipe):
    session = db.session
    base = base_slug(target.title)
    target.slug = uniquify_slug(session, Recipe, base)

# --- If title changes, rotate slug + save redirect history ---
@event.listens_for(Recipe, "before_update")
def recipe_before_update(mapper, connection, target: Recipe):
    session = db.session
    # Load current DB state to compare
    db_obj = session.get(Recipe, target.id)
    if not db_obj:
        return
    if db_obj.title != target.title:
        old_slug = db_obj.slug
        new_base = base_slug(target.title)
        target.slug = uniquify_slug(session, Recipe, new_base, exclude_id=target.id)
        if old_slug != target.slug:
            session.add(RecipeSlugHistory(recipe_id=target.id, old_slug=old_slug))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"
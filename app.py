# app.py
from flask import Flask, request, jsonify, redirect, url_for
from services.db import db
from services.models import Recipe, RecipeSlugHistory
from flask_migrate import Migrate

migrate = Migrate(app, db)

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Create a recipe (JSON: {title, content})
    @app.post("/api/recipes")
    def create_recipe():
        data = request.get_json(force=True) or {}
        r = Recipe(title=data.get("title", "").strip(), content=data.get("content", ""))
        db.session.add(r)
        db.session.commit()
        return jsonify({"id": r.id, "slug": r.slug, "title": r.title}), 201

    # Canonical detail URL: /recipes/<id>-<slug>
    @app.get("/recipes/<id_slug>")
    def recipe_detail(id_slug: str):
        try:
            rid_str, _, tail = id_slug.partition("-")
            rid = int(rid_str)
        except Exception:
            return jsonify({"error": "Bad id"}), 400

        r = db.session.get(Recipe, rid)
        if not r:
            # check old slugs -> redirect
            old = RecipeSlugHistory.query.filter_by(old_slug=tail or id_slug).first()
            if old:
                canonical = f"{old.recipe_id}-{db.session.get(Recipe, old.recipe_id).slug}"
                return redirect(url_for("recipe_detail", id_slug=canonical), code=301)
            return jsonify({"error": "Not found"}), 404

        canonical = f"{r.id}-{r.slug}"
        if id_slug != canonical:
            return redirect(url_for("recipe_detail", id_slug=canonical), code=301)

        return jsonify({"id": r.id, "title": r.title, "slug": r.slug, "content": r.content})

    # Simple list
    @app.get("/api/recipes")
    def list_recipes():
        rows = Recipe.query.order_by(Recipe.created_at.desc()).all()
        return jsonify([{"id": r.id, "title": r.title, "slug": r.slug} for r in rows])

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

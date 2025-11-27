# app.py
from datetime import timedelta
from flask import Flask, request, jsonify, redirect, url_for, redirect, render_template, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from argon2 import PasswordHasher
from sqlalchemy.exc import SQLAlchemyError
from services.db import db
from services.models import Recipe, RecipeSlugHistory, User

ph = PasswordHasher()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    # --- security & session config ---
    app.config.update(
        SECRET_KEY="replace-me",  # set via env in prod
        SQLALCHEMY_DATABASE_URI="sqlite:///site.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,     # True behind HTTPS
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        WTF_CSRF_TIME_LIMIT=None,        # CSRF token lifetime (optional)
    )

    # --- init extensions in the right order ---
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))
    
    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/about")
    def about_us():
        return render_template("about_us.html")

    @app.route("/recipes")
    def recipes():
        # Fetch featured recipes (first 3 or random)
        featured_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(3).all()
        return render_template("recipes.html", featured_recipes=featured_recipes)

    @app.route("/blog")
    def blog():
        return render_template("blog.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")
    
    @app.route("/recipes/create")
    @login_required
    def create_recipe_page():
        """Display the recipe creation form (requires login)"""
        return render_template("create_recipe.html")

    @csrf.exempt
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            try:
                username = (request.form.get("username") or "").strip()
                password = request.form.get("password") or ""
                confirm  = request.form.get("confirmPassword") or ""
                email = (request.form.get("email") or "").strip()
                first_name = (request.form.get("firstName") or "").strip()
                last_name = (request.form.get("lastName") or "").strip()
                dob = request.form.get("dob") or None
                gender = request.form.get("gender") or None

                # Basic validation
                if not username or not password:
                    flash("Missing username or password", "error")
                    return render_template("signup.html"), 400

                if password != confirm:
                    flash("Passwords do not match", "error")
                    return render_template("signup.html"), 400

                # Check if username already exists
                if User.query.filter_by(username=username).first():
                    flash("Username already taken", "error")
                    return render_template("signup.html"), 409
                    
                # Check if email already exists
                if email and User.query.filter_by(email=email).first():
                    flash("Email already registered", "error")
                    return render_template("signup.html"), 409

                # Create the user with all fields
                u = User(
                    username=username,
                    email=email or None,
                    first_name=first_name or None,
                    last_name=last_name or None,
                    gender=gender or None
                )
                
                # Handle date of birth
                if dob:
                    from datetime import datetime as dt
                    try:
                        u.date_of_birth = dt.strptime(dob, "%Y-%m-%d").date()
                    except ValueError:
                        pass
                
                u.set_password(password, ph)
                db.session.add(u)
                db.session.commit()
                
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login"))
            
            except Exception as e:
                db.session.rollback()
                print(f"ERROR during signup: {e}")
                import traceback
                traceback.print_exc()
                flash("An error occurred during signup. Please try again.", "error")
                return render_template("signup.html"), 500

        return render_template("signup.html")

    
    # ---- login manager user loader ----
    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # ---- util: JSON & basic validation ----
    def _json():
        return request.get_json(force=True) or {}

    # ---- public: CSRF token for JS (double submit header pattern) ----
    @app.get("/api/auth/csrf-token")
    def csrf_token():
        # Frontend should read this and send it back in header:
        # X-CSRFToken: <value> on POST/PUT/PATCH/DELETE
        return jsonify({"csrfToken": generate_csrf()})

    # ---- auth: register/login/logout/me ----
    @csrf.exempt
    @app.post("/api/auth/register")
    def register():
        data = _json()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return jsonify({"error": "username and password required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "username already registered"}), 409

        u = User(username=username)
        u.set_password(password, ph)  # argon2
        db.session.add(u)
        db.session.commit()
        return jsonify({"ok": True})

    @csrf.exempt
    @app.post("/api/auth/login")
    def api_login():
        data = _json()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password, ph):
            return jsonify({"error": "invalid credentials"}), 401

        login_user(user, remember=False, duration=timedelta(hours=8))
        return jsonify({"ok": True})
    
    @csrf.exempt
    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Already logged in? send them home
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            user = User.query.filter_by(username=username).first()
            # NOTE: pass ph here, same as api_login
            if not user or not user.check_password(password, ph):
                flash("Invalid username or password", "error")
                return render_template("login.html"), 401

            login_user(user, remember=False, duration=timedelta(hours=8))
            return redirect(url_for("index"))

        # GET: just show the form
        return render_template("login.html")

    @app.get("/api/auth/me")
    def me():
        if current_user.is_authenticated:
            return jsonify({"id": current_user.id, "username": current_user.username})
        return jsonify({"id": None, "username": None})

    # ---- RECIPES (unchanged behavior, plus auth on create) ----

    # Create a recipe (JSON: {title, content})
    @csrf.exempt
    @app.post("/api/recipes")
    @login_required
    def create_recipe():
        # Try to parse JSON safely
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        content = data.get("content") or ""

        if not title:
            return jsonify({"error": "title is required"}), 400

        r = Recipe(title=title, content=content)
        db.session.add(r)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            # TEMP: print error so you see it in the Flask console
            print("ERROR saving recipe:", e)
            return jsonify({"error": "server error saving recipe", "detail": str(e)}), 500

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

    @app.get("/api/whoami")
    def whoami():
        if current_user.is_authenticated:
            return {
                "authenticated": True,
                "id": current_user.id,
                "username": current_user.username,
            }
        else:
            return {"authenticated": False}, 200
    
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

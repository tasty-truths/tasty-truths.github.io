# utilities/slug.py
from slugify import slugify

def base_slug(title: str, max_len: int = 80) -> str:
    # ascii, lowercase, hyphenated, trimmed
    s = slugify(title or "", max_length=max_len, word_boundary=True)
    return s or "recipe"

def uniquify_slug(session, Model, base: str, exclude_id: int | None = None) -> str:
    """
    Make `base` unique by appending -2, -3, ... as needed.
    exclude_id: ignore this PK (useful on updates)
    """
    slug = base
    i = 2
    while True:
        q = session.query(Model.id).filter_by(slug=slug)
        if exclude_id is not None:
            q = q.filter(Model.id != exclude_id)
        exists = session.query(q.exists()).scalar()
        if not exists:
            return slug
        slug = f"{base}-{i}"
        i += 1

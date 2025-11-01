// store.js  (ES module)
const STORAGE_KEY = "tt_store_v1"; // namespace your data

// ---------- internal utils ----------
function safeParse(json, fallback) {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}

function safeStringify(obj) {
  try {
    return JSON.stringify(obj);
  } catch {
    // Last resort: drop to a minimal string to avoid throwing
    return "{}";
  }
}

function loadAll() {
  const raw = localStorage.getItem(STORAGE_KEY);
  const data = safeParse(raw, {});
  return (typeof data === "object" && data) ? data : {};
}

function saveAll(data) {
  localStorage.setItem(STORAGE_KEY, safeStringify(data));
}

// Ensure a collection exists and return it
function ensureCollection(data, type) {
  if (!data[type]) data[type] = [];
  return data[type];
}

// Basic, readable slugify (ASCII, lowercase, hyphenated)
function slugify(text, maxLen = 80) {
  if (!text) return "item";
  return text
    .normalize("NFKD")                   // strip accents
    .replace(/[\u0300-\u036f]/g, "")    // combine marks
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, " ")      // keep alnum/space/hyphen
    .trim()
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, maxLen) || "item";
}

function uniquifySlug(items, base, excludeId = null) {
  let candidate = base;
  let i = 2;
  const taken = new Set(items.map(x => (excludeId && x.id === excludeId) ? null : x.slug));
  while (taken.has(candidate)) {
    candidate = `${base}-${i++}`;
  }
  return candidate;
}

function nowISO() {
  return new Date().toISOString();
}

function genId() {
  // Compact unique ID: time + random
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}`;
}

// ---------- public API ----------
export const store = {
  /**
   * Return an array of items in a collection.
   * @param {string} type e.g. "recipes" or "posts"
   */
  getAll(type) {
    const data = loadAll();
    return [...ensureCollection(data, type)];
  },

  /**
   * Return a single item by slug or null.
   */
  getBySlug(type, slug) {
    const data = loadAll();
    const col = ensureCollection(data, type);
    return col.find(x => x.slug === slug) || null;
  },

  /**
   * Create a new item. If no slug is provided, it is generated from title.
   * Returns the created item.
   */
  create(type, obj) {
    const data = loadAll();
    const col = ensureCollection(data, type);

    const id = obj.id ?? genId();
    const title = (obj.title ?? "").trim();
    const base = obj.slug ? slugify(obj.slug) : slugify(title || "item");
    const slug = uniquifySlug(col, base);

    const createdAt = nowISO();
    const item = {
      id,
      title,
      slug,
      ...obj,
      createdAt,
      updatedAt: createdAt,
    };

    col.push(item);
    saveAll(data);
    return item;
  },

  /**
   * Update an item found by current slug.
   * If title changes (and no explicit slug provided), slug is regenerated uniquely.
   * Returns the updated item, or null if not found.
   */
  update(type, slug, obj) {
    const data = loadAll();
    const col = ensureCollection(data, type);
    const idx = col.findIndex(x => x.slug === slug);
    if (idx === -1) return null;

    const current = col[idx];
    const next = { ...current, ...obj, updatedAt: nowISO() };

    // Handle slug logic:
    if (obj.slug && obj.slug !== current.slug) {
      // explicit slug override
      const base = slugify(obj.slug);
      next.slug = uniquifySlug(col, base, current.id);
    } else if (obj.title && obj.title !== current.title) {
      // title changed; regenerate slug
      const base = slugify(obj.title);
      next.slug = uniquifySlug(col, base, current.id);
    }

    col[idx] = next;
    saveAll(data);
    return next;
  },

  /**
   * Remove an item by slug. Returns true if removed.
   */
  remove(type, slug) {
    const data = loadAll();
    const col = ensureCollection(data, type);
    const lenBefore = col.length;
    const remaining = col.filter(x => x.slug !== slug);
    data[type] = remaining;
    saveAll(data);
    return remaining.length !== lenBefore;
  },
};

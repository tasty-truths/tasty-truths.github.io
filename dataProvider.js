// dataProvider.js
import { store as local } from "./store.js";

export const LocalProvider = {
  getAll: (t) => local.getAll(t),
  getBySlug: (t, s) => local.getBySlug(t, s),
  create: (t, o) => local.create(t, o),
  update: (t, s, o) => local.update(t, s, o),
  remove: (t, s) => local.remove(t, s),
};

// Later, if you want server-backed:
export const ApiProvider = {
  async getAll(t) {
    const res = await fetch(`/api/${t}`);
    return await res.json();
  },
  async getBySlug(t, s) {
    const res = await fetch(`/api/${t}/${encodeURIComponent(s)}`);
    if (!res.ok) return null;
    return await res.json();
  },
  async create(t, o) {
    const res = await fetch(`/api/${t}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(o) });
    return await res.json();
  },
  async update(t, s, o) {
    const res = await fetch(`/api/${t}/${encodeURIComponent(s)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(o) });
    return await res.json();
  },
  async remove(t, s) {
    const res = await fetch(`/api/${t}/${encodeURIComponent(s)}`, { method: "DELETE" });
    return res.ok;
  },
};

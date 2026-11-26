/**
 * silla/src/services/api.js
 * =========================
 * Centralized API service for communicating with SILLA FastAPI backend.
 * Provides resilient fallbacks and typed helper methods.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  try {
    const res = await fetch(url, config);
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errBody.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on [${options.method || "GET"} ${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // System Health
  getHealth: () => request("/health"),

  // Recipes
  getRecipes: (params = {}) => {
    const qs = new URLSearchParams();
    if (params.search) qs.append("search", params.search);
    if (params.category && params.category !== "all") qs.append("category", params.category);
    if (params.cuisine && params.cuisine !== "all") qs.append("cuisine", params.cuisine);
    if (params.limit) qs.append("limit", params.limit);
    if (params.offset) qs.append("offset", params.offset);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return request(`/recipes${query}`);
  },

  getRecipe: (recipeId) => request(`/recipes/${encodeURIComponent(recipeId)}`),

  getRecipeCost: (recipeId, storeId = null) => {
    const qs = storeId ? `?store_id=${encodeURIComponent(storeId)}` : "";
    return request(`/recipes/${encodeURIComponent(recipeId)}/cost${qs}`);
  },

  // NLP Semantic Search
  search: (query, topK = 6) =>
    request("/search", {
      method: "POST",
      body: JSON.stringify({ query, top_k: topK }),
    }),

  // Smart Cart Generation
  generateCart: ({ recipeIds, servings = 4, userPantry = {}, budgetEgp = null, storeId = null, optimizeBudget = true, enableSubstitutes = true }) =>
    request("/cart/generate", {
      method: "POST",
      body: JSON.stringify({
        recipe_ids: recipeIds,
        servings,
        user_pantry: userPantry,
        budget_egp: budgetEgp,
        store_id: storeId,
        optimize_budget: optimizeBudget,
        enable_substitutes: enableSubstitutes,
      }),
    }),

  // Multi-Store Price Comparison
  compareStores: ({ recipeIds, servings = 4, userPantry = {} }) =>
    request("/cart/compare-stores", {
      method: "POST",
      body: JSON.stringify({
        recipe_ids: recipeIds,
        servings,
        user_pantry: userPantry,
      }),
    }),

  // Catalog Lookups
  getIngredients: () => request("/ingredients"),
  getStores: () => request("/stores"),
  getProducts: (params = {}) => {
    const qs = new URLSearchParams();
    if (params.store_id) qs.append("store_id", params.store_id);
    if (params.ingredient_id) qs.append("ingredient_id", params.ingredient_id);
    if (params.limit) qs.append("limit", params.limit);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return request(`/products${query}`);
  },

  // SILLA AI Assistant
  chatAssistant: ({ message, servings = null, budgetEgp = null }) =>
    request("/assistant/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        servings,
        budget_egp: budgetEgp,
      }),
    }),
};

export default api;

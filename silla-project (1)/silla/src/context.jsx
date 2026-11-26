import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { P, RECIPES, STORES, UI } from "./data";
import api from "./services/api";

const Ctx = createContext();
export const useSilla = () => useContext(Ctx);

const norm = (s) => (s || "").toLowerCase().normalize("NFD").replace(/\p{M}/gu, "")
  .replace(/[أإآ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي");
const NUM = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8 };
const STOP = new Set("i want to make for people my budget egp the under and a with عايز اعمل لـ ميزانيتي جنيه اشخاص".split(" "));

export function matchRecipesLocal(q, catalog = RECIPES) {
  const text = norm(q).replace(/\b(one|two|three|four|five|six|seven|eight)\b/g, (w) => NUM[w]);
  const tokens = text.split(/[^\p{L}\p{N}]+/u).filter((w) => w.length > 1 && !STOP.has(w) && !/^\d+$/.test(w));
  if (!tokens.length) return [];
  return catalog.map((r) => {
    const hay = norm(`${r.en || r.recipe_name_en || ""} ${r.ar || r.recipe_name_ar || ""} ${r.alias || ""} ${r.cat || r.category || ""}`);
    return { r, score: tokens.filter((w) => hay.includes(w)).length };
  }).filter((x) => x.score > 0).sort((a, b) => b.score - a.score).map((x) => x.r);
}

// Pick the best offer for one ingredient
function pick(pid, need, store, saver) {
  const stores = store === "mix" ? STORES : [store];
  const best = (ids) => {
    let b = null;
    for (const id of ids) {
      if (!P[id]) continue;
      for (const s of stores) {
        if (P[id].out && P[id].out.includes(s)) continue;
        const price = (P[id].price && P[id].price[s]) || 25;
        const pack = P[id].pack || 500;
        const n = Math.ceil(need / pack);
        const cost = n * price;
        if (!b || cost < b.cost) b = { id, store: s, packs: n, cost };
      }
    }
    return b;
  };
  const sub = P[pid]?.sub;
  const b = best(saver && sub ? [pid, sub] : [pid]) || (sub && best([sub]));
  return b ? { pid, ...b, need, swapped: b.id !== pid } : { pid, need, id: pid, out: true, packs: 0, cost: 0 };
}

export function SillaProvider({ children }) {
  const [lang, setLang] = useState("en");
  const [query, setQuery] = useState("");
  const [defServ, setDefServ] = useState(4);
  const [budget, setBudget] = useState(300);
  const [diet, setDiet] = useState("all");
  const [plan, setPlan] = useState([]);
  const [pantry, setPantry] = useState({ salt: 700 });
  const [store, setStore] = useState("mix");
  const [saver, setSaver] = useState(false);
  const [removed, setRemoved] = useState(new Set());
  const [packs, setPacks] = useState({});
  const [results, setResults] = useState(null);

  // Backend integration state
  const [liveRecipes, setLiveRecipes] = useState([]);
  const [liveStores, setLiveStores] = useState([]);
  const [backendReady, setBackendReady] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.documentElement.lang = lang;
  }, [lang]);

  // Fetch initial catalog from FastAPI backend
  useEffect(() => {
    async function initCatalog() {
      try {
        const [healthRes, recipesRes, storesRes] = await Promise.allSettled([
          api.getHealth(),
          api.getRecipes({ limit: 400 }),
          api.getStores(),
        ]);

        if (healthRes.status === "fulfilled") {
          setBackendReady(true);
        }

        if (recipesRes.status === "fulfilled" && recipesRes.value?.recipes) {
          // Format DB recipes to match UI structure
          const formatted = recipesRes.value.recipes.map((r) => ({
            id: r.recipe_id,
            en: r.recipe_name_en,
            ar: r.recipe_name_ar,
            cat: r.category || "Classics",
            cuisine: r.cuisine || "Egyptian",
            servings: r.base_servings || 4,
            prep: r.prep_time_min,
            cook: r.cook_time_min,
            difficulty: r.difficulty || "Medium",
            photo: r.image_url,
            emoji: "🍲",
            estimated_cost: r.estimated_cost_egp || 85,
            ing: {},
            steps: [],
          }));
          setLiveRecipes(formatted);
        }

        if (storesRes.status === "fulfilled" && Array.isArray(storesRes.value)) {
          setLiveStores(storesRes.value.map((s) => s.store_name));
        }
      } catch (err) {
        console.warn("Backend connection notice (using fallback local dataset):", err);
      }
    }
    initCatalog();
  }, []);

  const t = (k) => UI[lang]?.[k] || k;
  const name = (o) => (o ? o[lang] || o.en || o.recipe_name_en || "" : "");

  // Hybrid Search: Calls SILLA NLP hybrid retrieval engine if online, otherwise local fuzzy
  const search = async (q) => {
    const text = norm(q).replace(/\b(one|two|three|four|five|six|seven|eight)\b/g, (w) => NUM[w]);
    const sv = text.match(/(\d+)\s*(?:people|persons?|serving|servings|اشخاص|افراد)/) || text.match(/for\s*(\d+)/) || text.match(/ل\s*(\d+)/);
    if (sv) setDefServ(Math.max(1, +sv[1]));
    const bd = text.match(/(?:budget|under|ميزانيه)\D{0,12}(\d+)/) || text.match(/(\d+)\s*(?:egp|جنيه)/);
    if (bd) setBudget(Math.max(0, +bd[1]));

    setIsSearching(true);
    try {
      const res = await api.search(q, 6);
      if (res && res.matched_recipes && res.matched_recipes.length > 0) {
        const mapped = res.matched_recipes.map((m) => ({
          id: m.recipe_id,
          en: m.recipe_name_en,
          ar: m.recipe_name_ar,
          cat: m.category || "Main",
          cuisine: m.cuisine || "Egyptian",
          emoji: "🍲",
          photo: m.image_url,
          score: m.similarity_score,
          servings: defServ,
          ing: {},
        }));
        setResults(mapped);
        setIsSearching(false);
        return mapped;
      }
    } catch (e) {
      console.warn("NLP backend search fallback:", e);
    }

    // Local fallback search
    const localCatalog = liveRecipes.length ? liveRecipes : RECIPES;
    const localResults = matchRecipesLocal(q, localCatalog);
    setResults(localResults);
    setIsSearching(false);
    return localResults;
  };

  const pantryQty = (id) => Number(pantry[id]) || 0;
  const setPantryQty = (id, qty) => {
    const n = Math.max(0, Number(qty) || 0);
    setPantry((p) => {
      const next = { ...p };
      if (n <= 0) delete next[id];
      else next[id] = n;
      return next;
    });
    setPacks({});
  };
  const removePantry = (id) => setPantryQty(id, 0);
  const togglePantry = (id) => {
    setPantry((p) => {
      const next = { ...p };
      if (next[id]) {
        delete next[id];
      } else {
        next[id] = P[id]?.pack || 100;
      }
      return next;
    });
    setPacks({});
  };

  const addRecipe = (id) => setPlan((p) => (p.some((x) => x.id === id) ? p : [...p, { id, servings: defServ }]));
  const setServ = (id, n) => {
    setPlan((p) => p.map((x) => (x.id === id ? { ...x, servings: Math.max(1, n) } : x)));
    setPacks({});
  };
  const dropRecipe = (id) => {
    setPlan((p) => p.filter((x) => x.id !== id));
    setPacks({});
  };
  const removeItem = (pid) => setRemoved((s) => new Set(s).add(pid));

  // Multi-recipe consolidation
  const activeCatalog = useMemo(() => {
    const merged = [...RECIPES];
    liveRecipes.forEach((lr) => {
      if (!merged.some((m) => m.id === lr.id)) merged.push(lr);
    });
    return merged;
  }, [liveRecipes]);

  const needs = useMemo(() => {
    const m = {};
    plan.forEach(({ id, servings }) => {
      const r = activeCatalog.find((x) => x.id === id);
      if (r && r.ing) {
        Object.entries(r.ing).forEach(([k, q]) => {
          m[k] = (m[k] || 0) + (q * servings) / (r.servings || 4);
        });
      }
    });
    return m;
  }, [plan, activeCatalog]);

  const build = (s) =>
    Object.entries(needs)
      .filter(([k]) => !removed.has(k))
      .map(([k, n]) => {
        const missing = Math.max(0, n - pantryQty(k));
        if (missing <= 0) return null;
        const l = pick(k, missing, s, saver);
        l.required = n;
        l.onHand = pantryQty(k);
        if (packs[k] && !l.out) {
          l.packs = packs[k];
          l.cost = packs[k] * (P[l.id]?.price?.[l.store] || 25);
        }
        return l;
      })
      .filter(Boolean);

  const sum = (ls) => ls.reduce((a, l) => a + (l.cost || 0), 0);

  const cart = useMemo(() => build(store), [needs, pantry, removed, store, saver, packs]);
  const total = sum(cart);

  const activeStoreList = liveStores.length ? liveStores : STORES;
  const compare = useMemo(
    () =>
      [...activeStoreList, "mix"].map((s) => {
        const ls = build(s);
        return {
          s,
          total: sum(ls),
          issues: ls.filter((l) => l.out || l.swapped).length,
        };
      }),
    [needs, pantry, removed, saver, packs, activeStoreList]
  );

  const estimate = (r, n = defServ) => {
    if (r.estimated_cost) return Math.round((r.estimated_cost * n) / (r.servings || 4));
    if (r.ing && Object.keys(r.ing).length) {
      return Object.entries(r.ing).reduce((a, [k, q]) => a + pick(k, (q * n) / (r.servings || 4), "mix", true).cost, 0);
    }
    return Math.round(75 * (n / 4));
  };

  return (
    <Ctx.Provider
      value={{
        lang,
        setLang,
        t,
        name,
        query,
        setQuery,
        search,
        results,
        isSearching,
        defServ,
        setDefServ,
        budget,
        setBudget,
        diet,
        setDiet,
        plan,
        addRecipe,
        setServ,
        dropRecipe,
        pantry,
        pantryQty,
        setPantryQty,
        removePantry,
        togglePantry,
        needs,
        store,
        setStore,
        saver,
        setSaver,
        cart,
        total,
        compare,
        removeItem,
        setPacks,
        estimate,
        liveRecipes,
        backendReady,
        activeStoreList,
      }}
    >
      {children}
    </Ctx.Provider>
  );
}

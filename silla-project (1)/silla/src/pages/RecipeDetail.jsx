import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { ChevronLeft, Plus, Minus, ShoppingCart, Check, Clock, Users, Flame, Utensils } from "lucide-react";
import { useSilla } from "../context";
import { P, RECIPES } from "../data";
import api from "../services/api";

export default function RecipeDetail() {
  const { id } = useParams();
  const { name, defServ, pantry, addRecipe, setServ, plan, lang } = useSilla();

  const [dbRecipe, setDbRecipe] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fallback local recipe
  const localR = RECIPES.find((x) => x.id === id);

  const [n, setN] = useState(plan.find((x) => x.id === id)?.servings ?? defServ);

  useEffect(() => {
    let mounted = true;
    async function fetchDetail() {
      try {
        const data = await api.getRecipe(id);
        if (mounted && data) {
          setDbRecipe(data);
        }
      } catch (e) {
        console.warn("Using local recipe detail:", e);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    fetchDetail();
    return () => {
      mounted = false;
    };
  }, [id]);

  const r = dbRecipe || localR;

  if (!r && !loading) {
    return (
      <section className="page">
        <p>
          {lang === "ar" ? "الوصفة غير موجودة." : "Recipe not found."}{" "}
          <Link to="/recipes">{lang === "ar" ? "العودة لكتاب الوصفات" : "Back to the recipe book"}</Link>
        </p>
      </section>
    );
  }

  if (loading) {
    return (
      <section className="page" style={{ textAlign: "center", padding: "4rem" }}>
        <p className="script" style={{ fontSize: "1.8rem" }}>
          {lang === "ar" ? "الشيف بيحضر مقادير الوصفة..." : "Chef is preparing recipe ingredients..."}
        </p>
      </section>
    );
  }

  const add = () => {
    addRecipe(id);
    setServ(id, n);
  };
  const added = plan.some((x) => x.id === id);

  const title = lang === "ar" ? r.recipe_name_ar || r.ar : r.recipe_name_en || r.en;
  const baseServings = r.base_servings || r.servings || 4;
  const prep = r.prep_time_min || r.prep || 15;
  const cook = r.cook_time_min || r.cook || 25;
  const totalTime = prep + cook;

  // Build ingredients list from backend or local
  const ingredientsList = r.ingredients
    ? r.ingredients.map((ing) => {
        const scaledQty = Math.round(((ing.quantity || 1) * n) / baseServings * 10) / 10;
        const ingName = lang === "ar" ? ing.canonical_name_ar || ing.original_name : ing.canonical_name_en || ing.original_name;
        const isAtHome = Boolean(
          pantry && (pantry[ing.ingredient_id] || pantry[ing.original_name?.toLowerCase()])
        );
        return {
          id: ing.ingredient_id || ing.original_name,
          name: ingName,
          quantity: scaledQty,
          unit: ing.unit || "g",
          isAtHome,
        };
      })
    : Object.entries(r.ing || {}).map(([k, q]) => ({
        id: k,
        name: name(P[k]) || k,
        quantity: Math.round((q * n) / baseServings),
        unit: P[k]?.unit || "g",
        isAtHome: Boolean(pantry && pantry[k]),
      }));

  const instructionsList =
    r.instructions && r.instructions.length > 0
      ? r.instructions
      : r.steps || [
          "Sauté aromatics in a hot pan.",
          "Add main ingredients and simmer until tender.",
          "Season to taste and serve hot with fresh bread.",
        ];

  return (
    <section className="page detail">
      <Link
        to="/recipes"
        className="muted"
        style={{ display: "inline-flex", alignItems: "center", gap: "4px", marginBottom: "1rem" }}
      >
        <ChevronLeft size={16} />
        {lang === "ar" ? "العودة لكتاب الوصفات" : "Back to Recipe Book"}
      </Link>

      <div style={{ display: "flex", gap: "2rem", alignItems: "flex-start", flexWrap: "wrap" }}>
        {r.image_url && (
          <img
            src={r.image_url}
            alt={title}
            style={{
              width: "100%",
              maxWidth: "380px",
              aspectRatio: "4/3",
              objectFit: "cover",
              borderRadius: "22px",
              boxShadow: "0 10px 28px rgba(36,74,58,.16)",
            }}
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80";
            }}
          />
        )}
        <div style={{ flex: 1, minWidth: "280px" }}>
          <h1 className="h1" style={{ margin: "0 0 0.5rem" }}>
            {r.emoji || "🍲"} {title}
          </h1>

          <p className="muted" style={{ margin: "0 0 1rem", fontSize: "1rem" }}>
            {r.category || r.cat} · {r.cuisine || "Egyptian"}
          </p>

          {/* Time & Servings Info Chips */}
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", margin: "1rem 0" }}>
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                background: "var(--blue)",
                padding: "6px 14px",
                borderRadius: "12px",
                fontWeight: 700,
                color: "var(--green)",
              }}
            >
              <Clock size={16} />
              {lang === "ar"
                ? `جاهزة في ${totalTime} دقيقة (تحضير: ${prep} د + طهي: ${cook} د)`
                : `Ready in ${totalTime} mins (Prep: ${prep}m, Cook: ${cook}m)`}
            </span>

            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                background: "var(--sage)",
                padding: "6px 14px",
                borderRadius: "12px",
                fontWeight: 700,
                color: "var(--green)",
              }}
            >
              <Flame size={16} />
              {lang === "ar" ? `مستوى الصعوبة: ${r.difficulty || "متوسطة"}` : `Difficulty: ${r.difficulty || "Medium"}`}
            </span>

            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                background: "#fff",
                border: "1.5px solid var(--green)",
                padding: "6px 14px",
                borderRadius: "12px",
                fontWeight: 700,
                color: "var(--green)",
              }}
            >
              <Utensils size={16} />
              {lang === "ar" ? `${ingredientsList.length} مكونات مطلوبة` : `${ingredientsList.length} ingredients required`}
            </span>
          </div>

          {/* Servings Stepper */}
          <div className="row" style={{ marginTop: "1.2rem" }}>
            <span style={{ fontWeight: 700, display: "inline-flex", alignItems: "center", gap: "6px" }}>
              <Users size={18} color="var(--green)" />
              {lang === "ar" ? "اضبط كمية المقادير لعدد الأفراد:" : "Scale ingredients for servings:"}
            </span>
            <div className="stepper">
              <button
                aria-label="Fewer servings"
                onClick={() => setN(Math.max(1, n - 1))}
                style={{ display: "inline-flex", alignItems: "center", justifyContent: "center" }}
              >
                <Minus size={14} />
              </button>
              <b style={{ fontSize: "1.1rem" }}>{n}</b>
              <button
                aria-label="More servings"
                onClick={() => setN(n + 1)}
                style={{ display: "inline-flex", alignItems: "center", justifyContent: "center" }}
              >
                <Plus size={14} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Ingredients & Instructions */}
      <div className="cols" style={{ marginTop: "2rem" }}>
        <div className="note">
          <h2>{lang === "ar" ? `المقادير الدقيقة (${ingredientsList.length})` : `Ingredients (${ingredientsList.length})`}</h2>
          <ul className="list">
            {ingredientsList.map((item, idx) => (
              <li key={idx} style={{ padding: "0.5rem 0" }}>
                <span>
                  <b>{item.name}</b>{" "}
                  {item.isAtHome && (
                    <small className="ok" style={{ display: "inline-flex", alignItems: "center", gap: "2px", marginInlineStart: "6px" }}>
                      <Check size={12} /> {lang === "ar" ? "متوفر في مطبخك" : "at home"}
                    </small>
                  )}
                </span>
                <span style={{ fontWeight: 600 }}>
                  {item.quantity} {item.unit}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className="note">
          <h2>{lang === "ar" ? "خطوات التحضير والطهي" : "Preparation & Cooking Steps"}</h2>
          <ol className="steps">
            {instructionsList.map((s, idx) => (
              <li key={idx} style={{ lineHeight: 1.7, marginBottom: "0.8rem" }}>
                {s}
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ marginTop: "2rem", display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
        <button
          className="btn"
          onClick={add}
          style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "0.9rem 1.8rem" }}
        >
          <ShoppingCart size={18} />
          {added
            ? lang === "ar"
              ? "تحديث المقادير في سلة السوبرماركت"
              : "Update items in grocery cart"
            : lang === "ar"
            ? "حساب تكلفة شراء المقادير في السوبرماركت"
            : "Calculate grocery cart cost"}
        </button>

        {added && (
          <Link
            to="/cart"
            className="btn ghost"
            style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
          >
            {lang === "ar" ? "مقارنة الأسعار بين المتاجر في السلة →" : "Compare store prices in cart →"}
          </Link>
        )}
      </div>
    </section>
  );
}

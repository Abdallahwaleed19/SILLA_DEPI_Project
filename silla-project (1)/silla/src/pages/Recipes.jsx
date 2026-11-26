import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { Search, Clock, Users, Flame, BookOpen, Sparkles, ArrowUpRight } from "lucide-react";
import { useSilla } from "../context";
import { RECIPES } from "../data";

const CATEGORIES = [
  { id: "All", en: "All Dishes", ar: "جميع الأكلات" },
  { id: "Main Course", en: "Main Dishes", ar: "أطباق رئيسية" },
  { id: "Dessert", en: "Desserts & Sweets", ar: "حلويات شرقية وغربية" },
  { id: "Seafood", en: "Seafood", ar: "مأكولات بحرية وأسماك" },
  { id: "Breakfast", en: "Breakfast & Foul", ar: "فطار وشعبيات" },
  { id: "Soup", en: "Soups", ar: "شوربات وطواجن" },
  { id: "Salad", en: "Salads & Mezze", ar: "سلطات ومقبلات" },
  { id: "Beverage", en: "Drinks", ar: "مشروبات وعصائر" },
  { id: "Appetizer", en: "Appetizers", ar: "مقبلات خفيفة" },
];

export default function Recipes() {
  const { liveRecipes, lang } = useSilla();
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("All");

  const catalog = useMemo(() => {
    return liveRecipes.length > 0 ? liveRecipes : RECIPES;
  }, [liveRecipes]);

  const list = useMemo(() => {
    return catalog.filter((r) => {
      const rCat = (r.cat || r.category || "").toLowerCase();
      const categoryMatch = cat === "All" || rCat.includes(cat.toLowerCase());
      const searchMatch =
        !q.trim() ||
        `${r.en || r.recipe_name_en || ""} ${r.ar || r.recipe_name_ar || ""}`
          .toLowerCase()
          .includes(q.toLowerCase());
      return categoryMatch && searchMatch;
    });
  }, [catalog, cat, q]);

  const difficultyLabel = (diff) => {
    const d = (diff || "Medium").toLowerCase();
    if (d.includes("easy")) return lang === "ar" ? "سهلة" : "Easy";
    if (d.includes("hard")) return lang === "ar" ? "متقدمة" : "Hard";
    return lang === "ar" ? "متوسطة" : "Medium";
  };

  return (
    <section className="page">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "10px", marginBottom: "6px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span className="page-icon-pill">
            <BookOpen size={24} strokeWidth={2.2} color="#fff" />
          </span>
          <h1 className="h1" style={{ margin: 0 }}>
            {lang === "ar" ? "موسوعة الأكلات والمقادير" : "Authentic Recipe Encyclopedia"}
          </h1>
        </div>
        <span className="count-pill">
          <Sparkles size={15} />
          {lang === "ar" ? `${list.length} أكلة موثقة` : `${list.length} dishes`}
        </span>
      </div>

      <p className="script" style={{ fontSize: "1.45rem", marginTop: "4px" }}>
        {lang === "ar"
          ? "اعرف مكونات أي أكلة مشهورة، خطوات تحضيرها، والوقت اللازم لإعدادها."
          : "Explore authentic dishes, exact ingredients, and how long each meal takes to prepare."}
      </p>

      {/* Search Bar */}
      <div style={{ position: "relative", maxWidth: "520px", margin: "1.2rem 0" }}>
        <input
          className="search"
          type="search"
          aria-label="Search recipes"
          placeholder={
            lang === "ar"
              ? "ابحث عن أي أكلة: كشري، مكرونة بشاميل، ملوخية، حواوشي، فتة، كفتة..."
              : "Search any dish: Koshari, Béchamel, Molokhia, Hawawshi, Fattah..."
          }
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ paddingInlineStart: "2.9rem", width: "100%", maxWidth: "100%" }}
        />
        <Search
          size={18}
          strokeWidth={2.3}
          color="var(--green)"
          style={{
            position: "absolute",
            top: "50%",
            transform: "translateY(-50%)",
            insetInlineStart: "1.05rem",
            pointerEvents: "none",
          }}
        />
      </div>

      {/* Category Chips */}
      <div className="chips" style={{ marginBottom: "1.8rem" }}>
        {CATEGORIES.map((c) => {
          const isSelected = cat === c.id;
          const label = lang === "ar" ? c.ar : c.en;
          return (
            <button
              key={c.id}
              className={"chip" + (isSelected ? " on" : "")}
              aria-pressed={isSelected}
              onClick={() => setCat(c.id)}
              style={{ fontWeight: isSelected ? 700 : 600 }}
            >
              {label}
            </button>
          );
        })}
      </div>

      {/* Full-Bleed Background Dish Cards */}
      <div className="cards" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(265px, 1fr))" }}>
        {list.map((r, idx) => {
          const title = lang === "ar" ? r.ar || r.recipe_name_ar : r.en || r.recipe_name_en;
          const prep = r.prep || 15;
          const cook = r.cook || 25;
          const totalTime = prep + cook;
          const servings = r.servings || 4;
          const imgSrc = r.photo || r.image_url;

          return (
            <Link
              key={r.id}
              to={`/recipe/${r.id}`}
              className="card recipe dish-bg-card"
              style={{ animationDelay: `${Math.min(idx, 12) * 40}ms` }}
            >
              {/* Background Dish Photo */}
              <img
                src={imgSrc || "https://www.themealdb.com/images/media/meals/4er7mj1598733193.jpg"}
                alt={title}
                loading="lazy"
                className="dish-bg-img"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "https://www.themealdb.com/images/media/meals/4er7mj1598733193.jpg";
                }}
              />
              <div className="dish-bg-overlay" />

              {/* Top Badges */}
              <div className="dish-card-top">
                <span className="dish-cat-pill">
                  {r.cat || r.category || "Classics"}
                </span>
                <span className="dish-diff-pill">
                  <Flame size={12} />
                  {difficultyLabel(r.difficulty)}
                </span>
              </div>

              {/* Bottom Dish Content over Gradient */}
              <div className="dish-card-bottom">
                <h3 className="dish-card-title">{title}</h3>

                <div className="dish-card-meta">
                  <span className="dish-meta-chip">
                    <Clock size={13} />
                    {lang === "ar" ? `تتعمل في ${totalTime} د` : `${totalTime} mins`}
                  </span>
                  <span className="dish-meta-chip">
                    <Users size={13} />
                    {lang === "ar" ? `${servings} أفراد` : `${servings} srv`}
                  </span>
                  <span className="dish-arrow-btn" aria-hidden="true">
                    <ArrowUpRight size={15} />
                  </span>
                </div>
              </div>
            </Link>
          );
        })}

        {!list.length && (
          <p className="muted" style={{ gridColumn: "1 / -1", textAlign: "center", padding: "4rem" }}>
            {lang === "ar" ? "لم نجد وصفة مطابقة لبحثك في هذا التصنيف." : "No recipe found matching your criteria in this category."}
          </p>
        )}
      </div>
    </section>
  );
}

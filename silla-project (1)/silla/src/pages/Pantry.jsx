import { useState, useEffect } from "react";
import { Archive, Check, Plus, AlertCircle } from "lucide-react";
import { useSilla } from "../context";
import { P, RECIPES } from "../data";
import api from "../services/api";

export default function Pantry() {
  const { name, pantry, togglePantry, plan, lang } = useSilla();
  const [dbIngredients, setDbIngredients] = useState([]);

  useEffect(() => {
    async function loadIngredients() {
      try {
        const data = await api.getIngredients();
        if (data && data.length) {
          setDbIngredients(data);
        }
      } catch (e) {
        console.warn("Using fallback local pantry items:", e);
      }
    }
    loadIngredients();
  }, []);

  const hasInPantry = (k) => Boolean(pantry && pantry[k]);

  const needed = new Set(
    plan.flatMap(({ id }) => {
      const r = RECIPES.find((rec) => rec.id === id);
      return r?.ing ? Object.keys(r.ing) : [];
    })
  );

  const baseItems = Object.keys(P);
  const have = baseItems.filter((k) => hasInPantry(k));
  const missing = [...needed].filter((k) => !hasInPantry(k));
  const rest = baseItems.filter((k) => !hasInPantry(k) && !needed.has(k));

  const Chips = ({ ids, cls }) =>
    ids.length ? (
      <div className="chips">
        {ids.map((k) => {
          const item = P[k];
          const itemName = name(item) || k;
          return (
            <button
              key={k}
              className={`chip ${cls}`}
              onClick={() => togglePantry(k)}
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              {cls === "on" ? <Check size={14} /> : <Plus size={14} />}
              {itemName}
            </button>
          );
        })}
      </div>
    ) : (
      <p className="muted" style={{ padding: "0.5rem 0" }}>
        {lang === "ar" ? "لا توجد عناصر هنا." : "Nothing here."}
      </p>
    );

  return (
    <section className="page">
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
        <Archive size={28} color="var(--green)" />
        <h1 className="h1" style={{ margin: 0 }}>
          {lang === "ar" ? "مخزون المطبخ (My Pantry)" : "My Pantry"}
        </h1>
      </div>
      <p className="script">
        {lang === "ar"
          ? "اضغط على أي مكون لإضافته أو حذفه من مخزون بيتك لتوفير تكلفة الشراء."
          : "Tap an ingredient to move it in or out of your kitchen to save on shopping."}
      </p>

      <div className="cols" style={{ marginTop: "1rem" }}>
        <div className="note">
          <h2>
            {lang === "ar" ? `متوفر في مطبخي (${have.length})` : `In my kitchen (${have.length})`}
          </h2>
          <Chips ids={have} cls="on" />
        </div>
        <div className="note">
          <h2>
            {lang === "ar"
              ? `نواقص للوصفات المختارة (${missing.length})`
              : `Missing for my recipes (${missing.length})`}
          </h2>
          <Chips ids={missing} cls="miss" />
        </div>
      </div>

      <h3 style={{ marginTop: "1.5rem" }}>
        {lang === "ar" ? "مكونات أخرى شائعة" : "Other common ingredients"}
      </h3>
      <Chips ids={rest} cls="" />
    </section>
  );
}

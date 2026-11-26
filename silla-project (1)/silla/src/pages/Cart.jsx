import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart, Store, Trash2, Plus, Minus, AlertTriangle, CheckCircle, TrendingDown } from "lucide-react";
import { useSilla } from "../context";
import { P, STORES } from "../data";
import api from "../services/api";

export default function Cart() {
  const {
    name,
    cart,
    total,
    budget,
    setBudget,
    store,
    setStore,
    saver,
    setSaver,
    compare,
    removeItem,
    setPacks,
    plan,
    pantry,
    lang,
    activeStoreList,
  } = useSilla();

  const [dbStoreComparisons, setDbStoreComparisons] = useState(null);

  // If user has recipes in plan, fetch real comparison from backend
  useEffect(() => {
    async function fetchBackendComparison() {
      if (!plan || plan.length === 0) return;
      try {
        const recipeIds = plan.map((p) => p.id);
        const res = await api.compareStores({
          recipeIds,
          servings: plan[0]?.servings || 4,
          userPantry: pantry,
        });
        if (res && res.store_rankings) {
          setDbStoreComparisons(res);
        }
      } catch (err) {
        console.warn("Backend store comparison notice:", err);
      }
    }
    fetchBackendComparison();
  }, [plan, pantry]);

  const over = total - budget;
  const pct = Math.min(100, (total / Math.max(budget, 1)) * 100);
  const label = (s) => (s === "mix" ? (lang === "ar" ? "أرخص تشكيلة متاجر" : "Cheapest mix") : s);

  const availableStores = activeStoreList && activeStoreList.length ? activeStoreList : STORES;

  return (
    <section className="page">
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
        <ShoppingCart size={28} color="var(--green)" />
        <h1 className="h1" style={{ margin: 0 }}>
          {lang === "ar" ? "سلة المشتريات الذكية" : "My Cart"}
        </h1>
      </div>

      <div className="row" style={{ marginTop: "1rem" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span>{lang === "ar" ? "الميزانية (جنيه):" : "Budget (EGP):"}</span>
          <input
            type="number"
            min={0}
            value={budget}
            onChange={(e) => setBudget(+e.target.value)}
          />
        </label>

        <label style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <Store size={18} color="var(--green)" />
          <select aria-label="Store" value={store} onChange={(e) => setStore(e.target.value)}>
            {[...availableStores, "mix"].map((s) => (
              <option key={s} value={s}>
                {label(s)}
              </option>
            ))}
          </select>
        </label>

        <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={saver}
            onChange={(e) => setSaver(e.target.checked)}
          />
          <span style={{ fontWeight: 600 }}>
            {lang === "ar" ? "تفعيل البدائل الأوفر (Budget Saver)" : "Budget saver (cheaper swaps)"}
          </span>
        </label>
      </div>

      {/* Budget Meter */}
      <div
        className="meter"
        role="progressbar"
        aria-valuenow={total}
        aria-valuemax={budget}
        style={{ marginTop: "1rem" }}
      >
        <div className={over > 0 ? "over" : ""} style={{ width: pct + "%" }} />
      </div>

      <p
        className={over > 0 ? "warn" : "ok"}
        style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "0.5rem" }}
      >
        {over > 0 ? <AlertTriangle size={16} /> : <CheckCircle size={16} />}
        {total} EGP {lang === "ar" ? "من" : "of"} {budget} EGP ·{" "}
        {over > 0
          ? `${over} EGP ${lang === "ar" ? "تجاوز الميزانية" : "over budget"}`
          : `${-over} EGP ${lang === "ar" ? "متبقي في الميزانية" : "left"}`}
      </p>

      {/* Cart Items */}
      {cart.length === 0 ? (
        <div style={{ textAlign: "center", padding: "3rem", background: "#fff", borderRadius: "20px", marginTop: "1rem" }}>
          <p className="muted" style={{ fontSize: "1.1rem" }}>
            {lang === "ar" ? "سلة المشتريات فارغة حالياً." : "Your cart is empty."}{" "}
            <Link to="/recipes">{lang === "ar" ? "تصفح كتاب الوصفات" : "Open the recipe book"}</Link>
          </p>
        </div>
      ) : (
        <div className="cards" style={{ marginTop: "1.5rem" }}>
          {cart.map((l) => (
            <div className="card prod" key={l.pid}>
              <h3>{name(P[l.id]) || l.id}</h3>
              {l.out ? (
                <p className="warn" style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <AlertTriangle size={14} />
                  {name(P[l.pid]) || l.pid} {lang === "ar" ? "غير متوفر بالمتجر" : "is out of stock"}
                </p>
              ) : (
                <p className="muted">
                  {l.store} · {lang === "ar" ? "عبوة" : "pack of"} {P[l.id]?.pack || 500}
                  {P[l.id]?.unit || "g"}
                </p>
              )}
              {l.swapped && (
                <span className="badge" style={{ marginBottom: "6px" }}>
                  {lang === "ar" ? "تم استبداله ببديل أوفر" : `swapped for ${name(P[l.pid])}`}
                </span>
              )}
              <div className="row" style={{ marginTop: "0.5rem" }}>
                <div className="stepper">
                  <button
                    aria-label="Less"
                    disabled={l.out}
                    onClick={() =>
                      setPacks((p) => ({ ...p, [l.pid]: Math.max(1, (l.packs || 1) - 1) }))
                    }
                    style={{ display: "inline-flex", alignItems: "center", justifyContent: "center" }}
                  >
                    <Minus size={13} />
                  </button>
                  <b>{l.packs}</b>
                  <button
                    aria-label="More"
                    disabled={l.out}
                    onClick={() =>
                      setPacks((p) => ({ ...p, [l.pid]: (l.packs || 1) + 1 }))
                    }
                    style={{ display: "inline-flex", alignItems: "center", justifyContent: "center" }}
                  >
                    <Plus size={13} />
                  </button>
                </div>
                <b>{l.cost} EGP</b>
                <button
                  className="x"
                  aria-label={`Remove ${name(P[l.id])}`}
                  onClick={() => removeItem(l.pid)}
                  style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Multi-Store Comparison */}
      <h3 style={{ marginTop: "2rem", display: "flex", alignItems: "center", gap: "8px" }}>
        <Store size={22} color="var(--green)" />
        {lang === "ar" ? "مقارنة الأسعار بين السوبرماركت" : "Compare Supermarket Stores"}
      </h3>

      {dbStoreComparisons ? (
        <div style={{ background: "#fff", borderRadius: "14px", padding: "1rem", marginTop: "0.5rem" }}>
          {dbStoreComparisons.potential_store_savings_egp > 0 && (
            <p className="ok" style={{ display: "flex", alignItems: "center", gap: "6px", margin: "0 0 10px" }}>
              <TrendingDown size={18} />
              {lang === "ar"
                ? `أوفر متجر: ${dbStoreComparisons.cheapest_store} يوفر لك حوالي ${dbStoreComparisons.potential_store_savings_egp.toFixed(0)} جنيه!`
                : `Cheapest store: ${dbStoreComparisons.cheapest_store} saves up to ${dbStoreComparisons.potential_store_savings_egp.toFixed(0)} EGP!`}
            </p>
          )}
          <div className="table-wrap" role="region" aria-label="Store comparison" tabIndex={0}>
            <table className="tbl">
              <tbody>
                {dbStoreComparisons.store_rankings?.map((sr) => (
                  <tr key={sr.store_name} className={sr.store_id === store ? "sel" : ""}>
                    <td>
                      <b>{sr.store_name}</b>
                      <small className="muted" style={{ display: "block" }}>
                        {lang === "ar" ? "توفر المنتجات" : "Coverage"}: {(sr.coverage_ratio * 100).toFixed(0)}%
                      </small>
                    </td>
                    <td>
                      <b>{sr.total_cart_cost_egp.toFixed(0)} EGP</b>
                    </td>
                    <td>
                      {sr.missing_items_count === 0 ? (
                        <span className="ok" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                          <CheckCircle size={14} /> {lang === "ar" ? "كل الأصناف متوفرة" : "All items in stock"}
                        </span>
                      ) : (
                        <span className="warn" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                          <AlertTriangle size={14} /> {sr.missing_items_count} {lang === "ar" ? "نواقص" : "missing"}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="table-wrap" role="region" aria-label="Store comparison" tabIndex={0} style={{ marginTop: "0.5rem" }}>
          <table className="tbl">
            <tbody>
              {compare.map((c) => (
                <tr key={c.s} className={c.s === store ? "sel" : ""}>
                  <td>{label(c.s)}</td>
                  <td>{c.total} EGP</td>
                  <td>{c.issues ? `⚠ ${c.issues}` : "✓"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

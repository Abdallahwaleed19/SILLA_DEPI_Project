import { useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, ChefHat, Send, Check, Eye, AlertCircle, Plus } from "lucide-react";
import { useSilla } from "../context";
import api from "../services/api";

export default function Cook() {
  const {
    query,
    setQuery,
    name,
    addRecipe,
    plan,
    defServ,
    setDefServ,
    budget,
    setBudget,
    lang,
  } = useSilla();

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text:
        lang === "ar"
          ? "أهلاً بك في سيلا! 👩‍🍳 أنا مساعد الطبخ الذكي. قولي نفسك تطبخ إيه النهاردة؟ ومعاك كام شخص أو ميزانية معينة؟"
          : "Bonjour! I'm your SILLA kitchen chef! 👩‍🍳 What are you craving today? You can specify people and budget (e.g. 'Béchamel pasta for 4 with 300 EGP')!",
      recipes: [],
      entities: {},
    },
  ]);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    const text = query.trim();
    if (!text) return;

    // Add user message
    const userMsg = { sender: "me", text };
    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setLoading(true);

    try {
      const res = await api.chatAssistant({
        message: text,
        servings: defServ,
        budgetEgp: budget,
      });

      if (res.extracted_entities?.servings) {
        setDefServ(res.extracted_entities.servings);
      }
      if (res.extracted_entities?.budget_egp) {
        setBudget(res.extracted_entities.budget_egp);
      }

      const botMsg = {
        sender: "bot",
        text: res.reply,
        recipes: res.suggested_recipes || [],
        entities: res.extracted_entities || {},
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.warn("Assistant fallback error:", err);
      // Friendly fallback
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            lang === "ar"
              ? "جميل جداً! استكشف الوصفات المقترحة في كتاب الطبخ وسأساعدك في ضبط المقادير والميزانية فوراً 🍲"
              : "Wonderful! Explore the recommended dishes in our recipe book and I will optimize your ingredients and budget! 🍲",
          recipes: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page chat">
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
        <ChefHat size={32} color="var(--green)" />
        <h1 className="h1" style={{ margin: 0 }}>
          {lang === "ar" ? "المساعد الذكي للطبخ" : "Let's Cook"}
        </h1>
      </div>

      <p className="script" style={{ marginTop: "4px" }}>
        {lang === "ar"
          ? "اكتب طلبك بالعربي أو الإنجليزي بالكمية والميزانية"
          : "Tell me what you're craving, in Arabic or English."}
      </p>

      {/* Chat messages */}
      <div className="bubbles" aria-live="polite">
        {messages.map((m, idx) => (
          <div key={idx} className={`bubble ${m.sender}`}>
            {m.sender === "bot" && (
              <img
                src="/images/remy-avatar.jpg"
                className="mini remy-avatar"
                alt="Chef"
                style={{ borderRadius: "50%", border: "2px solid var(--gold)" }}
              />
            )}
            <div style={{ width: "100%" }}>
              <p style={{ whiteSpace: "pre-line" }}>{m.text}</p>

              {/* Extracted badges */}
              {m.entities && (m.entities.servings || m.entities.budget_egp) && (
                <div style={{ display: "flex", gap: "8px", marginTop: "8px", flexWrap: "wrap" }}>
                  {m.entities.servings && (
                    <span className="badge" style={{ background: "var(--sage)" }}>
                      🍽️ {m.entities.servings} {lang === "ar" ? "أفراد" : "people"}
                    </span>
                  )}
                  {m.entities.budget_egp && (
                    <span className="badge" style={{ background: "var(--gold)" }}>
                      💰 {m.entities.budget_egp} EGP
                    </span>
                  )}
                </div>
              )}

              {/* Recipe Cards returned by SILLA NLP */}
              {m.recipes && m.recipes.length > 0 && (
                <div style={{ marginTop: "12px", display: "grid", gap: "8px" }}>
                  {m.recipes.map((r) => {
                    const rid = r.recipe_id || r.id;
                    const isAdded = plan.some((x) => x.id === rid);
                    return (
                      <div className="found" key={rid} style={{ background: "#fff", padding: "10px", borderRadius: "12px" }}>
                        <div>
                          <b>{lang === "ar" ? r.recipe_name_ar || r.ar : r.recipe_name_en || r.en}</b>
                          <div className="muted" style={{ fontSize: "0.85rem" }}>
                            {r.cuisine || "Egyptian"} · {r.prep_time_min || 15}m prep · {r.cook_time_min || 25}m cook
                          </div>
                        </div>

                        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                          <Link to={`/recipe/${rid}`} className="btn sm ghost" style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                            <Eye size={14} />
                            {lang === "ar" ? "الوصفة" : "Recipe"}
                          </Link>
                          <button
                            className="btn sm"
                            disabled={isAdded}
                            onClick={() => addRecipe(rid)}
                            style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}
                          >
                            {isAdded ? <Check size={14} /> : <Plus size={14} />}
                            {isAdded ? (lang === "ar" ? "في السلة" : "In Cart") : (lang === "ar" ? "أضف للسلة" : "Add to Cart")}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="bubble bot">
            <img
              src="/images/remy-avatar.jpg"
              className="mini remy-avatar"
              alt="Chef"
              style={{ borderRadius: "50%", border: "2px solid var(--gold)" }}
            />
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Sparkles size={18} className="spin" color="var(--gold)" />
              <span>{lang === "ar" ? "الشيف بيحضر لك أشهى الوصفات والأسعار..." : "Chef is checking the best recipes and store prices..."}</span>
            </div>
          </div>
        )}
      </div>

      {/* User input */}
      <form className="ask" onSubmit={submit}>
        <input
          aria-label="Your craving"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            lang === "ar"
              ? "عايز أعمل مكرونة بشاميل لـ 4 أفراد بميزانية 300 جنيه"
              : "I want macaroni béchamel for four people, budget 300 EGP"
          }
        />
        <button className="btn" type="submit" disabled={loading} style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
          <Send size={16} />
          {lang === "ar" ? "اسأل الشيف" : "Ask Chef"}
        </button>
      </form>
    </section>
  );
}

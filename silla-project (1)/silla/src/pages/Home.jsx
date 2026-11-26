import { Link } from "react-router-dom";
import { MessageSquareHeart, PackageCheck, ShoppingBag, ArrowRight, Sparkles, UtensilsCrossed, Timer, ChefHat } from "lucide-react";
import { useSilla } from "../context";

export default function Home() {
  const { lang } = useSilla();

  const STEPS = [
    {
      icon: <MessageSquareHeart size={28} strokeWidth={2} color="var(--green)" />,
      h: lang === "ar" ? "اسأل عن أي أكلة" : "Tell us your craving",
      p: lang === "ar" ? "اكتب الأكلة بالعامية المصرية أو الإنجليزية واعرف مكوناتها ووقتها فوراً." : "Write it in Arabic or English to discover ingredients & prep time.",
      to: "/cook",
    },
    {
      icon: <PackageCheck size={28} strokeWidth={2} color="var(--green)" />,
      h: lang === "ar" ? "راجع مخزون مطبخك" : "Check your pantry",
      p: lang === "ar" ? "حدد الحاجات الموجودة في بيتك واستبعدها بضغطة زر." : "Skip ingredients you already have at home effortlessly.",
      to: "/pantry",
    },
    {
      icon: <ShoppingBag size={28} strokeWidth={2} color="var(--green)" />,
      h: lang === "ar" ? "قارن أسعار المكونات" : "Smart grocery cart",
      p: lang === "ar" ? "اعرف أوفر سوبرماركت تشتري منه النواقص بميزانيتك." : "Compare ingredient prices across 8 Egyptian supermarkets.",
      to: "/cart",
    },
  ];

  return (
    <>
      <section className="hero">
        {/* Decorative Animated Floating Shapes inside Hero */}
        <div className="hero-float-badge badge-1" aria-hidden="true">
          <Timer size={16} color="var(--green)" />
          <span>{lang === "ar" ? "320+ وصفة أصلية" : "320+ Authentic Dishes"}</span>
        </div>
        <div className="hero-float-badge badge-2" aria-hidden="true">
          <UtensilsCrossed size={16} color="var(--gold)" />
          <span>{lang === "ar" ? "مقادير دقيقة بالجرام" : "Exact Gram Scaling"}</span>
        </div>

        <div className="hero-text">
          <p className="kicker">
            <Sparkles size={15} style={{ display: "inline", verticalAlign: "middle", marginInlineEnd: "6px" }} />
            {lang === "ar" ? "مساعدك الذكي في المطبخ والتوفير" : "YOUR SMART KITCHEN & GROCERY COMPANION"}
          </p>
          <h1>{lang === "ar" ? "اطبخ بذكاء واستمتع بكل وجبة." : "Anyone can cook."}</h1>
          <p className="script big">{lang === "ar" ? "كل أكلاتك المصرية في مكان واحد!" : "Even you, chef!"}</p>
          <p className="lead">
            {lang === "ar"
              ? "مطبخك الذكي.. من فكرة الأكلة لأقرب سوبرماركت في ثواني. اعرف مكونات كل طبق، وقت تحضيره الدقيق، وقارن أسعار النواقص في مصر."
              : "Your smart kitchen companion — from craving to cart in seconds. Discover authentic recipes, exact prep times, and smart ingredient lists."}
          </p>
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", alignItems: "center" }}>
            <Link
              className="btn"
              to="/recipes"
              style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}
            >
              <span>{lang === "ar" ? "استكشف موسوعة الأكلات" : "Explore the recipe book"}</span>
              <ArrowRight size={18} />
            </Link>
            <Link
              className="btn ghost"
              to="/cook"
              style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}
            >
              <ChefHat size={18} />
              <span>{lang === "ar" ? "اسأل الشيف الذكي" : "Ask SILLA Chef"}</span>
            </Link>
          </div>
          <p className="script">♡ {lang === "ar" ? "صُنع بكل حب، ودقيق، وقليل من الخيال." : "Made with love, flour and a little imagination."}</p>
        </div>

        <div className="frame">
          <img
            src="/images/remy.jpg"
            alt="SILLA Chef"
            className="remy-hero"
            style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "50%" }}
          />
        </div>
      </section>

      <section className="band">
        <h2>{lang === "ar" ? "من فكرة الأكلة إلى مطبخك في 3 خطوات" : "From craving to kitchen in three simple steps"}</h2>
        <div className="cards">
          {STEPS.map((s, idx) => (
            <Link
              key={idx}
              to={s.to}
              className="card step animated-step-card"
              style={{ textAlign: "center", padding: "2rem 1.3rem", animationDelay: `${idx * 100}ms` }}
            >
              <div className="step-icon-circle">
                {s.icon}
              </div>
              <h3 style={{ fontSize: "1.18rem", marginTop: "0.6rem" }}>{s.h}</h3>
              <p className="muted" style={{ fontSize: "0.95rem" }}>{s.p}</p>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}

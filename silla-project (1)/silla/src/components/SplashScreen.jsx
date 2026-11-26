import { useEffect, useState } from "react";
import { Sparkles, UtensilsCrossed, ShoppingCart, Flame } from "lucide-react";

export default function SplashScreen({ onFinish }) {
  const [exiting, setExiting] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setExiting(true), 2200);
    const t2 = setTimeout(() => {
      setHidden(true);
      if (onFinish) onFinish();
    }, 2800);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [onFinish]);

  if (hidden) return null;

  const dismiss = () => {
    setExiting(true);
    setTimeout(() => {
      setHidden(true);
      if (onFinish) onFinish();
    }, 450);
  };

  return (
    <div
      className={`splash-overlay ${exiting ? "splash-exit" : ""}`}
      onClick={dismiss}
      role="status"
      aria-label="Loading SILLA"
    >
      {/* Animated Ambient Orbs matching SILLA Logo colors */}
      <div className="splash-orb orb-1" />
      <div className="splash-orb orb-2" />
      <div className="splash-orb orb-3" />

      {/* Modern Floating Culinary Badges */}
      <div className="splash-float-icon icon-a">
        <UtensilsCrossed size={26} strokeWidth={1.9} />
      </div>
      <div className="splash-float-icon icon-b">
        <ShoppingCart size={26} strokeWidth={1.9} />
      </div>
      <div className="splash-float-icon icon-c">
        <Flame size={26} strokeWidth={1.9} />
      </div>
      <div className="splash-float-icon icon-d">
        <Sparkles size={24} strokeWidth={1.9} />
      </div>

      {/* Center Brand Card */}
      <div className="splash-core">
        <div className="splash-logo-ring">
          <div className="splash-ring-pulse" />
          <img
            src="/images/silla-logo.jpg"
            alt="SILLA Logo"
            className="splash-brand-img"
          />
        </div>

        <h1 className="splash-title">SILLA</h1>

        <p className="splash-subtitle-en">
          From Cravings to Smart Cart — Your AI Kitchen Companion
        </p>
        <p className="splash-subtitle-ar" dir="rtl">
          من نفسك في الأكلة... لمقاديرك وسلتك الذكية في ثواني
        </p>

        <div className="splash-progress-track">
          <div className="splash-progress-fill" />
        </div>
      </div>
    </div>
  );
}

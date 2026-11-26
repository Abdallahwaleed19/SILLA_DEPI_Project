import { useEffect, useRef, useState } from "react";
import { Sparkles, Soup, ShoppingCart, Flame } from "lucide-react";

export default function SplashScreen({ onFinish }) {
  const [exiting, setExiting] = useState(false);
  const [hidden, setHidden] = useState(false);
  const finishRef = useRef(onFinish);
  const exitTimer = useRef();
  const hideTimer = useRef();
  finishRef.current = onFinish;

  useEffect(() => {
    exitTimer.current = window.setTimeout(() => setExiting(true), 1500);
    hideTimer.current = window.setTimeout(() => {
      setHidden(true);
      finishRef.current?.();
    }, 1950);
    return () => {
      window.clearTimeout(exitTimer.current);
      window.clearTimeout(hideTimer.current);
    };
  }, []);

  if (hidden) return null;

  const dismiss = () => {
    window.clearTimeout(exitTimer.current);
    window.clearTimeout(hideTimer.current);
    setExiting(true);
    hideTimer.current = window.setTimeout(() => {
      setHidden(true);
      finishRef.current?.();
    }, 450);
  };

  return (
    <div
      className={`splash-overlay ${exiting ? "splash-exit" : ""}`}
      role="status"
      aria-label="Loading SILLA"
    >
      {/* Animated Ambient Orbs matching SILLA Logo colors */}
      <div className="splash-orb orb-1" />
      <div className="splash-orb orb-2" />
      <div className="splash-orb orb-3" />

      {/* Modern Floating Culinary Badges */}
      <div className="splash-float-icon icon-a">
        <Soup size={26} strokeWidth={1.9} />
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
        <div className="splash-food-scene" aria-hidden="true">
          <svg viewBox="0 0 360 220" role="presentation">
            <g className="splash-plate splash-plate-left">
              <circle cx="92" cy="111" r="63" />
              <circle className="plate-well" cx="92" cy="111" r="47" />
              <circle className="plate-food food-green" cx="92" cy="111" r="29" />
              <path className="food-leaf" d="M75 112c9-22 26-18 33-4-10 15-24 19-33 4Zm16 11c5-13 14-18 24-18" />
              <circle className="food-dot" cx="83" cy="101" r="3" />
              <circle className="food-dot" cx="105" cy="119" r="3" />
            </g>
            <g className="splash-plate splash-plate-center">
              <circle cx="180" cy="92" r="76" />
              <circle className="plate-well" cx="180" cy="92" r="57" />
              <circle className="plate-food food-orange" cx="180" cy="92" r="39" />
              <path className="food-pasta" d="M151 89c13-23 42-16 51-2s-4 30-22 26-32-3-29-24Zm13-14c12 3 19 10 24 22m-29 12c12-8 27-9 39-2" />
              <circle className="food-dot" cx="169" cy="82" r="3" />
              <circle className="food-dot" cx="193" cy="103" r="3" />
            </g>
            <g className="splash-plate splash-plate-right">
              <circle cx="274" cy="121" r="57" />
              <circle className="plate-well" cx="274" cy="121" r="42" />
              <circle className="plate-food food-red" cx="274" cy="121" r="25" />
              <path className="food-leaf" d="M260 122c7-17 20-14 27-4-8 12-19 15-27 4Zm14 9c4-10 11-14 19-14" />
              <circle className="food-dot" cx="267" cy="112" r="2.5" />
            </g>
          </svg>
        </div>
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
        <button className="splash-skip" type="button" onClick={dismiss}>
          Continue
        </button>
      </div>
    </div>
  );
}

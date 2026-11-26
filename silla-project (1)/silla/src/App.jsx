import { useState } from "react";
import { Link, NavLink, Route, Routes } from "react-router-dom";
import { Home as HomeIcon, BookOpen, ShoppingCart, UtensilsCrossed, Archive, Globe } from "lucide-react";
import Home from "./pages/Home";
import Recipes from "./pages/Recipes";
import RecipeDetail from "./pages/RecipeDetail";
import Cook from "./pages/Cook";
import Pantry from "./pages/Pantry";
import Cart from "./pages/Cart";
import SplashScreen from "./components/SplashScreen";
import { useSilla } from "./context";

export default function App() {
  const { cart, lang, setLang, backendReady } = useSilla();
  const [showSplash, setShowSplash] = useState(true);

  return (
    <>
      {showSplash && <SplashScreen onFinish={() => setShowSplash(false)} />}

      {/* Ambient Animated Background Shapes */}
      <div className="bg-shapes" aria-hidden="true">
        <span className="bg-blob blob-1" />
        <span className="bg-blob blob-2" />
      </div>

      <header className="nav">
        <Link to="/" className="logo" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <img
            src="/images/silla-logo.jpg"
            alt="SILLA"
            className="nav-brand-logo"
          />
          <span>SILLA</span>
          {backendReady && (
            <span className="live-pill">
              <span className="live-dot" />
              LIVE
            </span>
          )}
        </Link>
        <nav aria-label="Main">
          <NavLink to="/" end className="nav-pill-link">
            <HomeIcon size={17} strokeWidth={2.2} />
            <span>{lang === "ar" ? "الرئيسية" : "Home"}</span>
          </NavLink>
          <NavLink to="/recipes" className="nav-pill-link">
            <BookOpen size={17} strokeWidth={2.1} />
            <span>{lang === "ar" ? "الأكلات" : "Recipes"}</span>
          </NavLink>
          <NavLink to="/cook" className="nav-pill-link">
            <UtensilsCrossed size={17} strokeWidth={2.1} />
            <span>{lang === "ar" ? "المساعد الذكي" : "Let's Cook"}</span>
          </NavLink>
          <NavLink to="/pantry" className="nav-pill-link">
            <Archive size={17} strokeWidth={2.1} />
            <span>{lang === "ar" ? "مخزوني" : "My Pantry"}</span>
          </NavLink>
        </nav>
        <div className="nav-right">
          <button
            className="lang"
            onClick={() => setLang(lang === "en" ? "ar" : "en")}
            style={{ display: "inline-flex", alignItems: "center", gap: "5px" }}
          >
            <Globe size={14} strokeWidth={2.2} />
            {lang === "en" ? "عربي" : "EN"}
          </button>
          <Link
            to="/cart"
            className="cart-link"
            aria-label={`Cart, ${cart.length} items`}
            style={{ display: "inline-flex", alignItems: "center" }}
          >
            <ShoppingCart size={22} strokeWidth={2.1} color="var(--green)" />
            <span className="count">{cart.length}</span>
          </Link>
        </div>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/recipes" element={<Recipes />} />
          <Route path="/recipe/:id" element={<RecipeDetail />} />
          <Route path="/cook" element={<Cook />} />
          <Route path="/pantry" element={<Pantry />} />
          <Route path="/cart" element={<Cart />} />
        </Routes>
      </main>
    </>
  );
}

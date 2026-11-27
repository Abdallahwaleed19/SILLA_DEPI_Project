import { Link, NavLink, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Recipes from "./pages/Recipes";
import RecipeDetail from "./pages/RecipeDetail";
import Cook from "./pages/Cook";
import Pantry from "./pages/Pantry";
import Cart from "./pages/Cart";
import { useSilla } from "./context";

export default function App() {
  const { cart, lang, setLang } = useSilla();
  return (
    <>
      <header className="nav">
        <Link to="/" className="logo">SILLA</Link>
        <nav aria-label="Main">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/recipes">Recipes</NavLink>
          <NavLink to="/cook">Let's Cook</NavLink>
          <NavLink to="/pantry">My Pantry</NavLink>
        </nav>
        <div className="nav-right">
          <button className="lang" onClick={() => setLang(lang === "en" ? "ar" : "en")}>{lang === "en" ? "عربي" : "EN"}</button>
          <Link to="/cart" className="cart-link" aria-label={`Cart, ${cart.length} items`}>🛒<span className="count">{cart.length}</span></Link>
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

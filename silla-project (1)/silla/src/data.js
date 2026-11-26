export const STORES = ["Carrefour", "Spinneys", "Metro"];
// p(en, ar, packSize, unit, [price per store], substituteId, [storesOutOfStock])
const p = (en, ar, pack, unit, pr, sub, out = []) =>
  ({ en, ar, pack, unit, sub, out, price: Object.fromEntries(STORES.map((s, i) => [s, pr[i]])) });

export const P = {
  macaroni: p("Macaroni", "مكرونة", 500, "g", [30, 34, 28]),
  mince: p("Minced meat", "لحمة مفرومة", 500, "g", [180, 195, 175]),
  milk: p("Milk", "لبن", 1000, "ml", [40, 44, 38]),
  flour: p("Flour", "دقيق", 1000, "g", [28, 30, 26]),
  butter: p("Butter", "زبدة", 100, "g", [35, 38, 33], "oil"),
  oil: p("Cooking oil", "زيت", 500, "ml", [25, 28, 24]),
  mozzarella: p("Mozzarella", "موتزاريلا", 200, "g", [75, 80, 72], "roumi", ["Spinneys"]),
  roumi: p("Roumi cheese", "جبنة رومي", 250, "g", [55, 60, 52]),
  salt: p("Salt", "ملح", 700, "g", [8, 9, 7]),
  rice: p("Rice", "رز", 1000, "g", [38, 42, 36]),
  lentils: p("Lentils", "عدس", 500, "g", [30, 33, 29]),
  chickpeas: p("Chickpeas", "حمص", 500, "g", [32, 35, 30]),
  tomatosauce: p("Tomato sauce", "صلصة", 400, "ml", [15, 17, 14]),
  onion: p("Onion", "بصل", 1000, "g", [20, 24, 18]),
  garlic: p("Garlic", "ثوم", 100, "g", [10, 12, 9]),
  molokhia: p("Molokhia", "ملوخية", 400, "g", [25, 28, 24], null, ["Metro"]),
  chicken: p("Chicken", "فراخ", 1000, "g", [95, 105, 90]),
};

export const RECIPES = [
  { id: "bechamel", photo: "/images/bechamel.jpg", emoji: "🍲", cat: "Pasta", steps: ["Boil the macaroni until al dente, then drain.", "Brown the minced meat with salt.", "Make the béchamel: melt butter, stir in flour, then add milk slowly until thick.", "Layer macaroni, meat and sauce, top with mozzarella and bake until golden."], en: "Macaroni béchamel", ar: "مكرونة بشاميل", servings: 4, veg: false,
    alias: "pasta bechamel baked macaroni", ing: { macaroni: 500, mince: 500, milk: 1000, flour: 100, butter: 100, mozzarella: 200, salt: 5 } },
  { id: "koshari", photo: "/images/Authentic Egyptian Kushari 🇪🇬.jpg", emoji: "🍚", cat: "Vegetarian", steps: ["Cook rice, lentils and macaroni separately.", "Simmer tomato sauce with garlic and salt.", "Fry sliced onions in oil until crisp.", "Layer everything in a bowl and top with chickpeas and sauce."], en: "Koshari", ar: "كشري", servings: 4, veg: true,
    alias: "kushari koshary", ing: { rice: 300, lentils: 200, macaroni: 200, chickpeas: 200, tomatosauce: 400, onion: 500, oil: 100, salt: 5 } },
  { id: "molokhia", photo:"/images/32 Egyptian Foods Worth Trying.jpg", emoji: "🥣", cat: "Classics", steps: ["Simmer the chicken until tender and keep the broth.", "Fry garlic until golden.", "Add molokhia to the hot broth, then stir in the garlic.", "Serve over rice."], en: "Molokhia", ar: "ملوخية", servings: 4, veg: false,
    alias: "mulukhiyah jute chicken", ing: { molokhia: 400, chicken: 800, garlic: 50, rice: 300, salt: 5 } },
  { id: "hawawshi", photo:"/images/hawawshi.jpg", emoji: "🥙", cat: "Street food", steps: ["Knead flour, oil and salt into a dough and rest it.", "Mix minced meat with chopped onion and salt.", "Stuff the dough with the meat mix.", "Bake until crisp and golden."], en: "Hawawshi", ar: "حواوشي", servings: 4, veg: false,
    alias: "hawawshy stuffed bread meat", ing: { flour: 500, mince: 600, onion: 300, oil: 50, salt: 5 } },
];

export const UI = {
  en: { tag: "From cravings to cart.", ph: "I want macaroni béchamel for four people, budget 300 EGP", find: "Find recipes",
    plan: "Plan", cart: "Cart", kitchen: "My kitchen", about: "About", add: "Add to plan", all: "All", veg: "Vegetarian",
    picks: "Picks for your budget", fits: "fits budget", total: "Total", budget: "Budget (EGP)", saver: "Budget saver (cheaper swaps)",
    mix: "Cheapest mix", compare: "Compare stores", swap: "swapped", out: "out of stock", over: "over budget by", left: "left in budget",
    empty: "Nothing here yet. Add a recipe first.", serves: "Serves", remove: "Remove", noMatch: "No recipe matched. Try a dish name." },
  ar: { tag: "من الشهوة للعربة.", ph: "عايز أعمل مكرونة بشاميل لـ 4 أشخاص، الميزانية 300 جنيه", find: "ابحث عن وصفة",
    plan: "الخطة", cart: "السلة", kitchen: "مطبخي", about: "عن سيلا", add: "أضف للخطة", all: "الكل", veg: "نباتي",
    picks: "اختيارات تناسب ميزانيتك", fits: "ضمن الميزانية", total: "الإجمالي", budget: "الميزانية (جنيه)", saver: "توفير (بدائل أرخص)",
    mix: "الأرخص من كل المتاجر", compare: "قارن المتاجر", swap: "بديل", out: "غير متوفر", over: "تتجاوز الميزانية بـ", left: "متبقي من الميزانية",
    empty: "لا شيء بعد. أضف وصفة أولاً.", serves: "عدد الأفراد", remove: "حذف", noMatch: "لا توجد وصفة مطابقة. جرّب اسم طبق." },
};

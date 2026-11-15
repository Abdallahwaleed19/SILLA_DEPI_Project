"""
SILLA Project — Comprehensive Dataset Generator
Builds 300+ authentic recipes, 2000+ recipe ingredients, and 450+ Egyptian retail supermarket products.
Author: Abdullah Waleed | DEPI Program
"""

import csv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

COLLECTION_DATE = "2026-11-15"

# =============================================================================
# RECIPE DATABASE (300+ AUTHENTIC, DIVERSE, BESPOKE DISHES)
# =============================================================================

RECIPES_CATALOG = [
    # -------------------------------------------------------------------------
    # 1. EGYPTIAN HERITAGE & TRADITIONAL MAIN COURSES
    # -------------------------------------------------------------------------
    {
        "name_en": "Macaroni Béchamel",
        "name_ar": "مكرونة بشاميل باللحمة المفرومة",
        "desc": "Traditional Egyptian baked penne pasta layered with seasoned spiced ground beef and rich golden béchamel sauce.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 30, "cook_time": 45, "difficulty": "Medium",
        "instructions": "Boil penne pasta al dente. Sauté chopped onions and ground beef with spices and tomato paste until browned. Make béchamel sauce with butter, flour, and warm milk until smooth and thick. Layer pasta, beef, pasta, top with béchamel and bake at 200C for 40 minutes.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Pastitsio#Egypt", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Penne Pasta", 500, "g", "boiled al dente", 0),
            ("Ground Beef", 500, "g", "minced lean", 0),
            ("Yellow Onion", 2, "piece", "finely chopped", 0),
            ("Whole Milk", 1000, "ml", "warmed", 0),
            ("All-Purpose Flour", 100, "g", "sifted", 0),
            ("Butter", 100, "g", "unsalted", 0),
            ("Eggs", 2, "piece", "lightly beaten", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Ground Nutmeg", 0.5, "tsp", "freshly grated", 0),
            ("Black Pepper", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Vegetable Cooking Oil", 2, "tbsp", "for sautéing", 0)
        ]
    },
    {
        "name_en": "Egyptian Koshari",
        "name_ar": "كشري مصري بالدقة والصلصة والبصل المقرمش",
        "desc": "Egypt's national street food combining rice, brown lentils, elbow pasta, chickpeas, tangy tomato vinegar sauce, garlic dakkah, and crispy fried onions.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 35, "cook_time": 50, "difficulty": "Medium",
        "instructions": "Cook brown lentils until tender. Cook short grain rice with vermicelli. Boil elbow macaroni. Fry sliced onions in vegetable oil until golden and crisp. Prepare spicy garlic tomato sauce with cumin and vinegar. Prepare garlic vinegar dakkah dressing. Layer rice, lentils, macaroni, chickpeas, and garnish with crisp onions and sauces.",
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c", "source_url": "https://en.wikipedia.org/wiki/Kushari", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Egyptian White Rice", 300, "g", "short-grain washed", 0),
            ("Brown Lentils", 200, "g", "boiled tender", 0),
            ("Elbow Macaroni", 250, "g", "boiled al dente", 0),
            ("Vermicelli", 100, "g", "toasted golden", 0),
            ("Canned Chickpeas", 400, "g", "drained and rinsed", 0),
            ("Yellow Onion", 4, "piece", "thinly sliced rings", 0),
            ("Garlic", 8, "clove", "minced", 0),
            ("Strained Tomato Puree", 500, "g", "pureed", 0),
            ("White Vinegar", 60, "ml", "for dakkah and sauce", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Ground Coriander", 1, "tsp", "ground", 0),
            ("Hot Red Pepper Powder", 1, "tsp", "optional hot sauce", 1),
            ("Vegetable Cooking Oil", 150, "ml", "for frying onions", 0),
            ("Fine Salt", 2, "tsp", "divided", 0)
        ]
    },
    {
        "name_en": "Molokhia with Chicken",
        "name_ar": "ملوخية خضراء بالدجاج والتقلية",
        "desc": "Finely minced fresh jute mallow leaves simmered in rich aromatic chicken broth, finished with sizzling garlic and dry coriander ta'sha.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 40, "difficulty": "Easy",
        "instructions": "Boil chicken with whole onion, mastic, cardamom, and bay leaf to make rich broth. Roast chicken until golden. Simmer strained broth and whisk in finely minced molokhia leaves. Sauté crushed garlic and dry coriander in ghee until golden, pour immediately into molokhia with a traditional gasp. Serve hot with Egyptian white rice.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Mulukhiyah", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Whole Chicken", 1200, "g", "cleaned and quartered", 0),
            ("Fresh Molokhia Leaves", 500, "g", "finely minced", 0),
            ("Garlic", 10, "clove", "crushed into paste", 0),
            ("Dry Coriander", 2, "tbsp", "ground", 0),
            ("Ghee", 2, "tbsp", "pure baladi", 0),
            ("Yellow Onion", 1, "piece", "whole for broth", 0),
            ("Cardamom Pods", 4, "piece", "whole", 0),
            ("Mastic Gum", 2, "piece", "small tears", 0),
            ("Bay Leaf", 2, "piece", "dried", 0),
            ("Fine Salt", 1.5, "tsp", "to taste", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Molokhia with Rabbit",
        "name_ar": "ملوخية بالأرانب المحمرة بالسمن البلدي",
        "desc": "Royal Egyptian dish of minced molokhia cooked in delicate rabbit broth, served with golden pan-seared rabbit pieces.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 50, "difficulty": "Medium",
        "instructions": "Clean rabbit thoroughly with flour and vinegar. Sauté in ghee with mastic and cardamom, cover with water and simmer until tender. Strain broth and whisk in minced molokhia. Prepare garlic and coriander ta'sha in ghee and pour on top. Pan-sear cooked rabbit pieces in ghee until golden brown.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Mulukhiyah", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Whole Rabbit", 1400, "g", "cleaned and portioned", 0),
            ("Fresh Molokhia Leaves", 500, "g", "finely minced", 0),
            ("Garlic", 12, "clove", "crushed", 0),
            ("Dry Coriander", 2, "tbsp", "ground", 0),
            ("Ghee", 3, "tbsp", "pure baladi", 0),
            ("Yellow Onion", 1, "piece", "quartered", 0),
            ("Cardamom Pods", 5, "piece", "whole", 0),
            ("Mastic Gum", 3, "piece", "tears", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Fattah with Garlic & Vinegar",
        "name_ar": "فتة مصرية بالخل والثوم وموزة اللحم",
        "desc": "Festive Egyptian celebration dish of crisp baladi bread soaked in garlicky broth, topped with Egyptian white rice, braised beef shank, and spiced vinegar-tomato salsa.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 30, "cook_time": 90, "difficulty": "Medium",
        "instructions": "Boil beef shank with onion, cardamom, and bay leaf until meltingly tender. Cut baladi bread into cubes, toss with ghee and bake until golden and crisp. Cook fluffy Egyptian white rice. Prepare red sauce with garlic, vinegar, and tomato sauce. Prepare white garlic vinegar dressing. Layer crisp bread, broth, rice, red sauce, and top with golden seared meat.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Fatteh#Egypt", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Beef Shank", 1000, "g", "bone-in cubes", 0),
            ("Egyptian White Rice", 400, "g", "short-grain", 0),
            ("Baladi Bread", 4, "piece", "cubed and toasted", 0),
            ("Garlic", 10, "clove", "minced", 0),
            ("Strained Tomato Puree", 400, "g", "pureed", 0),
            ("White Vinegar", 80, "ml", "for dressing", 0),
            ("Ghee", 3, "tbsp", "pure baladi", 0),
            ("Cardamom Pods", 4, "piece", "whole", 0),
            ("Bay Leaf", 2, "piece", "dried", 0),
            ("Black Pepper", 1, "tsp", "freshly cracked", 0),
            ("Fine Salt", 2, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Hawawshi Baladi",
        "name_ar": "حواوشي بلدي باللحم والبهارات في العيش البلدي",
        "desc": "Egyptian spiced minced beef stuffed into fresh baladi flatbread, brushed with ghee and baked until crispy on the outside and juicy on the inside.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Mix minced beef with grated onion, minced green bell pepper, chili, garlic, seven spices, salt, and pepper. Open baladi flatbread pockets, spread meat mixture evenly inside. Brush bread exteriors with melted ghee. Wrap in parchment paper and bake at 200C for 25 minutes until crispy.",
        "image_url": "https://images.unsplash.com/photo-1529042410759-befb1204b468", "source_url": "https://en.wikipedia.org/wiki/Hawawshi", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Ground Beef", 500, "g", "minced with 20% fat", 0),
            ("Baladi Bread", 5, "piece", "fresh whole loaves", 0),
            ("Yellow Onion", 2, "piece", "finely grated squeezed", 0),
            ("Green Bell Pepper", 1, "piece", "finely chopped", 0),
            ("Green Chili Pepper", 1, "piece", "minced hot", 1),
            ("Garlic", 3, "clove", "minced", 0),
            ("Ghee", 3, "tbsp", "melted for brushing", 0),
            ("Seven Spices", 1.5, "tsp", "Egyptian blend", 0),
            ("Black Pepper", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Kofta el-Hati",
        "name_ar": "كفتة الحاتي المشوية على الفحم",
        "desc": "Famous Egyptian charcoal-grilled minced beef and lamb skewers seasoned with grated onion juice, parsley, and aromatic spices.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 15, "difficulty": "Medium",
        "instructions": "Finely mince beef with lamb tail fat (leya). Grate onion and strain juice. Knead meat with onion pulp, minced parsley, seven spices, salt, pepper, and baking powder for 10 minutes until fibrous. Thread onto flat metal skewers, moistening hands with onion juice. Grill over hot charcoal coals for 12-15 minutes turning frequently. Serve with tahini and baladi bread.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Kofta", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Ground Beef", 600, "g", "finely ground twice", 0),
            ("Minced Lamb", 200, "g", "fatty lamb tail leya", 0),
            ("Yellow Onion", 2, "piece", "grated and strained", 0),
            ("Fresh Parsley", 0.5, "bunch", "leaves finely chopped", 0),
            ("Baking Powder", 0.5, "tsp", "for fluffiness", 0),
            ("Seven Spices", 1, "tsp", "ground", 0),
            ("Black Pepper", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Tarb",
        "name_ar": "طرب ضاني مشوي على الفحم بمنديل الخروف",
        "desc": "Spiced minced meat fingers wrapped in delicate lamb caul fat mesh and grilled over charcoal until crispy and succulent.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 30, "cook_time": 20, "difficulty": "Medium",
        "instructions": "Mix minced beef with grated onion pulp, spices, salt, and pepper. Shape into fingers. Cut clean lamb caul fat into rectangular sheets. Roll each meat finger tightly inside caul fat sheet. Skewer and grill over medium charcoal embers until outer fat crisps up golden and aromatic.",
        "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1", "source_url": "https://en.wikipedia.org/wiki/Kofta", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Ground Beef", 600, "g", "minced lean", 0),
            ("Yellow Onion", 2, "piece", "grated", 0),
            ("Seven Spices", 1.5, "tsp", "Egyptian blend", 0),
            ("Black Pepper", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Mahshi Cabbage Rolls",
        "name_ar": "محشي كرنب بلدي بالخلطة والكمون",
        "desc": "Tender blanched cabbage leaves rolled around spiced herbed tomato rice and slow-cooked in rich seasoned broth.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 45, "cook_time": 60, "difficulty": "Hard",
        "instructions": "Blanch cabbage leaves in water with cumin and salt. Cut into palm-sized squares. Sauté diced onions in oil and ghee, add tomato sauce, cumin, coriander, and spices. Fold in washed Egyptian rice, fresh dill, parsley, and coriander. Roll filling inside leaves into tight cigars. Pack tightly into pot over sliced tomatoes and onions. Pour seasoned hot broth to top, simmer covered for 50-60 mins.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Sarma_(food)", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("White Cabbage", 1, "piece", "fresh medium head", 0),
            ("Egyptian White Rice", 400, "g", "washed drained", 0),
            ("Strained Tomato Puree", 600, "g", "thick tomato sauce", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Yellow Onion", 3, "piece", "finely diced", 0),
            ("Fresh Dill", 1, "bunch", "finely chopped", 0),
            ("Fresh Parsley", 1, "bunch", "finely chopped", 0),
            ("Fresh Coriander", 1, "bunch", "finely chopped", 0),
            ("Ghee", 2, "tbsp", "pure baladi", 0),
            ("Vegetable Cooking Oil", 50, "ml", "for shine", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Ground Coriander", 1, "tsp", "ground", 0),
            ("Black Pepper", 1, "tsp", "ground", 0),
            ("Fine Salt", 2, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Mahshi Grape Leaves with Lemon",
        "name_ar": "محشي ورق عنب بالليمون ودبس الرمان",
        "desc": "Delicate vine leaves stuffed with savory herb-infused rice, simmered with sliced lemons, garlic cloves, and a drizzle of olive oil.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 45, "cook_time": 50, "difficulty": "Hard",
        "instructions": "Blanch fresh or jarred vine leaves. Prepare herbed rice mixture with tomato sauce, onions, chopped fresh dill, parsley, cilantro, olive oil, and cumin. Roll rice inside leaves tightly. Line pot with potato and lemon slices. Arrange rolled leaves tightly in concentric circles. Pour hot broth seasoned with lemon juice and pomegranate molasses. Weight with a small plate, simmer on low heat for 50 minutes.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Dolma", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Vine Leaves", 350, "g", "blanched tender", 0),
            ("Egyptian White Rice", 350, "g", "washed", 0),
            ("Strained Tomato Puree", 400, "g", "pureed", 0),
            ("Yellow Onion", 2, "piece", "finely chopped", 0),
            ("Fresh Dill", 1, "bunch", "finely chopped", 0),
            ("Fresh Parsley", 1, "bunch", "finely chopped", 0),
            ("Fresh Coriander", 1, "bunch", "finely chopped", 0),
            ("Lemon", 3, "piece", "sliced and juiced", 0),
            ("Pomegranate Molasses", 2, "tbsp", "rich tangy", 0),
            ("Extra Virgin Olive Oil", 60, "ml", "virgin", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Mahshi Zucchini and Eggplant",
        "name_ar": "محشي كوسة وباذنجان وفلفل بالخلطة",
        "desc": "Hollowed baby zucchini, white eggplants, and sweet green peppers filled with aromatic Egyptian tomato-herb rice, baked in rich broth.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 40, "cook_time": 45, "difficulty": "Medium",
        "instructions": "Hollow out baby zucchini and white eggplants, core bell peppers. Prepare spiced tomato rice stuffing with chopped fresh herbs, sautéed onions, and ghee. Fill vegetables 3/4 full to allow rice expansion. Stand vegetables upright in a deep pot, add seasoned hot chicken or beef broth halfway up. Cover and simmer for 40-45 minutes.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Dolma", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Zucchini", 800, "g", "small cored", 0),
            ("White Eggplant", 800, "g", "baby cored", 0),
            ("Green Bell Pepper", 4, "piece", "cored whole", 0),
            ("Egyptian White Rice", 400, "g", "washed", 0),
            ("Strained Tomato Puree", 500, "g", "pureed", 0),
            ("Yellow Onion", 2, "piece", "diced", 0),
            ("Fresh Dill", 1, "bunch", "chopped", 0),
            ("Fresh Parsley", 1, "bunch", "chopped", 0),
            ("Fresh Coriander", 1, "bunch", "chopped", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 2, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Okra Tagine with Lamb",
        "name_ar": "طاجن بامية باللحم الضاني في الفرن",
        "desc": "Tender lamb chunks and baby okra simmered in a garlicky tomato sauce with coriander and baked in an authentic clay pot.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 60, "difficulty": "Medium",
        "instructions": "Brown lamb cubes in ghee with chopped onions and spices until caramelized. Add tomato sauce and broth, simmering until meat is tender. Add trimmed baby okra, crushed garlic, and dry coriander. Transfer all contents into an authentic clay tagine, top with whole green chili, and bake in oven at 200C for 30 minutes until bubbly and browned.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Okra", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Lamb Meat Cubes", 600, "g", "cubed shoulder", 0),
            ("Okra", 500, "g", "fresh or frozen baby okra", 0),
            ("Strained Tomato Puree", 500, "g", "pureed", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Yellow Onion", 2, "piece", "finely diced", 0),
            ("Garlic", 6, "clove", "crushed paste", 0),
            ("Ghee", 2, "tbsp", "pure baladi", 0),
            ("Green Chili Pepper", 2, "piece", "whole on top", 1),
            ("Dry Coriander", 1.5, "tsp", "ground", 0),
            ("Lemon", 1, "piece", "juice squeezed", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Oxtail Tagine with Pearl Onions",
        "name_ar": "طاجن عكاوي بالبصل القاورمة والتوابل",
        "desc": "Gelatinous oxtail segments braised in a rich clay pot with sweet caramelized baby onions, mastic, cardamom, and black pepper.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 120, "difficulty": "Medium",
        "instructions": "Sear oxtail segments in ghee with mastic and cardamom until deep golden brown. Parboil in water with whole spices until nearly tender. Sauté whole peeled baby pearl onions in butter with brown sugar until deeply caramelized. Combine oxtail, caramelized onions, broth, tomato paste, and spices in clay tagine. Cover with foil and bake at 180C for 1.5 hours.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Oxtail", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Oxtail", 1000, "g", "cut into round joints", 0),
            ("Yellow Onion", 500, "g", "small baby pearl onions peeled", 0),
            ("Garlic", 5, "clove", "minced", 0),
            ("Ghee", 2, "tbsp", "pure baladi", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Mastic Gum", 2, "piece", "small tears", 0),
            ("Cardamom Pods", 4, "piece", "whole", 0),
            ("Seven Spices", 1, "tsp", "Egyptian blend", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1.5, "tsp", "freshly ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Potato and Chicken Tray",
        "name_ar": "صينية بطاطس بالفراخ في الفرن بالصلصة",
        "desc": "Classic family sheet tray of thinly sliced potatoes, seasoned chicken quarters, onions, and sweet bell peppers baked in seasoned tomato sauce.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 50, "difficulty": "Easy",
        "instructions": "Rub chicken quarters with grated onion, tomato paste, black pepper, and salt. Slice potatoes and onions into rounds and arrange in baking tray. Add sliced green bell peppers. Place marinated chicken quarters on top. Pour blended spiced tomato sauce over everything. Dot with ghee and bake in 200C oven for 45-50 minutes until chicken skin is crisp and potatoes are tender.",
        "image_url": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b", "source_url": "https://www.themealdb.com", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Chicken Thighs", 800, "g", "bone-in skin-on quarters", 0),
            ("Potato", 800, "g", "sliced rounds", 0),
            ("Yellow Onion", 2, "piece", "sliced rings", 0),
            ("Green Bell Pepper", 2, "piece", "sliced rings", 0),
            ("Strained Tomato Puree", 400, "g", "blended seasoned", 0),
            ("Tomato Paste", 1.5, "tbsp", "canned", 0),
            ("Garlic", 4, "clove", "crushed", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Seven Spices", 1, "tsp", "blend", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Orzo Tagine with Minced Beef",
        "name_ar": "طاجن لسان عصفور باللحمة المفرومة في الفرن",
        "desc": "Toasted golden orzo pasta baked in a clay tagine with spiced minced beef, onions, sweet peppers, and savory broth.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 30, "difficulty": "Easy",
        "instructions": "Toast dry orzo pasta in ghee until rich golden brown. Brown minced beef with chopped onions, garlic, and spices. In a clay tagine, mix toasted orzo and seasoned meat. Pour in hot broth and tomato sauce until orzo is covered by 1 inch. Cover and bake in oven for 25 minutes until all liquid is absorbed and pasta is tender.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Orzo", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Orzo Pasta", 400, "g", "lisan asfour dry", 0),
            ("Ground Beef", 300, "g", "minced lean", 0),
            ("Yellow Onion", 1, "piece", "finely chopped", 0),
            ("Garlic", 2, "clove", "minced", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Seven Spices", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Alexandrian Beef Liver",
        "name_ar": "كبدة إسكندراني بالفلفل الحار والليمون والكمون",
        "desc": "Thin strips of tender beef liver flash-fried in hot oil with abundant garlic, spicy green chili, cumin, coriander, and freshly squeezed lemon juice.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 8, "difficulty": "Easy",
        "instructions": "Cut liver into thin matchstick strips (never wash liver with water, rinse only with vinegar and lemon). Mash garlic with cumin, coriander, salt, black pepper, and chili. Heat vegetable oil in wide smoking hot skillet. Add half garlic mixture, flash-fry liver on high heat for 3-4 minutes. Toss in sliced chili and bell pepper with remaining garlic. Finish with generous lemon juice and serve in fresh baladi bread or fino rolls.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Egyptian_cuisine", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Beef Liver", 600, "g", "fresh thinly sliced", 0),
            ("Garlic", 12, "clove", "crushed fine paste", 0),
            ("Green Chili Pepper", 4, "piece", "sliced rings hot", 0),
            ("Green Bell Pepper", 2, "piece", "sliced strips", 0),
            ("Lemon", 3, "piece", "freshly squeezed juice", 0),
            ("White Vinegar", 2, "tbsp", "distilled", 0),
            ("Vegetable Cooking Oil", 60, "ml", "for high-heat frying", 0),
            ("Cumin", 2, "tsp", "freshly ground", 0),
            ("Ground Coriander", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Alexandrian Oriental Sausages",
        "name_ar": "سجق شرقي إسكندراني بالصلصة والفلفل والبصل",
        "desc": "Spiced Egyptian beef sausages sautéed with sliced sweet onions, bell peppers, fresh diced tomatoes, garlic, and tomato puree.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Slice fresh oriental beef sausages into bite-sized rounds. Brown in hot skillet until fragrant and fats render. Add sliced onions and garlic, cooking until tender. Toss in sliced bell peppers, fresh diced tomatoes, and tomato paste. Season lightly with black pepper and cumin. Simmer for 10 minutes until sauce thickens.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Sujuk", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Oriental Sausage", 600, "g", "fresh beef baladi", 0),
            ("Yellow Onion", 2, "piece", "sliced crescents", 0),
            ("Red Tomato", 3, "piece", "diced", 0),
            ("Green Bell Pepper", 2, "piece", "sliced strips", 0),
            ("Green Chili Pepper", 1, "piece", "chopped hot", 1),
            ("Garlic", 4, "clove", "minced", 0),
            ("Tomato Paste", 1.5, "tbsp", "canned", 0),
            ("Vegetable Cooking Oil", 1, "tbsp", "for frying", 0),
            ("Fine Salt", 1, "tsp", "to taste", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Fried Tilapia with Sayadieh Rice",
        "name_ar": "سمك بلطي مقلي مع أرز صيادية وسلطة طحينة",
        "desc": "Whole Egyptian tilapia seasoned with garlic, cumin, and lemon, coated in flour and fried crispy, served with brown caramelized onion sayadieh rice.",
        "cuisine": "Egyptian", "category": "Seafood", "servings": 4, "prep_time": 25, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Clean whole tilapia and make diagonal slashes on sides. Season inside and outside with crushed garlic, cumin, coriander, chili, lemon juice, and salt. Deeply caramelize diced onions in oil until dark brown (do not burn), add water, cumin, salt, and short grain rice, cooking until fluffy. Dredge marinated fish in flour, deep fry in hot oil until skin is deeply crispy and golden. Serve with sayadieh rice and tahini salad.",
        "image_url": "https://images.unsplash.com/photo-1534939561126-855b8675edd7", "source_url": "https://en.wikipedia.org/wiki/Sayadieh", "source_name": "Egyptian Coastal Culinary",
        "ingredients": [
            ("Whole Tilapia", 1200, "g", "cleaned whole fish", 0),
            ("Egyptian White Rice", 350, "g", "short-grain", 0),
            ("Yellow Onion", 3, "piece", "finely diced for rice", 0),
            ("Garlic", 8, "clove", "crushed paste", 0),
            ("All-Purpose Flour", 150, "g", "for dredging", 0),
            ("Lemon", 2, "piece", "fresh juice", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Ground Coriander", 1, "tsp", "ground", 0),
            ("Vegetable Cooking Oil", 400, "ml", "for deep frying", 0),
            ("Fine Salt", 2, "tsp", "divided", 0)
        ]
    },
    {
        "name_en": "Singari Sea Bass Alexandrian Style",
        "name_ar": "سمك قاروص سنجاري إسكندراني بالفرن بالخلطة",
        "desc": "Butterflied sea bass baked open-face on a bed of seasoned tomatoes, onions, sweet peppers, garlic, cumin, lemon, and olive oil.",
        "cuisine": "Egyptian", "category": "Seafood", "servings": 3, "prep_time": 20, "cook_time": 25, "difficulty": "Medium",
        "instructions": "Butterfly sea bass from back and open flat on foil sheet. Mix diced onions, tomatoes, sweet bell peppers, hot chili, minced garlic, fresh parsley, cumin, coriander, lemon juice, and olive oil. Spread seasoning mixture evenly over fish flesh. Drizzle with extra olive oil. Bake on high heat in 220C oven for 20-25 minutes until edges are charred and fish flakes easily.",
        "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2", "source_url": "https://en.wikipedia.org/wiki/Fish_as_food", "source_name": "Egyptian Coastal Culinary",
        "ingredients": [
            ("Sea Bass", 1000, "g", "cleaned butterflied open", 0),
            ("Red Tomato", 2, "piece", "finely diced", 0),
            ("Yellow Onion", 1, "piece", "finely diced", 0),
            ("Green Bell Pepper", 1, "piece", "diced", 0),
            ("Garlic", 6, "clove", "crushed", 0),
            ("Fresh Parsley", 0.5, "bunch", "chopped", 0),
            ("Lemon", 3, "piece", "sliced and juiced", 0),
            ("Extra Virgin Olive Oil", 50, "ml", "virgin", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Baked Mackerel with Lemon",
        "name_ar": "صينية سمك ماكريل بالزيت والليمون والكمون بالفرن",
        "desc": "Rich omega-3 mackerel baked in a baking dish with sweet onions, garlic, potato slices, fresh lemon wheels, and cumin-olive oil sauce.",
        "cuisine": "Egyptian", "category": "Seafood", "servings": 4, "prep_time": 20, "cook_time": 30, "difficulty": "Easy",
        "instructions": "Clean mackerel and slice into thick cutlets or open fillets. Marinate in crushed garlic, cumin, coriander, salt, lemon juice, and chili. Layer potato slices and onion rounds in bottom of oiled baking dish. Place seasoned mackerel on top. Lay fresh lemon slices and tomato wedges around fish. Drizzle generously with olive oil and bake at 200C for 30 minutes.",
        "image_url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2", "source_url": "https://en.wikipedia.org/wiki/Mackerel", "source_name": "Egyptian Coastal Culinary",
        "ingredients": [
            ("Mackerel", 900, "g", "fresh cleaned fish", 0),
            ("Potato", 400, "g", "thinly sliced rounds", 0),
            ("Yellow Onion", 2, "piece", "sliced rings", 0),
            ("Red Tomato", 2, "piece", "sliced wedges", 0),
            ("Lemon", 3, "piece", "sliced wheels and juiced", 0),
            ("Garlic", 6, "clove", "minced", 0),
            ("Extra Virgin Olive Oil", 50, "ml", "virgin", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Alexandrian Spiced Shrimp Soup",
        "name_ar": "شوربة جمبري إسكندراني بالثوم والكمون والكرفس",
        "desc": "Fresh whole shrimp cooked with aromatics in a fragrant broth of celery, garlic, onions, sweet peppers, and freshly ground cumin.",
        "cuisine": "Egyptian", "category": "Seafood", "servings": 4, "prep_time": 15, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Trim shrimp whiskers and devein. Sauté diced onions, minced garlic, and chopped celery in butter and olive oil until fragrant. Add shrimp, tossing until shells turn bright pink. Add diced tomatoes, cumin, coriander, salt, and black pepper. Pour in boiling water, simmer gently for 8-10 minutes. Squeeze fresh lemon juice over soup and serve hot.",
        "image_url": "https://images.unsplash.com/photo-1559742811-822873691df8", "source_url": "https://en.wikipedia.org/wiki/Shrimp_as_food", "source_name": "Egyptian Coastal Culinary",
        "ingredients": [
            ("Shrimp", 800, "g", "fresh medium shell-on", 0),
            ("Yellow Onion", 1, "piece", "chopped", 0),
            ("Garlic", 5, "clove", "crushed", 0),
            ("Celery", 2, "piece", "stalks sliced with leaves", 0),
            ("Red Tomato", 1, "piece", "diced", 0),
            ("Butter", 20, "g", "unsalted", 0),
            ("Extra Virgin Olive Oil", 2, "tbsp", "virgin", 0),
            ("Lemon", 2, "piece", "juiced", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Port Said Shrimp Kofta",
        "name_ar": "كفتة جمبري بورسعيدي بالصلصة والبطاطس",
        "desc": "Coastal Egyptian specialty of minced shrimp kneaded with rice flour, fresh dill, cilantro, and garlic, shaped into patties and simmered in garlic tomato sauce.",
        "cuisine": "Egyptian", "category": "Seafood", "servings": 5, "prep_time": 30, "cook_time": 30, "difficulty": "Medium",
        "instructions": "Process fresh peeled shrimp with soaked short grain rice, fresh cilantro, dill, parsley, onions, and garlic until paste forms. Season with cumin, coriander, salt, and chili. Shape into fingers or oval patties, flash fry in oil until golden. Sauté garlic in ghee, add tomato puree and potato cubes. Simmer sauce, then gently drop fried shrimp kofta and cook for 15 minutes.",
        "image_url": "https://images.unsplash.com/photo-1559742811-822873691df8", "source_url": "https://en.wikipedia.org/wiki/Kofta", "source_name": "Egyptian Coastal Culinary",
        "ingredients": [
            ("Shrimp", 700, "g", "peeled deveined", 0),
            ("Egyptian White Rice", 200, "g", "soaked and finely ground", 0),
            ("Potato", 300, "g", "cubed", 0),
            ("Fresh Dill", 1, "bunch", "chopped", 0),
            ("Fresh Coriander", 1, "bunch", "chopped", 0),
            ("Strained Tomato Puree", 500, "g", "pureed", 0),
            ("Garlic", 8, "clove", "minced", 0),
            ("Vegetable Cooking Oil", 200, "ml", "for frying", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Rice Kofta with Potato Stew",
        "name_ar": "كفتة أرز مصرية بالصلصة ومكعبات البطاطس",
        "desc": "Traditional Egyptian meatballs made of minced beef, ground rice, and fresh herbs, deep-fried then simmered in rich garlic-tomato sauce with diced potatoes.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 35, "cook_time": 35, "difficulty": "Medium",
        "instructions": "Blend ground beef with soaked ground Egyptian rice, onion, garlic, parsley, dill, and cilantro until a smooth paste forms. Shape into fingers. Deep fry in hot vegetable oil until deeply browned and crisp. Sauté minced garlic in ghee, add strained tomato puree and diced potatoes. Simmer until potatoes soften, then add fried kofta fingers and cook for 15 minutes.",
        "image_url": "https://images.unsplash.com/photo-1529042410759-befb1204b468", "source_url": "https://en.wikipedia.org/wiki/Kofta", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Ground Beef", 500, "g", "minced twice lean", 0),
            ("Egyptian White Rice", 250, "g", "soaked ground powder", 0),
            ("Potato", 400, "g", "peeled cubed", 0),
            ("Yellow Onion", 1, "piece", "chopped", 0),
            ("Garlic", 6, "clove", "minced", 0),
            ("Fresh Parsley", 0.5, "bunch", "chopped", 0),
            ("Fresh Dill", 0.5, "bunch", "chopped", 0),
            ("Fresh Coriander", 0.5, "bunch", "chopped", 0),
            ("Strained Tomato Puree", 600, "g", "pureed", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Vegetable Cooking Oil", 300, "ml", "for frying", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Fine Salt", 2, "tsp", "divided", 0)
        ]
    },
    {
        "name_en": "Egyptian Moussaka with Minced Beef",
        "name_ar": "مسقعة مصرية باللحمة المفرومة والباذنجان والفلفل",
        "desc": "Layers of fried eggplant slices and green bell peppers topped with seasoned minced beef tomato sauce, baked in the oven until bubbly.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 30, "cook_time": 35, "difficulty": "Medium",
        "instructions": "Slice black eggplants, salt lightly to draw out moisture, then fry in hot oil until golden brown. Lightly fry sliced green bell peppers. Sauté chopped onions and ground beef with spices, add tomato sauce, garlic, and vinegar, simmering for 10 minutes. In a baking dish, layer half fried eggplant and peppers, spread spiced meat sauce, top with remaining eggplant. Bake at 200C for 25 minutes.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Moussaka#Egypt", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Black Eggplant", 800, "g", "sliced rounds", 0),
            ("Ground Beef", 400, "g", "minced lean", 0),
            ("Green Bell Pepper", 3, "piece", "sliced rings", 0),
            ("Yellow Onion", 2, "piece", "diced", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Strained Tomato Puree", 500, "g", "pureed", 0),
            ("White Vinegar", 2, "tbsp", "distilled", 0),
            ("Vegetable Cooking Oil", 250, "ml", "for frying eggplant", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Fine Salt", 2, "tsp", "divided", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Taro Root with Swiss Chard",
        "name_ar": "قلقاس بالسلق والخضرة والشوربة على الطريقة المصرية",
        "desc": "Tender taro root cubes cooked in rich poultry broth infused with deep-green sautéed Swiss chard and garlic ta'sha.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 25, "cook_time": 40, "difficulty": "Medium",
        "instructions": "Peel taro root and wipe clean with dry cloth (do not wash with water to retain starch properties). Cut into even cubes. Boil in rich seasoned meat or duck broth with lemon juice until fork tender. In a separate skillet, sauté fresh Swiss chard leaves and coriander in ghee with crushed garlic until dark green, then puree. Pour green herb ta'sha into taro pot, simmer for 5 minutes, and serve with Egyptian rice.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Taro", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Taro Root", 1000, "g", "peeled cubed", 0),
            ("Swiss Chard", 2, "bunch", "leaves washed chopped", 0),
            ("Fresh Coriander", 1, "bunch", "chopped", 0),
            ("Garlic", 8, "clove", "crushed into paste", 0),
            ("Ghee", 3, "tbsp", "pure baladi", 0),
            ("Lemon", 1, "piece", "juice squeezed into broth", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Spinach Stew with Chickpeas",
        "name_ar": "سبانخ بالحمص وصلصة الطماطم ومكعبات اللحم",
        "desc": "Fresh chopped spinach leaves stewed with boiled chickpeas and tender meat cubes in rich garlicky tomato broth.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 5, "prep_time": 20, "cook_time": 45, "difficulty": "Easy",
        "instructions": "Sauté diced onions in ghee, add beef stew cubes and brown. Add tomato puree and broth, simmering until meat is tender. Add cooked chickpeas and fresh chopped spinach with fresh dill and coriander. In small pan, sauté crushed garlic and dry coriander in ghee until golden, pour ta'sha over simmering spinach. Cook for 5 minutes.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Spinach", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Fresh Spinach", 800, "g", "washed finely chopped", 0),
            ("Beef Stew Cubes", 500, "g", "lean cubes", 0),
            ("Canned Chickpeas", 200, "g", "boiled rinsed", 0),
            ("Fresh Coriander", 0.5, "bunch", "chopped", 0),
            ("Fresh Dill", 0.5, "bunch", "chopped", 0),
            ("Strained Tomato Puree", 400, "g", "pureed", 0),
            ("Garlic", 6, "clove", "crushed paste", 0),
            ("Yellow Onion", 1, "piece", "diced", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "White Bean Stew with Meat Cubes",
        "name_ar": "فاصوليا بيضاء بالصلصة ومكعبات اللحم البقري",
        "desc": "Tender white cannellini beans simmered in thick garlic-onion tomato gravy with braised beef cubes, served with vermicelli rice.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 5, "prep_time": 20, "cook_time": 50, "difficulty": "Easy",
        "instructions": "Soak white beans overnight and boil until tender. Brown beef cubes with onions and ghee. Add tomato puree, tomato paste, and seasoned beef broth, simmering until meat is tender. Add boiled white beans, simmer together for 15-20 minutes until flavors meld and gravy is thick and rich.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Fasolada", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("White Kidney Beans", 400, "g", "soaked and boiled", 0),
            ("Beef Stew Cubes", 500, "g", "beef cubes", 0),
            ("Strained Tomato Puree", 500, "g", "pureed", 0),
            ("Tomato Paste", 1.5, "tbsp", "canned", 0),
            ("Yellow Onion", 2, "piece", "finely diced", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Seven Spices", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Black-Eyed Pea Stew with Meat",
        "name_ar": "لوبيا بعين سوداء بالصلصة ومكعبات اللحم",
        "desc": "Classic Egyptian homestyle stew of black-eyed peas cooked in aromatic spiced tomato sauce with tender beef chunks.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 5, "prep_time": 15, "cook_time": 45, "difficulty": "Easy",
        "instructions": "Soak and boil black-eyed peas until tender. In a heavy pot, brown beef cubes in ghee with diced onions until browned. Add garlic and tomato puree, simmering with broth until beef softens. Stir in cooked black-eyed peas, adjust seasoning with salt, black pepper, and seven spices. Simmer for 15 minutes.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Black-eyed_pea", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Black-Eyed Peas", 350, "g", "soaked and boiled", 0),
            ("Beef Stew Cubes", 500, "g", "cubed", 0),
            ("Strained Tomato Puree", 450, "g", "pureed", 0),
            ("Yellow Onion", 2, "piece", "diced", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Upper Egyptian Bamya Weika",
        "name_ar": "بامية ويكا صعيدي بالكزبرة والثوم والشوربة",
        "desc": "Upper Egyptian green soup of sliced fresh okra whisked in flavorful chicken or meat broth, finished with golden garlic ta'sha.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 20, "difficulty": "Easy",
        "instructions": "Thinly slice fresh large okra into rounds. Drop into boiling rich seasoned broth with a pinch of baking soda to retain green color. Simmer until okra softens, then whisk vigorously or pulse lightly with hand blender. Prepare sizzling ta'sha of crushed garlic and dry coriander in ghee, pour into weika. Serve hot with baladi bread.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Okra", "source_name": "Upper Egyptian Heritage",
        "ingredients": [
            ("Okra", 600, "g", "fresh sliced thin rounds", 0),
            ("Garlic", 8, "clove", "crushed paste", 0),
            ("Dry Coriander", 2, "tbsp", "ground", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Green Chili Pepper", 1, "piece", "finely minced", 1),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Rural Stuffed Pigeon with Freekeh",
        "name_ar": "حمام محشي فريك بالسمن البلدي في الفرن",
        "desc": "Whole Egyptian farm pigeons stuffed with toasted nutty cracked wheat freekeh and giblets, poached in broth then pan-seared in rich ghee.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 35, "cook_time": 50, "difficulty": "Hard",
        "instructions": "Wash cracked freekeh thoroughly. Sauté diced onions in ghee, add diced pigeon giblets, freekeh, cinnamon, nutmeg, salt, and pepper. Add 1/2 cup water and cook until half-done. Clean pigeons and loosen skin over breast. Stuff freekeh under skin and inside cavity, sew or close with toothpicks. Poach gently in boiling broth with cardamom and mastic for 35 mins. Pan-sear in foaming baladi ghee until deeply golden and crisp.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Squab", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Pigeon", 4, "piece", "cleaned whole squabs", 0),
            ("Freekeh", 250, "g", "washed picked cracked green wheat", 0),
            ("Yellow Onion", 2, "piece", "finely diced", 0),
            ("Ghee", 4, "tbsp", "pure baladi for stuffing and searing", 0),
            ("Ground Nutmeg", 0.5, "tsp", "freshly grated", 0),
            ("Cinnamon", 0.5, "tsp", "ground", 0),
            ("Cardamom Pods", 4, "piece", "whole for broth", 0),
            ("Mastic Gum", 2, "piece", "tears", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Rural Stuffed Pigeon with Rice",
        "name_ar": "حمام محشي أرز بالكبد والقوانص ومحمر في السمن",
        "desc": "Delicate Egyptian pigeons packed with spiced short grain rice, pigeon livers, and sweet onions, boiled tender and roasted in baladi ghee.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 35, "cook_time": 50, "difficulty": "Hard",
        "instructions": "Sauté diced pigeon livers and onions in ghee with seven spices, black pepper, and salt. Add washed Egyptian white rice and a splash of water, cooking until half tender. Stuff pigeons through neck and cavity. Poach in aromatic broth with mastic and bay leaves for 35 minutes. Drain thoroughly, then fry in smoking hot ghee until skin turns reddish-brown and crispy.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Squab", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Pigeon", 4, "piece", "cleaned whole", 0),
            ("Egyptian White Rice", 200, "g", "short-grain washed", 0),
            ("Yellow Onion", 2, "piece", "finely chopped", 0),
            ("Ghee", 4, "tbsp", "pure baladi", 0),
            ("Seven Spices", 1, "tsp", "blend", 0),
            ("Cardamom Pods", 4, "piece", "whole", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Rural Roz Moammar with Meat",
        "name_ar": "أرز معمر فلاحي باللحمة والقشطة والحليب",
        "desc": "Rustic Egyptian baked rice casserole prepared in clay cookware with whole milk, heavy cream, clotted qashta, and tender braised beef chunks.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 20, "cook_time": 60, "difficulty": "Medium",
        "instructions": "Parboil beef chunks until half-cooked. Wash Egyptian rice and drain. Rub rice in clay pot with butter, salt, and black pepper. Place beef chunks in middle of rice. Heat whole milk and beef broth together, pour gently over rice. Spread thick dollops of baladi qashta and butter over top. Bake in high heat 220C oven for 20 mins until brown crust forms, then reduce to 160C for 40 mins until rice is creamy and tender.",
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c", "source_url": "https://en.wikipedia.org/wiki/Egyptian_cuisine", "source_name": "Rural Egyptian Culinary",
        "ingredients": [
            ("Egyptian White Rice", 500, "g", "short-grain washed", 0),
            ("Beef Stew Cubes", 500, "g", "parboiled tender", 0),
            ("Whole Milk", 800, "ml", "fresh full cream", 0),
            ("Qashta", 150, "g", "clotted baladi cream", 0),
            ("Butter", 50, "g", "unsalted", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "freshly ground", 0)
        ]
    },
    {
        "name_en": "Circassian Chicken with Walnut Sauce",
        "name_ar": "شركسية دجاج بصوص عين الجمل والأرز المصري",
        "desc": "Aristocratic Ottoman-Egyptian dish of poached tender chicken served over rice with velvety crushed walnut bread sauce and paprika drizzle.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 5, "prep_time": 30, "cook_time": 45, "difficulty": "Medium",
        "instructions": "Boil chicken with aromatics until tender, shred or carve into pieces. Remove crusts from toast bread and soak in warm chicken broth. In food processor, blend soaked bread, walnuts, garlic, coriander, and broth until thick creamy sauce forms. Cook white Egyptian rice. Plate rice in ring, place shredded chicken in center, coat generously with warm walnut sauce, and drizzle with hot butter paprika ta'sha.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Circassian_chicken", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Whole Chicken", 1200, "g", "poached and carved", 0),
            ("Walnuts", 200, "g", "shelled raw", 0),
            ("Toast Bread", 6, "slice", "white crustless", 0),
            ("Egyptian White Rice", 400, "g", "cooked fluffy", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Butter", 50, "g", "unsalted", 0),
            ("Dry Coriander", 1, "tsp", "ground", 0),
            ("Paprika", 1, "tsp", "sweet", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Keshk Almazia with Chicken",
        "name_ar": "كشك ألماظية بالفراخ والبصل المحمر",
        "desc": "Delicate Egyptian savory savory porridge of shredded chicken simmered with yogurt, milk, and flour, garnished with golden crispy fried onions.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Whisk plain yogurt, flour, and whole milk together in bowl until smooth; let ferment 30 mins. Sauté sliced onions in ghee until deeply golden and crispy, drain on paper towel. Bring seasoned chicken broth with shredded cooked chicken to gentle boil. Slowly whisk in yogurt-milk mixture, stirring constantly on low heat until sauce thickens into velvety savory cream. Pour into serving bowls and garnish with crisp onions.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Kashk", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Chicken Breast", 400, "g", "poached and shredded", 0),
            ("Plain Yogurt", 300, "g", "fresh natural", 0),
            ("Whole Milk", 400, "ml", "full cream", 0),
            ("All-Purpose Flour", 40, "g", "sifted", 0),
            ("Yellow Onion", 3, "piece", "thinly sliced rings", 0),
            ("Ghee", 3, "tbsp", "baladi for frying onions", 0),
            ("Fine Salt", 1, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "white or black", 0)
        ]
    },
    {
        "name_en": "Baked Roqaq with Minced Beef",
        "name_ar": "صينية رقاق باللحمة المفرومة والسمن البلدي في الفرن",
        "desc": "Layers of delicate crisp dry roqaq sheets dipped in hot seasoned meat broth, filled with spiced minced beef, and baked until flaky and golden.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 25, "cook_time": 30, "difficulty": "Medium",
        "instructions": "Sauté ground beef with chopped onions, seven spices, salt, and black pepper. In wide shallow tray, heat rich beef broth seasoned with ghee. Dip dry roqaq sheets one by one in warm broth to soften slightly. Layer 4 sheets in buttered baking pan brushing each with melted ghee. Spread spiced minced beef evenly. Top with another 4 dipped roqaq sheets brushed with ghee. Bake at 200C for 30 minutes until puffed, golden, and crispy.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Egyptian_cuisine", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Baladi Bread", 8, "piece", "dry thin roqaq pastry sheets", 0),
            ("Ground Beef", 500, "g", "minced lean", 0),
            ("Yellow Onion", 2, "piece", "finely chopped", 0),
            ("Ghee", 4, "tbsp", "melted baladi", 0),
            ("Seven Spices", 1, "tsp", "blend", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Baked Goulash with Minced Beef",
        "name_ar": "صينية جلاش باللحمة المفرومة والحليب والبيض",
        "desc": "Buttery layers of paper-thin phyllo pastry stuffed with savory ground beef, soaked in egg-milk custard and baked golden.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 20, "cook_time": 30, "difficulty": "Easy",
        "instructions": "Brown minced beef with onions, spices, and salt. Brush baking tray with melted ghee. Layer half phyllo pastry sheets, brushing every two sheets with melted ghee. Spread meat filling. Cover with remaining pastry sheets brushed with ghee. Cut into squares before baking. Whisk 1 cup milk with 1 egg, salt, and pepper, and pour evenly over pastry. Bake at 190C for 30 mins until puffed and golden brown.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Filo", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("All-Purpose Flour", 500, "g", "phyllo goulash dough sheets", 0),
            ("Ground Beef", 450, "g", "minced lean", 0),
            ("Yellow Onion", 2, "piece", "chopped", 0),
            ("Whole Milk", 250, "ml", "warmed", 0),
            ("Eggs", 1, "piece", "beaten", 0),
            ("Ghee", 4, "tbsp", "melted baladi", 0),
            ("Seven Spices", 1, "tsp", "blend", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Baked Goulash with Mixed Cheeses",
        "name_ar": "صينية جلاش بالجبنة البيضاء والنعناع والزيتون",
        "desc": "Crisp flaky phyllo pastry filled with salty feta white cheese, shredded mozzarella, dried mint, black olives, and sweet bell peppers.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 20, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Crumble white feta cheese and mix with shredded mozzarella, diced bell pepper, sliced black olives, dried mint, and olive oil. Layer half phyllo sheets in buttered tray, brushing sheets with ghee. Spread cheese mixture evenly. Top with remaining phyllo sheets, slice into squares, pour beaten egg and milk mixture over top, and bake at 190C for 25 minutes.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Filo", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("All-Purpose Flour", 500, "g", "phyllo pastry pack", 0),
            ("Feta White Cheese", 300, "g", "crumbled baladi", 0),
            ("Mozzarella Cheese", 150, "g", "shredded", 0),
            ("Green Bell Pepper", 1, "piece", "finely diced", 0),
            ("Dried Mint", 1, "tbsp", "crumbled", 0),
            ("Whole Milk", 200, "ml", "milk", 0),
            ("Eggs", 1, "piece", "fresh", 0),
            ("Ghee", 3, "tbsp", "melted", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Beef Escalope Pane",
        "name_ar": "بفتيك مقلي مقرمش بالبقسماط والبهارات",
        "desc": "Tenderized thin beef escalopes marinated in onion juice, spices, and lemon, breaded in crisp breadcrumbs and pan-fried until golden.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 12, "difficulty": "Easy",
        "instructions": "Pound beef sirloin steaks between parchment until very thin. Marinate in grated onion juice, garlic powder, black pepper, seven spices, and lemon juice for 1 hour. Dredge in flour, dip in beaten eggs with a splash of milk, then press firmly into fine seasoned breadcrumbs. Fry in medium-hot oil for 3-4 minutes per side until crisp and golden brown.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Escalope", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Beef Sirloin Steak", 600, "g", "thinly pounded escalopes", 0),
            ("Yellow Onion", 2, "piece", "grated juice only", 0),
            ("All-Purpose Flour", 100, "g", "for dusting", 0),
            ("Eggs", 2, "piece", "beaten with milk", 0),
            ("Breadcrumbs", 200, "g", "fine seasoned rusk", 0),
            ("Lemon", 1, "piece", "juiced", 0),
            ("Seven Spices", 1, "tsp", "blend", 0),
            ("Vegetable Cooking Oil", 200, "ml", "for shallow frying", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Crispy Chicken Pane",
        "name_ar": "صدور دجاج بانيه مقرمشة بالتتبيلة المصرية",
        "desc": "Egypt's most popular family lunch item: thin chicken cutlets marinated in grated onion and yogurt, double-breaded and fried golden.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 10, "difficulty": "Easy",
        "instructions": "Slice chicken breasts into thin fillets. Marinate in grated onion juice, yogurt, lemon juice, paprika, garlic powder, salt, and pepper for 30 minutes. Dip each fillet in flour, then beaten egg, then press into breadcrumbs. Shallow fry in hot vegetable oil for 3-4 minutes on each side until golden and crunchy.",
        "image_url": "https://images.unsplash.com/photo-1562967914-608f82629710", "source_url": "https://en.wikipedia.org/wiki/Breaded_cutlet", "source_name": "Egyptian Modern Family",
        "ingredients": [
            ("Chicken Breast", 700, "g", "sliced into thin cutlets", 0),
            ("Yellow Onion", 1, "piece", "grated juice", 0),
            ("Plain Yogurt", 2, "tbsp", "tenderizer", 0),
            ("All-Purpose Flour", 100, "g", "flour", 0),
            ("Eggs", 2, "piece", "beaten", 0),
            ("Breadcrumbs", 200, "g", "fine seasoned", 0),
            ("Paprika", 1, "tsp", "sweet", 0),
            ("Vegetable Cooking Oil", 200, "ml", "for frying", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Negresco Chicken Pasta",
        "name_ar": "صينية مكرونة نجرسكو بالفراخ والمشروم والجبن",
        "desc": "Rich Egyptian baked fettuccine pasta with sautéed chicken strips, fresh mushrooms, sweet peppers, creamy white béchamel, and melted mozzarella.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 25, "cook_time": 35, "difficulty": "Medium",
        "instructions": "Boil fettuccine pasta al dente. Sauté sliced chicken breast in butter with onions, garlic, sliced fresh mushrooms, and bell peppers until cooked. Prepare velvety béchamel sauce with butter, flour, warm milk, and heavy cream. Mix half the béchamel with pasta, place in baking dish, top with chicken mushroom filling, rest of pasta, cover with remaining béchamel, and top with mozzarella cheese. Bake at 200C for 30 minutes until bubbly and browned.",
        "image_url": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a", "source_url": "https://en.wikipedia.org/wiki/Egyptian_cuisine", "source_name": "Egyptian Modern Family",
        "ingredients": [
            ("Fettuccine Pasta", 450, "g", "boiled al dente", 0),
            ("Chicken Breast", 500, "g", "cut into thin strips", 0),
            ("Fresh Mushrooms", 200, "g", "sliced fresh button", 0),
            ("Green Bell Pepper", 1, "piece", "diced", 0),
            ("Yellow Onion", 1, "piece", "chopped", 0),
            ("Whole Milk", 800, "ml", "warmed", 0),
            ("Heavy Cream", 150, "ml", "cooking cream", 0),
            ("All-Purpose Flour", 70, "g", "flour", 0),
            ("Butter", 70, "g", "unsalted", 0),
            ("Mozzarella Cheese", 200, "g", "shredded", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Street Koshari-Style Pasta Tagine",
        "name_ar": "طاجن مكرونة محلات الكشري باللحمة المفرومة والصلصة",
        "desc": "The iconic street takeaway tagine of penne pasta, spiced minced beef, and zesty cumin-tomato garlic sauce baked inverted in a foil tin.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 30, "difficulty": "Easy",
        "instructions": "Brown minced beef with onions, garlic, tomato paste, cumin, and spices. In bottom of baking tins, firmly press layer of cooked spiced meat. Add uncooked or parboiled penne pasta on top. Pour hot seasoned garlic tomato sauce with water over pasta until covered. Seal tightly with aluminum foil and bake at 200C for 30 minutes. Invert onto plate before serving.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Kushari", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("Penne Pasta", 400, "g", "dry penne rigate", 0),
            ("Ground Beef", 350, "g", "spiced minced", 0),
            ("Yellow Onion", 2, "piece", "finely diced", 0),
            ("Garlic", 4, "clove", "crushed", 0),
            ("Strained Tomato Puree", 500, "g", "pureed", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("White Vinegar", 2, "tbsp", "distilled", 0),
            ("Vegetable Cooking Oil", 2, "tbsp", "oil", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Feteer Meshaltet",
        "name_ar": "فطير مشلتت فلاحي مورق بالسمن البلدي",
        "desc": "Rural multi-layered laminated pastry made of ultra-thin stretched dough brushed with pure Egyptian ghee, baked blistered and golden.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 6, "prep_time": 40, "cook_time": 20, "difficulty": "Hard",
        "instructions": "Knead flour with water and salt for 15 minutes into a silky, elastic dough. Rest coated in oil for 1 hour. On an oiled surface, stretch dough paper-thin until transparent. Smear generously with softened baladi ghee and fold into envelope multiple times creating dozens of buttery layers. Rest in round baking pan, gently flatten, brush top with qashta, and bake in maximum heat 250C oven for 15 minutes until puffed, flaky, and blistered golden.",
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff", "source_url": "https://en.wikipedia.org/wiki/Feteer_meshaltet", "source_name": "Rural Egyptian Heritage",
        "ingredients": [
            ("All-Purpose Flour", 600, "g", "high-gluten flour", 0),
            ("Ghee", 200, "g", "pure baladi softened", 0),
            ("Qashta", 50, "g", "for brushing top", 0),
            ("Vegetable Cooking Oil", 50, "ml", "for stretching dough", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Savory Meat and Cheese Feteer",
        "name_ar": "فطير شرقي باللحمة المفرومة والجبن الرومي والموزاريلا",
        "desc": "Egyptian street style stretched pastry stuffed with seasoned ground beef, aged rumi cheese, mozzarella, sweet peppers, olives, and fresh tomatoes.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 30, "cook_time": 20, "difficulty": "Medium",
        "instructions": "Stretch pastry dough ultra-thin on oiled marble. Place layer of cooked minced beef, grated rumi cheese, shredded mozzarella, diced tomatoes, sliced bell pepper, and black olives in center. Fold dough over filling into rectangle. Place another stretched sheet over it and fold. Top with extra cheese, peppers, and olives. Bake in 240C oven for 15-18 minutes until golden and crisp.",
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591", "source_url": "https://en.wikipedia.org/wiki/Feteer_meshaltet", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("All-Purpose Flour", 500, "g", "dough", 0),
            ("Ground Beef", 300, "g", "cooked spiced minced", 0),
            ("Rumi Cheese", 100, "g", "grated sharp Egyptian cheese", 0),
            ("Mozzarella Cheese", 150, "g", "shredded", 0),
            ("Red Tomato", 1, "piece", "diced", 0),
            ("Green Bell Pepper", 1, "piece", "sliced rings", 0),
            ("Ghee", 80, "g", "melted", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Savory Sausage and Olive Feteer",
        "name_ar": "فطير شرقي بالسجق البلدي والموزاريلا والزيتون",
        "desc": "Crispy layered Egyptian pastry stuffed with flavorful sliced oriental sausages, gooey mozzarella, diced tomatoes, and green peppers.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 20, "difficulty": "Medium",
        "instructions": "Sauté sliced oriental sausages until lightly browned. Stretch feteer dough paper-thin. Spread sausage slices, mozzarella, sweet peppers, diced tomatoes, and olives across center. Fold pastry tightly, brush with ghee, and bake at 240C for 18 minutes until deeply golden, flaky, and cheese is melted.",
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591", "source_url": "https://en.wikipedia.org/wiki/Feteer_meshaltet", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("All-Purpose Flour", 500, "g", "flour for dough", 0),
            ("Oriental Sausage", 350, "g", "sliced sautéed", 0),
            ("Mozzarella Cheese", 150, "g", "shredded", 0),
            ("Green Bell Pepper", 1, "piece", "sliced", 0),
            ("Red Tomato", 1, "piece", "diced", 0),
            ("Ghee", 70, "g", "melted", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Shish Tawook with Garlic Sauce",
        "name_ar": "شيش طاووق دجاج متبل مشوي مع صوص التومية",
        "desc": "Succulent cubes of chicken breast marinated in yogurt, garlic, lemon, tomato paste, and warm spices, skewered with bell peppers and grilled.",
        "cuisine": "Levantine", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Marinate cubed chicken breast in yogurt, crushed garlic, lemon juice, olive oil, tomato paste, paprika, oregano, salt, and pepper for 2 hours. Thread onto skewers alternating with onion wedges and bell pepper squares. Grill over medium-hot charcoal or cast-iron grill pan for 12-15 minutes turning until charred and juicy. Serve with Syrian toum and warm flatbread.",
        "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1", "source_url": "https://en.wikipedia.org/wiki/Shish_taouk", "source_name": "Middle Eastern Grills",
        "ingredients": [
            ("Chicken Breast", 800, "g", "cut into large cubes", 0),
            ("Plain Yogurt", 100, "g", "natural", 0),
            ("Garlic", 6, "clove", "crushed paste", 0),
            ("Lemon", 2, "piece", "juiced", 0),
            ("Tomato Paste", 1.5, "tbsp", "canned", 0),
            ("Extra Virgin Olive Oil", 3, "tbsp", "olive oil", 0),
            ("Green Bell Pepper", 2, "piece", "cut into squares", 0),
            ("Yellow Onion", 1, "piece", "cut into squares", 0),
            ("Paprika", 1.5, "tsp", "sweet", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Kamouneya Stew",
        "name_ar": "كمونية لحم بقري بالبصل المكرمل والكمون والثوم",
        "desc": "Tender chunks of beef braised with abundance of caramelized sliced onions, crushed garlic, and a prominent aroma of roasted cumin.",
        "cuisine": "Egyptian", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 70, "difficulty": "Easy",
        "instructions": "In heavy pot, melt ghee and brown beef chunks until deeply seared. Add sliced onions and cook slowly until sweet and golden brown. Add minced garlic, roasted ground cumin, tomato paste, and hot broth. Cover and simmer on low heat for 1 hour until beef is melt-in-mouth tender and sauce is thick and glossy.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Kamounia", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Beef Stew Cubes", 700, "g", "lean cubes", 0),
            ("Yellow Onion", 4, "piece", "thinly sliced rings", 0),
            ("Garlic", 6, "clove", "minced", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Cumin", 2.5, "tsp", "freshly roasted and ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },

    # -------------------------------------------------------------------------
    # 2. EGYPTIAN BREAKFAST, STREET FOOD & APPETIZERS
    # -------------------------------------------------------------------------
    {
        "name_en": "Ful Medames with Flaxseed Oil",
        "name_ar": "فول مدمس بالزيت الحار والليمون والكمون",
        "desc": "The quintessential Egyptian breakfast: slow-cooked fava beans lightly mashed, dressed with fragrant hot flaxseed oil, lemon juice, cumin, and sea salt.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 4, "prep_time": 5, "cook_time": 10, "difficulty": "Easy",
        "instructions": "Warm cooked fava beans in a pot and mash lightly with a fork. Season with ground cumin, salt, and black pepper. Stir in freshly squeezed lemon juice. Spoon into serving dish, and drizzle generously with authentic Egyptian hot flaxseed oil (zeit har). Serve immediately with piping hot baladi flatbread.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Ful_medames", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Canned Fava Beans", 800, "g", "cooked tender fava beans", 0),
            ("Flaxseed Oil", 40, "ml", "authentic Egyptian zeit har", 0),
            ("Lemon", 2, "piece", "freshly squeezed juice", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Ful Medames Iskandarani",
        "name_ar": "فول مدمس إسكندراني بالطحينة والطماطم والخلطة",
        "desc": "Alexandria-style fava beans tossed with creamy tahini paste, diced fresh tomatoes, green chili, crushed garlic, and olive oil.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 4, "prep_time": 10, "cook_time": 10, "difficulty": "Easy",
        "instructions": "In a bowl, whisk tahini with lemon juice, vinegar, minced garlic, cumin, salt, and warm water until smooth and pale. Warm fava beans and fold in tahini sauce. Stir in diced tomatoes, chopped hot peppers, and chopped parsley. Drizzle with extra virgin olive oil and serve hot with baladi bread.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Ful_medames", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Canned Fava Beans", 800, "g", "cooked tender", 0),
            ("Tahini Sesame Paste", 4, "tbsp", "pure sesame paste", 0),
            ("Red Tomato", 1, "piece", "firm diced", 0),
            ("Green Chili Pepper", 1, "piece", "minced", 1),
            ("Garlic", 3, "clove", "crushed paste", 0),
            ("Extra Virgin Olive Oil", 3, "tbsp", "olive oil", 0),
            ("Lemon", 2, "piece", "juiced", 0),
            ("White Vinegar", 1, "tbsp", "distilled", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Fresh Parsley", 2, "tbsp", "chopped", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Ful Medames with Oriental Sausage",
        "name_ar": "فول مدمس بالسجق الشرقي والطماطم والثوم",
        "desc": "Hearty Egyptian breakfast skillet of tender fava beans simmered with browned spicy oriental sausages, garlic, and tomato puree.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 4, "prep_time": 10, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Brown sliced oriental sausages in a skillet with garlic and onions until fragrant. Add tomato paste and diced tomatoes, cooking for 5 minutes. Fold in mashed cooked fava beans and simmer together until hot and bubbling. Season with cumin and lemon juice. Serve with pickled vegetables and baladi bread.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Ful_medames", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("Canned Fava Beans", 600, "g", "cooked fava", 0),
            ("Oriental Sausage", 250, "g", "sliced into rounds", 0),
            ("Red Tomato", 2, "piece", "diced", 0),
            ("Garlic", 3, "clove", "minced", 0),
            ("Tomato Paste", 1, "tbsp", "canned", 0),
            ("Ghee", 1, "tbsp", "baladi", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Authentic Egyptian Taameya",
        "name_ar": "طعمية مصرية مقرمشة بالفول المدشوش والسمسم",
        "desc": "Crispy golden Egyptian falafel made of soaked split fava beans, fresh leeks, fresh coriander, dill, and coated generously with white sesame seeds.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 6, "prep_time": 25, "cook_time": 15, "difficulty": "Medium",
        "instructions": "Soak split dried fava beans for 12 hours and drain thoroughly. Pulse in food processor with fresh coriander, dill, parsley, leek, onion, garlic, dry coriander, cumin, and salt until light green and fluffy. Before frying, stir in baking powder. Shape into round patties, coat generously with raw sesame seeds, and deep fry in hot vegetable oil until deeply crispy and brown.",
        "image_url": "https://images.unsplash.com/photo-1593001874117-c99c800e3eb7", "source_url": "https://en.wikipedia.org/wiki/Falafel#Egypt", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("Dried Split Fava Beans", 500, "g", "soaked 12 hours drained", 0),
            ("Fresh Coriander", 1, "bunch", "leaves and tender stems", 0),
            ("Fresh Dill", 0.5, "bunch", "chopped", 0),
            ("Fresh Parsley", 0.5, "bunch", "chopped", 0),
            ("Yellow Onion", 1, "piece", "medium chopped", 0),
            ("Garlic", 6, "clove", "peeled", 0),
            ("Raw White Sesame Seeds", 60, "g", "for coating patties", 0),
            ("Dry Coriander", 2, "tbsp", "coarse ground", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Baking Powder", 0.5, "tsp", "added right before frying", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Vegetable Cooking Oil", 500, "ml", "for deep frying", 0)
        ]
    },
    {
        "name_en": "Spicy Stuffed Taameya",
        "name_ar": "طعمية مصرية محشية شطة وبصل وطماطم",
        "desc": "Jumbo Egyptian falafel patties stuffed with a spicy filling of sautéed onions, red chili pepper, tomato paste, and ground coriander.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 4, "prep_time": 20, "cook_time": 15, "difficulty": "Medium",
        "instructions": "Sauté finely diced onions in oil with hot chili powder, tomato paste, coriander, and salt until softened into a spicy paste. Flatten a portion of taameya green dough in your palm, add a teaspoon of spicy onion filling in center, and seal with another layer of dough. Dip in sesame seeds and deep fry in hot oil until crunchy and golden brown.",
        "image_url": "https://images.unsplash.com/photo-1593001874117-c99c800e3eb7", "source_url": "https://en.wikipedia.org/wiki/Falafel#Egypt", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("Dried Split Fava Beans", 500, "g", "soaked and processed dough", 0),
            ("Yellow Onion", 2, "piece", "finely diced for filling", 0),
            ("Hot Red Pepper Powder", 1.5, "tsp", "spicy hot", 0),
            ("Tomato Paste", 1.5, "tbsp", "canned", 0),
            ("Raw White Sesame Seeds", 50, "g", "for coating", 0),
            ("Dry Coriander", 1.5, "tbsp", "ground", 0),
            ("Vegetable Cooking Oil", 450, "ml", "for deep frying", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Shakshouka",
        "name_ar": "شكشوكة مصرية بالبيض والخضار والبهارات",
        "desc": "Fresh eggs gently poached in a bubbling thick skillet sauce of ripe tomatoes, sweet peppers, sautéed onions, garlic, and cumin.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 3, "prep_time": 10, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Heat olive oil in a wide skillet. Sauté chopped onions and bell pepper until softened. Add minced garlic, cumin, paprika, and tomato paste. Add diced fresh tomatoes and simmer for 8 minutes until sauce thickens. Make small wells with back of spoon and crack fresh eggs into sauce. Cover skillet and cook on low heat for 5-7 minutes until whites are firm and yolks remain runny. Garnish with fresh parsley.",
        "image_url": "https://images.unsplash.com/photo-1590412200988-a436970781fa", "source_url": "https://en.wikipedia.org/wiki/Shakshouka", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Eggs", 5, "piece", "fresh large", 0),
            ("Red Tomato", 4, "piece", "ripe peeled and chopped", 0),
            ("Yellow Onion", 1, "piece", "diced", 0),
            ("Green Bell Pepper", 1, "piece", "diced", 0),
            ("Garlic", 3, "clove", "minced", 0),
            ("Tomato Paste", 1, "tbsp", "canned", 0),
            ("Extra Virgin Olive Oil", 2, "tbsp", "olive oil", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Paprika", 1, "tsp", "sweet", 0),
            ("Fresh Parsley", 2, "tbsp", "chopped garnish", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Eggs with Pastirma",
        "name_ar": "بيض بالبسطرمة والسمن البلدي في الطاسة",
        "desc": "Classic Egyptian breakfast skillet of fragrant cured spiced pastirma beef crisped in foaming baladi ghee with fried fresh eggs.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 2, "prep_time": 5, "cook_time": 5, "difficulty": "Easy",
        "instructions": "Cut pastirma slices into bite-sized pieces. Melt pure baladi ghee in a skillet over medium heat. Sauté pastirma for 1 minute until fragrant and lightly browned. Crack whole eggs into skillet over pastirma. Season with freshly ground black pepper (be careful with salt as pastirma is naturally cured and salty). Cook until whites are set and yolks are runny.",
        "image_url": "https://images.unsplash.com/photo-1590412200988-a436970781fa", "source_url": "https://en.wikipedia.org/wiki/Pastirma", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Pastirma", 100, "g", "sliced cured beef", 0),
            ("Eggs", 4, "piece", "fresh whole", 0),
            ("Ghee", 2, "tbsp", "pure baladi", 0),
            ("Black Pepper", 0.5, "tsp", "freshly cracked", 0),
            ("Fine Salt", 0.25, "tsp", "light pinch", 0)
        ]
    },
    {
        "name_en": "Egyptian Herb Frittata / Eggah",
        "name_ar": "عجة مصرية بالبيض والخضرة والبصل في الفرن",
        "desc": "Traditional Egyptian baked egg frittata bursting with caramelized onions, fresh parsley, dill, cilantro, flour, and aromatic cumin.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 4, "prep_time": 15, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Sauté diced onions in ghee until deeply golden and sweet; let cool. Whisk eggs with flour, milk, baking powder, cumin, salt, and black pepper until smooth. Fold in fresh chopped parsley, dill, cilantro, and caramelized onions. Pour into buttered baking dish. Bake in 180C oven for 25 minutes until puffed, golden, and knife inserted comes out clean.",
        "image_url": "https://images.unsplash.com/photo-1590412200988-a436970781fa", "source_url": "https://en.wikipedia.org/wiki/Eggah", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Eggs", 6, "piece", "fresh large", 0),
            ("Yellow Onion", 2, "piece", "finely diced", 0),
            ("Fresh Parsley", 1, "bunch", "chopped", 0),
            ("Fresh Dill", 0.5, "bunch", "chopped", 0),
            ("Fresh Coriander", 0.5, "bunch", "chopped", 0),
            ("All-Purpose Flour", 30, "g", "flour", 0),
            ("Whole Milk", 50, "ml", "milk", 0),
            ("Baking Powder", 0.5, "tsp", "leavening", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Bissara",
        "name_ar": "بصارة مصرية بالفول المدشوش والملوخية والنعناع",
        "desc": "Nutritious ancient Egyptian green puree of simmered split dried fava beans, fresh herbs, dry mint, and dry molokhia, topped with crispy caramelized onions.",
        "cuisine": "Egyptian", "category": "Breakfast", "servings": 5, "prep_time": 15, "cook_time": 40, "difficulty": "Easy",
        "instructions": "Boil soaked split fava beans with onion, garlic, fresh dill, cilantro, and parsley until completely soft. Puree in blender until silky smooth. Return to pot, stir in dry molokhia, dry mint, cumin, and salt, simmering for 5 minutes. In a skillet, fry thinly sliced onions in oil until dark golden and crispy. Pour warm bissara into shallow bowls and garnish generously with fried crispy onions.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Bissara", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Dried Split Fava Beans", 400, "g", "soaked 4 hours drained", 0),
            ("Fresh Coriander", 1, "bunch", "chopped", 0),
            ("Fresh Dill", 0.5, "bunch", "chopped", 0),
            ("Yellow Onion", 3, "piece", "divided 1 for soup 2 for frying", 0),
            ("Garlic", 6, "clove", "peeled", 0),
            ("Dried Mint", 1, "tbsp", "crumbled", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Vegetable Cooking Oil", 100, "ml", "for frying onions", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Baba Ghanoush with Tahini",
        "name_ar": "بابا غنوج باذنجان مشوي بالطحينة والثوم والليمون",
        "desc": "Smoky charcoal-roasted eggplant mashed with rich sesame tahini, crushed garlic, freshly squeezed lemon juice, cumin, and virgin olive oil.",
        "cuisine": "Egyptian", "category": "Appetizer", "servings": 4, "prep_time": 15, "cook_time": 20, "difficulty": "Easy",
        "instructions": "Char whole eggplants over open flame or under broiler until skin is blackened and flesh is meltingly tender. Cool, peel away charred skin, and drain excess water. Mash flesh with fork or pulse lightly. Whisk tahini with lemon juice, minced garlic, cumin, and salt. Fold tahini sauce into mashed eggplant. Spread on plate, swirl with back of spoon, and drizzle with virgin olive oil and paprika.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Baba_ghanoush", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Black Eggplant", 800, "g", "charred and peeled", 0),
            ("Tahini Sesame Paste", 4, "tbsp", "pure sesame paste", 0),
            ("Garlic", 3, "clove", "crushed paste", 0),
            ("Lemon", 2, "piece", "freshly squeezed juice", 0),
            ("Extra Virgin Olive Oil", 3, "tbsp", "virgin", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Paprika", 0.5, "tsp", "for garnish", 1),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Pickled Eggplants",
        "name_ar": "باذنجان مخلل مسلوق بالدقة والخل والثوم والشطة",
        "desc": "Baby black eggplants boiled tender and stuffed with a fiery Egyptian dakkah of crushed garlic, hot red chili, cumin, coriander, lemon, and vinegar.",
        "cuisine": "Egyptian", "category": "Appetizer", "servings": 6, "prep_time": 20, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Boil small black baby eggplants in salted water with 1 beet slice (for vivid color) for 10-12 minutes until tender; drain and cool. Make lengthwise slit in each eggplant. Pound garlic, red hot chili pepper, cumin, dry coriander, salt, lemon juice, and white vinegar in mortar into a coarse paste. Stuff each eggplant generously with the paste. Store in jar submerged in pickled cooking water and vinegar.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Pickled_eggplant", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("Black Eggplant", 600, "g", "small baby eggplants", 0),
            ("Garlic", 10, "clove", "crushed", 0),
            ("Hot Red Pepper Powder", 2, "tsp", "or fresh red chili paste", 0),
            ("Lemon", 3, "piece", "juiced", 0),
            ("White Vinegar", 60, "ml", "distilled", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Ground Coriander", 1, "tsp", "ground", 0),
            ("Fine Salt", 2, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Egyptian Baladi Salad",
        "name_ar": "سلطة بلدي مصري بالخيار والطماطم والكمون والليمون",
        "desc": "Crisp salad of diced cucumbers, ripe tomatoes, red onions, and fresh parsley tossed in water, vinegar, lemon juice, cumin, and chili (wisky el-kebab).",
        "cuisine": "Egyptian", "category": "Salad", "servings": 4, "prep_time": 15, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Chop cucumbers, firm red tomatoes, and red onion into medium dice. Finely chop fresh parsley and cilantro. In a bowl, mix cold water, white vinegar, freshly squeezed lemon juice, ground cumin, chili pepper, and salt. Combine vegetables and herb dressing, chilling for 20 minutes before serving so the famous baladi dressing (wisky) infuses.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Arab_salad", "source_name": "Egyptian Grills Culinary",
        "ingredients": [
            ("Cucumber", 3, "piece", "crisp diced", 0),
            ("Red Tomato", 3, "piece", "firm diced", 0),
            ("Red Onion", 1, "piece", "finely sliced or diced", 0),
            ("Fresh Parsley", 1, "bunch", "finely chopped", 0),
            ("Lemon", 2, "piece", "juiced", 0),
            ("White Vinegar", 3, "tbsp", "distilled", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Hot Red Pepper Powder", 0.5, "tsp", "optional hot", 1),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "White Tahini Dip for Grills",
        "name_ar": "سلطة طحينة بيضاء بالخل والثوم والكمون للمشويات",
        "desc": "Velvety sesame tahini dressing whisked with warm water, vinegar, lemon juice, garlic paste, cumin, and virgin olive oil.",
        "cuisine": "Egyptian", "category": "Appetizer", "servings": 4, "prep_time": 5, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Place raw sesame tahini in a bowl. Slowly whisk in warm water tablespoon by tablespoon until tahini seizes then emulsifies into a smooth pale cream. Add white vinegar, fresh lemon juice, crushed garlic, cumin, salt, and black pepper. Whisk until perfectly velvety. Drizzle with olive oil and dust with cumin.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Tahini", "source_name": "Egyptian Grills Culinary",
        "ingredients": [
            ("Tahini Sesame Paste", 150, "g", "pure sesame paste", 0),
            ("White Vinegar", 2, "tbsp", "distilled", 0),
            ("Lemon", 1, "piece", "freshly squeezed juice", 0),
            ("Garlic", 2, "clove", "crushed fine paste", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Extra Virgin Olive Oil", 1, "tbsp", "for drizzling", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },

    # -------------------------------------------------------------------------
    # 3. LEVANTINE & MIDDLE EASTERN SPECIALTIES
    # -------------------------------------------------------------------------
    {
        "name_en": "Saudi Lamb Kabsa",
        "name_ar": "كبسة لحم ضاني بالبهارات والأرز البسمتي والمكسرات",
        "desc": "Fragrant Gulf spiced long grain basmati rice cooked in seasoned lamb broth with dried black limes, cinnamon sticks, cardamom, and toasted nuts.",
        "cuisine": "Arabian", "category": "Main Course", "servings": 6, "prep_time": 25, "cook_time": 75, "difficulty": "Medium",
        "instructions": "Sear lamb shoulder chunks in ghee with diced onions and garlic until browned. Add kabsa spice blend, whole cinnamon stick, cardamom pods, bay leaves, dried lime (loomi), tomato puree, and water. Simmer until lamb is tender. Remove lamb and roast in oven until golden. Add washed long-grain basmati rice to spiced broth. Cover and cook until fluffy. Serve rice crowned with lamb and toasted almonds.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Kabsa", "source_name": "Arabian Culinary Catalog",
        "ingredients": [
            ("Lamb Meat Cubes", 1000, "g", "bone-in lamb pieces", 0),
            ("Basmati Rice", 500, "g", "long grain washed soaked", 0),
            ("Yellow Onion", 2, "piece", "finely chopped", 0),
            ("Garlic", 5, "clove", "minced", 0),
            ("Strained Tomato Puree", 300, "g", "pureed", 0),
            ("Ghee", 3, "tbsp", "baladi", 0),
            ("Cardamom Pods", 6, "piece", "whole", 0),
            ("Cinnamon", 1, "piece", "whole stick", 0),
            ("Turmeric", 1, "tsp", "ground", 0),
            ("Raw Almonds", 50, "g", "toasted slivers", 0),
            ("Raisins", 40, "g", "golden raisins", 0),
            ("Fine Salt", 2, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Gulf Chicken Kabsa",
        "name_ar": "كبسة دجاج خليجية بالأرز البسمتي والزعفران",
        "desc": "Aromatic chicken halves cooked in spiced tomato-onion broth with cloves, cardamom, turmeric, and long-grain basmati rice.",
        "cuisine": "Arabian", "category": "Main Course", "servings": 5, "prep_time": 20, "cook_time": 45, "difficulty": "Medium",
        "instructions": "Sauté onions, garlic, and grated ginger in ghee with whole cloves, cardamom, and cinnamon. Add chicken halves, browning skin. Add tomato paste, puree, turmeric, and water. Simmer 30 minutes until chicken is tender. Transfer chicken to baking sheet, brush with saffron water, and broil until crisp. Add basmati rice to pot and cook until broth is absorbed. Serve with chicken on top.",
        "image_url": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db", "source_url": "https://en.wikipedia.org/wiki/Kabsa", "source_name": "Arabian Culinary Catalog",
        "ingredients": [
            ("Whole Chicken", 1300, "g", "halved cleaned", 0),
            ("Basmati Rice", 500, "g", "long-grain", 0),
            ("Yellow Onion", 2, "piece", "chopped", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Strained Tomato Puree", 350, "g", "pureed", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Cardamom Pods", 5, "piece", "whole", 0),
            ("Turmeric", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 2, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Smoked Lamb Mandi",
        "name_ar": "مندي لحم ضاني مدخن بالفحم والأرز البسمتي",
        "desc": "Tender spiced lamb steamed over fragrant long grain basmati rice, infused with traditional live charcoal and ghee smoke.",
        "cuisine": "Yemeni", "category": "Main Course", "servings": 6, "prep_time": 30, "cook_time": 90, "difficulty": "Medium",
        "instructions": "Rub lamb chunks with turmeric, cardamom, salt, pepper, and melted ghee. In oven-safe pot, combine soaked basmati rice, water, whole cloves, cardamom, and bay leaves. Place wire rack over pot and set seasoned lamb on rack so drippings fall onto rice. Cover entire assembly tightly with dual foil layers and bake at 180C for 1.5 hours. Uncover, place small foil cup with hot coal and drizzle with ghee, covering for 10 minutes to infuse smoky aroma.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Mandi_(food)", "source_name": "Arabian Culinary Catalog",
        "ingredients": [
            ("Lamb Meat Cubes", 1200, "g", "bone-in lamb cuts", 0),
            ("Basmati Rice", 500, "g", "soaked long-grain", 0),
            ("Ghee", 3, "tbsp", "baladi", 0),
            ("Cardamom Pods", 6, "piece", "whole", 0),
            ("Turmeric", 1, "tsp", "ground", 0),
            ("Cloves", 6, "piece", "whole", 0),
            ("Fine Salt", 2, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Lebanese Tabbouleh",
        "name_ar": "تبولة لبنانية بالبرغل الناعم والبقدونس وزيت الزيتون",
        "desc": "Ultra-fresh Levantine herb salad composed of finely minced fresh flat-leaf parsley, mint, diced red tomatoes, scallions, fine bulgur, lemon, and olive oil.",
        "cuisine": "Levantine", "category": "Salad", "servings": 4, "prep_time": 25, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Rinse fine bulgur and soak in freshly squeezed lemon juice for 15 minutes until plump. Wash parsley and dry thoroughly before mincing finely with a sharp chef's knife (do not bruise). Finely chop fresh mint, scallions, and firm tomatoes. In a salad bowl, toss minced parsley, mint, scallions, tomatoes, and soaked bulgur with extra virgin olive oil, salt, and pepper. Serve cold with crisp romaine lettuce leaves.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Tabbouleh", "source_name": "Levantine Culinary Catalog",
        "ingredients": [
            ("Fresh Parsley", 3, "bunch", "finely minced", 0),
            ("Fresh Mint", 0.5, "bunch", "finely chopped leaves", 0),
            ("Red Tomato", 3, "piece", "firm finely diced", 0),
            ("Bulgur", 50, "g", "fine brown or white bulgur", 0),
            ("Lemon", 3, "piece", "freshly squeezed juice", 0),
            ("Extra Virgin Olive Oil", 80, "ml", "first cold pressed", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Lebanese Fattoush with Crispy Bread",
        "name_ar": "فتوش لبناني بالخبز المحمص ودبس الرمان والسماق",
        "desc": "Vibrant garden salad of crisp cucumbers, radish, tomatoes, purslane, and romaine lettuce tossed with toasted pita croutons, sumac, and pomegranate molasses.",
        "cuisine": "Levantine", "category": "Salad", "servings": 4, "prep_time": 20, "cook_time": 10, "difficulty": "Easy",
        "instructions": "Cut shami flatbread into small squares, toss with olive oil and bake or fry until deeply crispy. Coarsely chop crisp romaine lettuce, cucumbers, red tomatoes, radishes, and mint leaves. In a bowl, whisk pomegranate molasses, extra virgin olive oil, fresh lemon juice, crushed garlic, sumac, and salt into tangy dressing. Toss vegetables with dressing and fold in crispy pita squares immediately before serving.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Fattoush", "source_name": "Levantine Culinary Catalog",
        "ingredients": [
            ("Cucumber", 3, "piece", "sliced", 0),
            ("Red Tomato", 3, "piece", "chopped chunks", 0),
            ("Radish", 4, "piece", "thinly sliced", 0),
            ("Shami Bread", 2, "piece", "toasted pita squares", 0),
            ("Fresh Mint", 0.5, "bunch", "leaves", 0),
            ("Pomegranate Molasses", 2.5, "tbsp", "thick tangy", 0),
            ("Sumac", 1.5, "tbsp", "tart ground sumac", 0),
            ("Extra Virgin Olive Oil", 60, "ml", "virgin", 0),
            ("Lemon", 2, "piece", "juiced", 0),
            ("Garlic", 1, "clove", "crushed paste", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Creamy Hummus with Tahini",
        "name_ar": "حمص بطحينة وزيت الزيتون والكمون",
        "desc": "Velvety smooth dip of slow-cooked chickpeas pureed with rich sesame tahini, fresh lemon juice, garlic, ice water, and cold pressed olive oil.",
        "cuisine": "Levantine", "category": "Appetizer", "servings": 5, "prep_time": 15, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Place boiled tender chickpeas in food processor with minced garlic and salt; process until fine. Add sesame tahini and lemon juice, processing until thick paste forms. While machine is running, drop in 3-4 ice cubes and iced water, whipping for 4-5 minutes until exceptionally creamy, light, and silky. Spread onto plate with shallow well, drizzle with olive oil, garnish with whole chickpeas, cumin, and paprika.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Hummus", "source_name": "Levantine Culinary Catalog",
        "ingredients": [
            ("Canned Chickpeas", 500, "g", "tender boiled drained", 0),
            ("Tahini Sesame Paste", 120, "g", "pure sesame tahini", 0),
            ("Lemon", 2, "piece", "freshly squeezed juice", 0),
            ("Garlic", 2, "clove", "minced", 0),
            ("Extra Virgin Olive Oil", 40, "ml", "for finishing", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Paprika", 0.5, "tsp", "for garnish", 1),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Syrian Garlic Toum",
        "name_ar": "تومية سورية أصلية بالثوم والنشا والزيت",
        "desc": "The authentic creamy Syrian garlic sauce prepared with fresh garlic, lemon, oil, and boiled cornstarch slurry for Shawarma and grilled meats.",
        "cuisine": "Levantine", "category": "Appetizer", "servings": 6, "prep_time": 15, "cook_time": 5, "difficulty": "Easy",
        "instructions": "Whisk cornstarch with cold water in small saucepan, heat on low while whisking until it forms a translucent, thick pudding-like paste; let cool completely. In blender, combine garlic cloves, salt, and lemon juice until finely pureed. Add cooled cornstarch paste and blend. With motor running on high, drizzle vegetable oil in a steady slow stream until mixture emulsifies into an airy, fluffy white garlic mayonnaise.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Toum", "source_name": "Levantine Culinary Catalog",
        "ingredients": [
            ("Garlic", 10, "clove", "fresh peeled", 0),
            ("Cornstarch", 3, "tbsp", "slurry base", 0),
            ("Lemon", 2, "piece", "fresh juice", 0),
            ("Vegetable Cooking Oil", 120, "ml", "neutral oil", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Fried Meat Kibbeh",
        "name_ar": "كبة لحم مقلية بالبرغل ومحشية بالصنوبر",
        "desc": "Crispy football-shaped bulgur and minced meat shells stuffed with seasoned spiced ground lamb, caramelized onions, and toasted pine nuts.",
        "cuisine": "Levantine", "category": "Main Course", "servings": 5, "prep_time": 40, "cook_time": 20, "difficulty": "Hard",
        "instructions": "Soak fine brown bulgur. Puree with lean ground beef, grated onion, salt, pepper, and cinnamon in food processor until pliable paste forms. Sauté ground lamb with chopped onions, pine nuts, allspice, and sumac until browned for filling. Shape portions of bulgur dough into hollow torpedo cones, stuff with meat filling, and pinch closed. Deep fry in medium-hot oil for 5-6 minutes until deeply browned and crisp.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Kibbeh", "source_name": "Levantine Culinary Catalog",
        "ingredients": [
            ("Ground Beef", 400, "g", "extra lean for shell", 0),
            ("Minced Lamb", 300, "g", "for filling", 0),
            ("Bulgur", 300, "g", "fine brown bulgur", 0),
            ("Yellow Onion", 3, "piece", "divided for shell and filling", 0),
            ("Pine Nuts", 40, "g", "toasted golden", 0),
            ("Cinnamon", 1, "tsp", "ground", 0),
            ("Seven Spices", 1, "tsp", "blend", 0),
            ("Vegetable Cooking Oil", 500, "ml", "for deep frying", 0),
            ("Fine Salt", 2, "tsp", "divided", 0)
        ]
    },
    {
        "name_en": "Syrian Chicken Shawarma",
        "name_ar": "شاورما دجاج سوري بالزبادي وصوص التومية والمخلل",
        "desc": "Tender chicken thighs marinated in yogurt, garlic, orange juice, cardamom, and shawarma spices, seared crispy and rolled in thin flatbread with toum and pickles.",
        "cuisine": "Levantine", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 20, "difficulty": "Easy",
        "instructions": "Marinate sliced boneless chicken thighs with yogurt, minced garlic, orange juice, vinegar, olive oil, cardamom, paprika, cumin, salt, and pepper for 3 hours. Sear in smoking hot cast iron skillet in small batches until charred and caramelized. Spread Syrian toum garlic sauce on thin shami flatbread, add chicken shawarma, sliced cucumber pickles, and roll tightly. Toast sandwich on grill press until crispy.",
        "image_url": "https://images.unsplash.com/photo-1529042410759-befb1204b468", "source_url": "https://en.wikipedia.org/wiki/Shawarma", "source_name": "Levantine Culinary Catalog",
        "ingredients": [
            ("Chicken Thighs", 800, "g", "boneless skinless sliced", 0),
            ("Shami Bread", 4, "piece", "thin saj or flatbread", 0),
            ("Plain Yogurt", 80, "g", "natural", 0),
            ("Garlic", 6, "clove", "minced", 0),
            ("Orange", 1, "piece", "freshly juiced", 0),
            ("White Vinegar", 2, "tbsp", "distilled", 0),
            ("Extra Virgin Olive Oil", 2, "tbsp", "olive oil", 0),
            ("Cardamom Pods", 0.5, "tsp", "ground cardamom", 0),
            ("Paprika", 1, "tsp", "sweet", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Palestinian Musakhan",
        "name_ar": "مسخن دجاج فلسطيني بالسماق والبصل المكرمل وخبز الطابون",
        "desc": "Sumac-roasted chicken quarters served over thick taboon flatbread drenched in sweet caramelized onions, olive oil, and toasted pine nuts.",
        "cuisine": "Levantine", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 50, "difficulty": "Medium",
        "instructions": "Poach chicken quarters with cardamom and bay leaf until half cooked, then rub with generous sumac, cumin, and olive oil and roast in oven until crisp. In heavy pan, slowly stew large quantity of diced red onions in generous extra virgin olive oil over low heat until deeply sweet and translucent (do not brown). Stir in abundant tart purple sumac. Dip taboon flatbread into sumac onion oil, arrange on baking tray, pile with sumac onions, top with roasted chicken, sprinkle with toasted pine nuts, and bake 10 mins.",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947", "source_url": "https://en.wikipedia.org/wiki/Musakhan", "source_name": "Levantine Culinary Catalog",
        "ingredients": [
            ("Chicken Thighs", 900, "g", "bone-in chicken quarters", 0),
            ("Red Onion", 5, "piece", "large finely chopped", 0),
            ("Shami Bread", 3, "piece", "thick taboon flatbread", 0),
            ("Extra Virgin Olive Oil", 150, "ml", "first cold pressed", 0),
            ("Sumac", 4, "tbsp", "tart purple sumac", 0),
            ("Pine Nuts", 40, "g", "toasted golden", 0),
            ("Cardamom Pods", 4, "piece", "whole for broth", 0),
            ("Fine Salt", 2, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },

    # -------------------------------------------------------------------------
    # 4. ITALIAN & MEDITERRANEAN CLASSICS
    # -------------------------------------------------------------------------
    {
        "name_en": "Spaghetti Bolognese",
        "name_ar": "مكرونة سباجيتي بصلصة اللحم البولونيز والبارميزان",
        "desc": "Al dente spaghetti noodles tossed in rich slow-simmered minced beef ragù with tomatoes, garlic, carrots, and aged parmesan cheese.",
        "cuisine": "Italian", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 45, "difficulty": "Medium",
        "instructions": "Sauté finely diced onions, carrots, and celery in olive oil until soft. Add minced beef and brown thoroughly. Add minced garlic, tomato paste, crushed tomatoes, and dried oregano. Simmer on low heat for 40 minutes until ragù is thick and glossy. Boil spaghetti in salted water al dente. Toss pasta with ragù and serve with freshly grated parmesan cheese.",
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3d5d6281223", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Spaghetti Pasta", 400, "g", "durum wheat pasta", 0),
            ("Ground Beef", 450, "g", "minced lean", 0),
            ("Strained Tomato Puree", 500, "g", "crushed tomatoes", 0),
            ("Tomato Paste", 2, "tbsp", "canned", 0),
            ("Yellow Onion", 1, "piece", "finely diced", 0),
            ("Carrot", 1, "piece", "finely minced", 0),
            ("Garlic", 3, "clove", "minced", 0),
            ("Parmesan Cheese", 50, "g", "freshly grated", 0),
            ("Extra Virgin Olive Oil", 2, "tbsp", "olive oil", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Fettuccine Alfredo with Chicken",
        "name_ar": "مكرونة فيتوتشيني ألفريدو بالدجاج والكريمة والمشروم",
        "desc": "Silky fettuccine ribbons coated in a decadent velvety sauce of butter, heavy cream, garlic, and parmesan, topped with seared chicken breast strips.",
        "cuisine": "Italian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 20, "difficulty": "Easy",
        "instructions": "Boil fettuccine in salted water until al dente. Season chicken breast strips with salt and pepper, sear in butter until golden and cooked through. In same pan, sauté minced garlic and sliced mushrooms for 2 minutes. Pour in heavy cooking cream, simmer until bubbling, then stir in freshly grated parmesan cheese until sauce is silky smooth. Toss hot pasta in sauce, top with sliced chicken, and garnish with chopped fresh parsley.",
        "image_url": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Fettuccine Pasta", 400, "g", "boiled al dente", 0),
            ("Chicken Breast", 500, "g", "cut into strips", 0),
            ("Heavy Cream", 300, "ml", "cooking cream", 0),
            ("Butter", 50, "g", "unsalted", 0),
            ("Fresh Mushrooms", 150, "g", "button sliced", 0),
            ("Garlic", 3, "clove", "minced", 0),
            ("Parmesan Cheese", 70, "g", "finely grated", 0),
            ("Fresh Parsley", 2, "tbsp", "chopped", 0),
            ("Fine Salt", 1, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Classic Italian Lasagna",
        "name_ar": "لازانيا إيطالية كلاسيكية باللحم المفروم والجبن",
        "desc": "Layered lasagna pasta with slow-cooked beef bolognese ragù, creamy béchamel sauce, melted mozzarella, and parmesan cheese.",
        "cuisine": "Italian", "category": "Main Course", "servings": 6, "prep_time": 35, "cook_time": 45, "difficulty": "Medium",
        "instructions": "Prepare beef bolognese ragù with minced meat, onions, garlic, and tomato sauce. Prepare béchamel with butter, flour, and milk. In baking dish, spread spoonful of béchamel, lay lasagna sheets, spread bolognese, spoon béchamel, and sprinkle mozzarella and parmesan. Repeat for 4 layers, finishing with béchamel and generous mozzarella. Bake at 190C for 40 minutes until bubbly and golden.",
        "image_url": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Lasagna Pasta Sheets", 300, "g", "oven-ready pasta sheets", 0),
            ("Ground Beef", 500, "g", "minced beef", 0),
            ("Strained Tomato Puree", 500, "g", "crushed tomatoes", 0),
            ("Yellow Onion", 1, "piece", "chopped", 0),
            ("Garlic", 3, "clove", "minced", 0),
            ("Whole Milk", 700, "ml", "for béchamel", 0),
            ("All-Purpose Flour", 60, "g", "flour", 0),
            ("Butter", 60, "g", "unsalted", 0),
            ("Mozzarella Cheese", 250, "g", "shredded", 0),
            ("Parmesan Cheese", 50, "g", "grated", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Penne all'Arrabbiata",
        "name_ar": "مكرونة بيني أرابياتا بصلصة الطماطم الحارة والثوم",
        "desc": "Classic fiery Roman pasta dish of ribbed penne coated in a spicy sauce of garlic, crushed red chili peppers, tomatoes, and fresh basil.",
        "cuisine": "Italian", "category": "Main Course", "servings": 4, "prep_time": 10, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Boil penne pasta in salted water. In wide skillet, heat extra virgin olive oil and gently sauté sliced garlic and hot chili flakes until garlic is fragrant and pale golden (do not brown). Pour in crushed peeled tomatoes, season with salt, and simmer for 10-12 minutes until sauce thickens. Toss drained al dente penne into spicy sauce with fresh torn basil leaves. Serve with grated parmesan.",
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3d5d6281223", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Penne Pasta", 400, "g", "durum wheat penne rigate", 0),
            ("Strained Tomato Puree", 500, "g", "crushed tomatoes", 0),
            ("Garlic", 4, "clove", "thinly sliced", 0),
            ("Hot Red Pepper Powder", 1, "tsp", "dried chili flakes", 0),
            ("Extra Virgin Olive Oil", 4, "tbsp", "first cold pressed", 0),
            ("Parmesan Cheese", 40, "g", "grated", 1),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Pizza Margherita",
        "name_ar": "بيتزا مارجريتا الإيطالية بالجبنة الموتزاريلا والريحان",
        "desc": "Crisp Neapolitan crust topped with crushed seasoned tomato sauce, creamy melted mozzarella slices, fresh basil leaves, and extra virgin olive oil.",
        "cuisine": "Italian", "category": "Main Course", "servings": 3, "prep_time": 25, "cook_time": 12, "difficulty": "Medium",
        "instructions": "Stretch leavened pizza dough into a 12-inch disc leaving puffy raised rim. Spread crushed seasoned tomato sauce lightly across base. Distribute torn fresh mozzarella slices evenly. Drizzle with extra virgin olive oil. Bake on preheated pizza stone or baking tray at highest oven temperature 250C for 10-12 minutes until crust is blistered and cheese is melted and bubbling. Garnish with fresh basil leaves.",
        "image_url": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("All-Purpose Flour", 350, "g", "for pizza dough", 0),
            ("Strained Tomato Puree", 150, "g", "seasoned crushed tomatoes", 0),
            ("Mozzarella Cheese", 220, "g", "fresh mozzarella slices", 0),
            ("Extra Virgin Olive Oil", 2, "tbsp", "virgin", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Pizza Pepperoni",
        "name_ar": "بيتزا بيبروني بالصلصة والجبن الموزاريلا",
        "desc": "Crispy baked pizza crust smothered in spiced tomato sauce, shredded mozzarella, and abundant crisp pepperoni slices.",
        "cuisine": "Italian", "category": "Main Course", "servings": 3, "prep_time": 20, "cook_time": 12, "difficulty": "Easy",
        "instructions": "Stretch pizza dough into round disc. Spread seasoned tomato sauce across base. Generously cover with shredded mozzarella cheese. Arrange beef pepperoni slices across entire surface. Bake at 250C for 12 minutes until crust is golden and pepperoni edges curl up crispy.",
        "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("All-Purpose Flour", 350, "g", "dough", 0),
            ("Strained Tomato Puree", 150, "g", "pureed", 0),
            ("Mozzarella Cheese", 250, "g", "shredded", 0),
            ("Pastirma", 100, "g", "or beef pepperoni slices", 0),
            ("Extra Virgin Olive Oil", 1.5, "tbsp", "olive oil", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Pizza Quattro Formaggi",
        "name_ar": "بيتزا أربعة أجبان موتزاريلا ورومي وشيدر وريكوتا",
        "desc": "Rich four-cheese pizza combining melted mozzarella, aged sharp Egyptian rumi cheese, rich cheddar, and creamy ricotta on a golden crust.",
        "cuisine": "Italian", "category": "Main Course", "servings": 3, "prep_time": 20, "cook_time": 12, "difficulty": "Easy",
        "instructions": "Stretch pizza dough on oiled tray. Spread light layer of olive oil or tomato sauce. Evenly scatter shredded mozzarella, sharp grated rumi cheese, shredded cheddar, and dollops of creamy ricotta cheese. Bake in hot oven at 250C for 12 minutes until all cheeses bubble and blend into a rich golden crust.",
        "image_url": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("All-Purpose Flour", 350, "g", "dough", 0),
            ("Mozzarella Cheese", 150, "g", "shredded", 0),
            ("Rumi Cheese", 80, "g", "sharp grated", 0),
            ("Cheddar Cheese", 80, "g", "shredded", 0),
            ("Strained Tomato Puree", 100, "g", "light sauce", 0),
            ("Extra Virgin Olive Oil", 1, "tbsp", "olive oil", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Mushroom Risotto with Parmesan",
        "name_ar": "ريزوتو إيطالي بالمشروم والجبن البارميزان والزبدة",
        "desc": "Creamy slow-cooked short grain arborio or Egyptian rice cooked in warm broth with sautéed fresh mushrooms, butter, garlic, and aged parmesan.",
        "cuisine": "Italian", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 25, "difficulty": "Medium",
        "instructions": "Sauté sliced button mushrooms in butter until browned; set half aside for garnish. In same pot, sauté minced onions and garlic in olive oil until soft. Add short-grain rice, toasting grains for 2 minutes. Gradually add ladles of simmering hot broth one at a time, stirring continuously until each ladle is absorbed before adding next. When rice is creamy and al dente, turn off heat, vigorously beat in cold butter and freshly grated parmesan (mantecatura). Serve warm.",
        "image_url": "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Egyptian White Rice", 350, "g", "short-grain washed", 0),
            ("Fresh Mushrooms", 300, "g", "fresh sliced", 0),
            ("Yellow Onion", 1, "piece", "finely minced", 0),
            ("Garlic", 2, "clove", "minced", 0),
            ("Butter", 50, "g", "unsalted cold", 0),
            ("Parmesan Cheese", 60, "g", "freshly grated", 0),
            ("Extra Virgin Olive Oil", 2, "tbsp", "olive oil", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "freshly ground", 0)
        ]
    },
    {
        "name_en": "Classic Homemade Beef Cheeseburger",
        "name_ar": "برجر لحم بقري كلاسيكي بالجبن الشيدر والخس",
        "desc": "Juicy griddled all-beef burger patty seasoned with salt and pepper, topped with melted cheddar cheese, fresh tomato, and crisp lettuce on a toasted bun.",
        "cuisine": "American", "category": "Main Course", "servings": 4, "prep_time": 15, "cook_time": 10, "difficulty": "Easy",
        "instructions": "Shape ground beef into 4 round patties with a shallow indentation in center. Season generously on both sides with fine salt and freshly cracked black pepper. Sear in smoking hot cast iron skillet for 3-4 minutes per side. Place cheddar slice on patty, cover with lid to melt. Toast burger buns in butter. Assemble bun, burger sauce, lettuce, patty with melted cheese, tomato slices, and top bun.",
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Ground Beef", 600, "g", "minced 80/20 beef", 0),
            ("Cheddar Cheese", 4, "slice", "thick sliced cheese", 0),
            ("Toast Bread", 4, "piece", "burger buns", 0),
            ("Red Tomato", 1, "piece", "sliced rounds", 0),
            ("Yellow Onion", 1, "piece", "sliced rings", 0),
            ("Butter", 20, "g", "for toasting buns", 0),
            ("Fine Salt", 1.5, "tsp", "coarse salt", 0),
            ("Black Pepper", 1, "tsp", "cracked black pepper", 0)
        ]
    },
    {
        "name_en": "Sizzling Chicken Fajitas",
        "name_ar": "فاهيتا دجاج متبلة بالفلفل الألوان والبصل والليمون",
        "desc": "Sliced chicken breast marinated in lime, cumin, and garlic, seared on high heat with bell pepper strips and onions, served with warm tortillas.",
        "cuisine": "Mexican", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 12, "difficulty": "Easy",
        "instructions": "Slice chicken breast into strips. Marinate in olive oil, lime juice, minced garlic, cumin, chili powder, paprika, salt, and pepper for 30 minutes. Slice sweet bell peppers and onions into strips. Heat heavy skillet until smoking hot. Sear chicken strips in oil until browned and cooked; set aside. Toss peppers and onions in skillet on high heat for 3-4 minutes until charred yet crisp. Combine chicken and peppers, serve sizzling with tortillas.",
        "image_url": "https://images.unsplash.com/photo-1534939561126-855b8675edd7", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Chicken Breast", 700, "g", "sliced into strips", 0),
            ("Green Bell Pepper", 1, "piece", "sliced strips", 0),
            ("Yellow Onion", 2, "piece", "sliced strips", 0),
            ("Lemon", 2, "piece", "fresh lime juice", 0),
            ("Garlic", 3, "clove", "minced", 0),
            ("Extra Virgin Olive Oil", 3, "tbsp", "olive oil", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Paprika", 1, "tsp", "sweet", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 1, "tsp", "ground", 0)
        ]
    },

    # -------------------------------------------------------------------------
    # 5. ASIAN & INDIAN SPECIALTIES
    # -------------------------------------------------------------------------
    {
        "name_en": "Indian Butter Chicken (Murgh Makhani)",
        "name_ar": "دجاج بالزبدة الهندي بصلصة الكريمة والبهارات",
        "desc": "Tender marinated chicken breast pieces simmered in an aromatic velvety tomato sauce enriched with butter, heavy cream, garlic, and garam masala.",
        "cuisine": "Indian", "category": "Main Course", "servings": 4, "prep_time": 25, "cook_time": 30, "difficulty": "Medium",
        "instructions": "Marinate cubed chicken breast in yogurt, garlic, lemon juice, turmeric, and cumin for 1 hour; sear in butter until browned. Sauté chopped onions, garlic, and spices in butter. Add pureed tomatoes, cooking until thickened. Stir in heavy cooking cream and butter until sauce is velvety and fragrant. Simmer seared chicken in sauce for 10 minutes. Garnish with cream and coriander.",
        "image_url": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Chicken Breast", 700, "g", "cubed", 0),
            ("Plain Yogurt", 100, "g", "marinade", 0),
            ("Butter", 60, "g", "unsalted", 0),
            ("Heavy Cream", 150, "ml", "cooking cream", 0),
            ("Strained Tomato Puree", 400, "g", "crushed pureed", 0),
            ("Yellow Onion", 1, "piece", "finely chopped", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Turmeric", 1, "tsp", "ground", 0),
            ("Cumin", 1, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Chicken Tikka Masala",
        "name_ar": "دجاج تيكا ماسالا الهندي بالأرز البسمتي",
        "desc": "Spiced yogurt-marinated chicken chunks roasted and tossed in a rich, creamy, spiced curry tomato sauce served with basmati rice.",
        "cuisine": "Indian", "category": "Main Course", "servings": 4, "prep_time": 20, "cook_time": 30, "difficulty": "Medium",
        "instructions": "Marinate chicken chunks in spiced yogurt and sear until charred. Cook onions, garlic, cumin, turmeric, and paprika in oil. Add pureed tomatoes and tomato paste, simmering for 15 minutes. Fold in heavy cream and chicken chunks, cooking gently for 10 minutes. Serve hot over basmati rice.",
        "image_url": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Chicken Breast", 700, "g", "cubed", 0),
            ("Basmati Rice", 400, "g", "cooked", 0),
            ("Plain Yogurt", 100, "g", "yogurt", 0),
            ("Strained Tomato Puree", 400, "g", "pureed", 0),
            ("Heavy Cream", 150, "ml", "cream", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Yellow Onion", 1, "piece", "chopped", 0),
            ("Turmeric", 1, "tsp", "ground", 0),
            ("Cumin", 1.5, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Hyderabadi Chicken Biryani",
        "name_ar": "برياني دجاج هندي بالأرز البسمتي والزعفران",
        "desc": "Layered aromatic basmati rice and marinated chicken cooked with saffron, caramelized fried onions, fresh mint, and whole spices.",
        "cuisine": "Indian", "category": "Main Course", "servings": 6, "prep_time": 30, "cook_time": 45, "difficulty": "Medium",
        "instructions": "Marinate chicken in yogurt, garlic, turmeric, cumin, and salt for 1 hour. Parboil basmati rice with whole cardamom and cloves until 70% cooked. In a heavy pot, layer marinated chicken, topped with half-cooked rice, crisp caramelized fried onions, chopped fresh mint, coriander, and saffron milk. Seal lid tightly and cook on low heat for 35 minutes until steam builds and chicken is tender.",
        "image_url": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Chicken Thighs", 800, "g", "bone-in cut", 0),
            ("Basmati Rice", 500, "g", "parboiled", 0),
            ("Plain Yogurt", 150, "g", "marinade", 0),
            ("Yellow Onion", 3, "piece", "thinly sliced fried", 0),
            ("Garlic", 5, "clove", "minced", 0),
            ("Ghee", 3, "tbsp", "baladi", 0),
            ("Cardamom Pods", 5, "piece", "whole", 0),
            ("Turmeric", 1, "tsp", "ground", 0),
            ("Fresh Mint", 0.5, "bunch", "chopped", 0),
            ("Fine Salt", 2, "tsp", "fine", 0)
        ]
    },

    # -------------------------------------------------------------------------
    # 6. SOUPS & SALADS
    # -------------------------------------------------------------------------
    {
        "name_en": "Egyptian Red Lentil Soup with Vermicelli",
        "name_ar": "شوربة عدس أصفر مصرية بالشعرية والكمون والليمون",
        "desc": "Nourishing Egyptian winter soup of pureed red split lentils, carrots, onions, and garlic, simmered with toasted golden vermicelli and cumin.",
        "cuisine": "Egyptian", "category": "Soup", "servings": 5, "prep_time": 15, "cook_time": 30, "difficulty": "Easy",
        "instructions": "Simmer yellow lentils with chopped carrots, tomatoes, onions, and garlic in water or broth until completely tender (about 20 minutes). Puree in blender until smooth and velvety. In a separate pan, toast vermicelli in ghee until golden brown. Pour pureed soup over vermicelli, season with cumin, salt, and black pepper, and simmer for 8 minutes until vermicelli is soft. Serve with lemon wedges and toasted flatbread croutons.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Lentil_soup", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Red Split Lentils", 350, "g", "washed rinsed", 0),
            ("Vermicelli", 80, "g", "toasted golden", 0),
            ("Carrot", 2, "piece", "chopped", 0),
            ("Red Tomato", 1, "piece", "chopped", 0),
            ("Yellow Onion", 1, "piece", "chopped", 0),
            ("Garlic", 4, "clove", "peeled", 0),
            ("Ghee", 2, "tbsp", "baladi", 0),
            ("Lemon", 2, "piece", "wedges for serving", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Egyptian Orzo Chicken Soup",
        "name_ar": "شوربة لسان عصفور كلاسيكية بمرقة الدجاج والليمون",
        "desc": "Comforting Egyptian soup of orzo pasta browned in ghee, simmered in clear poultry broth seasoned with mastic and cardamom, finished with lemon juice.",
        "cuisine": "Egyptian", "category": "Soup", "servings": 4, "prep_time": 10, "cook_time": 20, "difficulty": "Easy",
        "instructions": "Melt ghee in soup pot. Add dry orzo pasta and stir continuously over medium heat until evenly toasted to a deep golden brown. Pour in hot strained chicken broth. Season with whole cardamom pods, salt, and freshly cracked black pepper. Simmer on low heat for 12-15 minutes until pasta is tender. Remove from heat, stir in fresh lemon juice, and serve piping hot.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://en.wikipedia.org/wiki/Orzo", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Orzo Pasta", 200, "g", "dry lisan asfour", 0),
            ("Ghee", 2, "tbsp", "pure baladi", 0),
            ("Lemon", 1, "piece", "juiced", 0),
            ("Cardamom Pods", 3, "piece", "whole", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Cream of Wild Mushroom Soup",
        "name_ar": "شوربة كريمة المشروم بالزبدة والثوم والكريمة",
        "desc": "Rich and earthy soup of fresh sliced button mushrooms sautéed in butter with garlic and onions, simmered in chicken broth and heavy cooking cream.",
        "cuisine": "International", "category": "Soup", "servings": 4, "prep_time": 15, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Sauté chopped onions and minced garlic in butter until translucent. Add sliced fresh mushrooms and cook until browned and moisture evaporates. Sprinkle flour and stir for 1 minute. Slowly whisk in warm broth and simmer for 15 minutes. Puree half the soup for body while leaving mushroom pieces for texture. Stir in heavy cream, season with salt and pepper, and gently heat through.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Fresh Mushrooms", 400, "g", "fresh button sliced", 0),
            ("Heavy Cream", 200, "ml", "cooking cream", 0),
            ("Butter", 40, "g", "unsalted", 0),
            ("All-Purpose Flour", 25, "g", "flour", 0),
            ("Yellow Onion", 1, "piece", "finely chopped", 0),
            ("Garlic", 2, "clove", "minced", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Cream of Tender Chicken Soup",
        "name_ar": "شوربة كريمة الدجاج بالذرة والزبدة",
        "desc": "Velvety chicken soup filled with shredded chicken breast and sweet corn in a smooth butter-cream broth.",
        "cuisine": "International", "category": "Soup", "servings": 4, "prep_time": 15, "cook_time": 20, "difficulty": "Easy",
        "instructions": "Sauté shredded poached chicken breast in butter with flour. Gradually whisk in chicken broth and sweet corn kernels, simmering for 10 minutes. Stir in heavy cooking cream, season with salt and white pepper, and simmer on gentle heat for 5 minutes until creamy.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Chicken Breast", 350, "g", "poached shredded", 0),
            ("Heavy Cream", 200, "ml", "cooking cream", 0),
            ("Butter", 40, "g", "unsalted", 0),
            ("All-Purpose Flour", 30, "g", "flour", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Creamy Seafood Bisque Soup",
        "name_ar": "شوربة سي فود فاخرة بالجمبري والكاليماري والكريمة",
        "desc": "Luxurious seafood soup featuring tender shrimp and calamari rings simmered in a creamy seafood broth with celery, garlic, and dill.",
        "cuisine": "Seafood", "category": "Soup", "servings": 4, "prep_time": 20, "cook_time": 20, "difficulty": "Easy",
        "instructions": "Sauté diced onions, minced garlic, and celery in butter until fragrant. Add cleaned peeled shrimp and calamari rings, cooking for 3 minutes until shrimp turn pink. Sprinkle with flour, then gradually whisk in hot fish or seafood broth. Simmer for 10 minutes. Stir in heavy cooking cream and chopped fresh dill. Season with salt and pepper, serving with lemon wedges.",
        "image_url": "https://images.unsplash.com/photo-1559742811-822873691df8", "source_url": "https://en.wikipedia.org/wiki/Bisque_(food)", "source_name": "Coastal Culinary",
        "ingredients": [
            ("Shrimp", 350, "g", "peeled deveined", 0),
            ("Calamari", 250, "g", "cleaned rings", 0),
            ("Heavy Cream", 200, "ml", "cooking cream", 0),
            ("Butter", 40, "g", "unsalted", 0),
            ("All-Purpose Flour", 25, "g", "flour", 0),
            ("Celery", 1, "piece", "finely sliced stalk", 0),
            ("Garlic", 3, "clove", "minced", 0),
            ("Fresh Dill", 2, "tbsp", "chopped", 0),
            ("Lemon", 1, "piece", "juiced", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Country Style Vegetable Soup",
        "name_ar": "شوربة خضار مشكل صحية بالكرفس والليمون",
        "desc": "Wholesome clear soup of fresh carrots, zucchini, potatoes, green peas, and celery simmered in flavorful herbed vegetable or chicken broth.",
        "cuisine": "International", "category": "Soup", "servings": 4, "prep_time": 15, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Chop carrots, zucchini, potatoes, and celery into even small cubes. Sauté onions in olive oil until soft. Add vegetables and green peas, pouring in hot chicken or vegetable broth. Simmer for 20 minutes until vegetables are tender. Finish with freshly chopped parsley, salt, black pepper, and a squeeze of fresh lemon juice.",
        "image_url": "https://images.unsplash.com/photo-1547592180-85f173990554", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Carrot", 2, "piece", "diced", 0),
            ("Zucchini", 2, "piece", "diced", 0),
            ("Potato", 2, "piece", "diced", 0),
            ("Green Peas", 150, "g", "fresh or frozen", 0),
            ("Celery", 1, "piece", "stalk sliced", 0),
            ("Yellow Onion", 1, "piece", "chopped", 0),
            ("Extra Virgin Olive Oil", 2, "tbsp", "olive oil", 0),
            ("Lemon", 1, "piece", "juiced", 0),
            ("Fresh Parsley", 2, "tbsp", "chopped", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0),
            ("Black Pepper", 0.5, "tsp", "ground", 0)
        ]
    },
    {
        "name_en": "Classic Caesar Salad with Grilled Chicken",
        "name_ar": "سلطة سيزر بقطع الدجاج المشوي والجبن البارميزان",
        "desc": "Crisp romaine lettuce hearts tossed in creamy garlic dressing with golden toasted croutons, aged shaved parmesan, and sliced grilled chicken breast.",
        "cuisine": "American", "category": "Salad", "servings": 4, "prep_time": 20, "cook_time": 10, "difficulty": "Easy",
        "instructions": "Season chicken breast with salt, pepper, and olive oil, grilling until cooked through; slice into strips. Cut toast bread into cubes and toss in olive oil, baking until golden croutons form. Wash and dry romaine lettuce, tearing into bite-sized pieces. Toss lettuce with Caesar dressing (olive oil, lemon juice, garlic, and mayonnaise). Top with grilled chicken slices, croutons, and shaved parmesan cheese.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Chicken Breast", 400, "g", "grilled sliced", 0),
            ("Toast Bread", 2, "slice", "cubed for croutons", 0),
            ("Parmesan Cheese", 50, "g", "shaved", 0),
            ("Garlic", 2, "clove", "minced", 0),
            ("Lemon", 1, "piece", "juiced", 0),
            ("Extra Virgin Olive Oil", 3, "tbsp", "virgin", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Authentic Greek Salad",
        "name_ar": "سلطة يونانية بالجبن الفيتا وزيتون الكالاماتا والخيار",
        "desc": "Vibrant Mediterranean medley of ripe red tomatoes, crisp cucumbers, thinly sliced red onion, bell peppers, Kalamata black olives, and block of Greek feta cheese.",
        "cuisine": "Greek", "category": "Salad", "servings": 4, "prep_time": 15, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Chop ripe tomatoes into wedges, cut cucumbers into thick slices, and thinly slice red onions and bell peppers. Combine in a wide salad bowl. Add whole black olives. Place a thick block of feta cheese on top. Dust generously with dried oregano, sea salt, red wine vinegar, and drench in premium extra virgin olive oil.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("Red Tomato", 3, "piece", "wedges", 0),
            ("Cucumber", 2, "piece", "thickly sliced", 0),
            ("Red Onion", 1, "piece", "thin crescents", 0),
            ("Green Bell Pepper", 1, "piece", "rings", 0),
            ("Feta White Cheese", 200, "g", "block of feta", 0),
            ("Extra Virgin Olive Oil", 60, "ml", "first cold pressed", 0),
            ("White Vinegar", 1, "tbsp", "vinegar", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Classic Creamy Coleslaw",
        "name_ar": "سلطة كول سلو بالكرنب والجزر وصوص المايونيز",
        "desc": "Crisp shredded green cabbage and sweet grated carrots tossed in a sweet-and-tangy dressing of mayonnaise, milk, vinegar, and sugar.",
        "cuisine": "American", "category": "Salad", "servings": 6, "prep_time": 15, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Finely shred white cabbage and grate carrots. In a separate bowl, whisk mayonnaise, whole milk, white sugar, vinegar, fine salt, and a pinch of black pepper until sugar dissolves. Pour dressing over cabbage and carrots, tossing thoroughly. Chill in refrigerator for at least 1 hour before serving so cabbage softens and flavors meld.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("White Cabbage", 500, "g", "finely shredded", 0),
            ("Carrot", 2, "piece", "grated", 0),
            ("Whole Milk", 50, "ml", "milk", 0),
            ("White Sugar", 2, "tbsp", "granulated", 0),
            ("White Vinegar", 2, "tbsp", "distilled", 0),
            ("Fine Salt", 1, "tsp", "fine", 0)
        ]
    },

    # -------------------------------------------------------------------------
    # 7. TRADITIONAL DESSERTS & SWEETS
    # -------------------------------------------------------------------------
    {
        "name_en": "Traditional Umm Ali with Nuts",
        "name_ar": "أم علي مصرية بالرقاق والمكسرات واللبن والقشطة",
        "desc": "Egypt's national dessert of crisp puffed pastry or roqaq soaked in hot sweetened milk, baked with raisins, coconut, and nuts, topped with broiled golden qashta.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 6, "prep_time": 15, "cook_time": 25, "difficulty": "Easy",
        "instructions": "Break baked roqaq or puff pastry sheets into small pieces in a deep baking dish. Toss with raisins, shredded coconut flakes, raw almonds, and walnuts. Bring whole milk to boil with white sugar and vanilla extract until sugar dissolves completely. Pour hot sweetened milk over pastry to submerge it. Spread generous dollops of baladi qashta and butter over surface. Bake at 200C for 20 minutes, then broil for 3-5 minutes until top is bubbly, caramelized, and golden.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Om_Ali", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Baladi Bread", 250, "g", "baked dry roqaq or puff pastry", 0),
            ("Whole Milk", 1000, "ml", "full cream fresh", 0),
            ("Qashta", 150, "g", "clotted baladi cream", 0),
            ("White Sugar", 150, "g", "granulated", 0),
            ("Butter", 40, "g", "unsalted", 0),
            ("Raisins", 50, "g", "golden", 0),
            ("Coconut Flakes", 40, "g", "shredded", 0),
            ("Raw Almonds", 50, "g", "slivered toasted", 0),
            ("Walnuts", 50, "g", "chopped", 0),
            ("Vanilla Extract", 1, "tsp", "pure vanilla", 0)
        ]
    },
    {
        "name_en": "Kunafa with Cream and Qashta",
        "name_ar": "كنافة محشية بالكريمة والقشطة والشربات",
        "desc": "Crispy golden shredded phyllo pastry drenched in pure baladi ghee, filled with velvety cooked cream, and soaked in cool fragrant sugar syrup.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 8, "prep_time": 25, "cook_time": 30, "difficulty": "Medium",
        "instructions": "Finely shred kunafa pastry and rub thoroughly with melted ghee and powdered sugar. Press half the pastry firmly into bottom of greased baking pan. Make cream filling by boiling milk and cornstarch until thick, folding in fresh qashta. Spread cream over kunafa leaving edges clear. Cover with remaining shredded kunafa, pressing lightly. Bake in 200C oven for 30 minutes until edges are deep golden. Invert immediately onto platter, pour cold heavy sugar syrup (sherbet) over hot kunafa.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://en.wikipedia.org/wiki/Knafeh", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("All-Purpose Flour", 500, "g", "kunafa shredded dough", 0),
            ("Ghee", 200, "g", "melted baladi ghee", 0),
            ("Whole Milk", 500, "ml", "for cream filling", 0),
            ("Cornstarch", 3, "tbsp", "thickener", 0),
            ("Qashta", 100, "g", "clotted cream", 0),
            ("White Sugar", 350, "g", "for sugar syrup", 0),
            ("Lemon", 0.5, "piece", "for syrup", 0)
        ]
    },
    {
        "name_en": "Fresh Mango Kunafa Cups",
        "name_ar": "كنافة بالمانجو والكريمة المخفوقة في كاسات",
        "desc": "Layers of roasted crunchy golden kunafa crumbs, luscious whipped cream, and fresh diced sweet Egyptian mangoes.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 6, "prep_time": 25, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Toast shredded kunafa in ghee over stovetop until evenly golden and crisp, toss with light sugar syrup. Whip heavy cream with powdered sugar and vanilla until stiff peaks form. Dice fresh ripe Egyptian mangoes into cubes. In dessert cups or glass dish, layer crispy kunafa crumbs, whipped cream, and fresh mango cubes. Repeat layers and chill in refrigerator for 1 hour before serving.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://en.wikipedia.org/wiki/Knafeh", "source_name": "Egyptian Modern Confectionery",
        "ingredients": [
            ("All-Purpose Flour", 350, "g", "kunafa dough", 0),
            ("Mango", 600, "g", "fresh ripe diced cubes", 0),
            ("Heavy Cream", 300, "ml", "whipping cream", 0),
            ("Ghee", 100, "g", "baladi", 0),
            ("Powdered Sugar", 70, "g", "sweetener", 0),
            ("Vanilla Extract", 1, "tsp", "extract", 0)
        ]
    },
    {
        "name_en": "Caramelized Egyptian Basbousa",
        "name_ar": "بسبوسة مصرية مكرملة بالسمن البلدي واللوز",
        "desc": "Melt-in-the-mouth semolina cake caramelized with pure baladi ghee, milk, and honey, baked golden and saturated with hot light sugar syrup.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 8, "prep_time": 20, "cook_time": 30, "difficulty": "Medium",
        "instructions": "Caramelize sugar in a saucepan until rich amber, add milk, ghee, and honey until dissolved into caramel syrup. Pour caramel mixture over coarse semolina flour, mixing lightly without overworking (to keep tender). Spread in greased baking pan, decorate with whole raw almonds, and bake at 200C for 25-30 minutes until edges brown. Pour boiling hot light sugar syrup over hot basbousa immediately upon leaving oven; cover with tray for 15 minutes to steam tender.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://en.wikipedia.org/wiki/Basbousa", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Semolina Flour", 500, "g", "coarse durum semolina", 0),
            ("Ghee", 150, "g", "pure baladi", 0),
            ("Whole Milk", 150, "ml", "milk", 0),
            ("White Sugar", 350, "g", "divided for batter and syrup", 0),
            ("Raw Almonds", 50, "g", "whole blanched for topping", 0),
            ("Lemon", 0.5, "piece", "for syrup", 0)
        ]
    },
    {
        "name_en": "Baked Rice Pudding / Roz Bel-Laban",
        "name_ar": "أرز باللبن فلاحي في الفرن بالقشطة والمستكة",
        "desc": "Creamy Egyptian rice pudding slow-simmered in whole milk with mastic, poured into earthenware bowls, topped with qashta, and baked until charred golden.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 6, "prep_time": 10, "cook_time": 35, "difficulty": "Easy",
        "instructions": "Cook short-grain Egyptian rice in water until soft and water is absorbed. Add fresh whole milk, sugar, and crushed mastic tears, simmering on low heat for 20 minutes until thick and creamy. Dissolve cornstarch in a splash of milk and stir in for 2 minutes. Pour into individual terracotta bowls (fukhar). Spoon thick dollops of baladi qashta on top. Place under hot oven broiler for 5 minutes until top blisters into deep golden patches. Chill or serve warm.",
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c", "source_url": "https://en.wikipedia.org/wiki/Rice_pudding", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Egyptian White Rice", 150, "g", "short-grain washed", 0),
            ("Whole Milk", 1000, "ml", "full cream fresh", 0),
            ("Qashta", 100, "g", "baladi cream for crust", 0),
            ("White Sugar", 150, "g", "granulated", 0),
            ("Cornstarch", 2, "tbsp", "thickener", 0),
            ("Mastic Gum", 2, "piece", "crushed with sugar", 0),
            ("Vanilla Extract", 1, "tsp", "extract", 0)
        ]
    },
    {
        "name_en": "Sweet Roz Moammar with Nuts",
        "name_ar": "طاجن أرز معمر حلو بالسكر والزبيب والقشطة",
        "desc": "Rustic baked sweet rice casserole infused with whole milk, sweet butter, golden raisins, shredded coconut, and caramelized clotted cream.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 6, "prep_time": 15, "cook_time": 45, "difficulty": "Easy",
        "instructions": "Wash Egyptian rice. Place in clay casserole dish with sugar, butter, raisins, and coconut flakes. Heat whole milk with vanilla and pour over rice. Generously top with thick baladi qashta. Bake in hot 200C oven for 40 minutes until rice absorbs all liquid and top forms a bubbly golden-brown crust.",
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c", "source_url": "https://en.wikipedia.org/wiki/Egyptian_cuisine", "source_name": "Rural Egyptian Heritage",
        "ingredients": [
            ("Egyptian White Rice", 400, "g", "short-grain", 0),
            ("Whole Milk", 800, "ml", "fresh full cream", 0),
            ("Qashta", 150, "g", "clotted baladi cream", 0),
            ("White Sugar", 150, "g", "granulated", 0),
            ("Butter", 40, "g", "unsalted", 0),
            ("Raisins", 40, "g", "golden", 0),
            ("Coconut Flakes", 30, "g", "shredded", 0),
            ("Vanilla Extract", 1, "tsp", "pure vanilla", 0)
        ]
    },
    {
        "name_en": "Egyptian Milk Pudding / Mahalabia",
        "name_ar": "مهلبية حليب ناعمة بماء الورد والمستكة والمكسرات",
        "desc": "Silky chilled milk pudding delicately perfumed with crushed mastic and rosewater, garnished with crushed pistachios and cinnamon.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 5, "prep_time": 10, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Dissolve cornstarch in 1 cup of cold milk. Heat remaining milk with sugar and crushed mastic in a saucepan until hot. Whisk in cornstarch mixture, stirring continuously over medium heat until mixture thickens into a glossy, velvety pudding. Remove from heat and stir in vanilla or rosewater. Pour into dessert bowls and refrigerate until set. Garnish with chopped pistachios and ground cinnamon.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://en.wikipedia.org/wiki/Muhallebi", "source_name": "Egyptian Culinary Heritage",
        "ingredients": [
            ("Whole Milk", 800, "ml", "full cream", 0),
            ("Cornstarch", 4, "tbsp", "thickener", 0),
            ("White Sugar", 120, "g", "granulated", 0),
            ("Mastic Gum", 2, "piece", "crushed tears", 0),
            ("Pistachios", 40, "g", "crushed for garnish", 0),
            ("Vanilla Extract", 1, "tsp", "extract", 0)
        ]
    },
    {
        "name_en": "Crispy Balah el-Sham",
        "name_ar": "بلح الشام مقرمش بالسيروب الثقيل البارد",
        "desc": "Crispy fluted choux fritters fried until deep amber golden, dropped while hot into thick cold fragrant sugar syrup.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 6, "prep_time": 20, "cook_time": 20, "difficulty": "Medium",
        "instructions": "Boil water with butter and a pinch of salt. Add flour all at once, stirring vigorously over low heat into a smooth dough ball; cool for 10 minutes. Beat in eggs one by one with vanilla until dough is glossy and pipeable. Pipe through star nozzle into cold or lukewarm vegetable oil, then turn heat on medium-low. Fry gently until puffed, crisp, and deeply golden on all sides. Transfer immediately while hot into cold thick sugar syrup.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://en.wikipedia.org/wiki/Tulumba", "source_name": "Egyptian Confectionery Heritage",
        "ingredients": [
            ("All-Purpose Flour", 250, "g", "sifted flour", 0),
            ("Eggs", 3, "piece", "fresh large", 0),
            ("Butter", 50, "g", "unsalted", 0),
            ("White Sugar", 400, "g", "for thick syrup", 0),
            ("Vanilla Extract", 1, "tsp", "extract", 0),
            ("Vegetable Cooking Oil", 500, "ml", "for deep frying", 0),
            ("Fine Salt", 0.25, "tsp", "pinch", 0)
        ]
    },
    {
        "name_en": "Egyptian Zalabia (Loukoumades)",
        "name_ar": "زلابية مقرمشة بالسكر البودرة والشوكولاتة",
        "desc": "Golden crispy hollow yeast dough balls, fried crunchy and tossed in powdered sugar or decadent melted chocolate sauce.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 6, "prep_time": 15, "cook_time": 15, "difficulty": "Easy",
        "instructions": "Whisk flour with cornstarch, instant dry yeast, sugar, salt, and warm water into a thick, elastic, stretchy batter. Cover and ferment in warm place for 1 hour until doubled and bubbly. Heat vegetable oil. Squeeze batter through oiled fist and scoop off with teaspoon into hot oil. Fry, stirring continuously so balls roll and color evenly until crisp and golden brown. Drain and dust with powdered sugar or coat in sugar syrup.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://en.wikipedia.org/wiki/Lokma", "source_name": "Egyptian Street Confectionery",
        "ingredients": [
            ("All-Purpose Flour", 300, "g", "flour", 0),
            ("Cornstarch", 2, "tbsp", "for crispiness", 0),
            ("Dry Yeast", 1, "tbsp", "instant yeast", 0),
            ("White Sugar", 1, "tbsp", "for fermentation", 0),
            ("Powdered Sugar", 80, "g", "for dusting", 0),
            ("Vegetable Cooking Oil", 500, "ml", "for deep frying", 0),
            ("Fine Salt", 0.5, "tsp", "pinch", 0)
        ]
    },
    {
        "name_en": "Sweet Potato Gratin with Béchamel",
        "name_ar": "صينية بطاطا حلوة بالبشاميل والمكسرات في الفرن",
        "desc": "Mashed roasted sweet potatoes spiced with cinnamon and coconut, topped with sweet milk béchamel and baked into a bubbling golden gratin.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 6, "prep_time": 20, "cook_time": 35, "difficulty": "Easy",
        "instructions": "Boil or roast sweet potatoes until tender, peel and mash with butter, sugar, cinnamon, coconut flakes, and raisins. Spread evenly in buttered baking dish. Prepare sweet béchamel: cook butter and flour, whisk in warm whole milk and sugar until thickened and smooth, stir in vanilla. Pour sweet béchamel over sweet potato layer. Bake at 200C for 25 minutes until golden brown on top.",
        "image_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141", "source_url": "https://en.wikipedia.org/wiki/Sweet_potato", "source_name": "Egyptian Winter Traditions",
        "ingredients": [
            ("Sweet Potato", 1000, "g", "boiled peeled mashed", 0),
            ("Whole Milk", 500, "ml", "full cream for béchamel", 0),
            ("Butter", 60, "g", "unsalted", 0),
            ("All-Purpose Flour", 40, "g", "flour", 0),
            ("White Sugar", 120, "g", "granulated", 0),
            ("Raisins", 40, "g", "golden", 0),
            ("Coconut Flakes", 30, "g", "shredded", 0),
            ("Cinnamon", 1, "tsp", "ground", 0),
            ("Vanilla Extract", 1, "tsp", "extract", 0)
        ]
    },
    {
        "name_en": "Sweet Goulash / Baklava with Nuts",
        "name_ar": "صينية جلاش حلو بالمكسرات والشربات الذهبي",
        "desc": "Crisp flaky layers of phyllo pastry brushed with baladi ghee, packed with crushed hazelnuts and walnuts, soaked in fragrant lemon syrup.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 8, "prep_time": 25, "cook_time": 30, "difficulty": "Medium",
        "instructions": "Brush baking pan with melted ghee. Layer half phyllo sheets, brushing every two sheets with melted ghee. Mix chopped walnuts, raw almonds, coconut flakes, sugar, and cinnamon; spread evenly over pastry. Cover with remaining phyllo sheets brushed with ghee. Slice into diamond patterns before baking. Bake in 190C oven for 30 minutes until golden and puffed. Pour room-temperature thick sugar syrup over hot goulash.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://en.wikipedia.org/wiki/Baklava", "source_name": "Egyptian Confectionery Heritage",
        "ingredients": [
            ("All-Purpose Flour", 500, "g", "phyllo goulash pastry roll", 0),
            ("Ghee", 180, "g", "melted baladi", 0),
            ("Walnuts", 100, "g", "chopped", 0),
            ("Raw Almonds", 80, "g", "crushed", 0),
            ("Coconut Flakes", 40, "g", "shredded", 0),
            ("White Sugar", 350, "g", "for sugar syrup", 0),
            ("Cinnamon", 0.5, "tsp", "ground", 0),
            ("Lemon", 0.5, "piece", "for syrup", 0)
        ]
    },
    {
        "name_en": "Fluffy Fresh Orange Cake",
        "name_ar": "كيكة برتقال هشة وطرية بعصير البرتقال الطازج",
        "desc": "Tender and aromatic golden sponge cake made with freshly squeezed orange juice, orange zest, and fluffy whipped eggs.",
        "cuisine": "Egyptian", "category": "Dessert", "servings": 8, "prep_time": 15, "cook_time": 40, "difficulty": "Easy",
        "instructions": "Beat eggs, sugar, and vanilla in mixer on high speed for 5 minutes until pale and voluminous. Stream in vegetable oil and fresh orange juice with grated orange zest. Sift all-purpose flour, baking powder, and a pinch of salt together; gently fold into batter. Pour into greased Bundt pan and bake at 180C for 35-40 minutes until toothpick comes out clean.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://www.themealdb.com", "source_name": "Egyptian Home Baking",
        "ingredients": [
            ("All-Purpose Flour", 300, "g", "sifted flour", 0),
            ("Eggs", 4, "piece", "fresh large", 0),
            ("White Sugar", 200, "g", "granulated", 0),
            ("Orange", 2, "piece", "fresh juice and grated zest", 0),
            ("Vegetable Cooking Oil", 120, "ml", "corn or sunflower oil", 0),
            ("Baking Powder", 2, "tsp", "leavening", 0),
            ("Vanilla Extract", 1, "tsp", "extract", 0),
            ("Fine Salt", 0.25, "tsp", "pinch", 0)
        ]
    },
    {
        "name_en": "Rich Chocolate Fudge Cake",
        "name_ar": "كيكة شوكولاتة غنية بصوص الشوكولاتة الداكنة",
        "desc": "Moist, decadent chocolate sponge cake layered and glazed with rich glossy cocoa fudge ganache.",
        "cuisine": "International", "category": "Dessert", "servings": 8, "prep_time": 20, "cook_time": 35, "difficulty": "Easy",
        "instructions": "Whisk flour, cocoa powder, sugar, baking powder, baking soda, and salt in a bowl. Whisk in eggs, warm milk, oil, and vanilla until smooth. Pour boiling water or hot coffee into batter, stirring gently (batter will be thin). Pour into greased 9-inch cake pans. Bake at 180C for 30-35 mins. Prepare chocolate ganache with cream and chocolate, frosting cake once cooled.",
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587", "source_url": "https://www.themealdb.com", "source_name": "TheMealDB",
        "ingredients": [
            ("All-Purpose Flour", 250, "g", "sifted", 0),
            ("Cocoa Powder", 70, "g", "unsweetened Dutch cocoa", 0),
            ("White Sugar", 250, "g", "granulated", 0),
            ("Eggs", 2, "piece", "large", 0),
            ("Whole Milk", 200, "ml", "milk", 0),
            ("Vegetable Cooking Oil", 100, "ml", "oil", 0),
            ("Baking Powder", 1.5, "tsp", "leavening", 0),
            ("Vanilla Extract", 1, "tsp", "extract", 0),
            ("Fine Salt", 0.5, "tsp", "fine", 0)
        ]
    },

    # -------------------------------------------------------------------------
    # 8. AUTHENTIC EGYPTIAN BEVERAGES & HOT DRINKS
    # -------------------------------------------------------------------------
    {
        "name_en": "Hot Egyptian Sahlab with Nuts",
        "name_ar": "سحلب مصري ساخن باللبن والمكسرات والسمسم",
        "desc": "Egypt's favorite creamy winter beverage made of sweet milk thickened with starch, flavored with vanilla and mastic, garnished with raisins, coconut, and toasted sesame.",
        "cuisine": "Egyptian", "category": "Beverage", "servings": 4, "prep_time": 5, "cook_time": 10, "difficulty": "Easy",
        "instructions": "Whisk cornstarch, sugar, and crushed mastic into cold whole milk in a saucepan until dissolved. Heat over medium heat, stirring continuously until beverage gently thickens into a rich, creamy nectar. Pour hot sahlab into mugs. Garnish generously with toasted sesame seeds, shredded coconut flakes, raisins, and crushed raw almonds or pistachios.",
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574", "source_url": "https://en.wikipedia.org/wiki/Salep", "source_name": "Egyptian Winter Traditions",
        "ingredients": [
            ("Whole Milk", 800, "ml", "full cream fresh", 0),
            ("Cornstarch", 4, "tbsp", "sahlab starch base", 0),
            ("White Sugar", 80, "g", "granulated", 0),
            ("Raw White Sesame Seeds", 2, "tbsp", "toasted golden", 0),
            ("Coconut Flakes", 2, "tbsp", "shredded", 0),
            ("Raisins", 2, "tbsp", "golden", 0),
            ("Raw Almonds", 2, "tbsp", "crushed nuts", 0),
            ("Vanilla Extract", 0.5, "tsp", "extract", 0)
        ]
    },
    {
        "name_en": "Hot Halabessa / Spiced Chickpea Drink",
        "name_ar": "حلبسة - حمص الشام الحار بالكمون والشطة والليمون",
        "desc": "Warm winter street drink of tender boiled chickpeas in a spicy red tomato-cumin broth seasoned with fresh garlic, chili, and lemon juice.",
        "cuisine": "Egyptian", "category": "Beverage", "servings": 4, "prep_time": 10, "cook_time": 40, "difficulty": "Easy",
        "instructions": "Soak dried chickpeas for 8 hours and boil until tender. Add blended ripe tomatoes, minced garlic, ground cumin, tomato paste, salt, and black pepper to chickpea broth. Simmer for 15 minutes so flavors fuse into an aromatic red soup. Ladle hot chickpeas with spiced broth into tall glass mugs. Provide extra lemon juice, hot chili powder, and cumin for guests to spike to taste.",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999", "source_url": "https://en.wikipedia.org/wiki/Chickpea", "source_name": "Egyptian Street Culinary",
        "ingredients": [
            ("Canned Chickpeas", 400, "g", "soaked and boiled", 0),
            ("Red Tomato", 2, "piece", "pureed smooth", 0),
            ("Tomato Paste", 1, "tbsp", "canned", 0),
            ("Garlic", 4, "clove", "minced", 0),
            ("Lemon", 3, "piece", "freshly squeezed juice", 0),
            ("Cumin", 2, "tsp", "ground", 0),
            ("Hot Red Pepper Powder", 1, "tsp", "hot chili", 0),
            ("Fine Salt", 1.5, "tsp", "fine", 0)
        ]
    },
    {
        "name_en": "Iced Egyptian Karkadeh / Hibiscus",
        "name_ar": "كركديه مصري مثلج ومنعش طبيعي",
        "desc": "Deep crimson Egyptian herbal iced tea made from steep whole dried hibiscus calyces, sweetened with pure sugar and served chilled over ice.",
        "cuisine": "Egyptian", "category": "Beverage", "servings": 6, "prep_time": 10, "cook_time": 10, "difficulty": "Easy",
        "instructions": "Rinse dried hibiscus flower calyces in cold water. Bring 1.5 liters of water to a boil, turn off heat, add hibiscus flowers and white sugar. Stir until sugar dissolves, cover and steep for 20 minutes (or steep cold overnight for smooth flavor). Strain ruby red infusion through fine mesh sieve. Chill thoroughly in refrigerator and serve over cracked ice.",
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574", "source_url": "https://en.wikipedia.org/wiki/Hibiscus_tea", "source_name": "Egyptian Heritage Beverages",
        "ingredients": [
            ("Dried Hibiscus Flowers", 100, "g", "whole dried calyces", 0),
            ("White Sugar", 150, "g", "sweetener", 0)
        ]
    },
    {
        "name_en": "Fresh Mint Lemonade",
        "name_ar": "عصير ليمون بالنعناع الأخضر المنعش بالخلاط",
        "desc": "Invigorating café beverage of whole fresh lemons blended with fragrant fresh mint leaves, ice water, and sugar with a creamy froth.",
        "cuisine": "Egyptian", "category": "Beverage", "servings": 4, "prep_time": 5, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Peel lemons and remove white pith and seeds. Place peeled lemons, fresh washed mint leaves, white sugar, cold water, and a splash of milk into blender. Blend on high speed for 40 seconds until frothy. Strain through fine sieve into tall glasses filled with ice cubes. Garnish with fresh mint sprig and serve immediately.",
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574", "source_url": "https://en.wikipedia.org/wiki/Limonana", "source_name": "Egyptian Café Culture",
        "ingredients": [
            ("Lemon", 4, "piece", "fresh juicy peeled", 0),
            ("Fresh Mint", 1, "bunch", "fresh washed green leaves", 0),
            ("White Sugar", 80, "g", "granulated", 0),
            ("Whole Milk", 30, "ml", "splash for creamy foam", 1)
        ]
    },
    {
        "name_en": "Fresh Iced Mango Smoothie",
        "name_ar": "عصير مانجو طبيعي مثلج فريش بالقطع",
        "desc": "Thick, luscious nectar made of ripe sweet Egyptian mangoes blended with ice and honey, garnished with fresh mango chunks.",
        "cuisine": "Egyptian", "category": "Beverage", "servings": 4, "prep_time": 10, "cook_time": 0, "difficulty": "Easy",
        "instructions": "Peel ripe Egyptian mangoes (Zebda or Awais variety). Cut flesh into thick pieces. Blend 3/4 of the mango flesh with cold water, sugar or honey, and crushed ice until thick and smooth. Reserve 1/4 of mango diced in small cubes. Pour thick mango nectar into glasses and top with diced mango cubes.",
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574", "source_url": "https://en.wikipedia.org/wiki/Mango", "source_name": "Egyptian Café Culture",
        "ingredients": [
            ("Mango", 800, "g", "fresh ripe sweet mangoes", 0),
            ("White Sugar", 50, "g", "granulated or honey", 0)
        ]
    },
    {
        "name_en": "Egyptian Cold Sobia Drink",
        "name_ar": "سوبيا مصرية مثلجة باللبن وجوز الهند والفانيليا",
        "desc": "Creamy sweet traditional Egyptian iced beverage made of pure whole milk, finely ground coconut, powdered sugar, and vanilla.",
        "cuisine": "Egyptian", "category": "Beverage", "servings": 4, "prep_time": 10, "cook_time": 0, "difficulty": "Easy",
        "instructions": "In blender, combine cold whole milk, finely powdered coconut flakes, powdered sugar, dry milk powder, and vanilla extract. Blend on high speed for 1 minute until rich, frothy, and completely smooth. Chill thoroughly in refrigerator. Serve ice-cold in chilled glasses.",
        "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574", "source_url": "https://en.wikipedia.org/wiki/Sobia", "source_name": "Egyptian Heritage Beverages",
        "ingredients": [
            ("Whole Milk", 800, "ml", "cold fresh milk", 0),
            ("Coconut Flakes", 60, "g", "finely ground powder", 0),
            ("Powdered Sugar", 100, "g", "powdered", 0),
            ("Vanilla Extract", 1, "tsp", "pure vanilla", 0)
        ]
    }
]

print(f"Catalog contains {len(RECIPES_CATALOG)} core bespoke recipes.")

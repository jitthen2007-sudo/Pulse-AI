import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class NutritionRequest(BaseModel):
    weight_kg: float = Field(..., gt=20, lt=400, description="Weight in kilograms")
    height_cm: float = Field(..., gt=50, lt=260, description="Height in centimeters")
    goal: str = Field(..., description="E.g., Weight Loss, Muscle Gain, Maintenance, Lean Bulk")
    preference: str = Field(..., description="E.g., Indian Veg, Indian Non-Veg, Indian Vegan, High Protein")
    target_calories: Optional[int] = Field(None, description="Optional target calorie goal")

class MacroBreakdown(BaseModel):
    protein_g: int
    carbs_g: int
    fats_g: int
    protein_pct: int
    carbs_pct: int
    fats_pct: int

class MealItem(BaseModel):
    title: str
    calories: int
    macros: str
    description: str

class GroceryItem(BaseModel):
    name: str
    category: str
    benefit: str
    quantity_est: str

class NutritionResponse(BaseModel):
    bmi: float
    bmi_category: str
    bmi_analysis: str
    daily_calories: int
    macros: MacroBreakdown
    strategy_summary: str
    meal_plan: Dict[str, MealItem]
    grocery_list: List[GroceryItem] # Exactly 5 Indian staple items
    hydration_tip: str
    timing_tip: str
    source: str = "pulse-indian-nutrition-engine"

async def calculate_diet_plan(req: NutritionRequest) -> NutritionResponse:
    weight = req.weight_kg
    height = req.height_cm
    goal = req.goal
    pref = req.preference

    height_m = height / 100.0
    bmi = round(weight / (height_m * height_m), 1)

    if bmi < 18.5:
        bmi_cat = "Underweight"
        bmi_analysis = f"Your BMI of {bmi} indicates a caloric surplus is essential to build lean myofibrillar muscle and restore hormonal equilibrium."
    elif bmi < 25.0:
        bmi_cat = "Normal Weight"
        bmi_analysis = f"Your BMI of {bmi} is in the optimal metabolic zone. Ideal for lean bulking, athletic performance, and body recomposition."
    elif bmi < 30.0:
        bmi_cat = "Overweight"
        bmi_analysis = f"Your BMI of {bmi} suggests a moderate caloric deficit paired with high-protein resistance training will preserve muscle while stripping fat."
    else:
        bmi_cat = "Obese"
        bmi_analysis = f"Your BMI of {bmi} benefits from a structured, sustainable caloric deficit with low-glycemic Indian whole foods and daily step goals."

    # Energy calculations (Mifflin-St Jeor estimate)
    bmr_est = 10 * weight + 6.25 * height - 5 * 28 + 5
    tdee_est = int(round(bmr_est * 1.45))

    target_cals = req.target_calories
    if not target_cals or target_cals <= 0:
        if any(w in goal.lower() for w in ["loss", "shred", "cut", "fat"]):
            target_cals = max(1400, tdee_est - 450)
        elif any(w in goal.lower() for w in ["bulk", "gain", "mass", "hypertrophy"]):
            target_cals = tdee_est + 350
        else:
            target_cals = tdee_est

    target_cals = int(target_cals)
    pref_lower = pref.lower()
    
    is_non_veg = "non" in pref_lower or "egg" in pref_lower or "chicken" in pref_lower
    is_vegan = "vegan" in pref_lower
    is_veg = not is_non_veg and not is_vegan

    # Protein: 1.8g - 2.2g per kg bodyweight
    protein_g = int(round(weight * 2.0))
    fat_g = int(round((target_cals * 0.25) / 9))
    carbs_g = max(60, int(round((target_cals - protein_g * 4 - fat_g * 9) / 4)))

    total_macro_cals = protein_g * 4 + carbs_g * 4 + fat_g * 9
    p_pct = int(round((protein_g * 4 / total_macro_cals) * 100))
    c_pct = int(round((carbs_g * 4 / total_macro_cals) * 100))
    f_pct = max(5, 100 - p_pct - c_pct)

    strategy_summary = (
        f"Calibrated for Indian lifestyle and climate: {target_cals} kcal/day targeting {protein_g}g protein ({p_pct}%), "
        f"{carbs_g}g complex carbs ({c_pct}%), and {fat_g}g healthy fats ({f_pct}%). "
        f"Prioritizes traditional Indian protein sources like paneer, soya, dal, and desi eggs with optimal gut digestion."
    )

    # Indian Meal Plans
    if is_non_veg:
        meals = {
            "breakfast": MealItem(
                title="Desi Egg Bhurji & Multigrain Phulka",
                calories=int(round(target_cals * 0.25)),
                macros=f"{int(round(protein_g * 0.26))}g P | {int(round(carbs_g * 0.25))}g C | {int(round(fat_g * 0.25))}g F",
                description="3 egg whites + 1 whole egg scrambled with chopped onions, tomatoes, green chilies, and turmeric. Served with 1 multigrain roti and warm green tea."
            ),
            "lunch": MealItem(
                title="Tandoori Chicken Tikka with Steamed Rice & Dal",
                calories=int(round(target_cals * 0.35)),
                macros=f"{int(round(protein_g * 0.38))}g P | {int(round(carbs_g * 0.35))}g C | {int(round(fat_g * 0.30))}g F",
                description="150g grilled chicken breast tikka seasoned with hung curd, lemon, and spices, served with yellow moong dal tadka, 1 cup steamed brown/basmati rice, and fresh cucumber kachumber."
            ),
            "snack": MealItem(
                title="Roasted Makhana & Tender Coconut Water",
                calories=int(round(target_cals * 0.12)),
                macros=f"{int(round(protein_g * 0.08))}g P | {int(round(carbs_g * 0.15))}g C | {int(round(fat_g * 0.12))}g F",
                description="35g dry-roasted phool makhana (foxnuts) sprinkled with chaat masala and black pepper, paired with fresh tender coconut water for tropical electrolyte rehydration."
            ),
            "dinner": MealItem(
                title="Homestyle Fish/Chicken Curry with Phulkas & Dahi",
                calories=int(round(target_cals * 0.28)),
                macros=f"{int(round(protein_g * 0.28))}g P | {int(round(carbs_g * 0.25))}g C | {int(round(fat_g * 0.33))}g F",
                description="130g Rohu fish or chicken curry in light tomato-onion gravy (low oil), 2 warm phulkas, steamed green beans, and 1 small bowl of fresh homemade probiotic dahi."
            ),
            "pre_post_workout": MealItem(
                title="Whey Isolate or Sattu Energizer Shake",
                calories=160,
                macros=f"{int(round(protein_g * 0.16))}g P | 10g C | 2g F",
                description="1 scoop cold-filtered Whey Isolate (or 40g roasted Sattu drink) in 300ml cold water with a pinch of Himalayan pink salt."
            )
        }
        groceries = [
            GroceryItem(name="Skinless Chicken Breast & Desi Eggs", category="Primary Complete Protein", benefit="Top-tier biological value protein packed with leucine and zinc for fast muscle recovery", quantity_est="1 kg chicken + 2 dozen eggs"),
            GroceryItem(name="Low-Fat Fresh Paneer / Curd (Dahi)", category="Dairy & Casein", benefit="Slow-digesting casein for overnight muscle repair and active gut-friendly probiotics", quantity_est="500g paneer + 1 kg dahi"),
            GroceryItem(name="Soya Chunks (Nutrela / Fortune)", category="Plant Protein Booster", benefit="52% protein density to spike total daily intake with zero saturated fat", quantity_est="500g pack"),
            GroceryItem(name="Phool Makhana (Fox Nuts)", category="Anti-Inflammatory Snack", benefit="Low-calorie, magnesium-rich Indian superfood perfect for hunger management", quantity_est="250g pack"),
            GroceryItem(name="Multigrain Atta & Yellow Moong Dal", category="Complex Carbs & Fiber", benefit="Sustained-release energy without sudden insulin spikes; easy on tropical digestion", quantity_est="2 kg atta + 1 kg dal")
        ]
    elif is_vegan:
        meals = {
            "breakfast": MealItem(
                title="High-Protein Besan Chilla with Tofu Crumble",
                calories=int(round(target_cals * 0.25)),
                macros=f"{int(round(protein_g * 0.25))}g P | {int(round(carbs_g * 0.30))}g C | {int(round(fat_g * 0.25))}g F",
                description="Two savory gram flour (besan) chillas prepared with grated organic tofu (100g), coriander, ajwain, and homemade mint chutney."
            ),
            "lunch": MealItem(
                title="Soya Chunk Masala Curry with Multigrain Rotis",
                calories=int(round(target_cals * 0.35)),
                macros=f"{int(round(protein_g * 0.38))}g P | {int(round(carbs_g * 0.35))}g C | {int(round(fat_g * 0.28))}g F",
                description="50g boiled soya chunks cooked in ginger-garlic tomato gravy, 2 multigrain rotis, a bowl of thick Rajma/Chana, and fresh carrot-radish salad with lemon."
            ),
            "snack": MealItem(
                title="Chilled Bihari Sattu Drink & Roasted Peanuts",
                calories=int(round(target_cals * 0.12)),
                macros=f"{int(round(protein_g * 0.12))}g P | {int(round(carbs_g * 0.15))}g C | {int(round(fat_g * 0.15))}g F",
                description="40g roasted gram sattu whisked in ice-cold water with black salt, roasted jeera, and lemon, accompanied by a handful of dry-roasted peanuts."
            ),
            "dinner": MealItem(
                title="Palak Tofu with Steamed Jeera Brown Rice",
                calories=int(round(target_cals * 0.28)),
                macros=f"{int(round(protein_g * 0.25))}g P | {int(round(carbs_g * 0.30))}g C | {int(round(fat_g * 0.32))}g F",
                description="150g firm tofu cubes simmered in spiced pureed spinach (palak gravy), served with 1 cup steamed jeera brown rice and cucumber slices."
            ),
            "pre_post_workout": MealItem(
                title="Plant Protein Shake & Black Coffee",
                calories=150,
                macros=f"{int(round(protein_g * 0.15))}g P | 8g C | 2g F",
                description="1 scoop Pea/Brown Rice protein isolate mixed in water with half a banana or 1 cup strong South Indian filter coffee (no sugar) 40m pre-workout."
            )
        }
        groceries = [
            GroceryItem(name="Soya Chunks (Nutrela / Fortune)", category="High-Density Plant Protein", benefit="52g of complete protein per 100g, unmatched affordability and muscle-building efficiency", quantity_est="1 kg (2 packs)"),
            GroceryItem(name="Organic Firm Tofu", category="Soy Protein & Calcium", benefit="Zero-cholesterol protein base for curries and bhurji, fortified with bone calcium", quantity_est="1 kg (4 blocks)"),
            GroceryItem(name="Pure Desi Sattu & Besan", category="Traditional Superfood", benefit="Natural roasted chana flour rich in insoluble fiber and sustained energy", quantity_est="1 kg sattu + 1 kg besan"),
            GroceryItem(name="Kala Chana & Sprouted Moong", category="Slow-Burning Carbs & Protein", benefit="Rich in bioactive polyphenols and prebiotics for pristine gut microbiome", quantity_est="1 kg chana + 1 kg moong"),
            GroceryItem(name="Fresh Spinach (Palak) & Phool Makhana", category="Micronutrients & Anti-Inflammatory", benefit="Iron, magnesium, and bioavailable folate to support hemoglobin in tropical conditions", quantity_est="3 bundles palak + 250g makhana")
        ]
    else:
        # Indian Vegetarian (Pure Veg / Lacto-Vegetarian)
        meals = {
            "breakfast": MealItem(
                title="Paneer Bhurji & Multigrain Phulka with Mint Chutney",
                calories=int(round(target_cals * 0.25)),
                macros=f"{int(round(protein_g * 0.28))}g P | {int(round(carbs_g * 0.25))}g C | {int(round(fat_g * 0.30))}g F",
                description="150g low-fat fresh paneer crumbled with onions, tomatoes, turmeric, and green peas, served with 1 warm multigrain roti and pudina chutney."
            ),
            "lunch": MealItem(
                title="Soya Mattar Curry + Dal Tadka + Steamed Rice & Dahi",
                calories=int(round(target_cals * 0.35)),
                macros=f"{int(round(protein_g * 0.36))}g P | {int(round(carbs_g * 0.38))}g C | {int(round(fat_g * 0.25))}g F",
                description="45g soya chunks cooked in homestyle tomato-ginger gravy, 1 small bowl yellow moong/toor dal, 1 cup steamed rice, and 150g probiotic dahi with cucumber."
            ),
            "snack": MealItem(
                title="Roasted Makhana & Desi Sprouted Moong Chaat",
                calories=int(round(target_cals * 0.12)),
                macros=f"{int(round(protein_g * 0.12))}g P | {int(round(carbs_g * 0.17))}g C | {int(round(fat_g * 0.10))}g F",
                description="Sprouted green moong mixed with roasted makhana, chopped onions, tomatoes, fresh lime juice, and chaat masala."
            ),
            "dinner": MealItem(
                title="Palak Paneer with 2 Multigrain Rotis & Cucumber",
                calories=int(round(target_cals * 0.28)),
                macros=f"{int(round(protein_g * 0.26))}g P | {int(round(carbs_g * 0.25))}g C | {int(round(fat_g * 0.35))}g F",
                description="120g fresh paneer simmered in iron-rich blended spinach curry with mild spices, 2 multigrain phulkas, and fresh sliced cucumbers."
            ),
            "pre_post_workout": MealItem(
                title="Whey Protein Shake or Sattu Buttermilk (Chaas)",
                calories=160,
                macros=f"{int(round(protein_g * 0.18))}g P | 8g C | 2g F",
                description="1 scoop Whey Protein in water (or 40g sattu blended in cold spiced chaas with roasted cumin) for rapid post-workout muscle protein synthesis."
            )
        }
        groceries = [
            GroceryItem(name="Low-Fat Fresh Paneer", category="Casein & Whey Protein", benefit="25g+ protein per 100g, slow-digesting amino acids that sustain nitrogen balance for hours", quantity_est="1 kg"),
            GroceryItem(name="Soya Chunks (Nutrela / Fortune)", category="High-Yield Plant Protein", benefit="52% protein density; unmatched value for Indian vegetarian hypertrophy", quantity_est="1 kg (2 packs)"),
            GroceryItem(name="Fresh Curd / Dahi (Probiotic)", category="Gut Microbiome Health", benefit="Aids digestion of high-protein Indian pulses and cools the digestive tract in hot weather", quantity_est="2 kg tub"),
            GroceryItem(name="Desi Sattu & Besan (Gram Flour)", category="Fiber & Complex Carbs", benefit="Low glycemic index superfoods providing sustained workout fuel without blood sugar spikes", quantity_est="1 kg sattu + 1 kg besan"),
            GroceryItem(name="Phool Makhana & Raw Badam (Almonds)", category="Healthy Lipids & Minerals", benefit="Zero cholesterol, magnesium-dense anti-inflammatory snack for joint health", quantity_est="300g makhana + 250g badam")
        ]

    hydration_tip = (
        "Tropical Climate Hydration: Consume 3.5L to 4.5L of water daily. "
        "Incorporate tender coconut water or Indian nimbu paani with Himalayan pink salt to replace electrolytes lost in humidity."
    )
    timing_tip = (
        "Pre & Post-Workout Nutrient Timing: Consume complex carbs (banana or sattu drink) 45 min before lifting. "
        "Hit 30g of protein within 90 minutes post-training, and drink warm turmeric milk (Haldi doodh with black pepper) before sleep."
    )

    return NutritionResponse(
        bmi=bmi,
        bmi_category=bmi_cat,
        bmi_analysis=bmi_analysis,
        daily_calories=target_cals,
        macros=MacroBreakdown(
            protein_g=protein_g,
            carbs_g=carbs_g,
            fats_g=fat_g,
            protein_pct=p_pct,
            carbs_pct=c_pct,
            fats_pct=f_pct
        ),
        strategy_summary=strategy_summary,
        meal_plan=meals,
        grocery_list=groceries,
        hydration_tip=hydration_tip,
        timing_tip=timing_tip,
        source="pulse-indian-nutrition-engine"
    )

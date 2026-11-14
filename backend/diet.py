import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class NutritionRequest(BaseModel):
    weight_kg: float = Field(..., gt=20, lt=400, description="Weight in kilograms")
    height_cm: float = Field(..., gt=50, lt=260, description="Height in centimeters")
    goal: str = Field(..., description="E.g., Weight Loss, Muscle Gain, Maintenance, Lean Bulk")
    preference: str = Field(..., description="E.g., Veg, Non-Veg, Vegan, Keto, High Protein")
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
    grocery_list: List[GroceryItem] # Exactly 5 items
    hydration_tip: str
    timing_tip: str
    source: str = "gemini"

async def calculate_diet_plan(req: NutritionRequest) -> NutritionResponse:
    weight = req.weight_kg
    height = req.height_cm
    goal = req.goal
    pref = req.preference

    height_m = height / 100.0
    bmi = round(weight / (height_m * height_m), 1)

    if bmi < 18.5:
        bmi_cat = "Underweight"
        bmi_analysis = f"Your BMI of {bmi} indicates a caloric surplus is optimal to build lean myofibrillar muscle and balance hormonal health."
    elif bmi < 25.0:
        bmi_cat = "Normal Weight"
        bmi_analysis = f"Your BMI of {bmi} is in the optimal metabolic zone. Ideal for lean bulking, athletic performance, or body recomposition."
    elif bmi < 30.0:
        bmi_cat = "Overweight"
        bmi_analysis = f"Your BMI of {bmi} suggests a slight caloric deficit paired with high-protein resistance training will efficiently shred fat while preserving muscle."
    else:
        bmi_cat = "Obese"
        bmi_analysis = f"Your BMI of {bmi} benefits from a structured, sustainable caloric deficit with low-glycemic foods and daily non-exercise physical activity."

    # Energy calculations (Mifflin-St Jeor estimate)
    bmr_est = 10 * weight + 6.25 * height - 5 * 28 + 5
    tdee_est = int(round(bmr_est * 1.45))

    target_cals = req.target_calories
    if not target_cals or target_cals <= 0:
        if any(w in goal.lower() for w in ["loss", "shred", "cut", "fat"]):
            target_cals = max(1350, tdee_est - 450)
        elif any(w in goal.lower() for w in ["bulk", "gain", "mass", "hypertrophy"]):
            target_cals = tdee_est + 350
        else:
            target_cals = tdee_est

    target_cals = int(target_cals)
    pref_lower = pref.lower()
    is_keto = "keto" in pref_lower
    is_vegan = "vegan" in pref_lower
    is_veg = ("veg" in pref_lower) and not is_vegan and ("non" not in pref_lower)

    protein_g = int(round(weight * 2.0))
    fat_g = int(round((target_cals * 0.25) / 9))
    carbs_g = max(50, int(round((target_cals - protein_g * 4 - fat_g * 9) / 4)))

    if is_keto:
        protein_g = int(round(weight * 1.8))
        carbs_g = 30
        fat_g = max(40, int(round((target_cals - protein_g * 4 - carbs_g * 4) / 9)))

    total_macro_cals = protein_g * 4 + carbs_g * 4 + fat_g * 9
    p_pct = int(round((protein_g * 4 / total_macro_cals) * 100))
    c_pct = int(round((carbs_g * 4 / total_macro_cals) * 100))
    f_pct = max(5, 100 - p_pct - c_pct)

    if is_keto:
        meals = {
            "breakfast": MealItem(
                title="Keto Power Scramble with Avocado & Ghee",
                calories=int(round(target_cals * 0.26)),
                macros=f"{int(round(protein_g * 0.28))}g P | 4g C | {int(round(fat_g * 0.32))}g F",
                description="Pasture-raised whole eggs scrambled in grass-fed ghee with baby spinach, feta cheese, and sliced avocado."
            ),
            "lunch": MealItem(
                title="Wild Salmon Bowl with Cauliflower Rice",
                calories=int(round(target_cals * 0.34)),
                macros=f"{int(round(protein_g * 0.35))}g P | 6g C | {int(round(fat_g * 0.35))}g F",
                description="Oven-baked wild salmon fillet served over riced cauliflower sautéed in cold-pressed virgin olive oil and garlic."
            ),
            "snack": MealItem(
                title="Raw Macadamia Nuts & Dark Cacao (90%)",
                calories=int(round(target_cals * 0.12)),
                macros=f"{int(round(protein_g * 0.08))}g P | 3g C | {int(round(fat_g * 0.15))}g F",
                description="Raw macadamia nuts providing heart-healthy monounsaturated fats and essential minerals."
            ),
            "dinner": MealItem(
                title="Grass-Fed Ribeye with Roasted Garlic Asparagus",
                calories=int(round(target_cals * 0.28)),
                macros=f"{int(round(protein_g * 0.32))}g P | 5g C | {int(round(fat_g * 0.28))}g F",
                description="Seared ribeye steak basted in rosemary herb butter alongside charred asparagus spears."
            ),
            "pre_post_workout": MealItem(
                title="BHB Ketones & Whey/Collagen Peptide Shake",
                calories=160,
                macros=f"{int(round(protein_g * 0.15))}g P | 2g C | 4g F",
                description="Zero-sugar cold-filtered isolate blended with unsweetened almond milk and MCT oil powder."
            )
        }
        groceries = [
            GroceryItem(name="Wild Atlantic Salmon Fillets", category="Omega-3 Protein", benefit="Zero-carb complete protein packed with anti-inflammatory EPA and DHA", quantity_est="800g (4 fillets)"),
            GroceryItem(name="Hass Avocados", category="Monounsaturated Fat", benefit="Potassium-dense healthy lipids to prevent keto-adaptation cramping", quantity_est="1 bag (5 avocados)"),
            GroceryItem(name="Pasture-Raised Large Eggs", category="Whole Food Protein", benefit="Choline and lutein rich with perfect 1:1 protein to healthy fat ratio", quantity_est="2 dozen"),
            GroceryItem(name="Raw Macadamia Nuts", category="Healthy Lipids", benefit="Highest monounsaturated fat concentration of any nut, keeping blood sugar flat", quantity_est="400g pack"),
            GroceryItem(name="Fresh Asparagus & Baby Spinach", category="Low-Carb Greens", benefit="Sulforaphane and magnesium without kicking you out of ketosis", quantity_est="1 kg bundle")
        ]
    elif is_veg or is_vegan:
        meals = {
            "breakfast": MealItem(
                title="High-Protein Sprouted Oatmeal Bowl",
                calories=int(round(target_cals * 0.25)),
                macros=f"{int(round(protein_g * 0.25))}g P | {int(round(carbs_g * 0.35))}g C | {int(round(fat_g * 0.2))}g F",
                description="Rolled oats simmered in almond milk, mixed with 1 scoop plant protein isolate, chia seeds, and fresh blueberries."
            ),
            "lunch": MealItem(
                title="Mediterranean Tofu & Quinoa Power Bowl",
                calories=int(round(target_cals * 0.35)),
                macros=f"{int(round(protein_g * 0.35))}g P | {int(round(carbs_g * 0.35))}g C | {int(round(fat_g * 0.35))}g F",
                description="Pan-seared extra-firm organic tofu, tri-color quinoa, roasted chickpeas, cucumbers, and tahini dressing."
            ),
            "snack": MealItem(
                title="Greek / Soy Yogurt with Crushed Walnuts",
                calories=int(round(target_cals * 0.12)),
                macros=f"{int(round(protein_g * 0.12))}g P | {int(round(carbs_g * 0.1))}g C | {int(round(fat_g * 0.2))}g F",
                description="High-protein strained yogurt offering slow-digesting casein/pea protein to suppress catabolism."
            ),
            "dinner": MealItem(
                title="Spiced Lentil Dal with Brown Basmati & Greens",
                calories=int(round(target_cals * 0.28)),
                macros=f"{int(round(protein_g * 0.28))}g P | {int(round(carbs_g * 0.2))}g C | {int(round(fat_g * 0.25))}g F",
                description="Protein-rich yellow and red lentils tempered with cumin, turmeric, garlic, served with brown rice."
            ),
            "pre_post_workout": MealItem(
                title="Plant / Whey Isolate with Crisp Rice Cakes",
                calories=190,
                macros=f"{int(round(protein_g * 0.15))}g P | 22g C | 1g F",
                description="Rapidly absorbed protein isolate providing 3g leucine to initiate muscle protein synthesis immediately."
            )
        }
        groceries = [
            GroceryItem(name="Extra-Firm Organic Tofu", category="Plant Protein", benefit="Complete amino acid profile providing 48g of bioavailable protein per pack", quantity_est="2 blocks (800g)"),
            GroceryItem(name="Tri-Color Sprouted Quinoa", category="Complex Carbs", benefit="Contains all 9 essential amino acids plus slow-burning sustained energy", quantity_est="1 kg bag"),
            GroceryItem(name="Sprouted Green Moong & Lentils", category="Legume Protein", benefit="Rich in zinc, magnesium, and slow-fermenting prebiotic fiber", quantity_est="1.5 kg bag"),
            GroceryItem(name="Raw California Almonds", category="Essential Lipids", benefit="High in alpha-tocopherol (Vitamin E) to protect cell membranes from training stress", quantity_est="500g bag"),
            GroceryItem(name="Fresh Baby Spinach Crowns", category="Nitric Oxide Greens", benefit="High dietary nitrates increase blood flow and muscle pump efficiency", quantity_est="1 kg bundle")
        ]
    else:
        meals = {
            "breakfast": MealItem(
                title="Anabolic Egg & Sweet Potato Hash",
                calories=int(round(target_cals * 0.25)),
                macros=f"{int(round(protein_g * 0.25))}g P | {int(round(carbs_g * 0.3))}g C | {int(round(fat_g * 0.25))}g F",
                description="3 whole pasture-raised eggs scrambled with 2 egg whites, diced sweet potato hash, and sautéed bell peppers."
            ),
            "lunch": MealItem(
                title="Herb-Roasted Chicken Breast & Jasmine Rice",
                calories=int(round(target_cals * 0.35)),
                macros=f"{int(round(protein_g * 0.35))}g P | {int(round(carbs_g * 0.4))}g C | {int(round(fat_g * 0.25))}g F",
                description="200g rosemary garlic chicken breast alongside 1.5 cups steamed jasmine rice and charred green beans."
            ),
            "snack": MealItem(
                title="Low-Fat Greek Yogurt with Berries & Honey",
                calories=int(round(target_cals * 0.12)),
                macros=f"{int(round(protein_g * 0.12))}g P | {int(round(carbs_g * 0.1))}g C | {int(round(fat_g * 0.1))}g F",
                description="Zero-fat strained Greek yogurt loaded with organic blueberries, delivering a sustained leucine drip."
            ),
            "dinner": MealItem(
                title="Seared Wild Salmon with Roasted Russet Wedges",
                calories=int(round(target_cals * 0.28)),
                macros=f"{int(round(protein_g * 0.28))}g P | {int(round(carbs_g * 0.2))}g C | {int(round(fat_g * 0.4))}g F",
                description="Crispy pan-seared Atlantic salmon fillet with seasoned russet potato wedges and steamed broccoli florets."
            ),
            "pre_post_workout": MealItem(
                title="Hydrolyzed Whey Isolate & Sliced Banana",
                calories=210,
                macros=f"{int(round(protein_g * 0.18))}g P | 28g C | 1g F",
                description="Ultra-clean whey isolate with high-glycemic fruit to rapidly reload intramuscular glycogen."
            )
        }
        groceries = [
            GroceryItem(name="Boneless Skinless Chicken Breast", category="Lean Protein", benefit="Complete ultra-lean amino acid source to repair microtears in muscle fibers", quantity_est="1.5 kg"),
            GroceryItem(name="Wild-Caught Salmon Fillets", category="Omega-3 Protein", benefit="High EPA/DHA fatty acids combat exercise-induced inflammation and protect joints", quantity_est="4 fillets (600g)"),
            GroceryItem(name="Organic Sweet Potatoes", category="Complex Carbs", benefit="Low-glycemic complex starch rich in potassium to prevent intra-workout cramps", quantity_est="2 kg bag"),
            GroceryItem(name="Pasture-Raised Large Eggs", category="Whole Food Protein", benefit="Choline-packed yolks optimize neuromuscular transmission and cell structure", quantity_est="2 dozen"),
            GroceryItem(name="Fresh Broccoli Crowns & Asparagus", category="Cruciferous Greens", benefit="Sulforaphane and indole-3-carbinol for optimal hormonal balance", quantity_est="1 kg")
        ]

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
        strategy_summary=f"Scientifically calibrated for {goal} with a {pref} protocol. Evenly spaces leucine-rich boluses to keep muscle protein synthesis elevated 24/7.",
        meal_plan=meals,
        grocery_list=groceries,
        hydration_tip=f"Consume a baseline of {round(weight * 0.04, 1)} Liters of water daily, adding 500ml per 45 minutes of heavy resistance training.",
        timing_tip="Consume your primary carbohydrate allotment within 90 minutes before and immediately after your heaviest resistance training.",
        source="pulse-engine"
    )

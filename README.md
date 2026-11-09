# ⚡ Pulse AI — Autonomous Fitness & Form Correction Platform

[![Next.js](https://img.shields.io/badge/Next.js-14.2-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?logo=google)](https://aistudio.google.com/)
[![MediaPipe Pose](https://img.shields.io/badge/MediaPipe-Pose_Vision-FF6F00)](https://developers.google.com/mediapipe)

**Pulse AI** is a production-ready, full-stack fitness and biomechanical form-correction platform architected for modern athletes and fitness enthusiasts. It combines **100% client-side computer vision** (zero video upload latency or privacy concerns) with **Google Gemini 2.5-powered intelligence** through a secured FastAPI backend.

---

## 🌟 Key Architecture & Security

```
+--------------------------------------------------------------+
|                     Next.js 14 Frontend                      |
| (React, Tailwind CSS, Lucide Icons, Client-Side MediaPipe)   |
+------------------------------+-------------------------------+
                               |
                   Next.js Rewrites /api/*
                               |
                               v
+--------------------------------------------------------------+
|                    FastAPI Python Backend                    |
| (Protected Gemini 2.5 API Gateway, Kinesiology Logic)        |
+------------------------------+-------------------------------+
                               |
                        Secure SDK Call
                               |
                               v
+--------------------------------------------------------------+
|                      Google Gemini 2.5                       |
|           (AI Studio Key isolated in backend/.env)           |
+--------------------------------------------------------------+
```

### Security Highlights
* **Zero Video Streaming:** The AI Pose Coach operates **100% inside the browser** using MediaPipe Pose WebAssembly. No video frames, camera streams, or images are ever transmitted to any server.
* **Server-Side API Key Storage:** The `GEMINI_API_KEY` is strictly accessed by the FastAPI backend through `.env`. It is never bundled into client-side JS bundles.
* **Vercel Deployment Ready:** Includes `next.config.js` rewrites to proxy `/api/*` to the FastAPI backend, along with `api/index.py` and `vercel.json` for serverless function deployments.

---

## 🚀 The 4 Core Modules

### 1. 🤖 Pulse AI Virtual Coach (Flexible Q&A Chatbot)
* **Adaptive Prompt Engine:** Powered by Gemini 2.5 Flash with a sports-science system prompt covering muscle anatomy, joint kinematics, CNS recovery, workout splits (PPL, Upper/Lower, Arnold), macro nutrition, and injury prevention.
* **Psychological Mood Detection:** Automatically classifies user sentiment (e.g., fatigued, motivated, injury-alert, burnout) and tailors tone with autoregulation advice.
* **Rich Markdown & Actionable Takeaways:** Delivers structured form cues and immediate coach takeaways.

### 2. 🥗 AI Dietician & Nutritionist
* **Biometric Calibration:** Takes Weight (kg), Height (cm), Goal, Dietary Preference (Veg, Non-Veg, Vegan, Keto), and optional Target Calories.
* **Clinical BMI & Metabolic Analysis:** Automatically computes BMI with color-coded classification and metabolic insights.
* **Macronutrient Breakdown:** Calibrates grams and percentages of Protein, Carbs, and Fats.
* **5-Item Curated Grocery Haul:** Generates exactly 5 synergistic items with quantities and nutritional benefits, with one-click clipboard copying.
* **Hydration & Nutrient Timing:** Specific recommendations for pre- and post-workout windows.

### 3. 🏋️ Smart Gym & Routine Recommender
* **Hyperlocal Gym Discovery:** Identifies 3 real gym chains in the user's specific locality (e.g., Austin, London, New York, Bangalore) with amenities, vibe, and goal alignment.
* **Engineered Workout Split:** Multi-day split complete with exercise names, sets, reps, rest intervals in seconds, and kinematic cues.
* **Score-Calibrated Daily Challenge:** Benchmark workout challenge scaled dynamically to performance scores (1–100) with interactive checkoffs.

### 4. 📹 High-Accuracy AI Pose Coach (Client-Side Computer Vision)
* **Browser-Native Inference:** Runs `@mediapipe/pose` and `@mediapipe/camera_utils` directly in the user's browser.
* **HTML5 Canvas Skeletal Overlay:** Uses `@mediapipe/drawing_utils` (`drawLandmarks`, `drawConnectors`) overlaid directly on the video feed.
* **High-Accuracy Visibility Filter:** Discards any landmark with a visibility confidence score below **0.65**.
* **Knee Angle Kinematics:** Computes mathematical 2D angle between Left Hip (23), Left Knee (25), and Left Ankle (27).
* **Squat Repetition State Machine:**
  - Dips below **95°**: triggers *Depth Achieved*.
  - Returns above **160°**: increments the Rep Counter and triggers celebration.
* **Lag-Free Voice Coach:** Dynamically synthesizes speech cues (*"Good rep"*, *"Go lower"*) using `window.speechSynthesis` with non-blocking debounce that never drops frame rates.
* **Simulation Demo Mode:** Integrated virtual test mode to evaluate angle triggers and audio feedback even without a physical webcam connected!

---



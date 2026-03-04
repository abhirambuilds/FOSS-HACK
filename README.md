# 🔍 NutriScan - Smart Snack Ingredient Analyzer

> **Scan the label. Know your food. Eat better.** 
> A FOSS Hack project that demystifies food labels, identifies harmful ingredients, and helps you make healthier choices instantly.

---

## 🎯 What is NutriScan?

Ever looked at the back of a snack packet and wondered what "E621" or "Maltodextrin" actually is? **NutriScan** is an open-source tool that lets you scan the back of any food product using your camera. It automatically extracts the ingredient list, cross-references it with public nutritional datasets, and tells you exactly what you are putting into your body.

No corporate jargon. No hidden sugars. Just simple, readable facts.

---

## ✨ Features

### Current Features (MVP)
*   📷 **Camera-Based Scanning**: Snap a picture of any ingredient label for immediate extraction.
*   🔍 **Automatic Ingredient Parsing**: Uses robust OCR and NLP to read and understand complex, messy ingredient lists.
*   ⚠️ **Personalization & Allergy Alerts**: Set up a custom profile (e.g., "Vegan", "Nut Allergy", "Keto", "Low Sodium"). If a scanned product violates your dietary needs, the app instantly flags it.
*   🥗 **Healthy Alternatives Recommendation**: If a snack gets a poor health verdict, NutriScan suggests 2-3 healthier open-source/community-curated alternatives in the same category.
*   📊 **Nutritional Verdict**: Gives a clear "Healthy / Moderate / Unhealthy" score based on standardized nutritional benchmarks.

### RoadMap: Future Enhancements
*   🔒 **Privacy-First / Offline Mode**: We plan to move OCR and data matching entirely on-device using local models and an offline SQLite database. Your dietary habits stay on your phone.
*   🌍 **Crowdsourced Database**: Allowing users to manually add missing products or correct OCR errors to build a public good, similar to Open Food Facts but focusing on ingredient flag mapping.

---

## 🤖 Why Not Just Take a Picture with Gemini or ChatGPT?

While general-purpose AI is powerful, **NutriScan is purpose-built for speed and utility in a grocery store aisle.**

1.  **Instant Structured Data, Not a Conversation**: General LLMs (like Gemini) return paragraphs of text. You have to read through a conversational response to find out if the snack is safe. NutriScan instantly flashes a red/green/yellow score, highlights specific harmful ingredients, and presents data visually. It’s a 1-second interaction, not a reading exercise.
2.  **Zero-Prompting Diet Profile**: With Gemini, you have to type or speak your dietary restrictions every single time: *"Here is an image of ingredients. Tell me if it violates my Keto diet or my peanut allergy."* NutriScan saves your specific dietary profile once. You just point the camera, and it automatically tests the ingredients against your saved restrictions without you ever having to ask.

---

## ⚙️ How It Works (Architecture Flow)

```text
📸 User Action       🤖 Core Engine                             📂 Data & Output
-------------       -------------                             ----------------
[ Mobile App ] ---> [ Tesseract OCR ] ---> [ NLP Text Cleaning ] ---> [ Ingredient DB Match ]
(Image Scan)        (Extracts Text)        (Extracts Items)           (Checks for flags/allergens)
                                                                            |
                                                                            v
[ User Screen ] <------------------------------------------------- [ Health Analysis Engine ]
(Verdict, Alerts,                                                  (Calculates Score,
 Alternatives)                                                      Finds Alternatives)
```

1. **Scan**: The user captures an image of the ingredient list.
2. **Extract & Clean**: The image is processed through OCR, and the raw text is cleaned using NLP to identify individual ingredients.
3. **Analyze**: The parsed ingredients are checked against our database and the user's personal dietary profile.
4. **Report**: The system calculates a final health score, highlights any allergens or red flags, and offers better alternatives if necessary.

---

## 🛠️ Tech Stack & Justification

| Component | Technology | Why we chose it |
| :--- | :--- | :--- |
| **OCR / Image Processing** | Tesseract OCR / OpenCV | Open-source, reliable text extraction that can be optimized for mobile or quick backend processing. |
| **Database/Datasets** | Open Food Facts / Kaggle | Comprehensive, community-driven nutritional data to map ingredients to their health impacts. |
| **Backend** | Python / FastAPI | Fast, lightweight, and excellent for serving ML/NLP endpoints. |
| **Frontend** | React / Flutter (TBD) | Cross-platform flexibility so users can scan from any device. |
| **ML / NLP** | spaCy / scikit-learn | Efficiently parsing unstructured text (like "Contains 2% or less of...") into clean data arrays. |

---

## 🏗️ Proposed Implementation Plan

### 1. High-Level Folder Structure
To keep concerns separated, the project is structured into a React frontend and a Python backend:
```text
FOSS HACK/
├── backend/                   # Python FastAPI Server (ML/OCR Engine)
│   ├── main.py                # Entry point for the API
│   ├── database.py            # PostgreSQL connection setup
│   ├── models.py              # SQLAlchemy Data Models
│   ├── ocr_engine.py          # Functions to process images with Tesseract
│   ├── nlp_parser.py          # Functions to clean text with spaCy
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React Web App
│   ├── src/
│   │   ├── App.jsx            # Main routing component
│   │   ├── components/        # CameraView, ResultCard, AlertBadge
│   │   └── pages/             # Home, ScanPage, ProfilePage
│   └── package.json
```
### 2. Database Schema (PostgreSQL)
We need three primary tables to make the MVP work:
*   **Users**: Stores the custom profile for Personalization & Allergy alerts (e.g., "Vegan", "Keto").
*   **Ingredients**: Our curated FOSS dictionary of foods with health scores (-1 to 1), descriptions, and flags.
*   **User_Allergies**: Maps a User to specific ingredient flags they want to avoid (e.g., "dairy", "peanut", "artificial").

### 3. API Endpoints Contract (FastAPI)
The frontend app will communicate with the backend via:
*   `POST /api/scan`: Uploads the image and `user_id`. Runs the image through OpenCV -> Tesseract -> spaCy -> Database Match. Returns found ingredients, allergy alerts, and an overall health verdict.
*   `GET /api/user/{user_id}`: Retrieves the user's dietary preferences and specific allergy restrictions.

---


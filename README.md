# 🇮🇳 IndiaGuide — Your Smart Travel Companion for India

> Submitted for **FOSS Hack 2026** | Open Source Hackathon

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [About the Project](#-about-the-project)
- [Features & Implementation](#-features--implementation)
- [Tech Stack](#-tech-stack)
- [Team](#-team)
- [Getting Started](#-getting-started)
- [License](#-license)

---

<!--
=============================================================================
  SECTION OWNER: TEAMMATE 2 — PROBLEM STATEMENT
  Edit everything between this block and the next section marker.
=============================================================================
-->

## 🚨 Problem Statement

India welcomes millions of international tourists every year, yet navigating the country remains one of the most overwhelming experiences for foreign visitors. Despite holding a valid visa, tourists frequently face critical challenges:

- *Lack of centralized, reliable information* — Travel information is scattered across dozens of unverified websites, outdated blogs, and unofficial apps, making it hard for tourists to plan safely and efficiently.
- *Language and cultural barriers* — India has 22 official languages and hundreds of dialects. Foreign tourists often struggle to communicate, understand local customs, or read signage.
- *Safety concerns* — Tourists, especially solo travellers and women, face risks ranging from scams and overcharging to genuine emergencies, with no single point of contact for help.
- *Visa and regulatory confusion* — Tourists are often unaware of restricted areas, e-visa conditions, photography bans, and region-specific entry rules, leading to inadvertent violations.
- *No government-integrated support* — There is no direct, real-time link between a tourist's visit and government databases, embassies, or local law enforcement, leaving tourists unsupported during crises.

*Our Solution:* IndiaGuide bridges this gap by building a government-integrated, open-source web platform that serves as a single, trusted companion for every tourist visiting India — from landing at the airport to safely completing their journey.

---

<!--
=============================================================================
  SECTION OWNER: TEAMMATE 3 — FEATURES & IMPLEMENTATION
  Edit everything between this block and the next section marker.
=============================================================================
-->

## ✨ Features & Implementation

### 🗺️ 1. Personalized Travel Planner
- Tourist fills in their visa type, nationality, duration of stay, and interests.
- The system generates a **customized day-by-day itinerary** with UNESCO sites, hidden gems, and local experiences.
- Integration with **Google Maps API** for routing and navigation.

### 🏛️ 2. Government-Integrated Tourist Portal
- Tie-up with **Ministry of Tourism, India** data feeds to display:
  - Official entry rules, restricted zones, and permit requirements.
  - Real-time updates on closures, festivals, and public holidays.
- Tourist profile is optionally linked to their **e-Visa number** for personalised advisories.

### 🆘 3. Safety & Emergency Features
- **SOS Button** — One tap sends the tourist's GPS location to:
  - Nearest police station.
  - Local Indian embassy/consulate of their home country.
  - A trusted emergency contact.
- **Safe Zone Map** — Highlights government-rated safe areas, tourist police booths, and hospitals.
- **Scam Alert Feed** — Crowdsourced and verified list of common tourist scams in each city, updated regularly.
- **Women Safety Mode** — Shows women-only transport options, safe accommodation, and nearby women helpline numbers.

### 🌐 4. Multilingual Support
- Full UI available in **10+ languages** covering major tourist demographics (English, French, German, Mandarin, Japanese, Arabic, Russian, Korean, Portuguese).
- **Real-time translation** of local signage via phone camera (OCR + Translation API).

### 📍 5. Destination Explorer
- Rich destination cards with:
  - Best time to visit, entry fees, dress code, and dos & don'ts.
  - Offline-capable maps for low/no connectivity regions.
  - User reviews filtered by nationality for relatable experiences.

### 💱 6. Practical Travel Tools
- **Currency Converter** (live INR exchange rates).
- **Local Transport Guide** — Auto, metro, bus, and train booking redirects.
- **Weather Widget** per destination.
- **Cultural Etiquette Guide** — Region-wise customs, temple rules, tipping norms.

### 🔐 7. Visa Compliance Assistant
- Notifies tourists of:
  - Visa expiry reminders.
  - Restricted photography zones.
  - Areas requiring special Inner Line Permits (ILP).
- Helps tourists find the nearest Foreigner Regional Registration Office (FRRO).

### 🛠️ Implementation Plan

| Phase | Milestone | Timeline |
|-------|-----------|----------|
| Phase 1 | Core website setup, authentication, and destination database | Week 1 |
| Phase 2 | Government data integration and itinerary planner | Week 2 |
| Phase 3 | Safety features (SOS, scam alerts, safe zones) | Week 3 |
| Phase 4 | Multilingual support and OCR translation | Week 4 |
| Phase 5 | Testing, accessibility audit, and deployment | Week 5 |

---

<!--
=============================================================================
  SECTION OWNER: TEAMMATE 1 — TECH STACK
  Edit everything between this block and the next section marker.
=============================================================================
-->

## 🛠️ Tech Stack

IndiaGuide is built as a **fully open-source web application**.

### Frontend
| Technology | Purpose |
|------------|---------|
| **React.js** (with Vite) | Fast, component-based UI |
| **Tailwind CSS** | Responsive and accessible styling |
| **React Router** | Client-side navigation |
| **Leaflet.js / Mapbox GL** | Interactive maps |
| **i18next** | Multilingual (i18n) support |

### Backend
| Technology | Purpose |
|------------|---------|
| **Node.js + Express.js** | REST API server |
| **PostgreSQL** | Relational database (destinations, users, alerts) |
| **Redis** | Caching for high-frequency API calls |
| **JWT + OAuth 2.0** | Secure tourist authentication |

### Integrations & APIs
| API / Service | Purpose |
|---------------|---------|
| **Google Maps API** | Navigation and routing |
| **Ministry of Tourism Open Data** | Official destination and permit data |
| **OpenWeatherMap API** | Live weather per destination |
| **Twilio / Firebase Cloud Messaging** | SOS alerts and push notifications |
| **Google Cloud Vision (OCR)** | Real-time signage translation |
| **ExchangeRate-API** | Live currency conversion |

### DevOps & Deployment
| Tool | Purpose |
|------|---------|
| **Docker + Docker Compose** | Containerised local development |
| **GitHub Actions** | CI/CD pipeline |
| **Vercel** (Frontend) | Frontend hosting |
| **Railway / Render** (Backend) | Backend hosting |

### Why Open Source?
- All code is under the **MIT License**.
- Government data integrations use publicly available open APIs.
- Community contributions are welcome via Pull Requests.

---

## 👥 Team

| Name | Role | GitHub |
|------|------|--------|
| Nikhil Karur | Team Lead / Database & Backend | [@Nikhilkarur](https://github.com/Nikhilkarur) |
| Raghu Prasad Manoj Kasyap | Backend Development | [@manojkasyap29](https://github.com/manojkasyap29) |
| Abhiram | Frontend Development | [@abhirambuilds](https://github.com/abhirambuilds) |

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/Nikhilkarur/FOSS-HACK.git
cd FOSS-HACK

# Install dependencies
npm install

# Start the development server
npm run dev
```

> Full setup instructions will be added as the project develops.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for FOSS Hack 2026 — Making India accessible to every traveller.*

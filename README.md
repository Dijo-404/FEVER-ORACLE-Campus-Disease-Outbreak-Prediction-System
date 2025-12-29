# FEVER ORACLE

**Campus Disease Outbreak Prediction System**

FEVER ORACLE is an AI-powered system designed to predict and prevent disease outbreaks on campus. It collects anonymous symptom reports, analyzes patterns using machine learning, and provides early warnings to health officials.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [License](#license)

---

## Features

- **Anonymous Symptom Reporting**: Students can report symptoms without providing personal information
- **Real-time Dashboard**: Health officials can monitor campus health status in real-time
- **Outbreak Predictions**: AI models predict outbreaks 5-7 days in advance
- **Campus Heatmaps**: Visual representation of symptom clusters by location
- **Automated Alerts**: Push notifications when outbreak probability exceeds thresholds
- **Privacy-First Design**: No personal data is collected or stored

---

## Architecture

```
FEVER-ORACLE-Campus-Disease-Outbreak-Prediction-System/
├── frontend/           # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/ # UI components (shadcn/ui)
│   │   ├── pages/      # Page components
│   │   └── lib/        # Utilities
│   └── public/         # Static assets
├── backend/            # FastAPI Python server
│   ├── main.py         # API endpoints
│   └── requirements.txt
└── README.md
```

---

## Technology Stack

### Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui (Radix UI primitives)
- React Router DOM
- Recharts (data visualization)
- TanStack React Query

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic

### Cloud Services (Production)

- Google Cloud Run (backend deployment)
- Firebase Hosting (frontend deployment)
- Vertex AI (ML predictions)
- BigQuery (data analytics)
- Cloud Pub/Sub (real-time alerts)

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- npm or yarn

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:8080`

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

---

## API Documentation

### Endpoints

| Method | Endpoint           | Description           |
| ------ | ------------------ | --------------------- |
| GET    | `/`                | API information       |
| GET    | `/api/health`      | Health check          |
| POST   | `/api/symptoms`    | Submit symptom report |
| GET    | `/api/stats`       | Dashboard statistics  |
| GET    | `/api/alerts`      | Active alerts         |
| GET    | `/api/heatmap`     | Campus zone data      |
| GET    | `/api/predictions` | 14-day forecast       |

### Submit Symptom Report

```bash
curl -X POST http://localhost:8000/api/symptoms \
  -H "Content-Type: application/json" \
  -d '{
    "location": "North Dorms",
    "symptoms": ["fever", "cough"],
    "severity": "moderate"
  }'
```

### Response

```json
{
  "success": true,
  "message": "Report submitted successfully",
  "report_id": "RPT-000001",
  "health_tip": "Stay hydrated and get plenty of rest."
}
```

---

## Deployment

### Frontend (Firebase Hosting)

```bash
cd frontend
npm run build
firebase deploy --only hosting
```

### Backend (Google Cloud Run)

```bash
cd backend
gcloud run deploy fever-oracle-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

---

## License

MIT License

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request

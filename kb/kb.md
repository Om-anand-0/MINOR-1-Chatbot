# Knowledge Base: Swasth AI (Med Aid Bot)

## Project Overview
**Name:** Swasth AI (also referred to as Med Aid Bot)
**Description:** An AI-powered healthcare assistant web application designed to provide medical guidance, connect users with healthcare facilities, and offer disease information.
**Primary Goal:** To serve as a trusted companion for health awareness and healthcare connections.

## Technology Stack
- **Frontend Framework:** React + Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui (Radix UI)
- **Icons:** Lucide React
- **Authentication:** Firebase Authentication (Email/Password + Google Sign-In)
- **Backend (Chatbot):** FastAPI (External RAG backend at `http://localhost:8000/chat`)

## Key Features & Architecture

### 1. Authentication & Security
- **Providers:** Supports Email/Password and Google Sign-In.
- **Protection:** The main application (`/`) is protected. Unauthenticated users are automatically redirected to the Login page (`/login`).
- **Implementation:**
    - `AuthContext.tsx`: Manages global user state (`currentUser`, `login`, `logout`, `googleLogin`).
    - `ProtectedRoute.tsx`: Wrapper component that enforces authentication on specific routes.
    - `firebase.ts`: Firebase configuration (Authentication only, no Storage Bucket).

### 2. Main Dashboard (`Index.tsx`)
The application uses a single-page architecture with a dashboard that switches between different functional sections:
- **Home:** Landing page with hero section, feature cards, and service highlights.
- **Chat:** AI Chatbot interface.
- **Hospitals:** Hospital finder and directory.
- **Diseases:** Disease information database.
- **Doctors:** *Currently Disabled/Hidden* (Commented out in code).

### 3. AI Chatbot (`ChatbotInterface.tsx`)
- **Name:** AI Health Assistant / AI स्वास्थ्य सहायक
- **Functionality:** Provides medical-style responses using a RAG (Retrieval-Augmented Generation) backend.
- **Backend Endpoint:** `POST http://localhost:8000/chat`
- **Features:**
    - Multilingual support (English & Hindi).
    - Pre-defined quick questions (e.g., "Tell me about hypertension").
    - Auto-scrolling and typing simulation.

### 4. Hospital Finder (`HospitalsSection.tsx`)
- **Focus:** Lists top hospitals in Bhopal.
- **Data:** Static list of hospitals (e.g., AIIMS Bhopal, Chirayu Medical College).
- **Features:**
    - Filter by type: All, Government, Private, Specialty.
    - Information: Rating, Distance, Beds, Phone, Departments.
    - Actions: Get Directions (Google Maps), Call Now.

### 5. Disease Database (`DiseaseDatabase.tsx`)
- **Functionality:** Searchable database of common diseases.
- **Data:** Static list of diseases (e.g., Diabetes, Hypertension, Common Cold).
- **Categories:** Common, Chronic, Infectious, Emergency.
- **Details Provided:** Symptoms, Prevention, Medication, Treatment, Causes, Diagnosis.
- **Search:** Filters by name or symptoms.

## Data Models

### User (Firebase)
- Standard Firebase `User` object containing `email`, `uid`, etc.

### Hospital
- `id`, `name`, `type` (Govt/Private), `rating`, `distance`, `beds`, `phone`, `address`, `departments`, `specialties`, `emergencyAvailable`, `ambulanceService`.

### Disease
- `id`, `name`, `category`, `severity`, `symptoms`, `causes`, `prevention`, `medication`, `treatment`, `diagnosis`, `prevalence`.

## Current State & Notes
- **Doctors Section:** The "Connect with Doctors" feature is currently commented out in the navigation and rendering logic of `Index.tsx`.
- **Localization:** The app has built-in support for English (`en`) and Hindi (`hi`), toggled via a `LanguageSelector`.
- **Routing:**
    - `/`: Main App (Protected)
    - `/login`: Login Page
    - `/register`: Registration Page

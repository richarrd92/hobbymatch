# HobbyMatch Frontend

This is the frontend for **HobbyMatch**, a modern social platform for discovering new hobbies, connecting with others, and joining real-life or virtual events. Built with React, Firebase Auth, and Tailwind CSS.

## Features

- Google Sign-In via Firebase (UMBC email restricted)
- Dynamic user dashboards (user, moderatort & admin)
- Profile editing with image upload and location detection
- Hobby-based feed and matchmaking
- Event creation and RSVP system
- Post creation with media, likes, and comments
- Responsive layout with toggleable sidebar and topbar
- Modular components with scoped styles

## Tech Stack

- React 18+
- React Router DOM
- Firebase Auth
- Cloudinary (for image uploads)
- Vite (dev/build tool)
- React Context API (global state)
- Custom Hooks & API utilities

## Directory Structure
```
frontend/
├── public/            
├── src/
│   ├── components/      # Reusable UI components (e.g., PostCard, AuthCard)
│   ├── pages/           # Page-level views (e.g., Dashboard, EditProfile)
│   ├── services/        # API functions (e.g., profile, location)
│   ├── contexts/        # Context for state management
│   ├── App.jsx          # Main app component with routes
│   └── Index.jsx        # Entry point for React/Vite
├── vite.config.js       # Vite configuration
├── .env                 # Firebase and backend URLs
├── index.html           # App entry point
└── package.json         # Project dependencies
```

> **Note:** Ensure that your `.env` file is properly configured with Firebase and backend API base URLs. Firebase Auth should be restricted to UMBC emails in the Firebase Console.
```
    VITE_FIREBASE_API_KEY=
    VITE_FIREBASE_AUTH_DOMAIN=
    VITE_FIREBASE_PROJECT_ID=
    VITE_FIREBASE_STORAGE_BUCKET=
    VITE_FIREBASE_MESSAGING_SENDER_ID=
    VITE_FIREBASE_APP_ID=
```
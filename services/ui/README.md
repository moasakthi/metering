# Metering UI

React frontend for the Metering Service Dashboard.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Start development server:
```bash
npm run dev
```

## Environment Variables

- `VITE_API_URL`: API endpoint URL (default: http://localhost:8000)
- `VITE_API_KEY`: API key for authentication

## Build

```bash
npm run build
```

## Features

- Dashboard with usage summary
- Tenant usage analytics
- Events explorer
- Settings/API key management


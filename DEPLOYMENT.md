# Render + Netlify Deployment

## Frontend on Netlify

- Publish directory: `frontend`
- Frontend calls `/api` and Netlify proxies that path to the Render backend.
- If you rename the Render service, update the redirect in `netlify.toml`.
- `frontend/admin/qrcodes.html` automatically builds the guest QR URL based on whether the site is served from Netlify or from the backend.

## Backend on Render

- Service type: Web Service
- Environment: Docker
- Dockerfile: `backend/Dockerfile`

### Required env vars

- `SECRET_KEY`
- `ALLOWED_ORIGINS`

`DATABASE_URL` is optional now. If you do not set it, the app uses a local SQLite file (`coffee.db`) and seeds demo data on first startup.

## Important note

This is the fastest free deployment path. It is good for demo/testing. If you need production-grade persistence, move from SQLite to a managed database later.

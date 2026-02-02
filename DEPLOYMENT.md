# Docker Compose Deployment Guide

## Deployment Options

### Option 1: Production Deployment (Using Pre-built Images)

**Recommended for production servers** - Uses images built by GitHub Actions and stored in GitHub Container Registry.

### Option 2: Local Development (Build Locally)

**For development** - Builds images locally from source code.

---

## Production Deployment

### Prerequisites

1. Docker and Docker Compose installed on your server
2. Access to the `nginx_pm_network` Docker network
3. GitHub Container Registry images (built via GitHub Actions)

### Initial Setup

1. **Clone the repository on your server:**
   ```bash
   git clone https://github.com/ACoullard/wizcord.git
   cd wizcord
   ```

2. **Copy and configure environment file:**
   ```bash
   cp .env.example .env
   nano .env  # or vim, etc.
   ```
   
   Set these required values:
   - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
   - `FRONTEND_URL`: Your frontend domain (e.g., `https://app.example.com`)

3. **Ensure the external network exists:**
   ```bash
   docker network ls | grep nginx_pm_network
   ```
   If it doesn't exist, create it:
   ```bash
   docker network create nginx_pm_network
   ```

4. **Pull and start the services:**
   ```bash
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Verify deployment:**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   docker-compose -f docker-compose.prod.yml logs -f
   ```

### Creating a Release (GitHub Actions)


2. **Create and push a tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   
   Or use GitHub UI: Releases → Create a new release

3. **GitHub Actions will automatically:**
   - Build both frontend and backend Docker images
   - Push them to `ghcr.io/acoullard/wizcord-backend` and `ghcr.io/acoullard/wizcord-frontend`
   - Tag them with both the version (e.g., `v1.0.0`) and `latest`

4. **Deploy on your server:**
   ```bash
   cd wizcord
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

---

## Local Development

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and set required values:**
   - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
   - `FRONTEND_URL`: `http://localhost:5173` (for Vite dev server)
   - `VITE_API_URL`: `http://localhost:8000` (for local backend)

3. **Build and start services:**
   ```bash
   docker-compose up -d --build
   ```

4. **Check status:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## Services

- **frontend**: React app served by nginx (accessible via reverse proxy)
- **backend**: Flask app with Gunicorn (accessible via reverse proxy)
- **mongodb**: MongoDB database (internal only)
- **redis**: Redis cache (internal only)

## Network Architecture

- `nginx_pm_network` (external): Frontend and backend are accessible here for your reverse proxy
- `wizcord_internal` (internal): Backend, MongoDB, and Redis communicate here

## Reverse Proxy Configuration

Configure your reverse proxy (e.g., Nginx Proxy Manager) to route:
- Frontend traffic to: `http://wizcord_frontend:80`
- Backend API traffic to: `http://wizcord_backend:8000`

## Persistent Data

Data is stored in named volumes:
- `wizcord_mongodb_data`: MongoDB database files
- `wizcord_redis_data`: Redis persistence files

## Common Commands

### Production
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Start/update services
docker-compose -f docker-compose.prod.yml up -d

# Stop services
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f [service-name]

# Deploy specific version
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Development
```bash
# Start services
docker-compose up -d

# Rebuild after code changes
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Remove everything including volumes (WARNING: deletes data!)
docker-compose down -v
```

## Troubleshooting

**Services won't start:**
- Check logs: `docker-compose logs`
- Verify network exists: `docker network ls | grep nginx_pm_network`
- Ensure `.env` file is properly configured

**Can't connect to services:**
- Verify services are healthy: `docker-compose ps`
- Check network connectivity: `docker network inspect nginx_pm_network`
- Verify reverse proxy configuration

**Database connection errors:**
- Wait for MongoDB to fully start (check with `docker-compose logs mongodb`)
- Healthchecks ensure backend waits for database readiness

## Before First Release

You need to set a GitHub secret for the frontend build:

1. Go to your repo → Settings → Secrets and variables → Actions
2. Add repository secret: `VITE_BACKEND_URL` = your backend API URL (e.g., `https://api.yourdomain.com/api`)

This is required because the frontend build embeds this URL into the compiled JavaScript at build time.

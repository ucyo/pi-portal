# Pi Portal - Docker Deployment Guide

Complete guide to deploying Pi Portal using Docker and Docker Compose.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Building the Image](#building-the-image)
- [Running with Docker Compose](#running-with-docker-compose)
- [Configuration](#configuration)
- [Data Persistence](#data-persistence)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/pi-portal.git
cd pi-portal

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Open browser
open http://localhost:8000
```

---

## Prerequisites

### Required Software

- **Docker** 20.10+ ([Installation guide](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ ([Installation guide](https://docs.docker.com/compose/install/))

### Verify Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10.0 or higher

# Check Docker Compose version
docker-compose --version
# Expected: Docker Compose version 2.0.0 or higher
```

---

## Building the Image

### Build Locally

```bash
# Build the Docker image
docker build -t pi-portal:latest .

# Verify image built successfully
docker images | grep pi-portal
```

### Build with Docker Compose

```bash
# Build image via docker-compose
docker-compose build

# Or rebuild without cache
docker-compose build --no-cache
```

### Multi-platform Build

For ARM64 (Apple Silicon, Raspberry Pi) and AMD64 (Intel/AMD):

```bash
# Create builder instance
docker buildx create --name pi-portal-builder --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t pi-portal:latest \
  --push \
  .
```

---

## Running with Docker Compose

### Start Services

```bash
# Start in detached mode (background)
docker-compose up -d

# Start in foreground (see logs)
docker-compose up

# Start and rebuild
docker-compose up -d --build
```

### Stop Services

```bash
# Stop containers (keep volumes)
docker-compose stop

# Stop and remove containers (keep volumes)
docker-compose down

# Stop, remove containers, and remove volumes (⚠️ DELETES DATA)
docker-compose down -v
```

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs (real-time)
docker-compose logs -f

# Logs for specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100
```

### Container Management

```bash
# List running containers
docker-compose ps

# Restart service
docker-compose restart backend

# Execute command in container
docker-compose exec backend /bin/bash

# View resource usage
docker stats
```

---

## Configuration

### Environment Variables

**Option 1: Use .env.docker file**

```bash
# Copy example file
cp .env.docker.example .env.docker

# Edit configuration
nano .env.docker

# Docker Compose automatically loads .env.docker
docker-compose up -d
```

**Option 2: Edit docker-compose.yml**

```yaml
services:
  backend:
    environment:
      PI_PORTAL_SERVER_PORT: 8000
      PI_PORTAL_PI_SESSION_DIR: /data/pi_sessions
```

**Option 3: Command-line override**

```bash
# Override port
PI_PORTAL_SERVER_PORT=3000 docker-compose up -d
```

### Available Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PI_PORTAL_SERVER_HOST` | `0.0.0.0` | Server bind address |
| `PI_PORTAL_SERVER_PORT` | `8000` | Server port (host) |
| `PI_PORTAL_PI_EXECUTABLE` | `/usr/bin/pi` | Pi executable path |
| `PI_PORTAL_PI_SESSION_DIR` | `/data/pi_sessions` | Session storage directory |
| `PI_PORTAL_SERVER_RELOAD` | `false` | Auto-reload (dev only) |

### Port Mapping

Change host port (container always uses 8000):

```yaml
ports:
  - "3000:8000"  # Access on http://localhost:3000
```

Or via environment:

```bash
PI_PORTAL_SERVER_PORT=3000 docker-compose up -d
```

---

## Data Persistence

### Session Storage

Session data is stored in a **Docker volume** for persistence.

**Volume Details:**
- Name: `pi-portal_pi-sessions`
- Mount point: `/data/pi_sessions` (inside container)
- Driver: `local`

### Inspect Volume

```bash
# List volumes
docker volume ls

# Inspect volume details
docker volume inspect pi-portal_pi-sessions

# Find volume location on host
docker volume inspect pi-portal_pi-sessions --format '{{ .Mountpoint }}'
```

### Backup Sessions

```bash
# Backup to tar archive
docker run --rm \
  -v pi-portal_pi-sessions:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/sessions-backup.tar.gz -C /data pi_sessions

# Restore from backup
docker run --rm \
  -v pi-portal_pi-sessions:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/sessions-backup.tar.gz -C /data
```

### Access Session Files

```bash
# Copy session files from container
docker cp pi-portal-backend:/data/pi_sessions ./sessions-local

# View session files
docker-compose exec backend ls -la /data/pi_sessions
```

### Using Host Directory (Alternative)

Mount local directory instead of Docker volume:

```yaml
volumes:
  - ./data/pi_sessions:/data/pi_sessions
```

**Advantages:**
- Easy access from host
- Simple backups

**Disadvantages:**
- Permission issues on some systems
- Slower on Docker Desktop (Mac/Windows)

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Port already in use: Change `PI_PORTAL_SERVER_PORT`
- Permission denied: Check volume permissions
- Image not found: Run `docker-compose build`

### Health Check Failing

```bash
# Check health status
docker-compose ps

# Manual health check
docker-compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

### WebSocket Connection Issues

**Check from host:**
```bash
# Test WebSocket connection
npm install -g wscat
wscat -c ws://localhost:8000/ws
```

**Check firewall:**
- Ensure port 8000 is open
- Check Docker network settings

### Pi Process Crashes

```bash
# Check Pi is installed
docker-compose exec backend which pi

# Test Pi directly
docker-compose exec backend pi --version

# Check logs for Pi errors
docker-compose logs -f backend | grep -i "pi"
```

### Permission Issues

```bash
# Check user inside container
docker-compose exec backend whoami
# Should be: piportal

# Check file permissions
docker-compose exec backend ls -la /data/pi_sessions

# Fix permissions (if needed)
docker-compose exec --user root backend chown -R piportal:piportal /data
```

### Rebuild Everything

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi pi-portal:latest

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

## Production Deployment

### Security Best Practices

1. **Use HTTPS/WSS**
   - Put behind reverse proxy (nginx, Traefik)
   - Use SSL certificates (Let's Encrypt)

2. **Restrict Access**
   - Add authentication
   - Use firewall rules
   - Limit exposed ports

3. **Update Regularly**
   ```bash
   git pull
   docker-compose build
   docker-compose up -d
   ```

4. **Monitor Logs**
   - Set up log aggregation (ELK, Loki)
   - Monitor container health
   - Set up alerts

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Restart Policies

Already configured as `restart: unless-stopped`

Options:
- `no`: Never restart
- `always`: Always restart
- `on-failure`: Restart on error
- `unless-stopped`: Restart unless manually stopped

### Example Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name pi-portal.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Swarm / Kubernetes

For orchestration at scale, see:
- Docker Swarm: [docs/SWARM.md](SWARM.md) (future)
- Kubernetes: [docs/KUBERNETES.md](KUBERNETES.md) (future)

---

## Advanced Configuration

### Custom Starter Prompts

Mount custom prompts file:

```yaml
volumes:
  - ./my-prompts.json:/app/config/starter_prompts.json:ro
```

### Development Mode

Enable auto-reload for development:

```yaml
environment:
  PI_PORTAL_SERVER_RELOAD: "true"
volumes:
  - ./backend:/app/backend  # Mount source code
  - ./frontend:/app/frontend
```

### Using External Pi Service

If running Pi separately (not recommended):

```yaml
environment:
  PI_PORTAL_PI_EXECUTABLE: /path/to/external/pi
```

---

## Docker Commands Cheat Sheet

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start services in background |
| `docker-compose down` | Stop and remove containers |
| `docker-compose logs -f` | Follow logs |
| `docker-compose ps` | List containers |
| `docker-compose restart` | Restart all services |
| `docker-compose build` | Build images |
| `docker-compose pull` | Pull latest images |
| `docker-compose exec backend bash` | Shell into container |
| `docker volume ls` | List volumes |
| `docker system prune` | Clean up unused resources |

---

## FAQ

### Why is Pi inside the backend container?

Pi runs as a subprocess of the backend, so they must be in the same container. This simplifies deployment and ensures they can communicate via stdin/stdout.

### Can I scale horizontally?

Not currently. The architecture uses a single Pi subprocess per backend instance. For scaling, you'd need to:
1. Separate Pi into its own service
2. Use a message queue
3. Implement session affinity

### How do I update Pi?

Rebuild the Docker image:

```bash
docker-compose build --no-cache
docker-compose up -d
```

Pi is installed during image build from npm.

### Can I use a different Python version?

Edit `Dockerfile`:

```dockerfile
FROM python:3.11-slim AS builder
```

Rebuild the image.

### How much disk space do sessions use?

Depends on usage. Estimate:
- ~10KB per session with 10 messages
- ~100KB per session with 100 messages
- Monitor with: `docker system df -v`

---

## Support

- **Documentation**: [README.md](../README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/pi-portal/issues)

---

**Deployment tested on:**
- Docker 20.10+ on Ubuntu 22.04
- Docker Desktop on macOS (M1/Intel)
- Docker Desktop on Windows 11

**Note:** This Docker setup is designed for single-instance deployment. For multi-user production environments, additional architecture changes are needed (see M5 notes in SPEC.md).

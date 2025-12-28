# 📝 Memos - Self-hosted Notes & Journal

**A modern, self-hosted note-taking and journaling system with PostgreSQL backend**

Memos provides a clean, fast interface for capturing thoughts, ideas, and daily notes. Perfect for homelab documentation, project notes, and personal journaling.

## 🚀 Features

- **Fast & Simple**: Clean web interface optimized for quick note capture
- **PostgreSQL Backend**: Reliable data persistence with full-text search
- **Site Host Mode**: Complete control over your data and users
- **Markdown Support**: Rich formatting for notes and documentation
- **Mobile Friendly**: Responsive design works on all devices
- **Docker Swarm Ready**: Optimized for multi-node deployment

## 🔗 Access

- **URL**: https://memos.homehill.de
- **First Visit**: Register as Site Host to set up admin account
- **Authentication**: Local accounts (no external dependencies)

## 🏗️ Infrastructure

- **Image**: `ghcr.io/usememos/memos:latest`
- **Database**: PostgreSQL (shared `postgres_database_network`)
- **Reverse Proxy**: Traefik with automatic HTTPS
- **Storage**: NFS volume mounted at `/var/opt/memos`
- **User**: UID 7001 (memos-svc) from homehill UID schema

## 🛠️ Deployment

```bash
# Deploy the stack
docker stack deploy -c memos-stack.yml memos

# Check service status
docker service ls | grep memos
docker service logs memos_memos
```

## 🔧 Configuration

Key configuration flags in the deployment:
- `--driver postgres`: Use PostgreSQL backend
- `--addr 0.0.0.0`: Bind to all interfaces (required for Swarm)
- `--port 5230`: Internal service port
- `--mode prod`: Production mode

## 📊 Monitoring

Check service health:
```bash
# Service status
docker service ps memos_memos

# Container logs
docker service logs memos_memos --tail=50

# Database connection test
docker exec -it $(docker ps -q --filter name=postgres) \
  psql -U memos_user -d memos -c "SELECT 1;"
```

---

*Deployed with ❤️ by Bear & Ana - First note: "Gateway timeout finally solved!" 🎉*
```
# 🔍 Memos Troubleshooting Guide

**Common issues and solutions for Memos in Docker Swarm**

## 🚨 Gateway Timeout (504)

**Symptoms**: Browser shows "Gateway Timeout" when accessing memos.homehill.de

### Root Cause: Network Disambiguation
When services are attached to multiple Docker overlay networks, Traefik may choose the wrong network for upstream connections.

### Solution: Network Label
Add explicit network label to service deployment:
```yaml
deploy:
  labels:
    - "traefik.docker.network=traefik_traefik_proxy"
```

### Debugging Steps

1. **Check Traefik Dashboard**
   ```
   https://traefik.homehill.de
   ```
   - Look for `memos@swarm` service
   - Verify "Server" IP is from proxy network (10.0.3.x)
   - Status should be green/healthy

2. **Test Direct Connection**
   ```bash
   # From Traefik container
   docker exec $(docker ps -q --filter name=traefik) \
     wget -T5 http://10.0.X.XXX:5230 -O-
   ```

3. **Check Service Networks**
   ```bash
   docker service inspect memos_memos \
     --format='{{json .Spec.TaskTemplate.Networks}}'
   ```

## 🔌 Application Not Binding

**Symptoms**: Service appears running but connections time out

### Root Cause: Localhost Binding
By default, memos binds to `127.0.0.1` (localhost only), making it unreachable from other containers.

### Solution: Explicit Bind Address
Add `--addr 0.0.0.0` flag to bind to all interfaces:
```yaml
command:
  - ./memos --addr 0.0.0.0 --port 5230 [other flags]
```

### Verification
Check service logs for bind address:
```bash
docker service logs memos_memos | grep "addr:"
# Should show: addr: 0.0.0.0
```

## 🗄️ Database Connection Issues

**Symptoms**: Memos starts but can't access data

### Common Causes
- Database not ready when memos starts
- Wrong connection string
- Missing database/user

### Debug Commands
```bash
# Check PostgreSQL service
docker service ps postgres_postgres

# Test database connection
docker exec -it $(docker ps -q --filter name=postgres) \
  psql -U memos_user -d memos -c "\dt"

# Check memos logs for database errors
docker service logs memos_memos | grep -i postgres
```

## 🔄 Cross-Node Communication

**Symptoms**: Service works when Traefik and memos are on same node, fails otherwise

### Root Cause: Overlay Network Issues
Docker Swarm routing mesh may have issues with cross-node communication.

### Debugging
```bash
# Check which nodes services run on
docker service ps traefik_traefik
docker service ps memos_memos

# Test overlay network connectivity
docker network ls | grep overlay
nc -zv [other-node-ip] 7946  # Swarm control plane
nc -zvu [other-node-ip] 4789  # VXLAN data plane
```

## 📋 Quick Health Check

Run this comprehensive check:
```bash
#!/bin/bash
echo "=== Memos Health Check ==="
echo "Service Status:"
docker service ls | grep memos

echo -e "\nTraefik Detection:"
curl -s http://traefik.homehill.de/api/http/services | grep -i memos

echo -e "\nDirect Connection Test:"
MEMOS_IP=$(docker service inspect memos_memos --format='{{range .Endpoint.VirtualIPs}}{{.Addr}}{{end}}' | cut -d'/' -f1)
timeout 5 bash -c "</dev/tcp/$MEMOS_IP/5230" && echo "Port reachable" || echo "Port unreachable"

echo -e "\nDatabase Connection:"
docker exec $(docker ps -q --filter name=postgres) \
  psql -U memos_user -d memos -c "SELECT version();" 2>/dev/null && echo "DB OK" || echo "DB Error"
```

---

*Debugged with forensic precision by Bear & Ana - October 27, 2025* 🔍💻
```
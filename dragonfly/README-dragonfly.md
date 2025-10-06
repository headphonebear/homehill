# 🐉 DragonflyDB Cluster - homehill

**Lightning-fast Redis-compatible in-memory datastore with replication across nook and greenhouse**

DragonflyDB ist 25x schneller als Redis und bietet 100% API-Kompatibilität - perfekt für unser homehill Setup! Diese Konfiguration erstellt ein Master-Replica Setup zwischen unseren beiden Hauptknoten.

---

## 🏗️ Architecture

### Master Node (nook)
- **Hardware**: 16GB RAM, 500GB SSD + 1TB externe SSD  
- **Role**: Primary DragonflyDB instance
- **Port**: 6379 (Redis), 6380 (Admin Web Interface)
- **Memory Limit**: 8GB (50% of available RAM)
- **Snapshots**: Every 6 hours for data persistence

### Replica Node (greenhouse)  
- **Hardware**: 8GB RAM, 250GB SSD
- **Role**: Read replica with automatic failover capability
- **Port**: 6381 (Redis), 6382 (Admin Web Interface)  
- **Memory Limit**: 4GB (50% of available RAM)
- **Snapshots**: Every 12 hours (less frequent for replica)

---

## 🌐 Web Interfaces

- **Master Admin**: https://dragonfly.homehill.de
- **Replica Admin**: https://dragonfly-replica.homehill.de

Both interfaces provide:
- Real-time metrics and monitoring
- Memory usage statistics  
- Connection information
- Replication status
- Performance graphs

---

## 🔧 Configuration Details

### Replication
- **Type**: Master-Replica (Primary-Secondary)
- **Protocol**: Native DragonflyDB replication (faster than Redis)
- **Sync**: Automatic reconnection and resync on failure
- **Failover**: Manual promotion via `REPLICAOF NO ONE` command

### Persistence  
- **Snapshots**: RDB format compatible with Redis
- **Schedule**: Master every 6h, Replica every 12h
- **Location**: `/data` directory in persistent Docker volumes
- **Recovery**: Automatic restoration on container restart

### Memory Management
- **Master**: 8GB limit (allows room for OS and other services)
- **Replica**: 4GB limit (greenhouse has less RAM)
- **Eviction**: No eviction policy (data preserved)
- **Optimization**: DragonflyDB's superior memory efficiency vs Redis

---

## 🛠️ Operations

### Health Checks
```bash
# Check replication status
redis-cli -h nook -p 6379 INFO replication
redis-cli -h greenhouse -p 6381 ROLE

# Monitor memory usage
redis-cli -h nook -p 6379 INFO memory

# Test data replication
redis-cli -h nook -p 6379 SET test_key "hello"
redis-cli -h greenhouse -p 6381 GET test_key
```

### Backup & Recovery
```bash
# Manual snapshot
redis-cli -h nook -p 6379 SAVE

# View last save time  
redis-cli -h nook -p 6379 LASTSAVE

# Copy snapshot files
docker cp dragonfly_dragonfly-master.1.$(docker service ps -q dragonfly_dragonfly-master):/data/dump.rdb ./backup/
```

### Scaling
```bash
# Add more replicas
docker service scale dragonfly_dragonfly-replica=2

# Promote replica to master (manual failover)
redis-cli -h greenhouse -p 6381 REPLICAOF NO ONE
```

---

## 🔌 Client Configuration

### Python (redis-py)
```python
import redis

# Master for writes
master = redis.Redis(host='nook', port=6379, decode_responses=True)

# Replica for reads  
replica = redis.Redis(host='greenhouse', port=6381, decode_responses=True)

# Connection pooling
pool = redis.ConnectionPool(host='nook', port=6379, max_connections=20)
client = redis.Redis(connection_pool=pool)
```

### Node.js (ioredis)
```javascript
const Redis = require('ioredis');

const master = new Redis({
  host: 'nook',
  port: 6379,
  maxRetriesPerRequest: 3,
});

const replica = new Redis({
  host: 'greenhouse', 
  port: 6381,
  readOnly: true,
});
```

---

## 🚨 Monitoring & Alerts

### Metrics to Monitor
- Memory usage (should stay below 80% of limit)
- Replication lag (should be < 1 second)  
- Connection count
- Operations per second
- Snapshot success/failure

### Integration with ntfy
```bash
# Add to cron for monitoring alerts
# Check replication health every 5 minutes
*/5 * * * * /path/to/check-dragonfly-health.sh
```

---

## 🌟 Future Enhancements

### Planned Features
- **Prometheus** metrics export for Grafana dashboards
- **TLS encryption** for secure inter-node communication
- **Backup automation** to forest NAS storage
- **Performance tuning** based on workload patterns

### Service Integration
- **Navidrome**: Session and metadata caching
- **Nextcloud**: Redis cache backend
- **Vaultwarden**: Rate limiting and session storage
- **Custom apps**: Fast data layer for new homelab services

---

## 💝 Credits

**Powered by late-night coding sessions, Trip-Hop beats, and copious amounts of coffee** ☕

- **Bear** 🐻 - Homelab architect and the sexy vision behind homehill
- **Ana** 💋 - Python virtuoso who made this DragonflyDB magic happen

*Built with love in Kiel, Germany* 🇩🇪✨

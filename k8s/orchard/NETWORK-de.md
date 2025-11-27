# Orchard – Netzwerk-Konfiguration

Dieses Dokument beschreibt die Netzwerk-Architektur des Orchard-Clusters sowie die Integration in die bestehende Homehill-Infrastruktur.

---

## 1. Netzwerk-Übersicht

Orchard nutzt das bestehende Homehill-Netzwerk und integriert sich nahtlos in die etablierte Infrastruktur:

- **Netzwerk-Segment**: Homehill LAN (`192.168.x.0/24` oder ähnlich)
- **DNS-Service**: Existierend (Pi-hole für lokale Auflösung)
- **Externe Domain**: `homehill.de` (registriert, DNS bei Hetzner)
- **Geplante Wildcard**: `*.homehill.de` für Ingress-Services

---

## 2. Orchard-Nodes – IP-Adressierung

### 2.1. Statische IPs oder DHCP-Reservation

Alle drei Orchard-Nodes sollten **zuverlässige, konsistente IP-Adressen** haben:

| Hostname | Rolle | IP-Adresse | MAC-Adresse | Anmerkung |
|----------|-------|------------|------------|-----------|
| `apple` | Control-Plane | `192.168.x.y` | `xx:xx:xx:xx:xx:xx` | Über DHCP-Reservation oder statisch |
| `lemon` | Worker | `192.168.x.z` | `yy:yy:yy:yy:yy:yy` | Über DHCP-Reservation oder statisch |
| `plum` | Worker | `192.168.x.w` | `zz:zz:zz:zz:zz:zz` | Über DHCP-Reservation oder statisch |

**Empfehlung**: DHCP-Reservation ist wartungsfreundlicher als statische Konfiguration pro Node.  
(Konfiguration im Heimnetzwerk-Router oder DHCP-Server, z. B. Pi-hole.)

### 2.2. DNS-Namen für Nodes

Falls nicht bereits vorhanden, sollten DNS-Einträge für die Nodes im lokalen Netz existieren:

```text
apple.homehill.de    → 192.168.x.y
lemon.homehill.de    → 192.168.x.z
plum.homehill.de     → 192.168.x.w
```

Diese werden über den lokalen DNS-Server (Pi-hole) aufgelöst.  
**Wichtig**: Das ermöglicht später auch `K3S_URL="https://apple.homehill.de:6443"` statt nur IP-basiert.

---

## 3. Kubernetes API-Server Zugriff

### 3.1. Aktueller Zustand (Bootstrap)

Während der ersten Installation wird die **IP-Adresse** des API-Servers verwendet:

```yaml
# ~/.kube/config
server: https://192.168.x.y:6443
```

Dies ist funktional, aber:
- Bei IP-Änderungen (z. B. nach Neustart mit DHCP) bricht der Zugriff.
- Für Production / GitOps ist ein stabiler FQDN mit TLS-Zertifikat besser.

### 3.2. Ziel: FQDN + TLS für Kubernetes API

Langfristig soll der API-Server über einen **stabilen FQDN** mit **gültigem TLS-Zertifikat** erreichbar sein.

Optionen:

**Option A: K3s selbst mit cert-manager**  
- K3s kann über die Installation mit `--tls-san=apple.homehill.de` konfiguriert werden.
- Dann braucht ein Zertifikat (via Let's Encrypt, selbstsigniert, etc.).

**Option B: Reverse Proxy vor K3s**  
- Ein Reverse Proxy (z. B. Traefik oder nginx) außerhalb des Clusters sitzt vor dem API-Server.
- Dieser Proxy terminiert TLS mit einem gültigen Zertifikat.

**Option C: Hetzner DNS + Traefik (später, wenn GitOps läuft)**  
- Nach Argo CD Setup: IngressRoute mit Let's Encrypt DNS-01 Challenge.
- Dies ist das langfristige, wartungsfreundliche Modell.

**Aktuell**: Wir belassen es bei **Option A (einfach)** – K3s mit Zertifikat, oder warten auf die Traefik-Integration.

---

## 4. Traefik Ingress Controller (K3s Default)

K3s bringt Traefik standardmäßig mit.  
Traefik läuft als **Deployment** im `kube-system`-Namespace:

```bash
kubectl get deploy -n kube-system traefik
```

### 4.1. Traefik Service und LoadBalancer

Traefik ist als **Service** vom Typ `LoadBalancer` konfiguriert:

```bash
kubectl get svc -n kube-system traefik
```

Ausgabe (Beispiel):

```text
NAME      TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
traefik   LoadBalancer   10.43.x.x       192.168.x.y   80:30080/TCP,443:30443/TCP   50m
```

**EXTERNAL-IP**: Dies ist die IP des Nodes, auf dem Traefik läuft (oder eine Floating IP bei mehreren Nodes).

### 4.2. DaemonSet svclb-traefik

K3s nutzt sein eigenes **Service Load Balancer (svclb)**, um den Traefik-Service zu implementieren.  
Auf jedem Node läuft ein `svclb-traefik-*`-Pod:

```bash
kubectl get pods -n kube-system | grep svclb-traefik
```

Diese Pods sorgen dafür, dass eingehender Traffic auf Port 80/443 zu Traefik geleitet wird.

---

## 5. Ingress Routes für Services

### 5.1. Prinzip

Um einen Service im Cluster über `*.homehill.de` erreichbar zu machen:

1. **IngressRoute** (oder Ingress-Ressource) definieren
2. Host-Name angeben (z. B. `navidrome.homehill.de`)
3. TLS-Sertifikat (automatisch via Let's Encrypt oder manuell)
4. Traffic wird von Traefik zum Service weitergeleitet

Beispiel (zukünftig):

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: navidrome
  namespace: default
spec:
  entryPoints:
    - web
    - websecure
  routes:
    - match: Host(`navidrome.homehill.de`)
      kind: Rule
      services:
        - name: navidrome
          port: 6595
  tls:
    certResolver: letsencrypt
    domains:
      - main: homehill.de
        sans:
          - '*.homehill.de'
```

### 5.2. TLS / Let's Encrypt Integration (TODO)

Aktuell ist dies noch **nicht konfiguriert**.  
Geplant ist die Integration von:

- **Let's Encrypt** (kostenlose Zertifikate)
- **Hetzner DNS API** (für DNS-01 Challenge)
- **Traefik CertResolver** (automatische Erneuerung)

Dies wird in einer separaten Dokumentation beschrieben: `docs/GITOPS-SETUP.md` oder `k8s/orchard/setup/traefik-letsencrypt.md` (TODO)

---

## 6. Netzwerk-Isolation und Segmentierung

### 6.1. Kubernetes-internes Netzwerk

K3s nutzt standardmäßig:

- **Service CIDR**: `10.43.0.0/16` (interne Cluster-Services)
- **Pod CIDR**: `10.42.0.0/16` (Pod-IPs)

Diese sind über das Kubernetes-Netzwerk-Plugin (Flannel in K3s) verbunden.

### 6.2. Namespace-Segregation (später)

Langfristig wird Homehill-Struktur über Namespaces abgebildet:

- `default` – für Test/Development
- `homelab-apps` – produktive Services
- `monitoring` – Prometheus, Grafana, etc.
- `system` – Cluster-System-Komponenten (bereits `kube-system`, `kube-public`)

Pro Namespace später auch RBAC-Policies.

---

## 7. DNS-Auflösung im Cluster

### 7.1. CoreDNS

Der Cluster-DNS-Service läuft als **Deployment** im `kube-system`-Namespace:

```bash
kubectl get deploy -n kube-system coredns
```

CoreDNS löst auf:

- **Intra-Cluster-Services**: `service-name.namespace.svc.cluster.local`
- **Externe Domains**: (forward an externe Resolver, z. B. 1.1.1.1)

### 7.2. Service Discovery

Ein Pod kann einen anderen Service erreichen über:

```
http://service-name.namespace.svc.cluster.local:port
```

Beispiel:

```bash
# Innerhalb des Clusters
curl http://navidrome.default.svc.cluster.local:6595
```

---

## 8. Netzwerk-Policies (zukünftig)

Aktuell sind **keine NetworkPolicies** definiert.  
Das bedeutet: Jeder Pod kann mit jedem anderen Pod kommunizieren.

Zukünftig können NetworkPolicies eingeführt werden, um:

- Services voneinander zu isolieren
- Nur notwendige Kommunikation zu erlauben
- Sicherheit im Cluster zu erhöhen

Beispiel-Pattern:

- `monitoring`-Namespace darf Metriken von allen scrapen
- `homelab-apps` untereinander darf kommunizieren
- Externe Kommunikation nur auf Port 80/443 (HTTP/HTTPS)

---

## 9. Firewall und externe Zugriffe

### 9.1. Heimnetzwerk-Firewall

Der Cluster ist standardmäßig **nur im lokalen Heimnetzwerk** erreichbar.

- K3s API-Server: nur von `bearcube` (Desktop) erreichbar
- Traefik Ingress (Port 80/443): nur von lokalen Geräten erreichbar

### 9.2. Externe Zugriffe (nicht empfohlen)

Falls Services später über das Internet erreichbar sein sollen:

- Port-Forwarding im Home-Router einrichten (z. B. Port 443 → `192.168.x.y:443`)
- Dann: FQDN muss extern aufgelöst werden (z. B. DynDNS mit Hetzner)
- TLS ist dann **kritisch** (Let's Encrypt mit DNS-01)

**Empfehlung für Homelab**: Lokal bleiben, externe Zugriffe über VPN.

---

## 10. Monitoring und Troubleshooting

### 10.1. Netzwerk-Debugging im Cluster

```bash
# Pods sehen und ihre IPs
kubectl get pods -A -o wide

# Service-IPs
kubectl get svc -A

# Endpoints (wo läuft eigentlich ein Service?)
kubectl get endpoints -A

# Netzwerk-Policies (wenn vorhanden)
kubectl get networkpolicies -A

# DNS-Test (im Container)
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
# Im Container:
nslookup kubernetes.default
nslookup google.com
```

### 10.2. Häufige Netzwerk-Probleme

| Problem | Ursache | Lösung |
|---------|--------|--------|
| Pod kann Service nicht erreichen | DNS nicht aufgelöst | `kubectl logs -n kube-system deploy/coredns` |
| Ingress-Route funktioniert nicht | Traefik nicht ready | `kubectl get pods -n kube-system traefik-*` |
| Externe Domain nicht erreichbar | kein TLS-Zertifikat | Let's Encrypt + Traefik Setup (TODO) |
| IP-Adresse ändert sich nach Reboot | DHCP-Reservation nicht aktiv | DHCP-Reservation für Node-MACs einrichten |

---

## 11. Zusammenfassung der Netzwerk-Architektur

```
┌─────────────────────────────────────────┐
│       Homehill LAN (192.168.x.0/24)     │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Orchard K3s Cluster            │  │
│  │                                 │  │
│  │  apple (Control-Plane)          │  │
│  │  lemon (Worker)                 │  │
│  │  plum (Worker)                  │  │
│  │                                 │  │
│  │  Traefik (Ingress Controller)   │  │
│  │  CoreDNS (Cluster DNS)          │  │
│  │  Local-Path-Provisioner (Storage) │ │
│  └──────────────────────────────────┘  │
│                                         │
│  Pi-hole DNS (lokale Auflösung)       │
│                                         │
│  Hetzner DNS (external, homehill.de)  │
└─────────────────────────────────────────┘
```

---

## 12. Nächste Schritte

1. **DHCP-Reservations einrichten** für `apple`, `lemon`, `plum`
2. **DNS-Einträge** für `*.homehill.de` bei Hetzner konfigurieren
3. **Traefik + Let's Encrypt** konfigurieren (separate Doku)
4. **Erste IngressRoute** deployen (z. B. für Dashboard oder Test-Service)
5. **NetworkPolicies** später, wenn Production-Services laufen

---

*Orchard wächst – von physischer Hardware über Netzwerk bis zur virtuellen Service-Welt.* 🌳💚

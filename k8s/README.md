# 🌳 Orchard – Homehill Kubernetes Cluster

Orchard ist der Kubernetes‑Cluster im Homehill‑Homelab.  
Er ersetzt nach und nach Teile der bisherigen Docker‑Swarm‑Umgebung durch eine K3s‑basierte Orchestrierung, bleibt aber eng in die bestehende Homehill‑Architektur integriert.

Ziel von Orchard:

- Plattform für zentrale Homelab‑Dienste (Nextcloud, Immich, Keycloak, Monitoring, Slack‑Bridge, AI‑Tools usw.)
- GitOps‑freundliche Basis (Argo CD), um Konfigurationen reproduzierbar und versionskontrolliert zu verwalten
- Saubere Trennung zwischen „alten“ Swarm‑Stacks und „neuen“ Kubernetes‑Workloads

---

## 🧱 Cluster Overview

**Distribution:** K3s (Lightweight Kubernetes)  
**Version:** v1.33.6+k3s1  
**Control Plane:** Single‑node control plane auf `apple`  
**Worker Nodes:** `lemon`, `plum`  
**Cluster Name (kubectl context):** `orchard`

### Nodes

Die drei Orchard‑Nodes laufen auf identischer NucBox‑G3‑Hardware (Alpine Linux):

- `apple` – Control‑Plane / Master
- `lemon` – Worker
- `plum` – Worker

(Die ursprünglichen Swarm‑Nodes `nook`, `greenhouse`, `dovecote` und weitere Geräte wie NAS und Desktop sind im Homehill‑Inventar dokumentiert und bleiben als Infrastruktur‑Backbone bestehen.)

---

## 🧩 Packaged Components (K3s Defaults)

Direkt nach der K3s‑Installation laufen im Cluster nur die von K3s mitgelieferten Komponenten:

- **CoreDNS** – DNS‑Service für den Cluster
- **Traefik** – Ingress Controller & Reverse Proxy (K3s‑Deployment)
- **local-path-provisioner** – StorageClass für einfache lokale PersistentVolumes
- **metrics‑server** – Ressourcenmetriken für `kubectl top` & HPA
- **svclb‑Pods für Traefik** – LoadBalancer‑Implementierung per DaemonSet (ein Pod pro Node)

Kontrolle direkt nach dem Bootstrap:

```bash
kubectl get nodes
kubectl get pods -A
```

---

## 🌐 Netzwerk & Zugriff

- **API‑Server:**  
  Intern aktuell per IP erreichbar (z.B. `https://192.168.x.y:6443`).  
  Geplant: FQDN wie `apple.homehill.de` bzw. `orchard-api.homehill.de` mit gültigem TLS‑Zertifikat.
- **kubectl Zugriff:**  
  Auf dem Desktop (`bearcube`) ist `kubectl` installiert; die `kubeconfig` wurde von `apple` kopiert und auf die interne IP des API‑Servers angepasst.  
  Der aktive Kontext heißt:

  ```bash
  kubectl config current-context
  # orchard
  ```

- **DNS / Externe Domains:**  
  Die bestehende Homehill‑DNS‑Infrastruktur (`*.homehill.de` via Pi‑hole und Hetzner‑DNS) wird später für Ingress‑Routen genutzt.  
  Ziel: Traefik + Let’s Encrypt (DNS‑01 Challenge via Hetzner) für Wildcard‑Zertifikate.

---

## 👥 Identity & Security (Homehill‑Schema)

Orchard orientiert sich am bestehenden Homehill‑UID/GID‑ und Rollen‑Schema (System‑User, Bear‑Identitäten, Service‑Goblins, AI‑Assistenten).  
Langfristig wird dieses Modell auf Kubernetes übertragen, u. a. durch:

- Namespaces entsprechend Rollen / Projekten
- ServiceAccounts und RBAC, die „Service‑Goblins“ abbilden
- Trennung zwischen **Content Owner** (z.B. `mk3`, `coder`) und **Service Runner** (technische Accounts / ServiceAccounts)
- eigene Identitäten für AI‑Assistenten (z.B. Ana) im Zugriff auf Cluster‑APIs

Aktuell ist der Cluster im **Bootstrap‑Zustand** ohne fein granulare RBAC‑Konfiguration; das folgt mit den ersten produktiven Workloads.

---

## 📌 Aktueller Status

- K3s v1.33.6 ist auf allen drei Nodes installiert.
- `apple` fungiert als Control‑Plane, `lemon` und `plum` sind erfolgreiche Worker‑Nodes.
- `kubectl` ist auf dem Desktop eingerichtet, Kontext `orchard` aktiv.
- Alle K3s‑Core‑Komponenten laufen (`coredns`, `traefik`, `local-path-provisioner`, `metrics-server`, `svclb-traefik`).
- Noch keine produktiven Workloads; Orchard ist bereit für die ersten „richtigen“ Deployments.

---

## 🚧 Nächste Schritte

1. **TLS & Ingress**
   - Traefik konfigurieren für:
     - Let’s‑Encrypt‑Zertifikate (DNS‑01 Challenge via Hetzner DNS API)
     - saubere Hosts wie `*.homehill.de` für Kubernetes‑Services
   - ggf. später Umstieg auf cert‑manager, wenn erforderlich.

2. **GitOps / Argo CD**
   - `k8s/orchard/gitops/` aufsetzen:
     - `base/` für Namespaces, grundlegende Infrastruktur (Monitoring, Ingress, Storage, Logging)
     - `argo-apps/` für App‑of‑Apps‑Pattern
   - Argo CD im Cluster deployen und mit diesem Repository verdrahten.

3. **Workload‑Migration & neue Services**
   - Geplante Projekte (Nextcloud, Immich, Jellyfin‑Nachfolger, Keycloak, Uptime Kuma, etc.) schrittweise auf Orchard bringen.
   - Services aus der Swarm‑Welt nach und nach migrieren, **nur** wenn sie sowieso angefasst werden („Never stop a running system“).

4. **Monitoring & Runbooks**
   - Kubernetes‑Monitoring (z.B. Netdata/Grafana/Prometheus) für Orchard etablieren.
   - Runbooks für häufige Tasks und Incident‑Response ergänzen.

---

## 📂 Weitere Dokumentation

- `k8s/orchard/setup/INSTALLATION.md`  
  Detaillierte Schritt‑für‑Schritt‑Anleitung: Von der NucBox‑G3‑Installation (Alpine Linux) bis zum ersten erfolgreichen `kubectl get pods -A`.

- `docs/ARCHITECTURE.md`  
  Gesamtübersicht über Homehill: Swarm‑Cluster, Orchard‑Cluster, NAS, Pi‑hole, Netzwerk‑Topologie.

- `docs/GITOPS-SETUP.md`  
  Design und Implementierung der GitOps‑Pipeline (Argo CD, Repos, Branching‑Strategie).

---

*Orchard ist das Kubernetes‑Herz von Homehill – gewachsen aus späten Nächten, Trip‑Hop‑Beats und einer Menge Liebe zum Detail.* 🌳💚

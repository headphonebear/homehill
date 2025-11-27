# Orchard – Installation und Bootstrap

Dieses Dokument beschreibt die Installation des Orchard‑Clusters, vom ersten Setup der drei NucBox‑G3‑Maschinen mit Alpine Linux bis zum ersten erfolgreichen `kubectl get pods -A` vom Desktop aus.

Orchard besteht aus einem einzelnen K3s‑Control‑Plane‑Node (`apple`) und zwei Worker‑Nodes (`lemon`, `plum`).  

Alle Schritte sind so dokumentiert, dass ein Rebuild (z. B. nach Hardwaretausch oder Neuinstallation) reproduzierbar möglich ist.

---

## 1. Ziel und Überblick

Ziel dieser Installation:

- Aufbau eines kleinen, aber vollwertigen Kubernetes‑Clusters auf Basis von K3s.
- Nutzung von drei identischen NucBox G3 als physische Nodes.
- Zugriff auf den Cluster von einem separaten Desktop‑Rechner (`bearcube`) per `kubectl`.
- Vorbereitung für späteres GitOps (Argo CD) und Ingress/TLS‑Konfiguration (Traefik + Let's Encrypt).

Kernentscheidungen:

- **K3s** statt „Full" Kubernetes (kubeadm), um Ressourcen auf den NUCs zu schonen.
- **Alpine Linux** als minimalistisches, schnelles Basis‑OS.
- Ein **einzelner Control‑Plane‑Node** (für Homelab völlig ausreichend).
- K3s‑Default‑Komponenten (Traefik, CoreDNS, local-path-provisioner, metrics‑server) werden genutzt und nicht deaktiviert.

---

## 2. Hardware und Rollen

Alle drei Orchard‑Nodes basieren auf gleicher Hardware:

- Modell: NucBox G3
- Rolle im Cluster:
  - `apple` – Control‑Plane / Master
  - `lemon` – Worker
  - `plum` – Worker

Die konkrete Hardware‑Spezifikation (CPU, RAM, SSD‑Größe, Besonderheiten) wird in einem separaten Dokument festgehalten:

- `k8s/orchard/setup/hardware-specs.md` (TODO)

---

## 3. Alpine Linux auf den NucBox G3 installieren

Jeder der drei Nodes erhält eine frische Alpine‑Installation. Die Schritte sind im Prinzip identisch, Unterschiede gibt es nur bei Hostname und IP/Netzwerk.

### 3.1. Boot von Alpine‑Installationsmedium

1. Alpine Linux (Extended) ISO herunterladen.
2. Bootfähigen USB‑Stick erstellen.
3. NucBox G3 von USB booten.
4. Im Alpine‑Boot‑Menü die Standard‑Option wählen (Extended Variante).

### 3.2. Basisinstallation

Auf jedem Node:

- Als `root` anmelden (kein Passwort).
- Den interaktiven Installer starten:

  ```sh
  setup-alpine
  ```

- Wichtige Entscheidungen während `setup-alpine`:
  - Keyboard layout, Zeitzone, Locale → passend zu Homehill.
  - Hostname:  
    - `apple`  
    - `lemon`  
    - `plum`
  - Netzwerk:
    - Entweder statische IPs im Homehill‑Netz
    - oder DHCP, solange die IPs zuverlässig sind bzw. via DHCP‑Reservation festgezurrt werden.
  - SSH‑Server: `openssh` installieren und aktivieren.
  - Disk‑Layout:
    - Übliche Partitionierung (root + ggf. separate EFI/Boot).
    - Alpine auf die interne SSD installieren.

Nach Abschluss:

- USB‑Stick entfernen.
- Neu starten.
- Per SSH von einem anderen Host einloggen (oder direkt an der Konsole weiterarbeiten).

---

## 4. Grundkonfiguration auf allen Nodes

Auf jedem der drei Nodes:

### 4.1. Aktualisieren und Basispakete installieren

```sh
apk update
apk upgrade
apk add htop curl nano
```

Optional: Zeitsynchronisation und kleine Komfort‑Settings (z. B. `chrony`, Alias für `kubectl`, etc.). Für den Bootstrap reicht das Minimum.

### 4.2. Überprüfen von Netzwerk und DNS

Sicherstellen, dass:

- Internetzugang vorhanden ist (`ping 1.1.1.1`, `ping github.com`).
- Namensauflösung für `*.homehill.de` funktioniert (falls bereits eingerichtet).
- Die Nodes sich gegenseitig pingen können (`ping apple`, `ping lemon`, `ping plum`), sofern DNS-Einträge existieren.

---

## 5. K3s‑Server auf `apple` installieren

`apple` ist der Control‑Plane‑Node (K3s‑Server).

### 5.1. K3s über das offizielle Install‑Script

Auf `apple` als `root`:

```sh
curl -sfL https://get.k3s.io | sh -
```

Wichtige Punkte:

- Das Script:
  - findet die aktuelle „stable" K3s‑Version,
  - lädt das passende Binary herunter,
  - verifiziert den Hash,
  - installiert `k3s` unter `/usr/local/bin`,
  - richtet den `k3s`‑Service ein und startet ihn.

Hinweis:  
Bei sehr langsamen Downloads von GitHub kann das Herunterladen des Binaries einige Zeit dauern, auch wenn die eigene Internetleitung schnell ist.

### 5.2. Erste Kontrolle des K3s‑Servers

Nach erfolgreicher Installation sollte:

```sh
k3s kubectl get nodes
```

die Node `apple` als `Ready` mit Rolle `control-plane,master` anzeigen, z. B.:

```text
NAME    STATUS   ROLES                  AGE   VERSION
apple   Ready    control-plane,master   2m    v1.33.6+k3s1
```

### 5.3. Node‑Token für Worker‑Nodes auslesen

Damit `lemon` und `plum` dem Cluster als Worker beitreten können, wird der `node-token` vom Server benötigt:

```sh
cat /var/lib/rancher/k3s/server/node-token
```

Den ausgegebenen Token sicher kopieren – er wird auf den Worker‑Nodes als `K3S_TOKEN` verwendet.

---

## 6. K3s‑Agent auf `lemon` und `plum` installieren

Auf `lemon` und `plum` wird K3s als Agent (Worker‑Node) installiert. Beide verbinden sich mit dem API‑Server auf `apple`.

### 6.1. K3s‑Agent mit K3S_URL und K3S_TOKEN

Auf `lemon` als `root`:

```sh
curl -sfL https://get.k3s.io | \
  K3S_URL="https://192.168.x.y:6443" \
  K3S_TOKEN="HIER_DEN_TOKEN_VON_APPLE_EINFÜGEN" \
  sh -
```

Auf `plum` analog:

```sh
curl -sfL https://get.k3s.io | \
  K3S_URL="https://192.168.x.y:6443" \
  K3S_TOKEN="HIER_DEN_TOKEN_VON_APPLE_EINFÜGEN" \
  sh -
```

Hinweis:  
Während des ersten Bootstraps wird die **IP‑Adresse** des API‑Servers verwendet (`https://192.168.x.y:6443`), da für `apple.homehill.de` noch kein gültiges TLS‑Zertifikat konfiguriert ist.  

Beides ist prinzipiell möglich; langfristig ist der FQDN mit passendem Zertifikat wünschenswert.

### 6.2. Kontrolle vom Server aus

Zurück auf `apple` (oder vom Desktop mit `kubectl`):

```sh
k3s kubectl get nodes
```

Erwartete Ausgabe:

```text
NAME    STATUS   ROLES                  AGE   VERSION
apple   Ready    control-plane,master   45m   v1.33.6+k3s1
lemon   Ready    <none>                 14m   v1.33.6+k3s1
plum    Ready    <none>                 15m   v1.33.6+k3s1
```

Damit ist der Cluster aus Sicht von K3s vollständig: eine Control‑Plane, zwei Worker‑Nodes.

---

## 7. kubectl auf dem Desktop einrichten

Der tägliche Zugriff auf den Cluster erfolgt von einem Desktop‑Rechner (z. B. `bearcube`), auf dem `kubectl` installiert wird.

### 7.1. kubectl installieren

Unter Linux (Ubuntu‑Basis) empfiehlt sich die offizielle Kubernetes‑Doku:

1. Nach Anleitung von  
   https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/  
   `kubectl` installieren.
2. Sicherstellen, dass `kubectl` im `PATH` liegt:

   ```sh
   kubectl version --client
   ```

### 7.2. kubeconfig von `apple` kopieren

Auf `apple` liegt die K3s‑kubeconfig normalerweise unter:

```text
/etc/rancher/k3s/k3s.yaml
```

Diese Datei wird auf den Desktop kopiert, z. B.:

```sh
# auf apple
scp /etc/rancher/k3s/k3s.yaml user@bearcube:/home/user/.kube/config
```

(Ordner `~/.kube` auf `bearcube` ggf. vorher anlegen.)

### 7.3. Server‑Adresse anpassen

Die von K3s erzeugte `k3s.yaml` verwendet standardmäßig `https://127.0.0.1:6443` als API‑Endpoint.  

Auf dem Desktop muss diese Adresse angepasst werden auf die IP von `apple`:

```yaml
server: https://192.168.x.y:6443
```

(Später, wenn TLS/Ingress stimmt, kann das auf einen FQDN umgestellt werden.)

### 7.4. Kontext umbenennen: `default` → `orchard`

Die von K3s bereitgestellte kubeconfig verwendet oft überall `default` als Namen für:

- Cluster
- Context
- User
- `current-context`

Zur besseren Lesbarkeit und Klarheit wird alles auf `orchard` umgestellt. Mit `sed`:

```sh
sed -i 's/name: default/name: orchard/g' ~/.kube/config
sed -i 's/cluster: default/cluster: orchard/g' ~/.kube/config
sed -i 's/user: default/user: orchard/g' ~/.kube/config
sed -i 's/current-context: default/current-context: orchard/g' ~/.kube/config
```

Danach prüfen:

```sh
kubectl config current-context
# erwartet: orchard
```

---

## 8. Erste Cluster-Checks

Mit eingerichtetem `kubectl` und aktivem `orchard`‑Kontext:

### 8.1. Nodes

```sh
kubectl get nodes
```

Erwartete Ausgabe (Beispiel):

```text
NAME    STATUS   ROLES                  AGE   VERSION
apple   Ready    control-plane,master   45m   v1.33.6+k3s1
lemon   Ready    <none>                 14m   v1.33.6+k3s1
plum    Ready    <none>                 15m   v1.33.6+k3s1
```

### 8.2. System‑Pods

```sh
kubectl get pods -A
```

Typische Ausgabe direkt nach der Installation:

```text
NAMESPACE     NAME                                      READY   STATUS      RESTARTS   AGE
kube-system   coredns-6d668d687-8swbm                   1/1     Running     0          50m
kube-system   helm-install-traefik-65f9n                0/1     Completed   1          50m
kube-system   helm-install-traefik-crd-nh54t            0/1     Completed   0          50m
kube-system   local-path-provisioner-869c44bfbd-vjwbp   1/1     Running     0          50m
kube-system   metrics-server-7bfffcd44-6j7p8            1/1     Running     0          50m
kube-system   svclb-traefik-7a9db005-8k7hm              2/2     Running     0          50m
kube-system   svclb-traefik-7a9db005-jg7vx              2/2     Running     0          20m
kube-system   svclb-traefik-7a9db005-r4g4x              2/2     Running     0          20m
kube-system   traefik-865bd56545-xfp82                  1/1     Running     0          50m
```

Damit ist der Cluster funktionsfähig und bereit für weitere Konfiguration (Ingress/TLS, Namespaces, GitOps usw.).

---

## 9. Bekannte Einschränkungen und offene Punkte

Zum Zeitpunkt dieser Installation sind folgende Punkte bewusst noch offen bzw. provisorisch:

1. **FQDN und TLS für den API‑Server**
   - Aktuell wird der API‑Server über eine interne IP angesprochen.
   - Geplant ist die Nutzung eines FQDN wie `apple.homehill.de` oder `orchard-api.homehill.de` mit gültigem TLS‑Zertifikat.
   - Dazu wird entweder K3s selbst oder ein vorgelagerter Reverse Proxy (Traefik mit Let's‑Encrypt‑Zertifikat) genutzt.

2. **Ingress und Public Services**
   - Traefik ist als Ingress Controller bereits aktiv, aber noch nicht für produktive IngressRoutes konfiguriert.
   - Geplant:
     - DNS‑01‑Challenge via Hetzner‑DNS für Let's‑Encrypt‑Zertifikate.
     - Nutzung von `*.homehill.de` für die Dienste im Cluster.

3. **GitOps / Argo CD**
   - Der Orchard‑Cluster ist noch nicht an Argo CD angebunden.
   - Das Repository (`homehill`) wird vorbereitet, um später:
     - Namespaces, Basis‑Infrastruktur und Workloads deklarativ zu definieren.
     - Änderungen über Git‑Commits auszurollen.

4. **Security & RBAC**
   - Aktuell läuft der Cluster noch ohne feingranulares RBAC‑Modell.
   - Ziel ist die Abbildung des bestehenden Homehill‑Identitäts‑Schemas:
     - System‑Benutzer, Service‑Goblins, AI‑Identitäten
     - Namespaces, ServiceAccounts, Rollen und RoleBindings.

---

## 10. Zusammenfassung

Mit diesen Schritten ist Orchard als dreiköpfiger K3s‑Cluster erfolgreich installiert:

- Drei Alpine‑basierte NucBox G3‑Nodes (`apple`, `lemon`, `plum`).
- K3s‑Server auf `apple`, Agents auf `lemon` und `plum`.
- Zugriff via `kubectl` vom Desktop, Kontext `orchard`.
- Alle K3s‑Core‑Komponenten laufen stabil und bereit für weitere Konfiguration.

Die nächsten Schritte (separate Dokumente):

- `k8s/orchard/README.md` → Überblick über den Cluster und seine Rolle in Homehill.
- `k8s/orchard/setup/network.md` → Netzwerk‑Details (IPs, DNS, Pi‑hole, Hetzner).
- `docs/GITOPS-SETUP.md` → Design und Aufbau der GitOps‑Pipeline mit Argo CD.

Orchard ist damit das Kubernetes‑Herz von Homehill – bereit, mit Leben gefüllt zu werden. 🌳💚

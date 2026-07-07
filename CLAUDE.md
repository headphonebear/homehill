# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Homehill is a personal homelab **infrastructure-as-code monorepo**. There is no application source code to build or test — it is declarative configuration (Kubernetes manifests, Helm values, Docker Compose) that is applied to running machines. "Correctness" means valid YAML/manifests and adherence to the GitOps conventions below, not passing a test suite.

Three top-level domains, each at a different lifecycle stage:

- `clusters/` — **the active focus.** A K3s cluster (`orchard`) managed by ArgoCD via GitOps. Most work happens here.
- `servers/` — Standalone hosts (`mk3` music server, `barn` desktop) running Docker Compose stacks. Applied manually per host.
- `swarm/` — Legacy Docker Swarm stacks being phased out (migrated into `orchard` or `servers/`). Avoid adding new things here.

The cluster is named after a season/orchard theme; nodes are `apple` (control-plane), `lemon`, `plum`.

## GitOps model (clusters/)

Git is the source of truth. **Do not `kubectl apply` workloads manually** — commit to Git and let ArgoCD reconcile. ArgoCD polls the repo (`targetRevision: main`, public HTTPS clone) roughly every 3 minutes.

The structure splits *what to deploy* from *how to configure it*:

- `clusters/argocd/orchard/<app>.yaml` — one ArgoCD `Application` manifest per app. Defines source path, destination namespace, and `syncPolicy`.
- `clusters/apps/<app>/orchard/` — a **local Helm umbrella chart** per app: `Chart.yaml` declares the upstream chart as a dependency, `values.yaml` configures it, and `templates/` holds repo-specific extras (IngressRoutes, SealedSecrets, ClusterIssuers, middlewares).
- `clusters/argocd/orchard/app-of-apps.yaml` — the **root app**. It watches the `clusters/argocd/orchard/` directory and deploys every `Application` manifest it finds. Adding a new `<app>.yaml` there is what registers a new app.

So the typical change is: edit `clusters/apps/<app>/orchard/values.yaml`, commit, push. To add a whole new app, create both the umbrella chart under `clusters/apps/` **and** the `Application` manifest under `clusters/argocd/orchard/`.

### Conventions that bite if ignored

- **`selfHeal` is intentionally `false` for `monitoring`.** Grafana uses a ReadWriteOnce Longhorn PVC; auto-sync on secret drift spawns a new ReplicaSet and triggers a Multi-Attach error. These apps need **manual** `argocd app sync`. Stateless apps (traefik, argocd) use `selfHeal: true`.
- **Deploy order is controlled by `argocd.argoproj.io/sync-wave`.** `victoriametrics` is wave `-1`, `monitoring` is wave `0` (Prometheus remote-writes to VM, so VM must exist first). Preserve relative ordering when touching these.
- **`monitoring` requires `ServerSideApply=true`** because kube-prometheus-stack CRDs exceed the 262KB client-side annotation limit. Don't remove that syncOption.
- Chart dependency `.tgz` files and `charts/` are **gitignored** — only `Chart.lock` is committed. After editing a `Chart.yaml` dependency you must run `helm dependency build` in that chart dir to refetch (ArgoCD does this server-side automatically; you only need it for local validation).

## Secrets

Secrets are stored in Git **only as SealedSecrets** (`bitnami.com/v1alpha1`), encrypted with the cluster's public key via `kubeseal`. The `sealed-secrets` controller (namespace `kube-system`) decrypts them in-cluster.

Plaintext is never committed: `.gitignore` blocks `*.key`, `*.pem`, `*.p12`, and the workflow uses temp `*-plain.yaml` files that are deleted after sealing. Create one with:

```bash
kubectl create secret generic <name> --namespace=<ns> \
  --from-literal=key=value --dry-run=client -o yaml \
  | kubeseal -o yaml > <name>-sealed.yaml
```

SealedSecrets are namespace+name scoped (`strict`) by default and **cannot be moved between clusters or namespaces** — re-seal if either changes. Full workflow and recovery (incl. backing up the sealing key) in `clusters/docs/SECRETS.md`.

## Common commands

```bash
# Validate an umbrella chart locally before committing
cd clusters/apps/<app>/orchard
helm dependency build          # refetch chart deps (charts/*.tgz are gitignored)
helm template . -f values.yaml # render to check output
helm lint .

# ArgoCD operations (require cluster access + argocd CLI logged in)
argocd app list
argocd app get <app-name>
argocd app diff <app-name>     # what Git vs cluster disagree on
argocd app sync <app-name>     # manual sync (required for selfHeal:false apps like monitoring)

# Docker Compose hosts (run on the host itself)
docker compose -f servers/<host>/<service>/docker-compose.yaml up -d
```

## Style

Manifests in this repo carry heavy inline documentation — boxed `# ╔══╗` headers and `# WHY:` comments explaining the *reasoning* behind non-obvious choices. Match that density when editing existing files; future-you debugging at 2am is the audience. Commit messages follow Conventional Commits (`feat(scope):`, `fix(scope):`, `add:`, `update:`).

## Docs map

- `clusters/README.md` — cluster quick-start, access, common tasks (start here for cluster work)
- `clusters/docs/SECRETS.md` — full SealedSecrets workflow
- `clusters/docs/TROUBLESHOOTING.md` — battle-tested fixes (Multi-Attach, stuck syncs, webhook TLS, cert issues)
- `clusters/docs/orchard/` — architecture, bootstrap, post-bootstrap tasks, runbooks
- `docs/` — repo-wide philosophy, architecture, UID/GID schema, team/credits

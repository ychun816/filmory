# Infrastructure

## to do

Ordered as a **walking skeleton**: get one thin slice running end-to-end before
making any single layer good. Working down the tech table in the README instead
means three weeks on Vault and Istio with nothing a human can look at.

Rule for branches: *a branch holds commits you intend to merge.* Machine setup
changes no files, so it gets no branch.

---

### Phase 0 — Local tooling

Tool versions live in `mise.toml`, pinned and identical on macOS and Linux —
see the README for the four-step setup. Deliberately not Ansible: that earns
its place across many machines or ones that get rebuilt, and the README scopes
it to the cloud phase. `mise.toml` rides along in the Phase 1 branch rather than
getting one of its own.

- [x] Docker Desktop — already installed
- [x] `brew install mise`
- [x] Activate mise in the shell (`eval "$(mise activate zsh)"` in `~/.zshrc`)
- [x] `mise install` — kubectl 1.36.4, kind 0.32.0, helm 4.2.4, k9s 0.51.0, stern 1.34.0
- [x] Versions pinned in `mise.toml` and committed
- [x] Confirmed in a fresh shell: `kubectl` and `kind` resolve to mise installs

### Phase 1 — Cluster · `infra/kind-setup`

First real branch — `kind-config.yaml` is the first file that gets committed.
Verify the cluster is up *before* opening the PR.

- [ ] Write `kind-config.yaml` (1 control-plane + 2 workers)
- [ ] `kind create cluster --config kind-config.yaml`
- [ ] Verify: `kubectl cluster-info` / `kubectl get nodes` → 3 nodes Ready
- [ ] **Check version skew**: note the k8s version kind reports and compare to
      `kubectl version`. kubectl is pinned at 1.36.4; if the cluster is more
      than one minor behind, pin kind's node image to match or drop kubectl's
      pin in `mise.toml`. This is exactly what pinning exists to make visible.
- [ ] PR → merge

### Phase 2 — The payload · `feat/backend-health`

Twenty lines of Python. Empty infrastructure cannot be tested — Helm charts that
deploy nothing and CI that builds nothing can't be told apart from broken ones.
This service stays in the repo forever as the liveness probe target.

- [ ] FastAPI app with a single `GET /health` → `{"ok": true}`
- [ ] `requirements.txt` / dependency pinning
- [ ] Runs locally: `uvicorn main:app`

### Phase 3 — Containerize · `infra/dockerfiles`

- [ ] Dockerfile for the backend service (multi-stage, non-root user)
- [ ] `.dockerignore`
- [ ] Verify: `docker build` + `docker run` → `/health` responds
- [ ] `kind load docker-image` → image available in-cluster

### Phase 4 — Deploy · `infra/helm-charts`

Reach it with `kubectl port-forward` for now. Needing MetalLB is a later
annoyance — that annoyance is the signal to add it, not a reason to add it yet.

- [ ] Helm chart for the backend (Deployment, Service, values.yaml)
- [ ] Liveness/readiness probes pointing at `/health`
- [ ] `helm install` → pod Running
- [ ] Verify: `kubectl port-forward` → `/health` responds from the browser

### Phase 5 — GitOps bootstrap · `infra/argocd-bootstrap`

Moved ahead of CI deliberately. Modern practice installs ArgoCD early and lets
it install everything else — you stop running `helm install` by hand and start
committing `Application` manifests. Phase 4 was the one manual pass, so you know
what is being automated.

Needs the **config repo** from the README: Helm charts + Kustomize overlays
(`overlays/dev`, `overlays/staging`, `overlays/prod`). ArgoCD watches that repo.

- [ ] Create the config repo, move the Phase 4 chart into it
- [ ] Install ArgoCD, bootstrap with the **app-of-apps** pattern
- [ ] Re-adopt the backend chart as an ArgoCD `Application`
- [ ] Verify: `helm uninstall` the manual release → ArgoCD puts it back
- [ ] Verify: commit to config repo → cluster converges with no kubectl

### Phase 6 — CI + supply chain · `infra/cicd-pipeline`

Signing and SBOMs are no longer advanced extras; at this scale the whole loop
fits in one workflow and one policy, which is exactly why it's worth doing.

- [ ] GitHub Actions: lint + test on PR
- [ ] Build image, tag with commit SHA (never `latest`)
- [ ] Push to GHCR (Harbor can come much later, if ever)
- [ ] Sign with **cosign**, generate an SBOM with **syft**
- [ ] **Kyverno** policy: refuse unsigned images at admission
- [ ] Bump the config repo tag — **Renovate** or **ArgoCD Image Updater**,
      not a hand-rolled `sed` in CI
- [ ] Require the CI check in branch protection now that it exists
- [ ] Raise required approving reviews back to 1

### Phase 7+ — Platform layers, all via GitOps

Every item is an ArgoCD `Application`, not a manual install. Add each when its
absence hurts, not in list order.

- [ ] **Cilium** — CNI. Also gives L2 announcements, Gateway API, and
      kube-proxy replacement, which removes the need for MetalLB and a separate
      gateway controller. Add Calico later only as a deliberate comparison.
- [ ] cert-manager — TLS for the Gateway
- [ ] local-path-provisioner first; **Longhorn** only once PVCs need to survive
      a node loss
- [ ] MySQL, Redis, MinIO, NATS — the real backing services
- [ ] **SOPS + age** for secrets in git; **External Secrets Operator** when you
      outgrow it. Vault/OpenBao is a much later problem than it looks.
- [ ] Prometheus + Grafana + Alertmanager — metrics
- [ ] Loki + **Grafana Alloy** — logs (Promtail is end-of-life; Alloy replaces it)
- [ ] KEDA — event-driven scaling for the news consumer
- [ ] Istio in **ambient mode** — sidecars are the legacy model. Check whether
      Cilium's mTLS already covers the need first.
- [ ] **OpenTofu** — if/when the cloud phase happens (Terraform is BUSL-licensed)

---

## Stack revisions pending team agreement

The README tech table still lists the superseded picks. Worth a joint decision
before editing it:

| README says | Current default | Reason |
|---|---|---|
| Promtail | Grafana Alloy | Promtail is EOL |
| Terraform | OpenTofu | BUSL license change |
| Vault + VSO (early) | SOPS + age → ESO | Vault is heavy; BUSL |
| MetalLB + separate gateway | Cilium does both | Fewer moving parts |
| Istio (sidecar) | Istio ambient | Sidecars are legacy |
| Harbor | GHCR until it hurts | One less service to run |

Versions and project statuses move fast — confirm current releases before
pinning anything.

# flimory
A movie index and insight sharing website

## index
- [Team](#Team)
- [Project Overview](#Project-Overview)
- [Tech Stack](#Tech-Stack)
  - [Frontend](#Frontend)
  - [Backend](#Backend)
  - [Infrastructure](#Infrastructure) 
- [Repo Structure](#Repo-Structure)
- [Git Branching Strategy](#Git-Branching-Strategy)
- 

## Team

| Name | Role |
|---|---|
| Sophia | Infrastructure, Backend |
| Jimmy | Frontend |

## Project Overview

- Homepage, login/signup, account management (incl. 2FA)
- Movies: browse, detail, rate, comment
- Movie news: list + detail, populated by a weekly scraper
- My Movie List
- New Releases
- Journal — deferred, not in scope for phase 1

## Tech Stack

### Frontend

| Category | Technology |
|---|---|
| Framework | Vue.js |
| (to be added...) |  |

### Backend
> Detailed list : [BACKEND.md](#BACKEND.md)

| Category | Technology | Purpose |
|---|---|---|
| Language | Python 3 | |
| Framework | FastAPI | REST API — auth, movies/ratings/comments, my list, news |
| Database | MySQL / MariaDB | Users, movies, ratings, comments, scraped news rows |
| Cache / sessions | Redis | Session tokens, 2FA codes, rate limiting |
| Object storage | MinIO (S3-compatible) | Scraped news images/thumbnails, movie posters |
| Messaging / events | NATS (JetStream) | Scraper → consumer event bus (`movie_news.created`) |
| Auth | JWT + TOTP (2FA) | Login/session/account security |
| Scraping | Python scraper, run as a k8s CronJob | Weekly movie news ingestion |

### Infrastructure

| Category | Technology | Purpose |
|---|---|---|
| Container runtime | Docker | Builds/runs every service's image |
| Local cluster | Kind | Real k8s nodes in Docker — where the learning happens |
| Orchestration | Kubernetes (vanilla) | Scheduling, self-healing, scaling |
| CNI | Calico / Cilium | Pod networking + NetworkPolicy (practice both) |
| Load balancer | MetalLB | Real LoadBalancer IPs — no cloud LB locally/bare-metal |
| Ingress / Gateway | Gateway API | Routes external traffic to services |
| TLS | cert-manager | Issues/renews certs for the Gateway |
| Service mesh | Istio | mTLS, traffic shaping (later phase) |
| Storage / CSI | Longhorn (start), Rook (optional) | Backs every PVC — DB, Redis, MinIO, NATS |
| Registry | Harbor | Private image registry, fed by CI |
| Secrets | Vault + Vault Secrets Operator | DB creds, JWT/2FA keys, scraper API keys |
| Event-driven autoscaling | KEDA | Scales the news consumer 0→N off event backlog |
| GitOps / CD | ArgoCD | Syncs the config repo into the cluster |
| Config templating | Kustomize | Dev/staging/prod overlays |
| CI | GitHub Actions | Build, test, push image, bump manifest tag |
| Monitoring | Prometheus + Grafana + Alertmanager | Metrics, dashboards, scraper-failure alerts |
| Logging | Loki + Promtail | Searchable logs — why, not just that, something broke |
| IaC (cloud phase only) | Terraform, optionally Ansible | Provisions EKS/EC2/RDS/S3 if/when moving to AWS |
| Unclear | Merlin | Ask Charly — not a widely-known public tool |


## Repo structure

- **App repo** — Vue.js, FastAPI, and scraper source + Dockerfiles. CI builds/tests/tags/pushes images here.
- **Config repo** — Helm charts + Kustomize overlays (`overlays/dev`, `overlays/staging`, `overlays/prod`).
- ArgoCD watches this repo, not the app repo.

## Git Branching Strategy

GitHub Flow, not Git Flow: one protected `main`, everything else a short-lived feature branch merged via PR + CI. Environments are handled by overlay directories, not long-lived branches — branching per environment fights ArgoCD instead of working with it.

Naming pattern: `type/scope-description` (`feat/`, `fix/`, `infra/`, `chore/`).

| Branch | Owner | Scope |
|---|---|---|
| `main` | both, protected | Always deployable, PR + CI required to merge |
| `feat/frontend-homepage` | Jimmy | Homepage layout/nav |
| `feat/frontend-auth` | Jimmy | Login, signup, account management, 2FA UI |
| `feat/frontend-movies` | Jimmy | Movie list, detail, rate/comment UI |
| `feat/frontend-news` | Jimmy | Movie news list + detail UI |
| `feat/frontend-mylist` | Jimmy | My Movie List UI |
| `feat/backend-auth` | Sophia | Auth API, JWT, 2FA, account management |
| `feat/backend-movies` | Sophia | Movies/ratings/comments/my-list API |
| `feat/news-scraper` | Sophia | Scraper logic + CronJob |
| `infra/kind-setup` | Sophia | Kind cluster config, base manifests |
| `infra/dockerfiles` | Sophia (+ Jimmy for frontend's own) | One Dockerfile per service |
| `infra/helm-charts` | Sophia | Helm chart per service |
| `infra/argocd-bootstrap` | Sophia | ArgoCD install + Application manifests |
| `infra/cicd-pipeline` | Sophia | GitHub Actions workflows |




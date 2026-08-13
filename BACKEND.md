# Backend — Filmory

Full breakdown of the backend stack, owned by Sophia. See the [README](./README.md) for the project overview and the rest of the stack.

## to do 

### Setup Backend

- [ ] Scaffold FastAPI project (routers, models/schemas, Alembic migrations)
- [ ] Add MySQL container + initial schema: users, movies, ratings, comments, news
- [ ] Add Redis container, wire session tokens + rate limiting
- [ ] Implement JWT auth: register, login, refresh
- [ ] Implement TOTP 2FA: setup + verify endpoints
- [ ] Build core REST endpoints: movies, ratings, comments, my-list
- [ ] Add MinIO container, wire poster/thumbnail upload+retrieval
- [ ] Add NATS container with JetStream enabled
- [ ] Write `docker-compose.yml` wiring everything together
- [ ] Smoke-test end to end: register → login → 2FA → rate → comment → add to list

---


## Core

| Category | Technology | Purpose |
|---|---|---|
| Language | Python 3 | |
| Framework | FastAPI | REST API — auth, movies/ratings/comments, my list, news |

## Data layer

| Category | Technology | Purpose |
|---|---|---|
| Database | MySQL / MariaDB | Users, movies, ratings, comments, scraped news rows |
| Cache / sessions | Redis | Session tokens, 2FA codes, rate limiting |
| Object storage | MinIO (S3-compatible) | Scraped news images/thumbnails, movie posters |

## Auth & security

| Category | Technology | Purpose |
|---|---|---|
| Auth | JWT + TOTP (2FA) | Login/session/account security |

## Async & background work

| Category | Technology | Purpose |
|---|---|---|
| Messaging / events | NATS (JetStream) | Scraper → consumer event bus (`movie_news.created`) |
| Scraping | Python scraper, run as a k8s CronJob | Weekly movie news ingestion |

## Data & storage model

- **User data**: MySQL/MariaDB, StatefulSet + PVC.
- **Weekly scrape**: same DB to start (`movie_news` table). Images/thumbnails go to MinIO rather than being stuffed into the relational DB.
- **Cache/session**: Redis — session tokens, 2FA codes, rate limiting.
- **Storage class**: use PVCs (not hostPath) from day one so swapping to Longhorn/Rook later is a non-event.

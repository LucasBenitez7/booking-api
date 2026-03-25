# Changelog

## [0.1.1](https://github.com/LucasBenitez7/booking-api/compare/v0.1.0...v0.1.1) (2026-03-25)


### Bug Fixes

* copy alembic.ini and alembic/ into Docker image for migrations ([118d33e](https://github.com/LucasBenitez7/booking-api/commit/118d33e3c792b74b652cceefb92563d7b1ab4c42))
* copy alembic.ini and alembic/ into Docker image for migrations ([49f5e0d](https://github.com/LucasBenitez7/booking-api/commit/49f5e0d61ce60bfb69f4bfc77061ed2033e8d2f3))
* correct migration and normalize DATABASE_URL driver prefix for Railway ([437c785](https://github.com/LucasBenitez7/booking-api/commit/437c7853b89f1da11c76425044fef30e25ca8db2))
* correct migration dbd0dc11056d and normalize DATABASE_URL for Railway ([0961c46](https://github.com/LucasBenitez7/booking-api/commit/0961c46ef4db003d07f51256a632bc742704ef0d))
* upgrade requests to 2.33.0 (CVE-2026-25645) ([68b80ab](https://github.com/LucasBenitez7/booking-api/commit/68b80ab293b754c5bc7c770e1c1b26a7bd755f6b))
* upgrade requests to 2.33.0 to resolve CVE-2026-25645 ([cd17b5f](https://github.com/LucasBenitez7/booking-api/commit/cd17b5f5cb79f4502ad008fc0cd8b6f5299a8f4f))


### Documentation

* add live API section with demo credentials and Swagger guide ([8eb2543](https://github.com/LucasBenitez7/booking-api/commit/8eb2543324dcf96e0f1657a61035928e0fd03e52))
* add live API URL, demo credentials and Swagger exploration guide ([a513973](https://github.com/LucasBenitez7/booking-api/commit/a5139732cc4689916490170d6345b1a2bbb1df56))

## 0.1.0 (2026-03-25)


### Features

* add automated Postman collection and fix critical session commit bug ([4fe92c0](https://github.com/LucasBenitez7/booking-api/commit/4fe92c036c41670e8decb64e10114d9ec0caa6d1))
* **api:** add domain exception handlers ([bc297c5](https://github.com/LucasBenitez7/booking-api/commit/bc297c51b3d0ae7044da88739ac62c707d20d5b9))
* **application:** add use cases and DTOs ([3d87109](https://github.com/LucasBenitez7/booking-api/commit/3d871096247a6598d2ea482b70326b4643bda0a2))
* automated Postman collection + critical bug fixes ([f805ea0](https://github.com/LucasBenitez7/booking-api/commit/f805ea04f8b8f09b12d15247177dd0871222d8f9))
* **domain:** add entities, value objects, ports and domain events ([bc8c6b0](https://github.com/LucasBenitez7/booking-api/commit/bc8c6b06ea00945d75db13f1a17efce85de2e9fc))
* **domain:** complete phase 2b domain business rules ([64ac118](https://github.com/LucasBenitez7/booking-api/commit/64ac11895b5ff092a2c3de01bd3eb0ff9fa35568))
* **domain:** hexagonal domain layer — entities, use cases and tests ([18345ba](https://github.com/LucasBenitez7/booking-api/commit/18345ba707f6aeb25ecd716e285f3408a6fa20ee))
* **domain:** phase 2b domain business rules ([3812ffb](https://github.com/LucasBenitez7/booking-api/commit/3812ffb6264f1e925f97eb86ff0c92e67003564c))
* implement Phase 3 — HTTP API, authentication and domain hardening ([4a5af12](https://github.com/LucasBenitez7/booking-api/commit/4a5af123d1ec0a44b1189c6faaea722f72ac5557))
* implement Phase 4 — availability cache, Celery workers and EXPIRED status ([21de241](https://github.com/LucasBenitez7/booking-api/commit/21de241614bc96e677e7eaf9b1a9951cfa39098f))
* implement Phase 5 — Kubernetes manifests, deploy pipeline and release automation ([a64e79e](https://github.com/LucasBenitez7/booking-api/commit/a64e79e5ddc2e3ab73a44d5546513d9708d8d416))
* implement Phase 6 — polish, documentation and release ([835daae](https://github.com/LucasBenitez7/booking-api/commit/835daaee75e73a382cb3640c110154484269c754))
* **infrastructure:** add SQLAlchemy models, mappers, repositories and Alembic migrations ([75e8028](https://github.com/LucasBenitez7/booking-api/commit/75e8028323fe327032eed6c7c34f6a12365cd028))
* **infrastructure:** database layer with SQLAlchemy, Alembic and integration tests ([cd48038](https://github.com/LucasBenitez7/booking-api/commit/cd48038fb998e42a176d45f4a482ea127c0459fd))
* Phase 3 — HTTP API, authentication and domain hardening ([049878d](https://github.com/LucasBenitez7/booking-api/commit/049878dadfec1f10d25b1433b37ac45f65b06cf7))
* Phase 4 — availability cache, Celery workers and EXPIRED status ([9280d31](https://github.com/LucasBenitez7/booking-api/commit/9280d31f9f2e7687ae4c03bf957c444d473cf44d))
* Phase 5 — Kubernetes manifests, deploy pipeline and release automation ([31f3aea](https://github.com/LucasBenitez7/booking-api/commit/31f3aea73712aaf7aa6a2ffda8341af4e6417566))
* Phase 6 — polish, documentation and release ([b0f1d4b](https://github.com/LucasBenitez7/booking-api/commit/b0f1d4be6b889f45cf03dd8d78671d28313f7ab5))


### Bug Fixes

* add required permissions for Trivy SARIF upload to Security tab ([56d5d7d](https://github.com/LucasBenitez7/booking-api/commit/56d5d7d8d05897dbede8794694b4cdfedd02fa3e))
* apply Phase 5 review corrections ([bd06dc0](https://github.com/LucasBenitez7/booking-api/commit/bd06dc0de17c49b6c0be17ea2510eb8a87866cf6))
* **domain:** move past date validation from TimeSlot to CreateBooking use case ([b606c50](https://github.com/LucasBenitez7/booking-api/commit/b606c503fb09af00b98bff262d55f43080c6dbde))
* ignore CVE-2026-4539 in pip-audit (no fix available in PyPI yet) ([b2b4fed](https://github.com/LucasBenitez7/booking-api/commit/b2b4feded7867e7ebe0f272c7977ce8b49e9a030))
* suppress bandit false positives in dev router (B105) ([2c2679b](https://github.com/LucasBenitez7/booking-api/commit/2c2679becf185a76601cec17bf6c6784daa6cb90))


### Documentation

* update CONTEXT.md and cursor rules ([7a21b05](https://github.com/LucasBenitez7/booking-api/commit/7a21b0597b2d24856b7cacb8cafca0f900cc5b9c))

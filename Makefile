.PHONY: up down logs ingest eval test fmt

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f api

ingest:
	docker compose exec api python -m scripts.ingest_docs

eval:
	docker compose exec api python -m scripts.run_eval

test:
	docker compose exec api pytest -q

shell:
	docker compose exec api bash
.PHONY: dev prod monitoring k8s-apply backup logs

dev:
	docker compose up -d --build

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

monitoring:
	docker compose -f docker-compose.yml -f docker-compose.monitoring.yml --profile monitoring up -d

down:
	docker compose down

logs:
	docker compose logs -f api web

k8s-apply:
	kubectl apply -k deploy/kubernetes

backup:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile backup run --rm backup /scripts/backup.sh

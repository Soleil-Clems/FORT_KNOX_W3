up:
		@echo "=== Demarrage du conteneur... ==="
		docker compose up -d

stop: 
		@echo "=== Arret de tous les containers actifs... ==="
		@if [ -n "$$(docker ps -q)" ]; then \
			docker stop $$(docker ps -q); \
			docker compose down -v; \
		else \
			echo "Aucun container actif."; \
		fi

help:
	@echo "Utilisation :"
	@echo "  make up       - Démarre les services"
	@echo "  make down        - Arrête les services"
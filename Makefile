.PHONY: help install run test clean build dmg reset-onboarding

help:
	@echo "Comandos disponibles:"
	@echo "  make install          - Instalar dependencias con Poetry"
	@echo "  make run              - Ejecutar la aplicación"
	@echo "  make test             - Ejecutar tests con pytest"
	@echo "  make clean            - Limpiar builds y cache"
	@echo "  make build            - Compilar ejecutable"
	@echo "  make dmg              - Crear DMG (solo macOS)"
	@echo "  make reset-onboarding - Resetear estado de onboarding"

install:
	poetry install

run:
	poetry run selladomx

test:
	poetry run pytest -v

clean:
	./scripts/clean.sh

build:
	./scripts/build.sh

dmg:
	./scripts/create-dmg.sh

reset-onboarding:
	poetry run python scripts/reset_onboarding.py

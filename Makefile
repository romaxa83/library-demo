.SILENT:

include .env

#======================================
# Information on commands, called by the "make" command

.DEFAULT_GOAL := help
.PHONY: help
help:  ## отображение данного сообщения help
	@awk 'BEGIN {FS = ":.*##"; printf "\n Usage:\n  make \033[36m<command>\033[0m\n \n Targets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

#======================================
# Сompound commands

.PHONY: up
up: docker_up start_app ## составная команда, для поднятия проекта [docker_up -> start_app]

##======================================
# Command

#.PHONY: build
#build: ## собирает контейнеры
#	docker compose build --build-arg USER_ID=${UID} --build-arg GROUP_ID=${GID}

.PHONY: start_app
start_app: ## запускаем сервер
	python -m src.main

.PHONY: docker_up
docker_up: ## подымает контейнеры
	docker-compose up -d

.PHONY: down
down: ## останавливает контейнеры и удаляет их образы
	docker-compose down --remove-orphans #очистит все запущенные контейнеры

.PHONY: ps
ps:	## информация по контейнерам докера
	docker-compose ps

.PHONY: venv
venv: ## активируем виртуальное окружение
	source venv/bin/activate

.PHONY: run_test
run_test: ## запускает тесты
	 pytest -vvs --tb=short -l
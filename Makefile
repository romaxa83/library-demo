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
up: docker_up ## составная команда, для поднятия проекта [docker_up -> start_app]

##======================================
# Command

#.PHONY: build
#build: ## собирает контейнеры
#	docker compose build --build-arg USER_ID=${UID} --build-arg GROUP_ID=${GID}

.PHONY: storage_link
storage_link: ## создание символьной ссылки: public/media -> storage/media
	mkdir -p storage/media
	mkdir -p public
	# Удаляем старую ссылку/папку если есть
	rm -rf public/media
	# Создаем ссылку. В macOS/Linux лучше использовать относительный путь внутри папки
	cd public && ln -s ../storage/media media
	echo "✅ Символьная ссылка создана: public/media -> storage/media"

.PHONY: start_app
start_app: ## запускаем сервер
	python -m src.main

.PHONY: generate_key
generate_key: ## Генерирует приватный и публичный ключ для создания jwt
	openssl genrsa -out jwt-private.pem 2048
	openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
	echo "✅ Сгенерированы private и public ключи в корне проекта"

.PHONY: queue_start
queue_start: ## запускаем брокер очередей (Faststream + RabbitMQ)
	python -m faststream run src.faststream.app:app

.PHONY: queue_docs
queue_docs: ## запускаем сервер с документацией очередей
	python -m faststream docs serve src.faststream.app:app --port 8081

.PHONY: app_structure
app_structure: ## Выведет структуру проекта
	python -m cli.main structure show

.PHONY: docker_up
docker_up: ## подымает контейнеры
	docker-compose up --build -d

.PHONY: down
down: ## останавливает контейнеры и удаляет их образы
	docker-compose down --remove-orphans #очистит все запущенные контейнеры

.PHONY: build
build: ## собирает контейнеры
	docker-compose build

.PHONY: rebuild
rebuild: down build up ## составная команда, для перезапуска контейнера [down -> build -> up]

.PHONY: ps
ps:	## информация по контейнерам докера
	docker-compose ps

.PHONY: app_bash
app_bash: ## зайти в контейнер приложения
	docker-compose exec app bash

.PHONY: venv
venv: ## активируем виртуальное окружение
	source venv/bin/activate

.PHONY: run_test
run_test: ## запускает тесты
	 pytest -vvs --tb=short -l

.PHONY: run_test_async
run_test_async: ## запускает тесты
	 pytest -vvs --tb=short -l -n auto

# запуск make install pkg=httpx
install:
	docker exec -it ${APP_NAME}__app pip install $(pkg)
	docker exec -it ${APP_NAME}__app pip freeze > requirements.txt
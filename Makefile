.SILENT:

# Дефис перед include указывает make игнорировать отсутствие файла и продолжать работу без ошибок
-include .env

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

.PHONY: init_app
init_app: build generate_key storage_link permissions up migration_run seed_data ps info ## разворачиваем проект, запускается один раз

.PHONY: seed_data ## загрузить данные
seed_data:
	docker exec -it ${APP_NAME}__app python -m cli.main seed perms
	docker exec -it ${APP_NAME}__app python -m cli.main seed superadmin
	docker exec -it ${APP_NAME}__app python -m cli.main seed books

.PHONY: info ## информация
info:
	echo '----------------------------------------------------------------------------------------------------------------------------------------';
	printf "\\033[36m[x] LOCAL\\033[0m\\n";
	echo ${APP_URL};
	echo ${APP_URL}/docs;
	echo Email - ${APP_URL}:8025;
	echo RabbitMQ - ${APP_URL}:15672;
	echo Prometheus - ${APP_URL}:9090;
	echo Grafana - ${APP_URL}:3000;
	echo '----------------------------------------------------------------------------------------------------------------------------------------';

#======================================
# Copy file
.PHONY: cp_file
cp_file: cp_env ## создает файл .env, .env.testing, docker-compose.yml [по дефолту заточено под linux, если mac, то вызываем - make cp_file os=mac]
ifeq ($(os),mac)
	$(MAKE) cp_docker_compose_mac
else
	$(MAKE) cp_docker_compose_linux
endif

.PHONY: cp_env
cp_env:
	cp -n .env.dist .env && echo "✅ copy .env from .env.dist" || echo "⚠️  .env already exists"
	cp -n .env.testing.dist .env.testing && echo "✅ copy .env.testing from .env.testing.dist" || echo "⚠️  .env.testing already exists"

.PHONY: cp_docker_compose_mac
cp_docker_compose_mac:
	cp -n infrastructures/docker/docker-compose-mac.yaml.dist docker-compose.yaml && echo "✅ copy docker-compose.yaml" || echo "⚠️  docker-compose.yaml already exists"

.PHONY: cp_docker_compose_linux
cp_docker_compose_linux:
	cp -n infrastructures/docker/docker-compose-linux.yaml.dist docker-compose.yaml && echo "✅ copy docker-compose.yaml" || echo "⚠️  docker-compose.yaml already exists"

##======================================
# Command

.PHONY: permissions
permissions: ## даем права папкам
	sudo chmod 777 -R -f logs
	sudo chmod 777 -R -f storage

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

.PHONY: migration_run
migration_run: ## Запуск миграций
	echo "✅ Запуск миграций"
	docker exec -it ${APP_NAME}__app alembic upgrade head

##======================================
# Docker command

.PHONY: docker_up
docker_up: ## подымает контейнеры (если нужно выводить логи пере)
ifeq ($(log),true)
	docker-compose up
else
	docker-compose up -d
endif

#.PHONY: docker_up
#docker_up: ## подымает контейнеры ()
#	docker-compose up --build -d

.PHONY: down
down: ## останавливает контейнеры и удаляет их образы
	docker-compose down --remove-orphans #очистит все запущенные контейнеры

.PHONY: build
build: ## собирает контейнеры
	docker-compose build
	echo "✅ Контейнеры собраны"

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
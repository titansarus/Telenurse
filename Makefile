ifneq (,$(wildcard ./.env))
	include .env
	export
	ENV_FILE_PARAM = --env-file .env
endif

build:
	docker-compose up --build -d
up:
	docker-compose up -d
down:
	docker-compose down
logs:
	docker-compose logs
migrate:
	docker-compose exec api python manage.py migrate
makemigrations:
	docker-compose exec api python manage.py makemigrations
superuser:
	docker-compose exec api python manage.py createsuperuser	
runserver:
	docker-compose exec api python manage.py runserver
down-v:
	docker-compose down -v
volume:
	docker volume inspect DORNA-SYSTEM_postgres_data	
shell:
	docker-compose exec api python manage.py shell
tests:
	docker-compose exec api python manage.py test
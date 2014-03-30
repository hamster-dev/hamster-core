all:
	@echo "Usage:"
	@echo "start_worker		Start celery worker"
	@echo "start_flower		Start celery monitoring"
	@echo "test			Run tests"
	@echo "runserver		Start Django development server"

start_worker:
	celery -A hamster worker --loglevel=info

start_flower:
	celery flower --broker=amqp://guest:guest@localhost:5672/ --address=0.0.0.0

test:
	python manage.py test

runserver:
	python manage.py runserver 0.0.0.0:8000

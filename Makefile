install:
	pip install poetry
	poetry install
	poetry run python manage.py migrate
run:
	poetry run python manage.py runserver
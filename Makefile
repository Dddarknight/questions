install:
	pip install poetry
        poetry config virtualenvs.in-project true
	poetry install
        poetry shell
	poetry run python manage.py migrate
run:
	poetry run python manage.py runserver

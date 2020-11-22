lint:
	poetry run flake8 page_loader tests

test:
	poetry run pytest tests -q

check: lint test

install:
	poetry install

coverage:
	poetry run coverage run --source=page_loader --omit=page_loader/scripts/* -m pytest tests
	poetry run coverage xml

build:
	poetry build

package-install:
	pip install --user dist/*.whl
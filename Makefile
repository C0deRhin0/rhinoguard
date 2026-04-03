.PHONY: install test lint validate demo api clean

install:
	python -m pip install -e '.[dev]'

test:
	python -m unittest discover -s tests -v

lint:
	ruff check src tests

validate:
	python -m rhinoguard validate

demo:
	python -m rhinoguard compare scenarios/prompt-injection/indirect-file.yaml

api:
	uvicorn rhinoguard.api.app:app --host 127.0.0.1 --port 8080 --reload

clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('reports', '.pytest_cache', '.ruff_cache', 'htmlcov', 'dist', 'build')]"

# Capture a cleanup item for makefile
# Align local documentation for makefile

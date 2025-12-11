.PHONY: docs docs-serve

docs:
	mkdocs build

docs-serve:
	mkdocs serve -a 0.0.0.0:8000

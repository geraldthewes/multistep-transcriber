.PHONY: docs docs-serve docs-api test publish clean devcontainer stop delete

# Generate API documentation using lazydocs
# Requires: conda activate mst (or environment with all dependencies)
docs-api:
	lazydocs --output-path=./docs/api \
		--src-base-url="https://github.com/geraldthewes/multistep-transcriber/blob/main/" \
		--overview-file="README.md" \
		--no-watermark \
		--toc \
		mst || true
	lazydocs --output-path=./docs/api \
		--src-base-url="https://github.com/geraldthewes/multistep-transcriber/blob/main/" \
		--no-watermark \
		--toc \
		mst.VideoTranscriber

docs: docs-api
	mkdocs build

docs-serve:
	mkdocs serve -a 0.0.0.0:8000

test:
	./test.sh

clean:
	rm -rf dist/ build/ *.egg-info

PYPI_URL ?= http://pypi.cluster:9999/
publish: test
	twine upload --repository-url $(PYPI_URL) dist/*

DEVCONTAINER_NAME ?= multistep-transcriber
devcontainer:
	devpod up $(DEVCONTAINER_NAME) --provider nomad

stop:
	devpod stop $(DEVCONTAINER_NAME)

delete:
	devpod delete $(DEVCONTAINER_NAME)

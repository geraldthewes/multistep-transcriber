.PHONY: docs docs-serve docs-api test publish clean devcontainer stop delete

DEVCONTAINER_NAME ?= multistep-transcriber
DEVCONTAINER_SRC ?= github.com/geraldthewes/multistep-transcriber
WORKSPACE_DIR ?= /workspaces/multistep-transcriber
PYPI_URL ?= http://pypi.cluster:9999/

REMOTE_EXEC = devpod ssh $(DEVCONTAINER_NAME) --command "cd $(WORKSPACE_DIR) && { set -a; . .vault-secrets 2>/dev/null; set +a; } &&

# Generate API documentation using lazydocs
# Requires: conda activate mst (or environment with all dependencies)
docs-api:
	conda run -n mst lazydocs --output-path=./documentation/api \
		--src-base-url="https://github.com/geraldthewes/multistep-transcriber/blob/main/" \
		--overview-file="README.md" \
		--no-watermark \
		--toc \
		mst || true
	conda run -n mst lazydocs --output-path=./documentation/api \
		--src-base-url="https://github.com/geraldthewes/multistep-transcriber/blob/main/" \
		--no-watermark \
		--toc \
		mst.VideoTranscriber \
		mst.steps.caching \
		mst.steps.diarization \
		mst.steps.entities \
		mst.steps.format \
		mst.steps.helpers \
		mst.steps.introductions \
		mst.steps.llm_client \
		mst.steps.merge_sentences \
		mst.steps.models \
		mst.steps.standardize \
		mst.steps.topic_segmentation \
		mst.steps.transcription

docs: docs-api
	mkdocs build

docs-serve:
	mkdocs serve -a 0.0.0.0:8000

test:
	$(REMOTE_EXEC) ./test.sh"

clean:
	$(REMOTE_EXEC) rm -rf dist/ build/ *.egg-info"

publish: test
	$(REMOTE_EXEC) twine upload --repository-url $(PYPI_URL) dist/*"

devcontainer:
	devpod up $(DEVCONTAINER_SRC) --provider nomad --ide none

stop:
	devpod stop $(DEVCONTAINER_NAME)

delete:
	devpod delete $(DEVCONTAINER_NAME)

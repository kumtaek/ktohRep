
.PHONY: all endpoints sql deps config errors
REPO ?= .
PY ?= python3

all: endpoints sql deps config errors

endpoints:
	scripts/generate_endpoints.sh $(REPO)

sql:
	$(PY) scripts/generate_sql_catalog.py $(REPO)

deps:
	scripts/generate_deps.sh $(REPO)

config:
	$(PY) scripts/generate_config_inventory.py $(REPO)

errors:
	$(PY) scripts/generate_error_registry.py $(REPO)

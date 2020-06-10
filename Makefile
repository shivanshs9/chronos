BUILD_DIR := build
SRC_PLUGINS_DIR := plugins/
BUILD_PLUGINS_DIR := $(BUILD_DIR)/plugins
BUILD_PLUGINS_LIST := $(BUILD_PLUGINS_DIR)/dcmp $(BUILD_PLUGINS_DIR)/ergo

.PHONY: help install-plugins docker-build build up clean

help: ### Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

$(BUILD_PLUGINS_DIR):
	mkdir -p $@

$(BUILD_PLUGINS_DIR)/%: $(SRC_PLUGINS_DIR)%
	@rm -r $@
	@echo "Copying from $<..."
	@cp -r `readlink -f $<` $@

install-plugins: $(BUILD_PLUGINS_DIR) $(BUILD_PLUGINS_LIST) ### Installs the necessary plugins for build step

build: install-plugins docker-build ### Builds the Chronos Airflow image as standalone

docker-build: ### Runs the standard docker build
	@echo "Building Chronos Airflow image"
	docker build -t airflow .

up: install-plugins ### Builds and deploys the Chronos service
	docker-compose up --build

clean: ### Cleans the build files
	@echo "Cleaning..."
	rm -r $(BUILD_DIR)
	@echo "Done!"

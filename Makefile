APP_NAME=BoreMapper
APP_DIR=boremapper
RESOURCES_DIR=resources
MAIN_FILE=${APP_DIR}/main.py
ICON_FILE=${APP_DIR}/${RESOURCES_DIR}/app_icon.png

.PHONY: init
init:
	python3 -m pip install -r requirements.txt

.PHONY: init-dev
init-dev:
	python3 -m pip install -r requirements_dev.txt

.PHONY: clean
clean:
	rm -rf dist/

.PHONY: test-unit
test-unit:
	tests/unit_tests.py

.PHONY: test-static
test-static:
	python3 -m pylint "${APP_DIR}/" \
		--errors-only \
		--init-hook='import sys; sys.path.insert(0, "./")' \
		--extension-pkg-whitelist=PySide6
	
.PHONY: build-windows
build-windows:
	pyinstaller \
		"${MAIN_FILE}" \
		--onefile \
		--name "${APP_NAME}" \
		--icon "${ICON_FILE}" \
		--add-data "${APP_DIR}/${RESOURCES_DIR}:${RESOURCES_DIR}" \
		--noconsole
	cp -r extras/* dist/
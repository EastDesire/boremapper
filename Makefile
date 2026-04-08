APP_NAME=BoreMapper
APP_DIR=boremapper

.PHONY: init
init:
	pip install -r requirements.txt

.PHONY: init-dev
init-dev:
	pip install -r requirements_dev.txt

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
	python3 -m nuitka \
		--assume-yes-for-downloads \
		--mode=app \
		--follow-imports \
		--enable-plugin=pyside6 \
		--include-package=pyttsx3 \
		--include-data-dir="${APP_DIR}/resources=resources" \
		--include-data-files="./data/*.xml=data" \
		--output-dir=dist/ \
		--output-filename="${APP_NAME}.exe" \
		--output-folder-name="${APP_NAME}" \
		"${APP_DIR}/main.py"
	
.PHONY: build-macos
build-macos:
	python3 -m nuitka \
		--assume-yes-for-downloads \
		--mode=app \
		--follow-imports \
		--enable-plugin=pyside6 \
		--include-package=pyttsx3 \
		--include-data-dir="${APP_DIR}/resources=resources" \
		--include-data-files="./data/*.xml=data" \
		--output-dir=dist/ \
		--output-filename="${APP_NAME}.bin" \
		--output-folder-name="${APP_NAME}" \
		--macos-app-name="${APP_NAME}" \
		"${APP_DIR}/main.py"
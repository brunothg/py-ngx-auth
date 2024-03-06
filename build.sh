#!/usr/bin/env bash

SCRIPT_PATH="${BASH_SOURCE}"
while [ -L "${SCRIPT_PATH}" ]; do
  TARGET="$(readlink "${SCRIPT_PATH}")"
  if [[ "${TARGET}" == /* ]]; then
    SCRIPT_PATH="$TARGET"
  else
    SCRIPT_PATH="$(dirname "${SCRIPT_PATH}")/${TARGET}"
  fi
done
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
SRC_DIR="$SCRIPT_DIR/src"
DIST_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build"

mkdir -p "$DIST_DIR"
rm -rf "${$DIST_DIR:?}"/*

mkdir -p "$BUILD_DIR"
rm -rf "${BUILD_DIR:?}"/*

( \
  cd "$SCRIPT_DIR" \
  && pipenv install --dev \
  && pipenv run pyinstaller --workpath "$BUILD_DIR/work" --specpath "$BUILD_DIR/spec" --distpath "$DIST_DIR" --onefile "$SRC_DIR/ngx-auth.py" \
)

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

( \
  cd "$SCRIPT_DIR" \
  && pipenv install \
  && cd "$SRC_DIR" \
  && pipenv run python ngx-auth.py "$@" \
)

#!/usr/bin/env bash
eval "$(direnv export bash)"
source $VIRTUAL_ENV/bin/activate
flask db downgrade

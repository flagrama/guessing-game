#!/usr/bin/env bash
export TEMP_APP_SETTINGS=$APP_SETTINGS
echo $APP_SETTINGS
export APP_SETTINGS=web.config.MigrationsConfig
flask db upgrade
export APP_SETTINGS=$TEMP_APP_SETTINGS
unset TEMP_APP_SETTINGS

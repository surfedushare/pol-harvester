#!/usr/bin/env bash

# Exit immediately on error
set -e

# Sets permissions of directories we want to have write access to
chown -R www-data:www-data /usr/src/app/pol_harvester/logs

# The git commit gets stored during the execution of start.bash
# Here we load the stored commit to be able to output it when running commands
if [[ -e "./.commit" ]]; then
    export DJANGO_GIT_COMMIT=$(cat ./.commit)
fi

# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
# Here we gather static files that get served through uWSGI if they don't exist
if [[ ! -d "statics" ]]; then
    ./manage.py collectstatic --noinput
fi

# When in DEBUG mode, and datagrowth project is present as a sibling, and datagrowth is installed as a site-package
# Then we uninstall datagrowth and install the sibling project as editable instead.
# That way we can more easily experiment with datagrowth during development.
if [ "$DJANGO_DEBUG" == "1" ]  && [ -d "/usr/src/datagrowth" ] && \
    [ $(pip show datagrowth | grep "Location:" | awk -F "/" '{print $NF}') == "site-packages" ]
then
    echo "Replacing datagrowth PyPi installation with editable version"
    pip uninstall -y datagrowth
    pip install -e /usr/src/datagrowth
fi

# Executing the normal commands
exec "$@"

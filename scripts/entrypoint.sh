#!/bin/sh
sleep 5

# Prepare prometheus multiprocess directory.
# Must be clean on every startup so stale worker files don't accumulate.
rm -rf "${PROMETHEUS_MULTIPROC_DIR:-/tmp/prometheus_multiproc}"
mkdir -p "${PROMETHEUS_MULTIPROC_DIR:-/tmp/prometheus_multiproc}"

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createcachetable
gunicorn review2.wsgi:application --bind=0.0.0.0:8000 --workers=3

exec "$@"

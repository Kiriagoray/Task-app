web: gunicorn taskmanager.wsgi --log-file -
#or works good with external database
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn taskmanager.wsgi:application --bind 0.0.0.0:$PORT

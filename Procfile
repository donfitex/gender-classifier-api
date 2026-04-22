web: python manage.py migrate && python manage.py seed_profiles && gunicorn gender_classify_api.wsgi:application --bind 0.0.0.0:$PORT

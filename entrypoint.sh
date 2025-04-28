#!/bin/bash

echo "Flush the manage.py command if any"

while ! python manage.py flush --no-input 2>&1; do
  echo "Flushing Django manage command"
  sleep 3
done

echo "Migrate the Database at startup of the project"

# Wait for a few seconds and run db migration
while ! python manage.py migrate 2>&1; do
   echo "Migration is in progress"
   sleep 3
done

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

echo "Create or update Django superuser"

# Check if the superuser already exists
user_exists=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists())")

if [ "$user_exists" = "True" ]; then
    echo "Superuser $DJANGO_SUPERUSER_USERNAME already exists, updating password."
    python manage.py shell -c "from django.contrib.auth.models import User; user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); user.set_password('$DJANGO_SUPERUSER_PASSWORD'); user.save()"
else
    echo "Creating superuser $DJANGO_SUPERUSER_USERNAME."
    python manage.py createsuperuser --no-input --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"
fi

echo "Django docker is fully configured successfully."

# Execute the CMD passed to the Docker container
exec "$@"
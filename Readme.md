# API-Manager
API-Manager is my internship project.

It allows running and managing docker containers and generates configuration files for a tool.

# Run
To run this program you will have to first install the requirements (inside your virtual env):

```bash
pip install -r requirements.txt
```

Then run migrations to create a database:

```bash
python manage.py makemigrations
python manage.py migrate
```

And finally run the django app:

```bash
python manage.py runserver
```

# Create an admin user
Accessing user admin panel requires an admin account. You can create an administrator using this command:

```bash
python manage.py createsuperuser
```

Now you can log into the user admin panel using the credentials that you just provided.

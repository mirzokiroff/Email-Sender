mig:
	python3 manage.py makemigrations
	python3 manage.py migrate
run:
	python3 manage.py runserver
create:
	python3 manage.py createsuperuser
pipsave:
	pip freeze > requirements.txt

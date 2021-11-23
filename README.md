# TeleNurse

Telenurse is a logistic project for providing healthcare and nursing.
It will be very useful to have an integrated system so that both job seekers and people who need nursing and medical services at home can use it and communicate easily with each other. In order to ensure the users of this system, this system should be implemented in such a way that the supervisors and managers in the support center are always aware of the status of all nurses and if there is a problem, they will deal with it as soon as possible.

### How to run the project

First, you need to have [Docker](https://docs.docker.com/get-docker/) installed. Then follow steps below:

- Build your docker image using:
```sh
$ make build
```
or
```sh
$ docker-compose up --build -d
```

- Generate the SQL commands for preinstalled apps using:
```sh
$ make makemigrations
```
or
```sh
$ docker-compose exec api python manage.py makemigrations
```

- Execute those SQL commands in the database file using:
```sh
$ make migrate
```
or
```sh
$ docker-compose exec api python manage.py migrate
```

- Create you admin with full access using:
```sh
$ make superuser
```
or
```sh
$ docker-compose exec api python manage.py createsuperuser
```

- Run your server using:
```sh
$ make runserver
```
or
```sh
$ docker-compose exec api python manage.py runserver
```

- Finally, open your browser and go to http://127.0.0.1:8000/ to see the project on your localhost.

You can use other commands of docker that are available in [Makefile](Makefile) easily.
FYI: In case of any errors in building images, turn on your VPN.
### How to run the tests

To test your code based on test.py files which include the tests you have written, run below command:
```sh
$ make tests
```
or
```sh
$ docker-compose exec api python manage.py test
```

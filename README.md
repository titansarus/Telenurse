# TeleNurse

Telenurse is a logistic project for providing healthcare and nursing.
It will be very useful to have an integrated system so that both job seekers and people who need nursing and medical services at home can use it and communicate easily with each other. In order to ensure the users of this system, this system should be implemented in such a way that the supervisors and managers in the support center are always aware of the status of all nurses and if there is a problem, they will deal with it as soon as possible.

## Run the project

First, you need to have [Docker](https://docs.docker.com/get-docker/) installed. Then follow steps below:

1. Build your docker image using:

```sh
$ make build
```

2. Generate the SQL commands for preinstalled apps using:

```sh
$ make makemigrations
```

3. Execute those SQL commands in the database file using:

```sh
$ make migrate
```

4. Create you admin with full access using:

```sh
$ make superuser
```

5. Run your server using:

```sh
$ make runserver
```

6. Finally, open your browser and go to address below to see the project on your [localhost](http://127.0.0.1:8000).

- Other commands are available in [Makefile](Makefile).
- In case of any errors in building images, turn on your VPN.

## Run the tests

To test your code based on test.py files which include the tests you have written, run below command:

```sh
$ make tests
```

## Development Notes

- If you want to run `manage.py` commands locally and connect to postgis running on docker, add following line to `/etc/hosts`:

```
127.0.0.1 postgres-db
```

- Only run postgres service:

```sh
docker-compose up --build -d postgres-db
```

## Database backup

The database can be backed up automatically every 12 hours using `pgbackups` service defined in docker compose.

Check [image's github page](https://github.com/prodrigestivill/docker-postgres-backup-local) for more info about configuration.

**Restore example:**

Run the following command to make a new postgres container:

```sh
docker run --rm -it --name restored-db -v $PWD/postgres_backups/daily/telenurse-20220103-143546.sql.gz:/tmp/backupfile.sql.gz kartoza/postgis:12.1 
```

Get into the container's shell:

```sh
docker exec -it restored-db /bin/sh 
```

Run the following command on the container:

```sh
zcat /tmp/backupfile.sql.gz | PGPASSWORD=docker psql --host=127.0.0.1 --port=5432 --username=docker --dbname=postgres
```

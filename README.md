# TeleNurse

Telenurse is a logistic project for providing healthcare and nursing.
It will be very useful to have an integrated system so that both job seekers and people who need nursing and medical services at home can use it and communicate easily with each other. In order to ensure the users of this system, this system should be implemented in such a way that the supervisors and managers in the support center are always aware of the status of all nurses and if there is a problem, they will deal with it as soon as possible.

### How to run the project

First, install all the dependencies in the [`requirement`](requirements.txt) file by running the below command:
```sh
$ pip install -r requirement.txt
```

Next, if your OS is Windows, download GDAL based on your python version from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) and add it to environment variables. If your OS is Linux, run following commands in your bash to install GDAL:
```sh
$ sudo aptitude install gdal-bin libgdal-dev
$ sudo aptitude install python3-gdal
```


Then, run below command to create new migrations for models in project.
```sh
$ python manage.py makemigrations
```

Then you should apply migrations which you created in the previous part to database. Run below command:
```sh
$ python manage.py migrate
```

Finally, to run the project, run the command `python manage.py runserver` in the location of your project and go to http://127.0.0.1:8000/ to see the project on your localhost.

### How to run the tests

To test your code based on test.py files which include the tests you have written, run below command:
```sh
$ python manage.py test
```

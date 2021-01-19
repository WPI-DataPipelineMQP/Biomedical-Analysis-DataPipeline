# Biomedical-Analysis-DataPipeline

This is a web application that allows researchers to upload, store, filter, and perform analyses on any type of biomedical data (assuming it is uploaded as a .csv file and follows some formatting standards). This is intended to provide a centralized source of data for different studies and provide a variety of different actions that would otherwise need to done through Excel, scripting, or statistical software. Additionally, one of the main goals of this project was to allow data analysis across different studies. 

This project was created over the course of 1.5 semesters as part of Worcester Polytechnic Institute's Major Qualifying Project. It utilizes a Python web framework called Django, with most of the back end written in Python. Bootstrap is used on the front end. 

## Installing Python Dependencies

- Install the python dependencies that this program requires. The dependencies are defined in the requirements.txt file so just follow the command below.

```console
$ pip3 install -r requirements.txt
```

## Config Environment Variables

- Obtain the most up-to-date .env file for running this program. It contains sensitive information and other development specific environment settings. Ensure the file is saved as a .env file and not .txt.

- Move this file to be within the Biomedical-Analysis-DataPipeline (root) directory

## Run Website (Locally)

- Navigate to the mqp_project directory and run the following command.

```console
$ python manage.py runserver
```
> NOTE: If you want to use the uploader feature, you need to follow the "Run the Progress Bar" instructions below

## Run the Progress Bar

### Linux Instructions
- In a separate terminal run the redis server 

```console
$ redis-server
```

- After the redis server is running successfully, navigate to the mqp_project directory in the project in a seperate terminal 
- Once you completed the above step, run the following command 

```console
$ celery -A mqp_project worker --loglevel=info
```

- After running the command, you can now run the project normally


### Windows Instructions
- Install redis. This is easier to do through the Windows subsystem for linux by running ```$ sudo apt-get install redis-server```. Otherwise, there are a large amount of unofficial windows versions of redis that can be found online and should work as well.

- In a separate terminal run the redis server 

```console
$ redis-server
```

- Celery is not officially supported on Windows but can be run via another another library called gevent (source for solution: https://stackoverflow.com/questions/37255548/how-to-run-celery-on-windows). Install gevent with the following command:

```console
$ pip install gevent
```

- After the redis server is running successfully, navigate to the mqp_project directory in a terminal separate from the redis server. Run the following command 

```console
$ python -m celery -A mqp_project worker --loglevel=info
```

- This should eventually show ```celery@<your device> ready.``` and then hang. If the redis server is not running, it will have an appropriate error message. After running the command sucessfully, you can now run the project normally in another terminal.
> NOTE: You will have 3 terminals in total. One to run redis, one to run celery, and another to run the django server.

## Developer Guide
This section provides additional information and advice for potential future developers of this project.

### Django
- [These video tutorials](https://www.youtube.com/watch?v=UmljXZIypDc&feature=youtu.be&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p) are very helpful for learning Django.


### .Env file
- The .env file externally stores sensitive or development specific environment variables that would otherwise be directly put in settings.py. For this reason, .env is purposely included in .gitignore and should be distributed to team members through less public means.
- An example of what the .env file would look like for this project is included in the example.env.txt file
- [This link](https://simpleisbetterthancomplex.com/2015/11/26/package-of-the-week-python-decouple.html) provides more information about setting up the .env file and accessing environment variables using the Decouple Python package
- One of the variables in .env is the secret key. This is used for cryptographic signing and general security so it should be hidden. It basically just needs to be a unique string so using a generator like [this](https://miniwebtool.com/django-secret-key-generator/) should be sufficient.

### Email Address for Password Reset Feature
- Currently, the password reset system utilizes a gmail account. Future developers should consider creating a new account or maybe even using an automated email service. 
- [This tutorial](https://youtu.be/-tyBEsHSv7w) provides additional information on setting up an email address for this.

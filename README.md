# Biomedical-Analysis-DataPipeline

## Installing Python Dependencies

Install the python dependencies that this program requires. The dependencies are defined in the requirements.txt file so just follow the command below. 

```console
$ pip3 install -r requirements.txt
```


## Run Website

```console
$ python manage.py runserver
```

## Helpful Link to Playlist of Django Tutorials

[Youtube Link](https://www.youtube.com/watch?v=UmljXZIypDc&feature=youtu.be&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p)

## Run the Progress Bar

- first run the requirements to install the necessary modules and software
- in a separate terminal run the redis server 

```console
$ redis-server
```

- after the redis server is running successfully, navigate to the mqp_project directory in the project in a seperate terminal 
- once you completed the above step, run the following command 

```console
celery -A mqp_project worker --loglevel=info
```

- after running the command, you can now run the project normally

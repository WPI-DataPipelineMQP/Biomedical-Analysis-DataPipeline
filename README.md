# Biomedical-Analysis-DataPipeline

## Installing Python Dependencies

Install the python dependencies that this program requires. The dependencies are defined in the requirements.txt file so just follow the command below. 

```console
$ pip3 install -r requirements.txt
```


## Run Website

Navigate to the mqp_project directory and run the following command.

```console
$ python manage.py runserver
```

## Helpful Link to Playlist of Django Tutorials

[Youtube Link](https://www.youtube.com/watch?v=UmljXZIypDc&feature=youtu.be&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p)

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

- After running the command, you can now run the project normally

# 61B Office Hour Queue
This is the newly redesigned OH queue for CS 61B.

## Running
### Running with Docker
A basic docker configuration is included in this project for both deployment in production and local development. This is the recommended way to run this on all platforms for uniformity as this docker deployment will be used on the actual production server.
#### Running Locally
The local version of the Docker configuration automatically mounts the local working directory and reloads changes to code (though this can sometimes be spotty for changing `settings.py` or `urls.py`) without having to reload the entire Docker configuration. Linux users should change the `user_id` build arg in `docker-compose.yml` to match the id of the user who owns the files you are working on. This is not a concern for macOS or Windows users.

#### Compose helper script
There is a simple helper script provided named `compose`. This should work on Mac and Linux and should work in Windows but this is untested. Alternatively, you can replace everywhere you see `./compose [CMD]` with `docker-compose -f docker-compose.yml -f local-compose.yml [CMD]`.

#### Compose Reference
To build run:
```
./compose build
```

You can verify that is runs properly by running
```
./compose up
```
And waiting for the Django startup line (`Starting development server at http://0.0.0.0:8000/`). IF there aren't any Python errors in the output then the configuration likely worked.

To run a command locally you can do the following:
```
./compose [DOCKER_CMD_HERE]
```

To start up the server:
```
./compose up
```
To run it in detached mode, you can append a `-d` to the previous command and Docker will not block your terminal while running.


**Note for Windows**:
If you followed the section above for building on Windows and you cannot connect to the development server, but it seems to be running properly, you are probably running Docker Toolbox and you need to forward the 80 port from the VM to your local computer. This is a decent guide on doing this: https://www.simplified.guide/virtualbox/port-forwarding


This is only necessary for the `up` and `run` commands. If you already have a container running (through `up -d` for example) you can use the following command to enter it:
```
./compose exec [SERVICE_NAME] [COMMAND]
```

For all of the following commands, the server must be up and running using the above instructions.

To enter a running interface (Django) server with a terminal shell:
```
./compose exec interfaceserver sh
```

To run a manage.py command:
```
./compose exec interfaceserver ./manage.py [MANAGE.PY COMMAND]
```

To install a new npm package:
```
./compose exec reactserver npm install [PACKAGE] --save
```

To install a new python requirement:

First add the requirement to `requirements.in` and then run the following command:
```
./compose exec interfaceserver sh -c "pip-tools compile requirements.in > requirements.txt"
```

#### Building for Windows
There have been known issues with running this on Windows after cloning from the repo due to the difference in line endings between UNIX-based systems and Windows. To fix you can run the following command: 
```
git config --global core.autocrlf false
```
After running this command, deleting and recloning the repo should fix the issue.

#### Running in Production
More will be added to this section

### Docker Services/Architecture
#### General Services
1. Postgres

    This project relies on a Postgres database service
2. Redis

    The websocket component (Django channels) relies on Redis for queuing and handling websocket requests.
3. Interface Server

    The interface server is the Django HTTP server that handles all HTTP requests and the majority of the web servers logic.
#### Local Services
1. React Server

    Locally, a server is ran to automatically keep track of and rebuild the React frontend. 
#### Production Servers
1. Nginx

    For production, a simple nginx server is added. This service has default support for a Let'sEncrypt cert stored in a particular place on server. More info will be added to this section eventually.
2. Worker Server

    Additionally, a worker server is added to handle Websockets requests as required by Django channels. This server runs the Django code and communicates with the Redis server to handle requests.

### Running Without Docker
It should also be easy to run without Docker for development purposes (as it is easier to drop a debugger in this manner). Please note that the following instructions will not work on Windows as Redis is a prerequisite and cannot run on Windows at the current time (you may be able to get around this by running Redis in a Docker container). All commands listed below are assumed to run in the root of this project.

#### Prerequisites
##### Postgres
[Postgres](https://www.postgresql.org/) is a necessary component of this project. You may need to change the Postgres password in `settings.py` depending on your Postgres configuration. Additionally, you could change the server to use a different SQL server than Postgres for development, but this is not recommended as there may be bugs or features that are specific to the SQL server you run.

##### Redis
[Redis](https://redis.io/) is necessary for this project. You can follow instructions on the Redis site or Google for installation instructions. As Redis relies on the `fork()` syscall that is unavailable on Windows, this will not run on Windows unless ran in a VM or Docker container.
##### Software Specific prerequistes
It is recommended to do the following in a virtual environment:
```
pip3 install requirements.txt
cd ohqueue/
npm install
```
#### Running
To build the react files:
```
npm run build
```

To watch for updates and hot reload:
```
cd ohqueue/
node react_server.js
```

To run Django server:
```
cd ohqueue/
python3 manage.py runserver 0.0.0.0:8000
```

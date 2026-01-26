# docker-workshop
Workshop Codesapces


docker run image

it run an instance of the docker image, which is called docker container, it contains spansht of information available
the docker image.

When we re-run docker run image, we crate another instance,another container, and what ever manipulation we performed 
in the previous run, it will not be present in the current, as it is stateless.

To run a python docker image we can do 
docker run -it python:3.13.11 or python:3.13.11-slim (slimmer version)
we will be inside python 
to get a bash cmd  we can do 
docker run -it --entrypoint=bash python:3.13.11-slim
is not entirely true that docker cotnainers are stateless.
because when we run an image again a version of the previous docker container is saved somewhere.
And we could access that version, bu we should not do this.
we can view all docker containers we run by doing docker ps -a
We can remove all this files by doing docker ps -aq to get the id of containers, and then docker rm `docker ps -aq`

But how do we preserve state in docker container

Lets say we have a script and we want to execute it inside our docker container how to do?
We can use Volumes

-- VOLUMES -- 
We have a folder in our own machine, we want that docker mirror the directory located in our machine
Therefore if the directory in our machine contain a python script this will be also represented in our docker container. 

we use this command 
docker run -it --entrypoint=bash -v $(pwd) python:3.13.11-slim
pwd is our current directory
we are mapping the content in the absolute path to the docker container

docker run -it --entrypoint=bash -v $(pwd)/test:/app/test python:3.13.11-slim
$(pwd)/test - > map the contet of our home directory 
/app/test - > to docker container location


-------------------------
---DATA PIPELINE--------
-----------------------


to parametrize a pipeline we can use 
import sys
and use sys.arv 

in general we want to create a virtual environemnt in our host machine to install 
all our dipendencies, instead of installing them directly in our host machine 


--------------------------------
---- UV ENVIRONMENT ----------
----------------------------
 
we can use the library uv, which helps managing multiple virtual environments 
we can use the command 
uv init --python 3.13  a version of python in our virtual environment
to install packages in our new envirnment we can run 
uv add pandas


Lets say in our virtual environment we build a pipeline, then we want to save 
the pipeline scripts inside  docker container
But we will create our own docker image that uses specficic python version, and the librairy we need.

---------------------------------
--- CREATING OWN DOCKER IMAGE----
----------------------------------
we first create a file called DockerFile inside our folder of interst.
Dockerfile describes how the container will be built,it contains all the instructions necessary to create a docker container from this image.
We always start with 

FROM python:3.13.11-slim
RUN pip install pandas pyarrow
WORKDIR /code -  the workdir we want to save the file
COPY pipeline.py .  - we copy from the host system to the docker image

Then we run the code below to build our docker image with teh name test:pandas
docker build -t test:pandas . -> t is the tag we give to the image

then we can run our docker image 

docker run -it --entrypoint=bash --rm test:pandas 

--rm is used to delete the version of the docker container that will be saved somewhere in our system, and its not ideal.

if we want to automatically execute the script inside the iamge as soon as container is crated 
we need to add to our dockerfile 

ENTRYPOINT ["python","pipeline.py"]

docker run -it --rm test:pandas 12  - it will immediatly exectue the script

We crated our data pipeline and dockerized it.


---------------------------------------------------
--- Installing UV ENV IN OUR DOCKER IMAGE  --------
-------------------------------------------------

FROM python:3.13.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/ 
we are coping uv from a docker image "ghcr.io/astral-sh/uv:latest /uv" and save it in our docker iamge location /bin/ 

WORKDIR /code
- we want to create our working directory in our image before the code below


ENV PATH="/code/.venv/bin:$PATH"

Why this is brilliant:

uv creates a Virtual Environment (a self-contained folder with libraries) at /code/.venv.

Usually, to use a virtual environment, you have to run a command like source .venv/bin/activate.

By changing the PATH here, the environment is always active automatically. You never have to type "activate".



COPY pyprojects.toml .python-version uv.lock ./    - we can cpy the pyprojects.toml from our uv envirement  

RUN uv sync --locked # it will install the dependencies from the uv.lock file, so that depndencies in 
our docker image are same as in our host machine 

COPY pipeline.py . --copy our pipeline.py script

ENTRYPOINT ["python","pipeline.py"] -- exectue the script as soon as we create a cotainer of the image
 the parquet file we created is saved inside the docker container



--------------------------------------------
-- INSTALL POSTGRES SQL in Dokcer image ----
---------------------------------------------

docker run -it --rm\
-e POSTGRES_USER="root"\ --> sets  -e environment variable inside the container, postgres image looks for this veriable during sturtup
-e POSTGRES_PASSWORD="root"\ define the password of for our user defined above
-e POSTGRES_DB="ny_taxi"\  -- create automatically database name at the startup.
-v ny_taxi_postgres_data:/var/lib/postgresql\ --> months a volume named ny_taxi_postgres_data in our host machine, which is managed by docker. Docker stores database files in the volume located in our host machine.The location of the stored data is defined on the right side of ":"
We have a folder in our host machine and we map it to our container.
-p 5432:5432\ - > it maps the network port hostport:containerport, without this mapping the dabase is isoldated inside the container network, and tools in our laptop cannot reach it.
If we send a request to our localhost 5432, we are actually sending it to whatever is runing in our container.
postgres:18 --> name of our image and version


Docker checks if you have the postgres:18 image. If not, it downloads it.
It creates a volume ny_taxi_postgres_data (if it doesn't exist).
It starts the container, creates a user root with password root, and creates a DB named ny_taxi.
It links your computer's port 5432 to the container.
It streams the logs to your screen so you can see it says "database system is ready to accept connections."

docker run -it --rm \
-e POSTGRES_USER="root" \ 
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v ny_taxi_postgres_data:/var/lib/postgresql \
-p 5432:5432 \


uv add --dev pgcli >- --dev will install the package as dev environment 
but it will not be copied in docker container, when we sincronize  the uv 
using sync --locked  as it sync only the main dependencies in our pyproject.tomail file
pgcli is  pakcage to interact with postgres from command line

uv run pgcli -h localhost -p 5432 -u root -d ny_taxi
with this code we conenct to our postgres inside our container where we can perform SQL statments.



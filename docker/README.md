# Run mutacc with docker

Optionally, **mutacc** can be run using docker. There exists several ways of how the containers
can be set up and used, so keep in mind that the solution given in this repository is merely
a suggestion of how the architecture could look.


## containers
The solution given here is to run *mongodb* in its own container, while all the CLI
operations done by mutacc will be handled through a separate image. The basic setup
for this is found in the [docker-compose.yml](docker-compose.yml) file.

### mongodb image

The mutacc-db image is created using the base *mongo* image. It is necessary to create
a volume saying where the data should be stored on the host system. This directory
will be used as the /data/db directory from within the mutacc-db container.

To start the mutacc-db container, change working directory to where the *docker-compose.yml*
and do

```
$ docker-compose up -d mutacc-db
```
This will start the mongodb service in its own container, mounting the data
to the directory specified in the volume.

To stop the process, do

```
$ docker-compose stop mutacc-db
```

### mutacc image

In the same *docker-compose.yml*, the mutacc container can be run. The container will
be installed from the [Dockerfile](../Dockerfile) in this repository. Here it is important
to create a volume to a *mutacc-root* directory on the host system. The config file *mutacc-docker-config.yaml*
will get copied to the *mutacc* image upon creation. It's important to change the mutacc config settings
here before the image is created.

This image have the entrypoint ```mutacc --config-file <config_file>```, so mutacc can be run from the docker-compose.yml file
with

```
$ docker-compose run --rm mutacc [mutacc options]
```

e.g.
```
$ docker-compose run --rm mutacc db cases
```

would get all cases in the database.

## Wrapper scripts

When mutacc need files from the host file system, these must be mounted to the
container when running it. This might be tedious. It might be a good idea to create
wrapper scripts when running mutacc through a container. To process reads from a case
using the ```mutacc extract``` command, an example wrapper script is found in *mutacc-docker-wrapper.py*.
Here, the yaml-file passed with the case-information is scanned for all the necessary paths, and volumes are
defined for the container before running it.

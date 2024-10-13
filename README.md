# videodl
A simple web app for family to download videos from the web (think vlogs for offline viewing).

## Running the dev database

If you just need to start postgres container:
```sh
docker compose -f postgres/compose.yml up --detach
```

If you need to rebuild the dev database (postgres container will be started automatically):
```sh
cd src
./init_db_dev.sh
```

### Installing Docker
Use docker for Postgresql.

1. Verify if docker is already installed

    ```sh
    sudo docker run hello-world
    ```

2. You should get a message that indicates Docker is installed correctly.
If not, follow [instructions to install Docker](https://docs.docker.com/engine/install/ubuntu/).

### Connecting to the dev database

The postgres container has an application specific database called "videodl".
This database is in addition to the standard "postgres" default database. To
connect to the "videodl" database execute the following:
```sh
docker exec -it videodl-db psql -U postgres -d videodl
```

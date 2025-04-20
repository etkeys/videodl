# videodl
A simple web app for family to download videos from the web (think vlogs for offline viewing).

## Development

### Running the dev database

If you just need to start postgres container:
```sh
cd src
docker compose up --detach
```

If you need to rebuild the dev database (postgres container will be started automatically):
```sh
cd src
./init_db_dev.sh
```

#### Connecting to the dev database

The postgres container has an application specific database called "videodl".
This database is in addition to the standard "postgres" default database. To
connect to the "videodl" database execute the following:
```sh
docker compose exec -it db psql -U postgres -d videodl
```

### Running the app

> **NOTE:** The dev database should be initialized and running first.

```sh
cd src
flask run
```

### Running the worker

> **NOTE:** The dev database should be initialized and running first.

```sh
cd src
python worker_run.py
```

## Installing

The Github Actions workflow will create the docker images for the videodl (web)
and videodl-worker (worker) services. You can download them from the release
page.

### Initial install

1. Copy the *videodl.image.tar* and *videodl-worker.image.tar* from the release
page to the machine you wish to run the app.

1. Import the images into docker.

    ```sh
    docker load < videodl.image.tar
    docker load < videodl-worker.image.tar
    ```

1. Create `compose.yml` and `.env` file (see samples).

1. Create containers

    ```sh
    docker compose create
    ```

1. Start the database service.

    ```sh
    docker compose start db
    ```

1. Run command apply database structure

    ```sh
    docker compose run --rm web flask db upgrade
    ```

    > **NOTE:** Using `--rm` will create and destroy a temporary container
    > which runs the command.

1. Start all services

    ```sh
    docker compose up -d
    ```

1. To gain initial access to the app, you'll need to use the recovery account
(see [Recovering access to the app](#recovering-access-to-the-app)).

### Upgrading to a newer version

1. Copy the *videodl.image.tar* and *videodl-worker.image.tar* from the release
page to the machine you wish to run the app.

1. Import the images into docker.

    ```sh
    docker load < videodl.image.tar.gz
    docker load < videodl-worker.image.tar.gz
    ```

1. Stop all containers

    ```sh
    docker compose stop
    ```

1. Update `compose.yml` and `.env` files as needed.

1. Recreate containers

    ```sh
    docker compose create --force-recreate
    ```

    > **NOTE:** Using `--force-recreate` will not affect data stored in volumes

1. If database migrations need to be applied (see Release Notes)

    1. Start the database service.

        ```sh
        docker compose start db
        ```

    1. Run command apply database structure

        ```sh
        docker compose run --rm web flask db upgrade
        ```

        > **NOTE:** Using `--rm` will create and destroy a temporary container
        > which runs the command.

1. Start all services

    ```sh
    docker compose up -d
    ```

## Recovering access to the app

If you loose your access token or are running the app for the first time, you
can use the *Recovery* account to create you're own account or generate a new
access token.

1. Generate a new access token for the *Recovery* account.

    ```sh
    docker compose exec web python /app/recovery.py
    ```

1. Copy the value generate, and use that to log into the app.
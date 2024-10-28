# videodl
A simple web app for family to download videos from the web (think vlogs for offline viewing).

## Development

### Running the dev database

If you just need to start postgres container:
```sh
docker compose -f postgres/compose.yml up --detach
```

If you need to rebuild the dev database (postgres container will be started automatically):
```sh
cd src
./init_db_dev.sh
```

#### Installing Docker
Use docker for Postgresql.

1. Verify if docker is already installed

    ```sh
    sudo docker run hello-world
    ```

2. You should get a message that indicates Docker is installed correctly.
If not, follow [instructions to install Docker](https://docs.docker.com/engine/install/ubuntu/).

#### Connecting to the dev database

The postgres container has an application specific database called "videodl".
This database is in addition to the standard "postgres" default database. To
connect to the "videodl" database execute the following:
```sh
docker exec -it videodl-db psql -U postgres -d videodl
```

### Running the app

> **NOTE:** The dev database should be initialized and running first.

```sh
cd src
python3 app.py
```

### Running the worker

> **NOTE:** The dev database should be initialized and running first.

```sh
cd src
python3 worker_run.py
```

## Deploying

> **NOTE:** The Github Actions workflow will package the application files, 
support files, and configuration files into a single tar file. The tar file will
then be copied to an ftp server.

1. Copy the tar file from the ftp server to the deploy server.

1. Stop the services that run the application. This is needed so the application
files can be safely replaced.

    ```sh
    sudo systemctl stop videodl_worker.service
    sudo systemctl stop videodl.service
    ```

1. `cd` into the directory that contains all the application files.

1. Delete all the files in the directory

    ```sh
    rm -rf *
    ```

1. Copy the tar file that was copied from the FTP server to the current directory.

1. Unpack the tar file

    ```sh
    tar xvfz <tar_file>
    ```

1. If the `systemd` service files have been updated:

    1. Copy the service files to `/usr/local/lib/systemd/system/`.

    1. Reload the `systemd` daemon to pickup the new changes.

        ```sh
        sudo systemctl daemon-reload
        ```

1. Create a new python virtual environment.

    ```sh
    python3 -m venv venv
    ```

1. Activate the python virtual environment.

    ```sh
    source venv/bin/activate
    ```

1. Install package dependencies

    ```sh
    pip install -r requirements.txt
    ```

1. If the application database needs to be upgraded.

    1. `cd` into the `src/` directory.

    1. Upgrade the database.

        ```sh
        flask db upgrade
        ```

1. Start the applications that run the application.

    ```sh
    sudo systemctl start videodl_worker.service
    sudo systemctl start videodl.service
    ```
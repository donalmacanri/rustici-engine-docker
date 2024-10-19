## Getting started

 - Retrieve the latest binary release of Rustici Engine and unzip it into the `rustici-engine` directory:

        curl <rustici_engine_release_url> | unzip -d ./rustici-engine/engine-release/

 - To build docker images locally:

        docker build -t rusticiengine:server .
        docker build -t rusticiengine:installer --target installer .

 - To initialize an empty database with a scorm engine database schema:

    a. Create an empty database, or obtain a URL to an empty database, eg

        echo "CREATE DATABASE rusticiengine" | psql "${ROOT_DATABASE_URL}/postgres"
        export DATABASE_URL="${ROOT_DATABASE_URL//localhost/host.docker.internal}/rusticiengine"
        
    b. Initialize scorm engine database:

        docker run -e DATABASE_URL=${DATABASE_URL} rusticiengine:installer

 - To run scorm engine server and expose it on port 8080 on the host machine:

        docker run -p 8080:80 -e API_BASIC_ACCOUNTS=apiUser:password -e DATABASE_SCHEMA=public -e DATABASE_URL=${DATABASE_URL} -e FILE_PATH_TO_UPLOADED_ZIP=/tmp/uploads -e FILE_PATH_TO_CONTENT_ROOT=/tmp -e WEB_PATH_TO_CONTENT_ROOT=/tmp rusticiengine:server

## Health Check

A 200 response should be available for GET requests to **/engine/api/v2/ping** using username and password specified in that environment's bln-rusticiengine-service instance's `API_BASIC_ACCOUNTS` environment variable, eg:

        curl -u apiUser:password http://localhost:8080/rusticiengine/api/v2/ping

## Getting started

 - Retrieve the latest binary release of Rustici Engine and unzip it into the `rustici-engine` directory:

        curl <rustici_engine_release_url> | unzip -d ./rustici-engine/engine-release/

 - First time setup: Initialize the database and install Rustici Engine:

        COMPOSE_PROFILES=install tilt up

 - For subsequent runs, start the development environment:

        tilt up

   This will start Rustici Engine, PostgreSQL database, and the My LMS application.
   
   The services will be available at:
   - Rustici Engine: http://localhost:8080
   - My LMS: http://localhost:8081

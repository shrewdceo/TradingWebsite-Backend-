New setup:


Video tutorial (from March 2021): 
https://www.youtube.com/watch?v=dHi2YpBPNbU



Get backups of InfluxDB and MongoDB to seed new project.

mkdir ./fusion
mkdir ./fusion/backend
mkdir ./fusion/front

cd ./fusion/backend && git clone git@gitlab.com:phoenix-upwork/arun/fpc-backend.git
cd ./fusion/front && git clone git@gitlab.com:phoenix-upwork/arun/frontend.git


# Docker-compose file:

    version: "3.8"
    services:
      mongodb_container:
        image: mongo:latest
        ports:
          - 27017:27017
        volumes:
          - "./mongovol/:/data/db"

      influxdb:
        image: influxdb:latest
        container_name: influxdb
        ports:
          - "8083:8083"
          - "8086:8086"
          - "8090:8090"
        volumes:
          - "./influxvol/:/var/lib/influxdb"
        deploy:
          resources:
            limits:
              memory: 20G
      redis:
        image: redis:latest
        container_name: redis
        ports:
          - "6379:6379"

# Mongorestore MongoDB from dump

Replace Influx Docker Vol with backed up Influx docker vol

# Run Docker-compose

#run server:
poetry install && poetry run python server.py

#run frontend:
yarn && yarn start

# If necessary, manually get stock data for days:

    localhost:8080/debug-gapfill_98w3y593852435jnk43645646n

# If necessary, manually reaggregate buckets:

    localhost:8080/debug-reaggregate-buckets_ow38u5o283u523g45n235tlkwj35235k

# Install CORS unblocker for local development:
	https://addons.mozilla.org/en-US/firefox/addon/cors-unblock/
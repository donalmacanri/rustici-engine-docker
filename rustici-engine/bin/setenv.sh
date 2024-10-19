#!/usr/bin/env bash

PORT=${PORT:-8080}
sed -i "s/port=\"8080\"/port=\"$PORT\"/g" /usr/local/tomcat/conf/server.xml 

read DB_USERNAME DB_PASSWORD DB_HOST DB_PORT DB_NAME <<<$(echo $DATABASE_URL | awk -F '[:/@]' '{print $4, $5, $6, $7, $8}')
export DB_URL="jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME"

CATALINA_OPTS="-DDB_URL=$DB_URL -DDB_USERNAME=$DB_USERNAME -DDB_PASSWORD=$DB_PASSWORD -DLOG_LEVEL=$LOG_LEVEL"

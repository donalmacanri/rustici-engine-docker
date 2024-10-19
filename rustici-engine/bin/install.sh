#!/usr/bin/env bash

cd "$(dirname "$0")"

awk -v loglevel="${LOG_LEVEL:-INFO}" '{gsub(/\${LOG_LEVEL}/, loglevel); print}' logback.xml.template > logback.xml

awk -v DB_SCHEMA="${DATABASE_SCHEMA}" -v PACKAGE_PROPERTIES_HANDLING="${PACKAGE_PROPERTIES_HANDLING:-DO_NOTHING}" \
'{
  split(ENVIRON["DATABASE_URL"], db_parts, /[:/@]/);
  DB_USERNAME=db_parts[4];
  DB_PASSWORD=db_parts[5];
  DB_HOST=db_parts[6];
  DB_PORT=db_parts[7];
  DB_NAME=db_parts[8];
  gsub(/\$\{DB_HOST\}/, DB_HOST);
  gsub(/\$\{DB_PORT\}/, DB_PORT);
  gsub(/\$\{DB_NAME\}/, DB_NAME);
  gsub(/\$\{DB_USERNAME\}/, DB_USERNAME);
  gsub(/\$\{DB_PASSWORD\}/, DB_PASSWORD);
  gsub(/\$\{DB_SCHEMA\}/, DB_SCHEMA);
  gsub(/\$\{PACKAGE_PROPERTIES_HANDLING\}/, PACKAGE_PROPERTIES_HANDLING);
  print;
}' ./EngineInstall.xml.template > ./EngineInstall.xml

echo $@

java -Dlogback.configurationFile=logback.xml -cp "lib/*" RusticiSoftware.ScormContentPlayer.Logic.Upgrade.ConsoleApp EngineInstall.xml $@

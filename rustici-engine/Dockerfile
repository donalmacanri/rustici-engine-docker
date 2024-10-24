# Installer stage
FROM eclipse-temurin:11-jdk as installer
COPY ./engine-release/Installer /usr/local/rustici-engine/Installer
COPY ./bin/install.sh /usr/local/rustici-engine/Installer/install.sh
RUN chmod +x /usr/local/rustici-engine/Installer/install.sh
WORKDIR /usr/local/rustici-engine/Installer
ENTRYPOINT ["/usr/local/rustici-engine/Installer/install.sh"]

# Server stage (no installer)
FROM tomcat:9.0.65-jdk11-temurin as main
WORKDIR /builder
COPY . ./
RUN mkdir -p build \
    && cp engine-release/RusticiEngine.war build/rustici-engine.war \
    && cd engine-customizations \
    && jar -uf ../build/rustici-engine.war .
RUN mv /builder/build/rustici-engine.war /usr/local/tomcat/webapps/rustici-engine.war
COPY ./bin/setenv.sh $CATALINA_HOME/bin

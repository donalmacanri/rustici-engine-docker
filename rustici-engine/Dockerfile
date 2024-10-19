FROM eclipse-temurin:11-jdk
FROM eclipse-temurin:11-jdk as builder
WORKDIR /builder
COPY . ./
RUN mkdir -p build \
    && cp rustici-engine/RusticiEngine.war build/scormengine.war \
    && cd overlay \
    && jar -uf ../build/scormengine.war .
RUN ls /builder/build

# Installer stage
FROM eclipse-temurin:11-jdk as installer
COPY ./rustici-engine/Installer /usr/local/rustici-engine/Installer
COPY ./bin/install.sh /usr/local/rustici-engine/Installer/install.sh
RUN chmod +x /usr/local/rustici-engine/Installer/install.sh
WORKDIR /usr/local/rustici-engine/Installer
ENTRYPOINT ["/usr/local/rustici-engine/Installer/install.sh"]

# Final stage without installer
FROM tomcat:9.0.65-jdk11-temurin as main 
COPY --from=builder /builder/build/scormengine.war /usr/local/tomcat/webapps/scormengine.war
COPY ./bin/setenv.sh $CATALINA_HOME/bin


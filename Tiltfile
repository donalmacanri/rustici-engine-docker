# Set COMPOSE_PROFILES to 'run' if not already set
if not os.getenv('COMPOSE_PROFILES'):
    os.environ['COMPOSE_PROFILES'] = 'run'

docker_compose('./docker-compose.yml')
docker_build('donalmacanri/rustici-engine', './rustici-engine')

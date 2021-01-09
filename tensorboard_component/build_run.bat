@REM GLOBAL @SETTINGS
@set registry=allmyregistry.azurecr.io
@set registryName=allmyregistry

@set dockerfile=docker-compose.yml
@set dockerfile_src=Dockerfile

@set repositoryName=tensoboard
@set versionNumber=0.1.0

@set permanent_storage=

@REM GENERATE DOCKER COMPOSE FILE
call docker-compose -f %dockerfile% build

call docker-compose -f %dockerfile% up
call docker-compose -f %dockerfile% down

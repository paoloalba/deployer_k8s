@REM GLOBAL SETTINGS
@set registry=
@set registryName=

@set mainRepositoryname=tensorboard
@set versionNumber=1.0.1

@set dockerfile=Dockerfile
@set repositoryName=%mainRepositoryname%
@set imageFullName=%registry%/%repositoryName%:%versionNumber%

call docker build -f %dockerfile% -t %imageFullName% .

call az acr login --name %registryName%

call docker push %imageFullName%

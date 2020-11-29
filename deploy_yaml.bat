@SET script_path=%~dp0
@set yaml_dir=

call python obj_detection_pipeline.py

@set namespace=carddetection

@REM @set secret_storage_yaml_path=%script_path%%yaml_dir%\secret_storage.yml
@REM @set app_yaml_path=%script_path%%yaml_dir%\application.yml

@REM @set job_yaml_path=%script_path%%yaml_dir%\job_training.yml
@set job_yaml_path=%script_path%%yaml_dir%\job_evaluation.yml

@REM call kubectl create namespace %namespace%
@REM call kubectl config set-context --current --namespace=%namespace%

@REM call kubectl apply -f %secret_storage_yaml_path% -n %namespace%
@REM call kubectl apply -f %app_yaml_path% -n %namespace%

call kubectl delete -f %job_yaml_path% -n %namespace%
call kubectl apply -f %job_yaml_path% -n %namespace%
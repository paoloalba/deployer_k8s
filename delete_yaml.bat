@SET script_path=%~dp0
@set yaml_dir=

@set namespace=carddetection

@set job_yaml_path=%script_path%%yaml_dir%\job_training.yml
call kubectl delete -f %job_yaml_path% -n %namespace%

@set job_yaml_path=%script_path%%yaml_dir%\job_evaluation.yml
call kubectl delete -f %job_yaml_path% -n %namespace%

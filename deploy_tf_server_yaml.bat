@SET script_path=%~dp0

@REM call python server_depl_yaml.py

@set namespace=siciliancardgames

@set secret_storage_yaml_path=%script_path%\secret_storage.yml
call kubectl apply -f %secret_storage_yaml_path% -n %namespace%

@set tf_servery_yaml_path=%script_path%\deploy_tf_server.yml
@set nginx_yaml_path=%script_path%\deploy_nginx.yml

@REM call kubectl create namespace %namespace%
@REM call kubectl config set-context --current --namespace=%namespace%

call kubectl apply -f %tf_servery_yaml_path% -n %namespace%
call kubectl apply -f %nginx_yaml_path% -n %namespace%


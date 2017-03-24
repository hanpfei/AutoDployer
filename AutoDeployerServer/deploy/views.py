from django.shortcuts import render
from django.http import HttpResponse

from deploy.models import AppConfig

import json
import os

import Deployer


def createConfig(request):
    config_name = request.GET.get('configName')
    repo_path = request.GET.get('repoPath')
    branch = request.GET.get('branch')
    submodule = request.GET.get('subdir')
    app_type = request.GET.get('appType')
    conf_path = request.GET.get('conf')

    server_name = request.GET.get('serverName')

    version = request.GET.get('serverName')
    if not version:
        version = ""

    configs = AppConfig.objects.filter(config_name=config_name)
    if len(configs) > 0:
        result = {}
        result["code"] = 500
        result["msg"] = "The config has already been existing."
        return HttpResponse(json.dumps(result))

    print(os.getcwd())

    config = AppConfig(config_name=config_name, repo_path=repo_path, branch=branch, submodule=submodule, app_type=app_type,
              conf_path=conf_path, server_name=server_name, version=version)
    config.save()

    serialized_config = {}
    serialized_config["config_name"] = config.config_name
    serialized_config["repo_path"] = config.repo_path
    serialized_config["branch"] = config.branch
    serialized_config["submodule"] = config.submodule
    serialized_config["app_type"] = config.app_type
    serialized_config["conf_path"] = config.conf_path
    serialized_config["server_name"] = config.server_name

    json_str = json.dumps(serialized_config)

    return HttpResponse(json_str)


def list_config(request):
    all_config_list = AppConfig.objects.order_by('-config_name')
    serialized_configs = []
    for config in all_config_list:
        serialized_config = {}
        serialized_config["config_name"] = config.config_name
        serialized_config["repo_path"] = config.repo_path
        serialized_config["branch"] = config.branch
        serialized_config["submodule"] = config.submodule
        serialized_config["app_type"] = config.app_type
        serialized_config["conf_path"] = config.conf_path
        serialized_config["server_name"] = config.server_name

        serialized_configs.append(serialized_config)
    json_str = json.dumps(serialized_configs)
    return HttpResponse(json_str)


def delete_config(request):
    config_name = request.GET.get('configName')
    configs = AppConfig.objects.filter(config_name=config_name)
    print(str(configs))
    for config in configs:
        config.delete()

    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"
    json_str = json.dumps(result)
    return HttpResponse(json_str)


def deploy(request):
    config_name = request.GET.get('configName')
    config = AppConfig.objects.get(config_name=config_name)

    repoPath = config.repo_path
    branch = config.branch
    subdir = config.submodule
    appType = config.app_type
    conf = config.conf_path
    serverName = config.server_name
    version = config.version

    print(os.getcwd())

    result = Deployer.deployAndRun(repoPath, branch, subdir, version, appType, conf, serverName)
    json_str = json.dumps(result)
    return HttpResponse(json_str)


def stop(request):
    config_name = request.GET.get('configName')
    config = AppConfig.objects.get(config_name=config_name)

    subdir = config.submodule
    appType = config.app_type

    result = Deployer.stopService(subdir, appType)
    json_str = json.dumps(result)
    return HttpResponse(json_str)


def restart(request):
    config_name = request.GET.get('configName')
    config = AppConfig.objects.get(config_name=config_name)

    subdir = config.submodule
    appType = config.app_type

    Deployer.restartService(subdir, appType)
    return HttpResponse("Success")
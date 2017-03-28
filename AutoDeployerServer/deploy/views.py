from django.shortcuts import render
from django.http import HttpResponse

from deploy.models import JavaAppConfig
from deploy.models import WebAppConfig

import json
import os

import Deployer


def checkAppType(app_type):
    result = None
    if app_type != "java" and app_type != "web":
        result["code"] = 500
        result["msg"] = "Unrecognined app type: " + str(app_type)
        json_str = json.dumps(result)

        result = HttpResponse(json_str)
    return result


def createConfig(request):
    app_type = request.GET.get('appType')
    check_result = checkAppType(app_type)
    if check_result:
        return check_result

    config_name = request.GET.get('configName')
    repo_path = request.GET.get('repoPath')
    branch = request.GET.get('branch')
    submodule = request.GET.get('subdir')
    conf_path = request.GET.get('conf')

    version = request.GET.get('version')
    if not version:
        version = ""

    if app_type == "java":
        configs = JavaAppConfig.objects.filter(config_name=config_name)
    elif app_type == "web":
        configs = WebAppConfig.objects.filter(config_name=config_name)

    if len(configs) > 0:
        result = {}
        result["code"] = 500
        result["msg"] = "The config has already been existing."
        return HttpResponse(json.dumps(result))

    print(os.getcwd())

    invalidte_param_result = {}
    invalidte_param_result["code"] = 500
    invalidte_param_result["msg"] = "Invalid parameter."

    if app_type == "java":
        server_name = request.GET.get('serverName')
        if not server_name:
            return HttpResponse(json.dumps(invalidte_param_result))

        config = JavaAppConfig(config_name=config_name, repo_path=repo_path, branch=branch, submodule=submodule,
                           app_type=app_type, conf_path=conf_path, server_name=server_name, version=version)
    elif app_type == "web":
        tomcat_version = request.GET.get('tomcatVersion')
        if not tomcat_version:
            return HttpResponse(json.dumps(invalidte_param_result))

        config = WebAppConfig(config_name=config_name, repo_path=repo_path, branch=branch, submodule=submodule,
                           app_type=app_type,
                           conf_path=conf_path, tomcat_version=tomcat_version, version=version)
    config.save()

    json_str = config.toJSON()

    return HttpResponse(json_str)


def list_config(request):
    app_type = request.GET.get('appType')
    check_result = checkAppType(app_type)
    if check_result:
        return check_result

    if app_type == "java":
        all_config_list = JavaAppConfig.objects.order_by('-config_name')
    elif app_type == "web":
        all_config_list = WebAppConfig.objects.order_by('-config_name')

    serialized_configs = []
    for config in all_config_list:
        serialized_configs.append(config.toJSON())
    json_str = json.dumps(serialized_configs)
    return HttpResponse(json_str)


def delete_config(request):
    app_type = request.GET.get('appType')
    check_result = checkAppType(app_type)
    if check_result:
        return check_result

    config_name = request.GET.get('configName')
    if app_type == "java":
        configs = JavaAppConfig.objects.filter(config_name=config_name)
    elif app_type == "web":
        configs = WebAppConfig.objects.filter(config_name=config_name)

    print(str(configs))
    for config in configs:
        config.delete()

    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"
    json_str = json.dumps(result)
    return HttpResponse(json_str)


def deploy(request):
    app_type = request.GET.get('appType')
    check_result = checkAppType(app_type)
    if check_result:
        return check_result

    result = {}
    config_name = request.GET.get('configName')
    if app_type == "java":
        config = None
        try:
            config = JavaAppConfig.objects.get(config_name=config_name)
        except Exception as err:
            result["code"] = 500
            result["msg"] = "The config has not been existing."

        if config:
            repoPath = config.repo_path
            branch = config.branch
            subdir = config.submodule
            appType = config.app_type
            conf = config.conf_path
            serverName = config.server_name
            version = config.version

            result = Deployer.deployAndRunJavaApp(repoPath, branch, subdir, version, appType, conf, serverName)
    elif app_type == "web":
        config = None
        try:
            config = WebAppConfig.objects.get(config_name=config_name)
        except Exception as err:
            result["code"] = 500
            result["msg"] = "The config has not been existing."

        if config:
            repoPath = config.repo_path
            branch = config.branch
            subdir = config.submodule
            appType = config.app_type
            conf = config.conf_path
            tomcat_version = config.tomcat_version
            version = config.version

            result = Deployer.deployAndRunTomcatApp(repoPath, branch, subdir, version, appType, conf, tomcat_version)

    json_str = json.dumps(result)
    return HttpResponse(json_str)


def stop(request):
    app_type = request.GET.get('appType')
    check_result = checkAppType(app_type)
    if check_result:
        return check_result

    config_name = request.GET.get('configName')
    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"
    try:
        if app_type == "java":
            config = JavaAppConfig.objects.get(config_name=config_name)
        elif app_type == "web":
            config = WebAppConfig.objects.get(config_name=config_name)

        subdir = config.submodule
        appType = config.app_type

        if app_type == "java":
            result = Deployer.stopService(subdir, appType, "")
        elif app_type == "web":
            tomcatVersion = config.tomcat_version
            result = Deployer.stopService(subdir, appType, tomcatVersion)
    except Exception as err:
        print(err)


    json_str = json.dumps(result)
    return HttpResponse(json_str)


def restart(request):
    app_type = request.GET.get('appType')
    check_result = checkAppType(app_type)
    if check_result:
        return check_result

    config_name = request.GET.get('configName')
    try:
        if app_type == "java":
            config = JavaAppConfig.objects.get(config_name=config_name)
        elif app_type == "web":
            config = WebAppConfig.objects.get(config_name=config_name)

        subdir = config.submodule
        appType = config.app_type

        Deployer.restartService(subdir, appType)
    except Exception as err:
        print(err)
    return HttpResponse("Success")
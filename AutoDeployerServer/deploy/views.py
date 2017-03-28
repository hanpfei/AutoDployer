# -*- coding: utf-8 -*-

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
        result = {}
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

config_line_template = """
<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>\n
"""

config_table_template = """
<table border="1">
<tr>
<th>%s</th>
<th>%s</th>
<th>%s</th>
<th>%s</th>
<th>%s</th>
<th>%s</th>
<th>%s</th>
</tr>
%s
</table>
"""


def list_config(request):
    all_javaapp_config_list = JavaAppConfig.objects.order_by('-config_name')
    all_webapp_config_list = WebAppConfig.objects.order_by('-config_name')

    result_str = ""
    if len(all_javaapp_config_list) > 0:
        table_lines = ""
        for config in all_javaapp_config_list:
            table_line = config_line_template % (config.config_name, config.repo_path, config.branch, config.submodule,
                                                 config.app_type, config.conf_path, config.server_name)
            table_lines = table_lines + table_line

        table = config_table_template % ("Config name", "Repo path", "Branch", "Sub module",
                                         "App tpye", "Conf path", "Server name", table_lines)
        result_str = result_str + table
        result_str = result_str + "<br /><br />"

    if len(all_webapp_config_list) > 0:
        table_lines = ""
        for config in all_webapp_config_list:
            table_line = config_line_template % (config.config_name, config.repo_path, config.branch, config.submodule,
                                                  config.app_type, config.conf_path, config.tomcat_version)
            table_lines = table_lines + table_line
        table = config_table_template % ("Config name", "Repo path", "Branch", "Sub module",
                                         "App tpye", "Conf path", "Tomcat version", table_lines)
        result_str = result_str + table

    if len(all_webapp_config_list) <= 0 and len(all_javaapp_config_list) <= 0:
        result_str = "No config now!"

    # print(result_str)
    content = '<html>' + result_str + '</html>'
    resp = HttpResponse()
    resp.write(content)
    return resp


def delete_config(request):
    config_name = request.GET.get('configName')
    configs = JavaAppConfig.objects.filter(config_name=config_name)
    if not configs:
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
    result = {}
    config_name = request.GET.get('configName')
    config = None

    nohupfile = "./nohup.out"
    nohup_size = os.path.getsize(nohupfile)

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
    else:
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

    response = HttpResponse()

    fileHandle = open(nohupfile, "r")
    fileHandle.seek(nohup_size)

    response.write('<html><head>')

    style = """
    <style>
    p{ padding:1px 0}
    /* css注释： 设置padding为上下10px */
    </style></head>
    """
    response.write(style)

    for line in fileHandle.readlines():
        response.write("%s<br/>" % (str(line)))

    response.write('</html>')
    return response


def stop(request):
    config_name = request.GET.get('configName')
    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"

    config = None
    try:
        config = JavaAppConfig.objects.get(config_name=config_name)
        if config:
            app_type = "java"
    except Exception as err:
        print(err)

    if not config:
        try:
            config = WebAppConfig.objects.get(config_name=config_name)
        except Exception as err:
            print(err)
        if config:
            app_type = "web"

    if app_type:
        subdir = config.submodule
        appType = config.app_type

        if app_type == "java":
            result = Deployer.stopService(subdir, appType, "")
        elif app_type == "web":
            tomcatVersion = config.tomcat_version
            result = Deployer.stopService(subdir, appType, tomcatVersion)

    json_str = json.dumps(result)
    return HttpResponse(json_str)


def restart(request):
    config_name = request.GET.get('configName')
    config = None
    try:
        config = JavaAppConfig.objects.get(config_name=config_name)
    except Exception as err:
        print(err)
    if not config:
        try:
            config = WebAppConfig.objects.get(config_name=config_name)
        except Exception as err:
            print(err)

    if config:
        subdir = config.submodule
        appType = config.app_type

        Deployer.restartService(subdir, appType)
    return HttpResponse("Success")
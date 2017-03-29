# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from deploy.models import JavaAppConfig
from deploy.models import WebAppConfig

import json
import os
try:
    from urllib.parse import unquote
except ImportError:
     from urlparse import unquote

import Deployer


def checkAppType(app_type):
    result = None
    if app_type != Deployer.JAVA_APP_INDENTIFIER and app_type != Deployer.WEB_APP_INDENTIFIER:
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

    if app_type == Deployer.JAVA_APP_INDENTIFIER:
        configs = JavaAppConfig.objects.filter(config_name=config_name)
    elif app_type == Deployer.WEB_APP_INDENTIFIER:
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
        javaopts = request.GET.get('javaopts')
        config.javaopts = unquote(javaopts)

        javaVersion = request.GET.get('javaVersion')
        if javaVersion:
            config.java_version = javaVersion

    elif app_type == "web":
        tomcat_version = request.GET.get('tomcatVersion')
        if not tomcat_version:
            return HttpResponse(json.dumps(invalidte_param_result))

        config = WebAppConfig(config_name=config_name, repo_path=repo_path, branch=branch, submodule=submodule,
                           app_type=app_type,
                           conf_path=conf_path, tomcat_version=tomcat_version, version=version)

        connectorPort = request.GET.get('connectorPort')
        if connectorPort:
            config.connector_port = connectorPort

        redirectPort = request.GET.get('redirectPort')
        if redirectPort:
            config.redirect_port = redirectPort

        javaVersion = request.GET.get('javaVersion')
        if javaVersion:
            config.java_version = javaVersion

    config.save()

    json_str = config.toJSON()

    return HttpResponse(json_str)

javaapp_config_line_template = """
<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>\n
"""

javaapp_config_table_template = """
<table border="1">
<tr>
<th>%s</th>
<th>%s</th>
<th>%s</th>
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

webapp_config_line_template = """
<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr>\n
"""

webapp_config_table_template = """
<table border="1">
<tr>
<th>%s</th>
<th>%s</th>
<th>%s</th>
<th>%s</th>
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
            table_line = javaapp_config_line_template % (config.config_name, config.repo_path, config.branch, config.submodule,
                                                 config.app_type, config.conf_path, config.server_name, config.version, config.javaopts,
                                                 config.java_version)
            table_lines = table_lines + table_line

        table = javaapp_config_table_template % ("Config name", "Repo path", "Branch", "Sub module",
                                         "App tpye", "Conf path", "Server name", "Version", "Java opts", "Java version", table_lines)
        result_str = result_str + table
        result_str = result_str + "<br /><br />"

    if len(all_webapp_config_list) > 0:
        table_lines = ""
        for config in all_webapp_config_list:
            table_line = webapp_config_line_template % (config.config_name, config.repo_path, config.branch, config.submodule,
                                                        config.app_type, config.conf_path, config.tomcat_version, config.version,
                                                        config.connector_port, config.redirect_port, config.java_version)
            table_lines = table_lines + table_line
        table = webapp_config_table_template % ("Config name", "Repo path", "Branch", "Sub module",
                                         "App tpye", "Conf path", "Tomcat version", "Version", "Connector port", "Redirect port",
                                                "Java version", table_lines)
        result_str = result_str + table

    if len(all_webapp_config_list) <= 0 and len(all_javaapp_config_list) <= 0:
        result_str = "No config now!"

    # print(result_str)
    content = '<html>' + result_str + '</html>'
    resp = HttpResponse()
    resp.write(content)
    return resp


def delete_config(request):
    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"

    config_name = request.GET.get('configName')
    if config_name:
        configs = JavaAppConfig.objects.filter(config_name=config_name)
        if not configs:
            configs = WebAppConfig.objects.filter(config_name=config_name)

        print(str(configs))
        for config in configs:
            config.delete()
    else:
        result["code"] = 500
        result["msg"] = "Unrecognized configName: " + str(config_name)


    json_str = json.dumps(result)
    return HttpResponse(json_str)


def deploy(request):
    result = {}
    config_name = request.GET.get('configName')

    nohupfile = "./nohup.out"
    nohup_size = 0
    if os.path.isfile(nohupfile):
        nohup_size = os.path.getsize(nohupfile)

    config, appType = getConfig(config_name)

    if not config:
        result["code"] = 500
        result["msg"] = "The config has not been existing."
        json_str = json.dumps(result)
        return HttpResponse(json_str)

    repoPath = config.repo_path
    branch = config.branch
    subdir = config.submodule
    appType = config.app_type
    conf = config.conf_path
    version = config.version
    javaVersion = config.java_version

    if appType == Deployer.JAVA_APP_INDENTIFIER:
        serverName = config.server_name
        javaopts = config.javaopts

        result = Deployer.deployAndRunJavaApp(repoPath, branch, subdir, version, appType, conf, serverName, javaopts, javaVersion)
    elif appType == Deployer.WEB_APP_INDENTIFIER:
        tomcat_version = config.tomcat_version
        connectorPort = config.connector_port
        redirectPort = config.redirect_port

        result = Deployer.deployAndRunTomcatApp(repoPath, branch, subdir, version, appType, conf, tomcat_version,
                                                connectorPort, redirectPort, javaVersion)

    response = HttpResponse()



    response.write('<html><head>')

    style = """
    <style>
    p{ padding:1px 0}
    /* css注释： 设置padding为上下10px */
    </style></head>
    """
    response.write(style)
    if os.path.isfile(nohupfile):
        print("To return result: start from " + str(nohup_size))
        fileHandle = open(nohupfile, "r")
        fileHandle.seek(nohup_size)
        for line in fileHandle.readlines():
            response.write("%s<br/>" % (str(line)))

        fileHandle.close()

    response.write('</html>')
    return response


def stop(request):
    config_name = request.GET.get('configName')
    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"

    config, appType = getConfig(config_name)

    if config:
        subdir = config.submodule
        appType = config.app_type

        if appType == Deployer.JAVA_APP_INDENTIFIER:
            result = Deployer.stopService(subdir, appType, "")
        elif appType == Deployer.WEB_APP_INDENTIFIER:
            tomcatVersion = config.tomcat_version
            result = Deployer.stopService(subdir, appType, tomcatVersion)

    json_str = json.dumps(result)
    return HttpResponse(json_str)


def restart(request):
    config_name = request.GET.get('configName')

    config, appType = getConfig(config_name)

    if config:
        subdir = config.submodule
        appType = config.app_type

        Deployer.restartService(subdir, appType)
    return HttpResponse("Success")


def getConfig(config_name):
    config = None
    appType = None
    try:
        config = JavaAppConfig.objects.get(config_name=config_name)
    except Exception as err:
        print(err)
    if config:
        appType = Deployer.JAVA_APP_INDENTIFIER
    else:
        try:
            config = WebAppConfig.objects.get(config_name=config_name)
            if config:
                appType = Deployer.WEB_APP_INDENTIFIER
        except Exception as err:
            print(err)

    return config, appType


def getlog(request):
    config_name = request.GET.get('configName')

    response = HttpResponse()
    response.write('<html><head>')

    style = """
        <style>
        p{ padding:1px 0}
        /* css注释： 设置padding为上下10px */
        </style></head>
        """
    response.write(style)

    nohupfile = "./nohup.out"
    if os.path.isfile(nohupfile):
        fileHandle = open(nohupfile, "r")

        for line in fileHandle.readlines():
            response.write("%s<br/>" % (str(line)))
        fileHandle.close()

    config, appType = getConfig(config_name)

    if config:
        subdir = config.submodule
        appType = config.app_type
        tomcat_verions = ""
        if appType == Deployer.WEB_APP_INDENTIFIER:
            tomcat_verions = config.tomcat_version
        appnohup_file_path = Deployer.getTargetExecDir(subdir, tomcat_verions, appType) + os.path.sep + "nohup.out"
        if os.path.isfile(appnohup_file_path):
            appnohup_fileHandle = open(appnohup_file_path, "r")
            for line in appnohup_fileHandle.readlines():
                response.write("%s<br/>" % (str(line)))
            appnohup_fileHandle.close()

    response.write('</html>')
    return response
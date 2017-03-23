from django.shortcuts import render
from django.http import HttpResponse

import json
import os

import Deployer

def deploy(request):
    repoPath = request.GET.get('repoPath')
    branch = request.GET.get('branch')
    subdir = request.GET.get('subdir')
    appType = request.GET.get('appType')
    version = request.GET.get('version')
    conf = request.GET.get('conf')

    if not version:
        version = ""

    serverName = request.GET.get('serverName')

    print(os.getcwd())

    result = Deployer.deployAndRun(repoPath, branch, subdir, version, appType, conf, serverName)
    json_str = json.dumps(result)
    return HttpResponse(json_str)


def stop(request):
    print("stop")
    subdir = request.GET.get('subdir')
    appType = request.GET.get('appType')
    result = Deployer.stopService(subdir, appType)
    json_str = json.dumps(result)
    return HttpResponse(json_str)


def restart(request):
    subdir = request.GET.get('subdir')
    appType = request.GET.get('appType')

    Deployer.restartService(subdir, appType)
    return HttpResponse("Success")
from django.shortcuts import render
from django.http import HttpResponse

import os

import Deployer

def deploy(request):
    repoPath = request.GET.get('repoPath')
    branch = request.GET.get('branch')
    subdir = request.GET.get('subdir')
    appType = request.GET.get('appType')
    version = request.GET.get('version')
    print(repoPath)
    print(branch)
    print(subdir)
    print(appType)
    print(str(version))
    if not version:
        version = ""

    print(os.getcwd())

    Deployer.deployAndRun(repoPath, branch, subdir, version, appType)
    return HttpResponse("Success")


def stop(request):
    print("stop")
    subdir = request.GET.get('subdir')
    appType = request.GET.get('appType')
    Deployer.stopService(subdir, appType)
    return HttpResponse("Success")


def restart(request):
    subdir = request.GET.get('subdir')
    appType = request.GET.get('appType')

    Deployer.restartService(subdir, appType)
    return HttpResponse("Success")
#!/usr/bin/python2.7

import getopt
import os
import shutil
import sys

import SourceCodeDownloader

SRC_ROOT_PATH = os.environ['HOME'] + os.path.sep + "Deployed"

ROOT_POM_FILE = "Resource/pom.xml"
JAVAAPP_ANT_CONFIG_FILE = "Resource/build-javaapp.xml"
WEBAPP_ANT_CONFIG_FILE = "Resource/build-webapp.xml"

def printUsageAndExit():
    print "Usage:"
    print sys.argv[0] + " -g [git_repo] [-b branch] [-s subdir] [-t appType] [-v version]"
    exit(1)

def constructProject(targetAppDir):
    cwd = os.getcwd()
    os.chdir(targetAppDir)
    build_command = "ant deploy"
    SourceCodeDownloader.executeCmd(build_command)
    os.chdir(cwd)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        printUsageAndExit()

    repo_path = ""
    branch = "master"
    subdir = "/"
    version = ""
    appType = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "g:b:s:v:t:");
        # check all param
        for opt, arg in opts:
            if opt == "-g":
                repo_path = arg
            elif opt == "-t":
                appType = arg
            elif opt == "-b":
                branch = arg
            elif opt == "-s":
                subdir = arg
            elif opt == "-v":
                version = arg

            else:
                print("%s  ==> %s" % (opt, arg));
    except getopt.GetoptError:
        printUsageAndExit()

    print repo_path + "(repo_path)--:--(branch)" + branch + "(branch)--:--(version)" + version + "(version)--:--(subdir)" \
          + subdir + "(subdir)--:--(appType)" + appType

    if repo_path == "" or (appType != "java" and appType != "web"):
        printUsageAndExit()

    targetDir = SourceCodeDownloader.downloadSourceCode(SRC_ROOT_PATH, repo_path, branch, version)
    shutil.copy(ROOT_POM_FILE, targetDir)

    targetAppDir = targetDir + os.path.sep + subdir;

    targetBuildXmlPath = targetAppDir + os.path.sep + "build.xml"
    print targetBuildXmlPath

    if appType == "java":
        shutil.copy(JAVAAPP_ANT_CONFIG_FILE, targetBuildXmlPath)
    elif appType == "web":
        shutil.copy(JAVAAPP_ANT_CONFIG_FILE, targetBuildXmlPath)

    constructProject(targetAppDir)
    # print "targetDir = " + targetDir
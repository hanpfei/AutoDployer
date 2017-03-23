#!/usr/bin/python2.7

import getopt
import os
import re
import shutil
import sys

import SourceCodeDownloader

DPLOY_ROOT_PATH = os.environ['HOME'] + os.path.sep + "Deployed"

ROOT_POM_FILE = "Resource/pom.xml"
JAVAAPP_ANT_CONFIG_FILE = "Resource/build-javaapp.xml"
WEBAPP_ANT_CONFIG_FILE = "Resource/build-webapp.xml"

TOMCAT_PACKAGE_PATH = "Resource/apache-tomcat-8.0.30-macos.tgz"

JAVAAPP_SCRIPT_FILE = "Resource/javaApp"

JAVA8_PATH = "/Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre"

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

def copyFiles(srcDir, dstDir):
    for dirItem in os.listdir(srcDir):
        srcPath = os.path.join(srcDir, dirItem)
        dstPath = os.path.join(dstDir, dirItem)
        print srcPath
        print dstPath

        if os.path.isfile(dstPath):
            os.remove(dstPath)
        shutil.copy(srcPath, dstPath)


def copyJavaConf(targetAppExecuteDir, conf):
    srcConfDir = targetAppExecuteDir + os.path.sep + "conf" + os.path.sep + conf
    dstConfDir = targetAppExecuteDir + os.path.sep + "conf/"

    copyFiles(srcConfDir, dstConfDir)


def copyWebConf(targetAppExecuteDir, conf):
    srcConfDir = targetAppExecuteDir + os.path.sep + "WEB-INF/classes" + os.path.sep + conf
    dstConfDir = targetAppExecuteDir + os.path.sep + "WEB-INF/classes"
    copyFiles(srcConfDir, dstConfDir)


def deployTomcat(targetAppExecuteDir, appname, ):
    global TOMCAT_PACKAGE_PATH

    tomcat_pkg_path = TOMCAT_PACKAGE_PATH
    filename = os.path.basename(tomcat_pkg_path)
    target_tomcat_dir_name = os.path.splitext(filename)[0]

    parentDir = os.path.dirname(targetAppExecuteDir)
    target_tomcat_path = parentDir + os.path.sep + target_tomcat_dir_name + "-" + appname

    uncompressedTargetDir = parentDir + os.path.sep + target_tomcat_dir_name
    if os.path.isdir(uncompressedTargetDir):
        shutil.rmtree(uncompressedTargetDir)
    if os.path.isdir(target_tomcat_path):
        shutil.rmtree(target_tomcat_path)

    uncompressedCmd = "tar xf " + TOMCAT_PACKAGE_PATH + " -C " + parentDir

    SourceCodeDownloader.executeCmd(uncompressedCmd)

    os.rename(uncompressedTargetDir, target_tomcat_path)

    return target_tomcat_path


def configTomcatApp(targetAppExecuteDir, target_tomcat_path):
    serverXmlPath = target_tomcat_path + os.path.sep + "conf/server.xml"

    connectorPort = "8080"
    redirectPort = "8443"
    docBase = targetAppExecuteDir
    sessionCookieName = os.path.basename(targetAppExecuteDir)

    connectorPortPlaceHolder = "{ConnectorPortPlaceHolder}"
    redirectPortPlaceHolder = "{RedirectPortPlaceHolder}"
    docBasePlaceHolder = "{DocBasePlaceHolder}"
    sessionCookieNamePlaceHolder = "{SessionCookieNamePlaceHolder}"

    fileHandle = open(serverXmlPath, "r")
    serverXmlPathTmp = target_tomcat_path + os.path.sep + "conf/server.xml_tmp"
    targetConfigFile = open(serverXmlPathTmp, "w")
    while 1:
        line = fileHandle.readline()

        if not line:
            break

        line = re.sub(connectorPortPlaceHolder, connectorPort, line)
        line = re.sub(redirectPortPlaceHolder, redirectPort, line)
        line = re.sub(docBasePlaceHolder, docBase, line)
        line = re.sub(sessionCookieNamePlaceHolder, sessionCookieName, line)
        targetConfigFile.write(line)

    fileHandle.close()
    targetConfigFile.close()

    os.remove(serverXmlPath)
    os.rename(serverXmlPathTmp, serverXmlPath)


def runTomcatApp(target_tomcat_path):
    global JAVA8_PATH
    os.environ["JAVA_HOME"] = JAVA8_PATH
    daemon_script_path = target_tomcat_path + os.path.sep + "bin/daemon.sh run &"

    print daemon_script_path
    os.system(daemon_script_path)
    print "After runTomcatApp"


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

    targetDir = SourceCodeDownloader.downloadSourceCode(DPLOY_ROOT_PATH, repo_path, branch, version)
    shutil.copy(ROOT_POM_FILE, targetDir)

    targetAppDir = targetDir + os.path.sep + subdir;

    targetBuildXmlPath = targetAppDir + os.path.sep + "build.xml"
    print targetBuildXmlPath

    if appType == "java":
        shutil.copy(JAVAAPP_ANT_CONFIG_FILE, targetBuildXmlPath)
    elif appType == "web":
        shutil.copy(WEBAPP_ANT_CONFIG_FILE, targetBuildXmlPath)

    os.environ["JAVA_HOME"] = ""

    constructProject(targetAppDir)

    targetAppExecuteDir = ""
    if appType == "java":
        targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir
    elif appType == "web":
        targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "webroot-" + subdir

    if os.path.isdir(targetAppExecuteDir):
        shutil.rmtree(targetAppExecuteDir)

    shutil.copytree(targetAppDir + os.path.sep + "compressed", targetAppExecuteDir)

    if appType == "java":
        copyJavaConf(targetAppExecuteDir, "conf/test")
        shutil.copy(JAVAAPP_SCRIPT_FILE, targetAppExecuteDir)
    elif appType == "web":
        copyWebConf(targetAppExecuteDir, "conf/test")
        target_tomcat_path = deployTomcat(targetAppExecuteDir, subdir)
        print target_tomcat_path

        configTomcatApp(targetAppExecuteDir, target_tomcat_path)

        runTomcatApp(target_tomcat_path)


    targetLibDir = targetAppExecuteDir + os.path.sep + "lib"
    # libs = ""
    # for dirItem in os.listdir(targetLibDir):
    #     path = os.path.join(targetLibDir, dirItem)
    #     libs = libs + path + ":"
    #
    # print libs
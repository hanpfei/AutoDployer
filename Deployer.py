#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import getopt
import os
import re
import shutil
import sys

import SourceCodeDownloader

DPLOY_ROOT_PATH = os.environ['HOME'] + os.path.sep + "Deployed"

RESOURCE_DIR_PATH = "../Resource"
JAVAAPP_ANT_CONFIG_FILE = RESOURCE_DIR_PATH + os.path.sep + "build-javaapp.xml"
WEBAPP_ANT_CONFIG_FILE = RESOURCE_DIR_PATH + os.path.sep + "build-webapp.xml"

TOMCAT7_PACKAGE_PATH = RESOURCE_DIR_PATH + os.path.sep + "apache-tomcat-7.0.70-macos.tgz"
TOMCAT8_PACKAGE_PATH = RESOURCE_DIR_PATH + os.path.sep + "apache-tomcat-8.0.30-macos.tgz"

JAVA8_PATH = "/Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre"

JAVA_APP_INDENTIFIER = "java"
WEB_APP_INDENTIFIER = "web"

def printUsageAndExit():
    print("Usage:")
    print(sys.argv[0] + " -g [git_repo] [-b branch] [-s subdir] [-t appType] [-v version]")
    exit(1)


def constructProject(targetAppDir):
    cwd = os.getcwd()
    os.chdir(targetAppDir)
    try:
        build_command = "ant deploy"
        SourceCodeDownloader.executeCmd(build_command)
    except Exception as err:
        print(err)
    os.chdir(cwd)


def copyFiles(srcDir, dstDir):
    for dirItem in os.listdir(srcDir):
        srcPath = os.path.join(srcDir, dirItem)
        dstPath = os.path.join(dstDir, dirItem)
        # print(srcPath)
        # print(dstPath)

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


def getTomcatPkgPath(tomcat_version):
    global TOMCAT7_PACKAGE_PATH
    global TOMCAT8_PACKAGE_PATH
    tomcat_version = tomcat_version.lower()
    tomcat_pkg_path = ""

    if tomcat_version == "tomcat7":
        tomcat_pkg_path =  TOMCAT7_PACKAGE_PATH
    elif tomcat_version == "tomcat8":
        tomcat_pkg_path = TOMCAT8_PACKAGE_PATH
    else:
        tomcat_pkg_path = TOMCAT7_PACKAGE_PATH

    return tomcat_pkg_path


def deployTomcat(targetAppExecuteDir, appname, tomcat_version):
    tomcat_pkg_path = getTomcatPkgPath(tomcat_version)

    filename = os.path.basename(tomcat_pkg_path)
    target_tomcat_dir_name = os.path.splitext(filename)[0]

    parentDir = os.path.dirname(targetAppExecuteDir)
    target_tomcat_path = parentDir + os.path.sep + target_tomcat_dir_name + "-" + appname

    uncompressedTargetDir = parentDir + os.path.sep + target_tomcat_dir_name
    if os.path.isdir(uncompressedTargetDir):
        shutil.rmtree(uncompressedTargetDir)
    if os.path.isdir(target_tomcat_path):
        shutil.rmtree(target_tomcat_path)

    uncompressedCmd = "tar xf " + tomcat_pkg_path + " -C " + parentDir

    SourceCodeDownloader.executeCmd(uncompressedCmd)

    os.rename(uncompressedTargetDir, target_tomcat_path)

    return target_tomcat_path


def configTomcatApp(targetAppExecuteDir, target_tomcat_path, connectorPort, redirectPort):
    serverXmlPath = target_tomcat_path + os.path.sep + "conf/server.xml"

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


def runTomcatApp(target_tomcat_path, java_version=""):
    if java_version != "":
        if java_version == "java8":
            global JAVA8_PATH
            os.environ["JAVA_HOME"] = JAVA8_PATH
    daemon_script_path = target_tomcat_path + os.path.sep + "bin/catalina.sh run &"
    daemon_script_path = "nohup " + daemon_script_path

    cwd = os.getcwd()
    os.chdir(target_tomcat_path)
    try:
        # print(daemon_script_path)
        os.system(daemon_script_path)
    except Exception as err:
        print(err)
    os.chdir(cwd)


def getTargetTomcatPath(appname, tomcat_version):
    global DPLOY_ROOT_PATH

    tomcat_pkg_path = getTomcatPkgPath(tomcat_version)


    filename = os.path.basename(tomcat_pkg_path)
    target_tomcat_dir_name = os.path.splitext(filename)[0]

    target_tomcat_path = DPLOY_ROOT_PATH + os.path.sep + target_tomcat_dir_name + "-" + appname

    return target_tomcat_path


def getProcessPid(key):
    get_pic_cmd = "ps -ef | grep " + key + " | grep -v grep | awk '{print $2}'"
    pid = SourceCodeDownloader.executeCmd(get_pic_cmd)
    pid = pid.strip()
    return pid


def savePid(pid_file_path, process_key):
    pid = getProcessPid(process_key)

    fileHandle = open(pid_file_path, "w")
    fileHandle.write(pid)
    fileHandle.close()

    return pid


def getTargetExecDir(subdir, tomcatVersion, appType):
    targetAppExecuteDir = ""
    if appType == "web":
        targetAppExecuteDir = getTargetTomcatPath(subdir, tomcatVersion)
    elif appType == "java":
        targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir
    return  targetAppExecuteDir


def deployAndRunTomcatApp(repoPath, branch, subdir, version, appType, conf, tomcatVersion, connectorPort, redirectPort, java_version=""):
    print(repoPath + "(repo_path)--:--(branch)" + branch + "(branch)--:--(version)" + version + "(version)--:--(subdir)" \
          + subdir + "(subdir)--:--(appType)" + appType + "(appType)--:--(conf)" + conf + "(conf)--:--(tomcatVersion)"
          + tomcatVersion + "(tomcatVersion)--:--(connectorPort)" + connectorPort + "(connectorPort)--:--(redirectPort)" + redirectPort)

    result = {}

    target_tomcat_path = getTargetTomcatPath(subdir, tomcatVersion)

    pid_file_path = target_tomcat_path + os.path.sep + "logs/catalina-daemon.pid"
    pid = getProcessPid(os.path.basename(target_tomcat_path))
    print(pid_file_path)
    print("pid = " + pid)
    if os.path.isfile(pid_file_path) or (pid != 0 and pid != ""):
        stopService(subdir, appType, tomcatVersion)

    targetDir = SourceCodeDownloader.downloadSourceCode(DPLOY_ROOT_PATH, repoPath, branch, version)

    targetAppDir = targetDir + os.path.sep + subdir;

    targetBuildXmlPath = targetAppDir + os.path.sep + "build.xml"
    # print(targetBuildXmlPath)

    shutil.copy(WEBAPP_ANT_CONFIG_FILE, targetBuildXmlPath)

    os.environ["JAVA_HOME"] = ""

    constructProject(targetAppDir)

    targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "webroot-" + subdir

    compressed_dir = targetAppDir + os.path.sep + "compressed"
    if not os.path.isdir(compressed_dir):
        return result

    if os.path.isdir(targetAppExecuteDir):
        shutil.rmtree(targetAppExecuteDir)

    shutil.copytree(compressed_dir, targetAppExecuteDir)

    copyWebConf(targetAppExecuteDir, conf)
    target_tomcat_path = deployTomcat(targetAppExecuteDir, subdir, tomcatVersion)
    print(target_tomcat_path)

    configTomcatApp(targetAppExecuteDir, target_tomcat_path, connectorPort, redirectPort)

    runTomcatApp(target_tomcat_path)

    pid_file_path = targetAppExecuteDir + os.path.sep + "webapp.pid"
    savePid(pid_file_path, os.path.basename(target_tomcat_path))

    result["code"] = 200
    result["msg"] = "Successfully"
    return result


def deployAndRunJavaApp(repoPath, branch, subdir, version, appType, conf, serverName, javaopts, java_version=""):
    print(repoPath + "(repo_path)--:--(branch)" + branch + "(branch)--:--(version)" + version + "(version)--:--(subdir)" \
          + subdir + "(subdir)--:--(appType)" + appType)

    if repoPath == "" or (appType != "java" and appType != "web"):
        printUsageAndExit()

    result = {}

    targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir
    pid_file_path = targetAppExecuteDir + os.path.sep + "javaapp.pid"

    pid = getProcessPid(serverName)

    if os.path.isfile(pid_file_path) or pid != 0:
        stopService(subdir, appType, "")

    # print(os.getcwd())

    targetDir = SourceCodeDownloader.downloadSourceCode(DPLOY_ROOT_PATH, repoPath, branch, version)
    if targetDir == "" or not os.path.isdir(targetDir):
        return result

    targetAppDir = targetDir + os.path.sep + subdir;

    targetBuildXmlPath = targetAppDir + os.path.sep + "build.xml"
    # print(targetBuildXmlPath)

    shutil.copy(JAVAAPP_ANT_CONFIG_FILE, targetBuildXmlPath)

    os.environ["JAVA_HOME"] = ""

    constructProject(targetAppDir)

    targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir

    compressed_dir = targetAppDir + os.path.sep + "compressed"
    if not os.path.isdir(compressed_dir):
        return result

    if os.path.isdir(targetAppExecuteDir):
        shutil.rmtree(targetAppExecuteDir)

    shutil.copytree(targetAppDir + os.path.sep + "compressed", targetAppExecuteDir)

    copyJavaConf(targetAppExecuteDir, conf)

    javapath = "java"
    if java_version != "":
        if java_version == "java8":
            global JAVA8_PATH
            os.environ["JAVA_HOME"] = JAVA8_PATH
            javapath = JAVA8_PATH + os.path.sep + "bin/java"
    javaOptsArray = javaopts.split(",")
    # print(str(javaOptsArray))
    javaopts = " ".join(javaOptsArray)
    # print(str(javaopts))
    cmd = javapath + " -Djava.library.path=lib/ -Dlog.dir=./logs -server " + javaopts \
          +" -Dcom.netease.appname=napm_" + subdir + " -classpath "

    targetLibDir = targetAppExecuteDir + os.path.sep + "lib"
    libs = ""
    for dirItem in os.listdir(targetLibDir):
        path = os.path.join(targetLibDir, dirItem)
        libs = libs + path + ":"

    cmd = cmd + libs + " " + serverName + " &"
    # print(cmd)

    cwd = os.getcwd()
    os.chdir(targetAppExecuteDir)
    try:
        cmd = "nohup " + cmd
        os.system(cmd)
    except Exception as err:
        print(err)

    os.chdir(cwd)

    pid_file_path = targetAppExecuteDir + os.path.sep + "javaapp.pid"
    pid = savePid(pid_file_path, serverName)

    result["pid"] = pid

    result["code"] = 200
    result["msg"] = "Successfully"
    return result


def getPidFormFile(appType, submodule):
    if appType == "java":
        targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + submodule
        pid_file_path = targetAppExecuteDir + os.path.sep + "javaapp.pid"
    elif appType == "web":
        targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "webroot-" + submodule
        pid_file_path = targetAppExecuteDir + os.path.sep + "webapp.pid"

    pid = 0
    if os.path.isfile(pid_file_path):
        file = open(pid_file_path)
        pid = file.readline()
        file.close()

    return pid, pid_file_path


def killProcess(appType, submodule):
    pid, pid_file_path = getPidFormFile(appType, submodule)

    if pid == 0:
        pid = getProcessPid(submodule)
        if not pid:
            pid = 0

    if pid != 0:
        kill_command = "kill -9 " + pid
        os.system(kill_command)
        if os.path.isfile(pid_file_path):
            os.remove(pid_file_path)

    return pid


def stopService(subdir, appType, tomcat_version):
    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"

    pid = killProcess(appType, subdir)
    result["pid"] = pid

    return result


def restartService(subdir, appType):
    if appType == "java":
        stopService(subdir, appType)
        targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir
    elif appType == "web":
        stopService(subdir, appType)
        target_tomcat_path = getTargetTomcatPath(subdir)
        runTomcatApp(target_tomcat_path)


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

    stopService(subdir, appType)
    # deployAndRun(repo_path, branch, subdir, version, appType)
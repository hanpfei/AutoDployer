#!/usr/bin/python2.7

import getopt
import os
import re
import shutil
import sys

import SourceCodeDownloader

DPLOY_ROOT_PATH = os.environ['HOME'] + os.path.sep + "Deployed"

ROOT_POM_FILE = "/Users/netease/Projects/MyProject/AutoDployer/Resource/pom.xml"
JAVAAPP_ANT_CONFIG_FILE = "/Users/netease/Projects/MyProject/AutoDployer/Resource/build-javaapp.xml"
WEBAPP_ANT_CONFIG_FILE = "/Users/netease/Projects/MyProject/AutoDployer/Resource/build-webapp.xml"

TOMCAT7_PACKAGE_PATH = "/Users/netease/Projects/MyProject/AutoDployer/Resource/apache-tomcat-7.0.70-macos.tgz"
TOMCAT8_PACKAGE_PATH = "/Users/netease/Projects/MyProject/AutoDployer/Resource/apache-tomcat-8.0.30-macos.tgz"

JAVAAPP_SCRIPT_FILE = "/Users/netease/Projects/MyProject/AutoDployer/Resource/javaApp"

JAVA8_PATH = "/Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre"


def printUsageAndExit():
    print("Usage:")
    print(sys.argv[0] + " -g [git_repo] [-b branch] [-s subdir] [-t appType] [-v version]")
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

    cwd = os.getcwd()
    os.chdir(target_tomcat_path)
    # print(daemon_script_path)
    os.system(daemon_script_path)
    os.chdir(cwd)

    print("After runTomcatApp")


def getTargetTomcatPath(appname, tomcat_version):
    global DPLOY_ROOT_PATH

    tomcat_pkg_path = getTomcatPkgPath(tomcat_version)


    filename = os.path.basename(tomcat_pkg_path)
    target_tomcat_dir_name = os.path.splitext(filename)[0]

    target_tomcat_path = DPLOY_ROOT_PATH + os.path.sep + target_tomcat_dir_name + "-" + appname

    return target_tomcat_path


def deployAndRunTomcatApp(repoPath, branch, subdir, version, appType, conf, tomcatVersion):
    print(repoPath + "(repo_path)--:--(branch)" + branch + "(branch)--:--(version)" + version + "(version)--:--(subdir)" \
          + subdir + "(subdir)--:--(appType)" + appType + "(appType)--:--(conf)" + conf + "(conf)--:--(tomcatVersion)" + tomcatVersion)

    result = {}

    target_tomcat_path = getTargetTomcatPath(subdir, tomcatVersion)

    pid_file_path = target_tomcat_path + os.path.sep + "logs/catalina-daemon.pid"
    if os.path.isfile(pid_file_path):
        result["code"] = 500
        result["msg"] = "The application is already running. Please stop it first."
        return result

    targetDir = SourceCodeDownloader.downloadSourceCode(DPLOY_ROOT_PATH, repoPath, branch, version)

    targetAppDir = targetDir + os.path.sep + subdir;

    targetBuildXmlPath = targetAppDir + os.path.sep + "build.xml"
    # print(targetBuildXmlPath)

    shutil.copy(WEBAPP_ANT_CONFIG_FILE, targetBuildXmlPath)

    os.environ["JAVA_HOME"] = ""

    constructProject(targetAppDir)

    targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "webroot-" + subdir

    if os.path.isdir(targetAppExecuteDir):
        shutil.rmtree(targetAppExecuteDir)

    shutil.copytree(targetAppDir + os.path.sep + "compressed", targetAppExecuteDir)

    copyWebConf(targetAppExecuteDir, conf)
    target_tomcat_path = deployTomcat(targetAppExecuteDir, subdir, tomcatVersion)
    print(target_tomcat_path)

    configTomcatApp(targetAppExecuteDir, target_tomcat_path)

    runTomcatApp(target_tomcat_path)

    result["code"] = 200
    result["msg"] = "Successfully"
    return result


def deployAndRunJavaApp(repoPath, branch, subdir, version, appType, conf, serverName):
    print(repoPath + "(repo_path)--:--(branch)" + branch + "(branch)--:--(version)" + version + "(version)--:--(subdir)" \
          + subdir + "(subdir)--:--(appType)" + appType)

    if repoPath == "" or (appType != "java" and appType != "web"):
        printUsageAndExit()

    result = {}

    targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir
    pid_file_path = targetAppExecuteDir + os.path.sep + "javaapp.pid"

    if os.path.isfile(pid_file_path):
        result["code"] = 500
        result["msg"] = "The application is already running. Please stop it first."
        return result

    # print(os.getcwd())

    targetDir = SourceCodeDownloader.downloadSourceCode(DPLOY_ROOT_PATH, repoPath, branch, version)

    targetAppDir = targetDir + os.path.sep + subdir;

    targetBuildXmlPath = targetAppDir + os.path.sep + "build.xml"
    # print(targetBuildXmlPath)

    shutil.copy(JAVAAPP_ANT_CONFIG_FILE, targetBuildXmlPath)

    os.environ["JAVA_HOME"] = ""

    constructProject(targetAppDir)

    targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir

    if os.path.isdir(targetAppExecuteDir):
        shutil.rmtree(targetAppExecuteDir)

    shutil.copytree(targetAppDir + os.path.sep + "compressed", targetAppExecuteDir)

    copyJavaConf(targetAppExecuteDir, conf)
    shutil.copy(JAVAAPP_SCRIPT_FILE, targetAppExecuteDir)

    global JAVA8_PATH
    cmd = JAVA8_PATH + os.path.sep + "bin/java" + " -Djava.library.path=lib/ -Dlog.dir=./logs -server -Xms512m -Xmx512m -XX:MaxPermSize=128m " \
                                                  "-verbose:gc -XX:+PrintGCDetails -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.ssl=false " \
                                                  "-Dcom.sun.management.jmxremote.authenticate=false -Dcom.netease.appname=napm_" + subdir + " -classpath "

    targetLibDir = targetAppExecuteDir + os.path.sep + "lib"
    libs = ""
    for dirItem in os.listdir(targetLibDir):
        path = os.path.join(targetLibDir, dirItem)
        libs = libs + path + ":"

    cmd = cmd + libs + " " + serverName + " &"
    # print(cmd)

    cwd = os.getcwd()
    os.chdir(targetAppExecuteDir)
    os.system(cmd)
    os.chdir(cwd)

    get_pic_cmd = "ps -ef | grep " + serverName + " | grep -v grep | awk '{print $2}'"
    pid = SourceCodeDownloader.executeCmd(get_pic_cmd)

    pid_file_path = targetAppExecuteDir + os.path.sep + "javaapp.pid"
    fileHandle = open(pid_file_path, "w")
    pid = pid.strip()
    fileHandle.write(pid)
    fileHandle.close()

    result["pid"] = pid

    result["code"] = 200
    result["msg"] = "Successfully"
    return result


def stopService(subdir, appType, tomcat_version):
    result = {}
    result["code"] = 200
    result["msg"] = "Successfully"

    if appType == "java":
        targetAppExecuteDir = DPLOY_ROOT_PATH + os.path.sep + "javaapp-" + subdir
        pid_file_path = targetAppExecuteDir + os.path.sep + "javaapp.pid"
        file = open(pid_file_path)
        pid = file.readline()

        kill_command = "kill -9 " + pid
        os.system(kill_command)

        result["pid"] = pid

        os.remove(pid_file_path)
    elif appType == "web":
        target_tomcat_path = getTargetTomcatPath(subdir, tomcat_version)

        pid_file_path = target_tomcat_path + os.path.sep + "logs/catalina-daemon.pid"
        if os.path.isfile(pid_file_path):
            daemon_script_path = target_tomcat_path + os.path.sep + "bin/daemon.sh stop"
            # print(daemon_script_path)
            os.system(daemon_script_path)
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
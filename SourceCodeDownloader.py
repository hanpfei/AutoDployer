# -*- coding: utf-8 -*-

import os
import re
import shutil
import subprocess

GIT_PATH = "/usr/bin/git"

def executeCmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = ""
    for line in p.stdout.readlines():
        print("  " + str(line.decode("utf-8")))
        if result == "":
            result = str(line.decode("utf-8"))
    return result

def getCurrentBranch():
    branch_cmd = GIT_PATH + " branch"
    p = subprocess.Popen(branch_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    curBranch = p.stdout.readlines()[0][1:].strip()

    return curBranch

def downloadSourceCode(target_dir, repo_path, branch, version):
    global GIT_PATH

    patternStr = ".+\/(.+)\.git"
    pattern = re.compile(patternStr)
    matcher = pattern.match(repo_path)
    if not matcher:
        print("Invalid repo path: " + str(repo_path))
        return
    repo_name = matcher.group(1)

    target_dir = target_dir + os.path.sep + repo_name
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
    clone_cmd = GIT_PATH + " clone " + repo_path + " " + target_dir
    print(str(clone_cmd))
    executeCmd(clone_cmd)

    if branch == "":
        branch = "master"

    cwd = os.getcwd()
    os.chdir(target_dir)

    curBranch = getCurrentBranch()

    if curBranch != branch:
        branch_cmd = GIT_PATH + " branch | grep " + branch
        p = subprocess.Popen(branch_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        tmpbranch = p.stdout.readlines()
        if tmpbranch:
            checkout_cmd = GIT_PATH + " checkout " + branch
        else:
            checkout_cmd = GIT_PATH + " checkout -t origin/" + branch
        print("\n" + str(checkout_cmd))
        executeCmd(checkout_cmd)
    if version:
        checkout_cmd = GIT_PATH + " checkout " + version
        print("\n" + str(checkout_cmd))
        executeCmd(checkout_cmd)

    os.chdir(cwd)
    return target_dir
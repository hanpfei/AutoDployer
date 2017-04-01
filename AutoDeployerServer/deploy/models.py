# -*- coding: utf-8 -*-

from django.db import models

from json import JSONEncoder
import json

import Deployer

JAVA7_INDENTIFIER = 'java7'
JAVA8_INDENTIFIER = 'java8'

class JavaAppConfig(models.Model):
    config_name = models.CharField(max_length=1024)
    repo_path = models.CharField(max_length=2048)
    branch = models.CharField(max_length=512, default='master')
    submodule = models.CharField(max_length=512)
    app_type = models.CharField(max_length=64)
    conf_path = models.CharField(max_length=512)
    server_name = models.CharField(max_length=1024)
    version = models.CharField(max_length=1024, default='')
    javaopts = models.CharField(max_length=2048, default='')
    java_version = models.CharField(max_length=32, default=JAVA7_INDENTIFIER)

    def toJSON(self):
        serialized_config = {}
        serialized_config["config_name"] = self.config_name
        serialized_config["repo_path"] = self.repo_path
        serialized_config["branch"] = self.branch
        serialized_config["submodule"] = self.submodule
        serialized_config["app_type"] = self.app_type
        serialized_config["conf_path"] = self.conf_path
        serialized_config["server_name"] = self.server_name
        serialized_config["version"] = self.version
        serialized_config["javaopts"] = self.javaopts
        serialized_config["java_version"] = self.java_version
        return json.dumps(serialized_config)

    def toString(self):
        str = "%-30s%-80s%-20s%-30s%-15s%-25s%-50s%-35s%-125s%-20s" % (self.config_name, self.repo_path, self.branch, self.submodule,
                                              self.app_type, self.conf_path, self.server_name, self.version, self.javaopts, self.java_version)
        return str

class WebAppConfig(models.Model):
    config_name = models.CharField(max_length=1024)
    repo_path = models.CharField(max_length=2048)
    branch = models.CharField(max_length=512, default='master')
    submodule = models.CharField(max_length=512)
    app_type = models.CharField(max_length=64)
    conf_path = models.CharField(max_length=512)
    tomcat_version = models.CharField(max_length=512, default='tomcat7')
    version = models.CharField(max_length=1024, default='')
    connector_port = models.CharField(max_length=32, default='8080')
    redirect_port = models.CharField(max_length=32, default='8443')
    java_version = models.CharField(max_length=32, default=JAVA7_INDENTIFIER)
    shutdown_port = models.CharField(max_length=32, default='8005')
    ajp_port = models.CharField(max_length=32, default='8009')

    def toJSON(self):
        serialized_config = {}
        serialized_config["config_name"] = self.config_name
        serialized_config["repo_path"] = self.repo_path
        serialized_config["branch"] = self.branch
        serialized_config["submodule"] = self.submodule
        serialized_config["app_type"] = self.app_type
        serialized_config["conf_path"] = self.conf_path
        serialized_config["tomcat_version"] = self.tomcat_version
        serialized_config["connector_port"] = self.connector_port
        serialized_config["redirect_port"] = self.redirect_port
        serialized_config["java_version"] = self.java_version
        return json.dumps(serialized_config)

    def toString(self):
        str = "%-30s%-80s%-20s%-30s%-15s%-25s%-20s%-10s%-10s%-20s" % (self.config_name, self.repo_path, self.branch, self.submodule,
                                                        self.app_type, self.conf_path, self.tomcat_version, self.connector_port,
                                                        self.redirect_port, self.java_version)
        return str
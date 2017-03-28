# -*- coding: utf-8 -*-

from django.db import models

from json import JSONEncoder
import json
# Create your models here.

class JavaAppConfig(models.Model):
    config_name = models.CharField(max_length=1024)
    repo_path = models.CharField(max_length=2048)
    branch = models.CharField(max_length=512)
    submodule = models.CharField(max_length=512)
    app_type = models.CharField(max_length=64)
    conf_path = models.CharField(max_length=512)
    server_name = models.CharField(max_length=1024)
    version = models.CharField(max_length=1024)

    def toJSON(self):
        serialized_config = {}
        serialized_config["config_name"] = self.config_name
        serialized_config["repo_path"] = self.repo_path
        serialized_config["branch"] = self.branch
        serialized_config["submodule"] = self.submodule
        serialized_config["app_type"] = self.app_type
        serialized_config["conf_path"] = self.conf_path
        serialized_config["server_name"] = self.server_name
        return json.dumps(serialized_config)

    def toString(self):
        str = "%-30s%-80s%-20s%-30s%-15s%-25s%-50s" % (self.config_name, self.repo_path, self.branch, self.submodule,
                                              self.app_type, self.conf_path, self.server_name)
        return str

class WebAppConfig(models.Model):
    config_name = models.CharField(max_length=1024)
    repo_path = models.CharField(max_length=2048)
    branch = models.CharField(max_length=512)
    submodule = models.CharField(max_length=512)
    app_type = models.CharField(max_length=64)
    conf_path = models.CharField(max_length=512)
    tomcat_version = models.CharField(max_length=512)
    version = models.CharField(max_length=1024)

    def toJSON(self):
        serialized_config = {}
        serialized_config["config_name"] = self.config_name
        serialized_config["repo_path"] = self.repo_path
        serialized_config["branch"] = self.branch
        serialized_config["submodule"] = self.submodule
        serialized_config["app_type"] = self.app_type
        serialized_config["conf_path"] = self.conf_path
        serialized_config["tomcat_version"] = self.tomcat_version
        return json.dumps(serialized_config)

    def toString(self):
        str = "%-30s%-80s%-20s%-30s%-15s%-25s%-20s" % (self.config_name, self.repo_path, self.branch, self.submodule,
                                                        self.app_type, self.conf_path, self.tomcat_version)
        return str
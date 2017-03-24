from django.db import models

from json import JSONEncoder
import json
# Create your models here.

class AppConfig(models.Model, json.JSONEncoder):

    config_name = models.CharField(max_length=1024)
    repo_path = models.CharField(max_length=2048)
    branch = models.CharField(max_length=512)
    submodule = models.CharField(max_length=512)
    app_type = models.CharField(max_length=64)
    conf_path = models.CharField(max_length=512)
    server_name = models.CharField(max_length=1024)
    version = models.CharField(max_length=1024)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
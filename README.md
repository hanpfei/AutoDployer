# 简介
AutoDployer 是一个基于 Web 的 Java/Tomcat 应用部署工具，用户可以以类似于使用 omad 的方式使用它。这个工具提供的操作大体如下：

1. 新建配置。指定配置名，repo 地址等参数，新建配置。
2. 部署配置。指定配置名，部署特定应用。
3. 删除配置。指定配置名，删除特定配置。
4. 杀掉应用进程。指定配置名，杀掉相应的应用进程。
5. 列出当前已建立的所有配置。
6. 获取日志。

下面进一步详细说明这些操作。

# 工具用法
所有接口参数，通过 URL 参数传递。

### 新建配置

在执行其它操作之前，首先要新建一个配置，对要部署的应用进行详细的描述。

接口：`createConfig`

参数：
  * `configName`：自定义的配置名称，用于标识此配置。
  * `appType`：应用的类型，对于 Tomcat 应用，传入 `web`；对于 Java 应用，传入 `java`。
  * `repoPath`：要部署的应用所在的 git repo的地址。
  * `branch`：要部署的应用所在 branch。
  * `subdir`：要部署的应用在 repo 中的子目录的名称（即模块名称）。
  * `conf`：部署时复制的配置的位置。
  * `serverName`：对于 Java 应用，必选，需要传入要运行的 Main class；对于 Tomcat 应用，无需传入。
  * `tomcatVersion`：对于 Tomcat 应用，必选，需要传入 tomcat 的版本，当前只支持 `tomcat7`；对于 Java 应用，无需传入；
  * `version`：该参数可选，当要部署 repo 的特定 revision 时指定，传入 git repo 的 commit id。
  * `connectorPort`：该参数可选。主要用于部署 Tomcat 应用，用于指定 Tomcat 监听的端口，不指定时，采用默认的 8080。
  * `redirectPort`：该参数可选。主要用于部署 Tomcat 应用，用于指定 Tomcat 的 redirect 端口，不指定时，采用默认的 8443。
  * `shutdownPort`：该参数可选。主要用于部署 Tomcat 应用，用于指定 Tomcat 的 Shutdown 服务端口，不指定时，采用默认的 8005。
  * `ajpPort`：该参数可选。主要用于部署 Tomcat 应用，用于指定 Tomcat 的 AJP 服务端口，不指定时，采用默认的 8009。
  * `javaopts`：对于 Java app 而言，该参数必选，用于指定 JVM 参数。需要传入多个参数时，各个参数以逗号分隔，参数需经过 URL Encode。

返回值：
 * 该接口会以 JSON 格式返回配置的描述。

示例：
```
http://localhost:7000/createConfig?configName=napm-collector&repoPath=ssh://git@g.hz.netease.com:22222/napm/napm-backend.git&branch=develop&subdir=napm-collector&appType=web&conf=conf/localDev&tomcatVersion=tomcat7&connectorPort=6080&redirectPort=6443&javaVersion=java7

http://localhost:7000/createConfig?configName=napm-hbase-consumer&repoPath=ssh://git@g.hz.netease.com:22222/napm/napm-backend.git&branch=develop&subdir=napm-hbase-consumer&conf=conf/test&serverName=com.netease.napm.consumer.hbase.NapmHbaseConsumer&appType=java&javaopts=-Xms512m%2c-Xmx512m%2c-XX%3aMaxPermSize%3d128m%2c-verbose%3agc%2c-XX%3a%2bPrintGCDetails%2c-Dcom.sun.management.jmxremote%2c-Dcom.sun.management.jmxremote.ssl%3dfalse%2c-Dcom.sun.management.jmxremote.authenticate%3dfalse
```

### 部署配置

创建配置之后，可以部署配置。如果要部署的应用当前已经处于运行状态，则该接口将先杀死正在运行的应用进程，然后部署。

接口：`deploy`

参数：
  * `configName`：用于标识配置的自定义配置名称。

返回值：
 * 该接口以 JSON 。

示例：
```
http://apm0:7000/deploy/?configName=napm-collector
```

该接口执行的时间可能比较长。

### 删除配置

创建配置之后，可以删除配置。

接口：`deleteConfig`

参数：
  * `configName`：用于标识配置的自定义配置名称。

返回值：
 * 该接口将以 JSON 格式返回操作执行的结果。

示例：
```
http://apm0:7000/deleteConfig?onfigName=napm-collector
```

### 杀掉应用进程

创建配置之后，可以杀掉对应的应用进程。如果当前相应的应用进程正在运行，则进程会把杀掉；如果没有在运行，则不做任何操作并退出。

接口：`stop`

参数：
  * `configName`：用于标识配置的自定义配置名称。

返回值：
 * 该接口将以 JSON 格式返回操作执行的结果。

示例：
```
http://apm0:7000/stop/?configName=napm-collector
```

### 列出当前已建立的所有配置

该接口可以在任何时候调用，以查看当前已创建的配置列表。它将通过两个表格，分别返回 Java App 配置和 Tomcat App 配置的列表。

接口：`listConfig`

参数：
  * 接口无需传入任何参数。

返回值：
 * 它将通过两个表格，分别返回 Java App 配置和 Tomcat App 配置的列表。

示例：
```
http://apm0:7000/listConfig
```

### 获取日志

该接口可以在任何时候调用，以查看工具的 Web 服务器输出的日志和应用部署过程中输出的日志。

接口：`getlog`

参数：
  * `configName`：可选的参数，用于标识配置的自定义配置名称。当不传参数时，返回Web 服务器输出的日志；而当带有该参数时，则将同时返回最近一次部署过程中，应用部署时产生的日志。

返回值：
 * 返回日志

示例：
```
http://apm0:7000/getlog/?configName=napm-collector

http://apm0:7000/getlog
```

＃ 工具的部署

工具基于 Python Django Web 框架开发，配置信息存于 MySQL 数据库，而在构建过程中需要用到 Ant、Maven 等工具。因而在部署之前，首先要先安装相应的依赖。依赖安装完成之后，使用 Django 项目中自带的测试用 Python Web Server 运行服务。

### 依赖
 * Java：Java 7 及以上。

 * Ant：若 Java 版本为 Java 8，可以使用较新的 `apache-ant-1.10.1`；若 Java 版本为 Java 7，则需要使用稍老的 `apache-ant-1.9.9`。[Ant 下载地址](http://ant.apache.org/bindownload.cgi)。`bin` 目录需要被加入 `PATH` 环境变量中。

 * Maven：`apache-maven-3.3.9` 测试可用。[Maven 下载地址](https://maven.apache.org/download.cgi)。`bin` 目录需要被加入 `PATH` 环境变量中。

 * Python：Python-2.7 和 Python 3 均可。

 * Django：开发基于 django-1.9.12 进行，其它版本暂未进行过测试。可在 Django 项目的 [GitHub 主页](https://github.com/django/django) 下载最新版本代码或特定的发行版，并参考 [Mac 搭建 Django 开发环境](https://cnbin.github.io/blog/2015/05/29/mac-da-jian-djangokai-fa-huan-jing/) 一文在 Mac OS 上安装 Django。

 * MySQL：需要安装 MySQL 和 MySQL 客户端的 Python binding。可通过如下命令安装 MySQL：
```
apm3:AutoDeployerServer apm$ brew install mysql
```
对于 Python 3，可通过 pip 安装 mysql-client；对于 Python 2.7，则安装 `MySQL-python`。
未安装 `pip` 的需要先通过如下命令安装 `pip`：
```
apm2:AutoDployer apm$ sudo easy_install pip
```
对于 Python 3，通过如下命令安装 `mysqlclient`：
```
NetEasedeiMac-8:AutoDployer netease$ sudo pip install mysqlclient
```
对于 Python 2.7，通过如下命令安装 `MySQL-python`：
```
apm2:AutoDployer apm$ sudo pip install MySQL-Python
```

### 工具部署
从repo 中下载代码（在 `~/tools/` 目录下执行）：
```
apm3:tools apm$ git clone ssh://git@g.hz.netease.com:22222/napm/AutoDployer.git
apm3:tools apm$ cd AutoDployer/
```
将路径 `~/tools/AutoDployer/`添加进 `PYTHONPATH` 环境变量：
```
export PYTHONPATH=$PYTHONPYTH:/Users/apm/tools/AutoDployer
```

然后执行如下命令运行工具：
```
apm3:AutoDeployerServer apm$ nohup python manage.py runserver 0.0.0.0:7000 &
```

### MySQL 配置

所采用的 MySQL 配置如下：
```
Database: autodeploy
Username: root
Password: 123456
MySql Server Host: apm2
Port: 3306

Java App Table: deploy_javaappconfig
Tomcat App Table: deploy_webappconfig
```
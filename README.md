> 本项目基于docker-compose单机部署，每个宿主机上都必须包含整套服务。

1. 原则上来说，正式服务器应该运行代码的master分支最新代码，测试用服务器则不受限制（develop分支或任意预发布版本）
1. 本文发布时，测试用服务器为http://192.168.30.109/ 该宿主机已经安装gitlab-runner，项目根目录下配置了一个最简单的.gitlab-ci.yml，该配置文件可以在develop分支有合并或修改的时候自动运行配置好的脚本。关于gitlab持续集成部分的配置方法参考 http://git.xiaoneng.cn/devops/oa_backend/settings/ci_cd
1. 关于整个后端django项目使用的settings文件。一个重要且容易忽略的点是，django在加载的时候会读取当前系统的环境变量oa_env，该环境变量决定了读取的配置文件是哪个，如oa_env=production 则从production_settings载入相关变量。请参考相关代码：
    ```python
    # libs.environment.py
    class ENV(object):
    def __init__(self):
        env = os.environ.get("oa_env", "local")
        # 如果没有读取到oa_env的值(没有配置)则读取local_settings
        file_name = env + "_settings"
        base_settings = __import__("ldap_server", fromlist=[file_name])
        self.settings = getattr(base_settings, file_name)

    def get_config(self, value):
        return getattr(self.settings, value)
    ```
1. 关于配置项的解释
    ```python
    # 线上域名
    BASE_URL = "http://oa-server.ntalker.com"
    # 重要！项目唯一secret-key
    SECRET_KEY = "t8w!2mju@sd9_)*xh*cp7$f-mdpymmr=l!oa0u_nb9l*s)eh!7"
    # 是否开启DEBUG模式
    DEBUG = False

    # DB Config 数据库相关配置
    DB_HOST = "192.168.30.139"
    DB_NAME = "oa_platform"
    DB_PASSWORD = "qwe123!@#"
    DB_PORT = 3306
    DB_USER = "root"

    # ldap_server 登录用相关ldap_server配置
    LDAP_SERVER_URL = "ldap://ldap.xiaoneng.cn"

    # Redis Config redis相关配置（主要用作celery broker）
    REDIS_DBNUM = 3
    REDIS_PASSWORD = 111111
    REDIS_PORT = 10009
    REDIS_SERVER = "dev-in.ntalker.com"
    ```
1. 关于Docker（该部分与前端类似，不再重复，可查看oa_frontend项目中Dockerfile具体实现）
    1. 生成base镜像。后端项目继承自该基础镜像，基础镜像的实现代码如下（BaseDockerfile）：
        ```dockerfile
        FROM reg.xiaoneng.cn/oa/python:alpine3.6.3
        MAINTAINER itsneo1990 <itsneo1990@gmail.com>
        WORKDIR /src
        COPY . .
        RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
            && apk add --update --no-cache build-base jpeg-dev zlib-dev freetype-dev openldap-dev \
            && pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
            && rm -rf celerybeat.pid /var/cache/apk/* /tmp/*
        ```
        大体逻辑：
        * 镜像基于alpine版python3.6版本，可从docker-hub获取
        * 项目目录为根目录下src
        * 安装必须的linux包（主要是Pillow需要），build-base jpeg-dev zlib-dev freetype-dev openldap-dev
        * 根据项目中requirements.txt文件安装django等python依赖
        * 删除一些不必须的缓存文件等
    
        生成base镜像的操作步骤：
        ```bash
        # 进入项目目录
        cd ~/oa_backend
        # 生成镜像
        docker build -t reg-bj.xiaoneng.cn/oa/backend_base -f BaseDockerfile .
        # 推送镜像
        docker push reg-bj.xiaoneng.cn/oa/backend_base
        ```
    2. 生成真正的项目镜像，理论上来讲正式服务器的tag应该是master, 测试用服务器为其他tag，这里以develop举例
        ```bash
        # 进入项目目录
        cd ~/oa_backend
        # 生成镜像
        docker build -t reg-bj.xiaoneng.cn/oa/backend:develop .
        # 推送镜像
        docker push reg-bj.xiaoneng.cn/oa/backend:develop
        ```
    3. 此时只需到对应的宿主机上重启docker-compose服务即可
        * `docker-compose pull && docker-compose down && docker-compose up -d`
        * 192.168.30.109上docker-compose文件路径在`/home/gitlab-runner`
1. 关于一些自定义脚本
    1. `python manage.py oa_migrate xxx` -> 旧oa迁移。
    1. `python manage.py server_group_fix_1130` -> 同步站点的服务组信息。（oa_migrate运行完之后需要运行。TODO: 将该部分内容整合入oa_migrate）
    1. 关于报表同步的脚本任务都在`applications/data_manage/task.py`文件中，如需手动运行，只需在服务运行的容器中运行`python manage.py shell`然后手动执行相关函数即可。
    1. 如需要手动获取某时间段内的咨询量信息
        ```bash
        python manage.py shell
        ```
        ```python
        from applications.data_manage.task import *
        from libs.datatimes import str_to_date
        manager = InquiresFetcherManager()
        manager.fetch_history(
            from_date=str_to_date('2017-12-01'),
            to_date=str_to_date('2017-12-31')
        )
        ```
    1. celery的定时任务在django后台admin中配置。
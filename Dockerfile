FROM reg.xiaoneng.cn/oa/backend_base:latest

WORKDIR /src
COPY . .

ENV TZ "Asia/Shanghai"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY localtime /etc/localtime
CMD ["gunicorn", "ldap_server.wsgi", "--workers=5", "--bind=0.0.0.0:8000", "--reload"]

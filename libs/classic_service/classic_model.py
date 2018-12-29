"""
本文件是和第三方数据库交互
"""
import time
from django.conf import settings
from libs.classic_service.mysqldbhelper import MysqldbHelper
from ldap_server.database_connect import CUSTORM_DATABASE,CUSTORM_HOST,CUSTORM_PASSWORD,CUSTORM_PORT,CUSTORM_USER
from libs.classic_service.basehelp import checkversion
"""
经典版基础类
"""

class KfModel:
    def __init__(self, dbcon):
        self.dbcon = dbcon

    # 修改企业信息表t2d_enterpriseinfo
    def modify_t2d_enterpriseinfo(self, **kwargs):
        siteid = kwargs.get('siteid', '')
        name = kwargs.get('name', '')
        deadline = kwargs.get('deadline', '')
        online_time_trial = kwargs.get('online_time_trial', '')
        online_status = kwargs.get('online_status', 1)
        version_id = kwargs.get('version_id', 'grid')
        classifyid = kwargs.get('classifyId', 0)
        createtime = kwargs.get('createtime', int(time.time()))
        level = kwargs.get('level', 1)
        kfsum = kwargs.get('kfsum', 100)
        smarteye = kwargs.get('smarteye', 1)
        captureimage = kwargs.get('captureimage', 1)
        mode = kwargs.get('mode', 'official')
        sql = f'select * from t2d_enterpriseinfo where siteid="{siteid}"'
        if self.dbcon.select(sql):
            sql = f'update t2d_enterpriseinfo set ' \
                  f'deadline="{deadline}",online_time_trial="{online_time_trial}",online_status={online_status},mode="{mode}",version_id="{version_id}",classifyid={classifyid},createtime="{createtime}",name="{name}",level={level},kfsum={kfsum},smarteye={smarteye},captureimage={captureimage} '\
                  f'where siteid="{siteid}"'
        else:
            sql = f'insert into t2d_enterpriseinfo' \
                  f'(siteid,deadline,online_time_trial,online_status,mode,version_id,classifyid,createtime,name,level,kfsum,smarteye,captureimage) values ' \
                  f'("{siteid}","{deadline}","{online_time_trial}",{online_status},"{mode}","{version_id}",{classifyid},{createtime},"{name}",{level},{kfsum},{smarteye},{captureimage})'
        return self.dbcon.add_up_de(sql)

    # 修改企业信息表t2d_user
    def modify_t2d_user(self, **kwargs):
        name = kwargs.get('name', '')
        nickname = kwargs.get('nickname', '')
        externalname = kwargs.get('externalname', '')
        active = kwargs.get('active', 1)
        siteid = kwargs['siteid'] if kwargs['siteid'] else ''
        createtime = kwargs.get('createtime', int(time.time()))
        userid = kwargs.get('userid', '')
        password = kwargs.get('password', '')
        role = kwargs.get('role', 'admin')
        gid = kwargs.get('gid', '')
        if name or siteid or userid or gid:
            sql = f'insert into t2d_user(name,nickname,externalname,active,password,siteid,createtime,userid,role,gid) values \
                                                ("{name}","{nickname}","{externalname}",{active},"{password}","{siteid}",{createtime},"{userid}","{role}",{gid})'
            return self.dbcon.add_up_de(sql)
        else:
            return False

    #修改账号禁用
    def active_t2d_user(self,**kwargs):
        siteid = kwargs.get('siteid','')
        active = kwargs.get('active', '')
        is_son = kwargs.get('is_son', '')
        if siteid and is_son == '':
            sql = f'update t2d_user set active={active} where siteid="{siteid}"'
            return self.dbcon.add_up_de(sql)
        elif siteid and is_son:
            sql = f'update t2d_user set active={active} where siteid like "{siteid}%"'
            return self.dbcon.add_up_de(sql)
        else:
            return False
    # 修改服务表t_wdk_sit
    def modify_t_wdk_sit(self, siteid, data):
        fides = val = ''
        for k in data:
            fides = fides + ',' + str(k['server_grp__ser_address__server__ser_id'])
            val = val + ',"' + str(k['server_grp__ser_address__ser_address']) + '"'
        sql = 'INSERT INTO t_wdk_sit(sitid%s) VALUES("%s"%s)' % (fides, siteid, val)
        return self.dbcon.add_up_de(sql)

    # 修改行政组表t2d_group
    def modify_t2d_group(self, siteid):
        groupname = "小能技术支持(勿删)"
        sql = f'insert into t2d_group(siteid,groupname) values ("{siteid}","{groupname}")'
        return self.dbcon.add_up_de(sql)

    # 修改t2d_syssetting表信息
    def modify_t2d_syssetting(self, **kwargs):
        siteid = kwargs.get('siteid', '')
        settingid = kwargs.get('settingid', '')
        settingname = kwargs.get('settingname', '')
        createtime = kwargs.get('createtime', int(time.time()))
        autoinvite = kwargs.get('autoinvite', 0)
        invitecontent = kwargs.get('invitecontent', '尊敬的客户您好，欢迎光临本公司网站！我是今天的在线值班客服，点击“开始交谈”即可与我对话。')
        invitetitle = kwargs.get('invitetitle', '在线客服')
        invitedelay = kwargs.get('invitedelay', 15000)
        mode = kwargs.get('mode', 'embed')
        sql = f'insert into t2d_syssetting(id,name,siteid,createtime,autoinvite,invitedelay,invitetitle,invitecontent,mode) values ("{settingid}","{settingname}","{siteid}",{createtime},{autoinvite},{invitedelay},"{invitetitle}","{invitecontent}","{mode}")'
        return self.dbcon.add_up_de(sql)

    # 修改t2d_syssetting_mode表信息
    def modify_t2d_syssetting_mode(self, **kwargs):
        siteid = kwargs.get('siteid', '')
        modeid = kwargs.get('modeid', '')
        settingid = kwargs.get('settingid', '')
        mode = kwargs.get('mode', '')
        enabled = kwargs.get('enabled', 1)
        sql = f'insert into t2d_syssetting_mode(modeid,settingid,mode,siteid,enabled) values ("{modeid}","{settingid}","{mode}","{siteid}",{enabled})'
        return self.dbcon.add_up_de(sql)

    # 修改t2d_chosenuser表信息
    def modify_t2d_chosenuser(self, **kwargs):
        siteid = kwargs.get('siteid', '')
        iconid = kwargs.get('iconid', '')
        groupid = kwargs.get('groupid', '')
        settingid = kwargs.get('settingid', '')
        sql = f'insert into t2d_chosenuser(settingid,modeid,userid,username,groupid,siteid) select "{settingid}","{iconid}",userid,externalname,"{groupid}",siteid from t2d_user where siteid="{siteid}"'
        return self.dbcon.add_up_de(sql)

    # 修改t2d_site_classify表信息
    def modify_t2d_site_classify(self, siteid):
        sql = f'insert into t2d_site_classify(name,platformId) values ("商户","{siteid}")'
        print(sql)
        return self.dbcon.add_up_de(sql)

    # 修改t2d_platform_level表信息
    def modify_t2d_platform_level(self, **kwargs):
        siteid = kwargs.get('siteid', '')
        kfsum = kwargs.get('kfsum', 100)
        level = kwargs.get('level', 1)
        sql = f'insert into t2d_platform_level(level,kfsum,platformId) values ({level},{kfsum},"{siteid}")'
        return self.dbcon.add_up_de(sql)

    # 获取t2d_enterpriseinfo表信息
    def get_t2d_enterpriseinfo(self, siteid):
        sql = f'select * from t2d_enterpriseinfo where siteid="{siteid}"'
        return self.dbcon.select(sql)

    # 获取服务表t_wdk_sit
    def get_t_wdk_sit(self, siteid):
        sql = f'select * from t_wdk_sit where sitid="{siteid}"'
        return self.dbcon.select(sql)

    # 获取t2d_group表信息
    def get_t2d_group(self, siteid):
        groupname = "小能技术支持(勿删)"
        sql = f'select id,groupname from t2d_group where siteid="{siteid}" and groupname="{groupname}"'
        return self.dbcon.select(sql)

    # 获取t2d_syssetting表信息（接待组表）
    def get_t2d_syssetting(self, siteid, mode):
        sql = f'select * from t2d_syssetting where siteid="{siteid}" and mode="{mode}"'
        return self.dbcon.select(sql)

    # 获取t2d_syssetting_mode表信息
    def get_t2d_syssetting_mode(self, siteid, mode):
        sql = f'select * from t2d_syssetting_mode where siteid="{siteid}" and mode="{mode}"'
        return self.dbcon.select(sql)

    # 获取t2d_chosenuser表信息
    def get_t2d_chosenuser(self, siteid):
        sql = f'select * from t2d_chosenuser where siteid="{siteid}"'
        return self.dbcon.select(sql)

    # 获取t2d_chosenuser表信息
    def get_t2d_site_classify(self, siteid):
        sql = f'select * from t2d_site_classify where platformId="{siteid}"'
        print(sql)
        return self.dbcon.select(sql)

    #获取企业对应微信公众号列表
    def get_weixin_list(self):
        sql = "select a.siteid as '企业ID',a.name as '企业名称',c.name as '微信公众号',openid from agent_weixin c ,agent_enterprise b,t2d_enterpriseinfo a where openid=v_openid and a.siteid=b.siteid"
        return self.dbcon.select(sql)

    #获取机器人基本信息列表
    def get_robot_list(self):
        sql = "SELECT a.siteid,a.`name`,b.robotversionid,b.servergroup from t2d_enterpriseinfo as a left JOIN t2d_robot_config as b on a.siteid=b.siteid where a.coop=9 and a.robot=2"
        return self.dbcon.select(sql)

    # 获取系统账号t2d_user表信息
    def get_t2d_user(self,name):
        sql = f'select `password` from t2d_user where userid like "%{name}" limit 1'
        return self.dbcon.select(sql)

    #获取b2b企业下属子商户列表
    def get_b2bsiteid_list(self,siteid):
        if checkversion(siteid) == 'b2b':
            siteid_prefix = str(siteid.split('_')[0]) + '_%'
            sql = f'select `password` from t2d_enterpriseinfo where siteid like "%{siteid_prefix}"'
            return self.dbcon.select(sql)



"""
经典版开站letao库相关表信息推送
"""


class LetaoModel:
    def __init__(self, dbcon):
        self.dbcon = dbcon

    # 获取t2d_site表信息
    def get_t2d_site(self, siteid):
        sql = f'select * from t2d_site where website="{siteid}"'
        return self.dbcon.select(sql)

    # 修改t2d_site表信息
    def modify_t2d_site(self, siteid):
        sql = f'insert into t2d_site(website,region_code) values ("{siteid}",(SELECT site.region_code FROM t2d_site as site GROUP BY site.region_code ORDER BY count(site.region_code) asc LIMIT 1))'
        return self.dbcon.add_up_de_commit(sql)

    #根据企业id获取region_code
    def get_region_code(self,siteid):
        sql = f'SELECT region_code from t2d_site where website="{siteid}" limit 1'
        return self.dbcon.select(sql)

    def modify_keypage_hits(self,**kwargs):
        clientid = kwargs.get('clientid','')
        siteid = kwargs.get('siteid','')
        price = kwargs.get('price','')
        date = kwargs.get('date','')
        userid = kwargs.get('userid','')
        ordernum = kwargs.get('ordernum','')
        sql = f'insert into t2d_{clientid}_keypage_hits(orderprice,sessid,time,website,clientid,uid,orderid,keypageid) values' \
              f'("{price}",unix_timestamp(),unix_timestamp(\'{date}\'),"{siteid}","{clientid}","{userid}","{ordernum}",2)'
        return self.dbcon.add_up_de_commit(sql)



"""
经典版开站阿里库相关表信息推送
"""


class AliModel:
    def __init__(self):
        self.dbcon = MysqldbHelper(CUSTORM_HOST, CUSTORM_USER, CUSTORM_PASSWORD, CUSTORM_DATABASE, CUSTORM_PORT)

    # 修改t2d_route_url表信息
    def modify_t2d_route_url(self, **kwargs):
        siteid = kwargs.get('siteid', '')
        scripturl = kwargs.get('scripturl', '')
        downturl = kwargs.get('downturl', '')
        updateurl = kwargs.get('updateurl', '')
        authorization_id = kwargs.get('authorization_id', '')
        apiurl = kwargs.get('apiurl', '')
        sql = f'insert into t2d_route_url(siteid,scripturl,downturl,updateurl,authorization_id,apiurl) values \
                        ("{siteid}","{scripturl}","{downturl}","{updateurl}","{authorization_id}","{apiurl}")'
        self.dbcon.add_up_de_commit(sql)

    # 根据企业id获取路由信息
    def get_siteid_routing(self, siteid):
        sql = f'select * from t2d_route_url where siteid="{siteid}"'
        data = self.dbcon.select(sql)
        return data

    # 根据路由url区分在哪个grid环境（截取域名前缀）
    def get_url_gridname(self, url):
        gridname = url[url.index('://') + 3:url.index('.ntalker')]
        return gridname

    def get_siteid_routing_list(self,siteids):
        sql = f'select * from t2d_route_url where siteid in ({siteids})'
        data = self.dbcon.select(sql)
        return data


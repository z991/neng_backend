from libs.classic_service.configjs import Configjs
from libs.classic_service.functionset import Functionset
from libs.classic_service.basehelp import *
from libs.classic_service.classic_model import *


# 创建和修改站点逻辑
def push_siteid_logic(kf_dbcon, letao_dbcon, **kwargs):
    try:
        # 企业id
        siteid = kwargs.get('siteid', '')
        # 开站时间戳
        createtime = kwargs.get('createtime', int(time.time()))
        # 站点到期时间戳
        deadline = kwargs.get('deadline', '')
        # 站点开通时间戳
        online_time_trial = kwargs.get('online_time_trial', '')
        # 企业名称
        name = kwargs.get('name', '')
        # 版本id
        version_id = kwargs.get('version_id', 'grid')
        # 企业默认用户名称
        accountconf_username = kwargs.get('accountconf_username', '')
        # 企业默认用户自定义密码
        accountconf_pwd = kwargs.get('accountconf_pwd', '')
        # 系统用户统一密码 ralf
        passIndex_ralf = kwargs.get('passIndex_ralf', '')
        # 系统用户统一密码 ntalker_lizhipeng
        passIndex_ntalker_lizhipeng = kwargs.get('passIndex_ntalker_lizhipeng', '')
        # 系统用户统一密码 ntalker_steven
        passIndex_ntalker_steven = kwargs.get('passIndex_ntalker_steven', '')
        # 系统用户统一密码 ntalker_maliqun
        passIndex_ntalker_maliqun = kwargs.get('passIndex_ntalker_maliqun', '')
        # 路由host
        host = kwargs.get('host', '')
        # 功能开关list
        func_lists = kwargs.get('func_lists', [])
        # 服务列表
        fuwu_lists = kwargs.get('fuwu_lists', [])
        # 接待组信息
        t = time.time()
        rand = int(round(t * 1000))
        rand1 = int(round(t * 1000)) + 1
        rand2 = int(round(t * 1000)) + 2
        settingid = siteid + '_' + str(rand)
        settingid2 = siteid + '_' + str(rand1)
        settingid3 = siteid + '_' + str(rand2)
        iconid = settingid + '_icon'
        listid = settingid + '_list'
        toolbarid = settingid + '_toolbar'
        iconid2 = settingid2 + '_icon'
        listid2 = settingid2 + '_list'
        toolbarid2 = settingid2 + '_toolbar'
        iconid3 = settingid3 + '_icon'
        listid3 = settingid3 + '_list'
        toolbarid3 = settingid3 + '_toolbar'
        groupid = siteid + '_ISME9754_GT2D_embed_' + iconid
        groupid2 = siteid + '_ISME9754_GT2D_embed_' + iconid2
        groupid3 = siteid + '_ISME9754_GT2D_embed_' + iconid3
        settingname = '默认代码'
        settingname2 = '正式代码'
        settingname3 = '小能技术支持(勿删)'
        # 系统自定义账号
        userid = siteid + '_ISME9754_T2D_' + str(accountconf_username)
        # 开站初始内置账号
        userid_kefu01 = siteid + '_ISME9754_T2D_kefu01'
        userid_kefu02 = siteid + '_ISME9754_T2D_kefu02'
        userid_kefu03 = siteid + '_ISME9754_T2D_kefu03'
        # 系统用户
        userid_ntalker_steven = siteid + '_ISME9754_T2D_ntalker_steven'
        userid_ntalker_maliqun = siteid + '_ISME9754_T2D_ntalker_maliqun'
        userid_ntalker_lizhipeng = siteid + '_ISME9754_T2D_ntalker_lizhipeng'
        userid_ralf = siteid + '_ISME9754_T2D_ralf'
        # 路由信息
        scripturl = 'http://%s/js/xn6/' % (host)
        downturl = 'http://%s/downt/t2d/' % (host)
        updateurl = 'http://%s/downt/update/' % (host)
        apiurl = 'http://%s/api/' % (host)
        # 查询企业id是否存在
        enterpriseinfo_data = KfModel(kf_dbcon).get_t2d_enterpriseinfo(siteid)
        # 查询企业id版本
        version = checkversion(siteid)
        if enterpriseinfo_data:
            # 开启禁用的账号
            if version == 'b2b':
                KfModel(kf_dbcon).modify_t2d_enterpriseinfo(siteid=siteid, deadline=deadline,
                                                            online_time_trial=online_time_trial, createtime=createtime,
                                                            name=name, version_id=version_id)
                KfModel(kf_dbcon).active_t2d_user(siteid=siteid, active=1, is_son=True)
            elif version == 'b2c':
                KfModel(kf_dbcon).modify_t2d_enterpriseinfo(siteid=siteid, deadline=deadline,
                                                            online_time_trial=online_time_trial,
                                                            createtime=createtime, name=name, version_id=version_id)
                KfModel(kf_dbcon).active_t2d_user(siteid=siteid, active=1)
            else:
                # 商户组id
                KfModel(kf_dbcon).modify_t2d_enterpriseinfo(siteid=siteid, deadline=deadline,
                                                            online_time_trial=online_time_trial,
                                                            createtime=createtime, name=name, version_id=version_id)
                KfModel(kf_dbcon).active_t2d_user(siteid=siteid, active=1)
            # 功能开关
            functionset = Functionset(kf_dbcon, siteid, 0)
            func_error = ''
            for v in func_lists:
                func_code = str(v['func_list__function__func_code'])
                func_val = str(v['func_list__select_value'])
                is_func = hasattr(functionset, func_code)
                if is_func == False:
                    func_error = func_error + func_code + '开通方法不存在,'
                else:
                    func = functionset.__getattribute__(func_code)
                    if func_code == str('xbot'):
                        func_data = func(func_val, host)
                    else:
                        func_data = func(func_val)
                    if func_data == False:
                        func_error = func_error + func_code + '开通失败,'
            if func_error:
                return {'status': False, 'error': func_error}
        else:
            if version == 'b2b':
                KfModel(kf_dbcon).modify_t2d_enterpriseinfo(siteid=siteid, deadline=deadline,
                                                            online_time_trial=online_time_trial, createtime=createtime,
                                                            name=name, version_id=version_id)
                KfModel(kf_dbcon).modify_t2d_site_classify(siteid)
                KfModel(kf_dbcon).modify_t2d_platform_level(siteid=siteid)
            elif version == 'b2c':
                KfModel(kf_dbcon).modify_t2d_enterpriseinfo(siteid=siteid, deadline=deadline,
                                                            online_time_trial=online_time_trial,
                                                            createtime=createtime, name=name, version_id=version_id)
            else:
                # 商户组id
                classifyId = KfModel(kf_dbcon).get_t2d_site_classify(str(siteid.split('_')[0]) + '_'+'1000')[0]['id']
                KfModel(kf_dbcon).modify_t2d_enterpriseinfo(siteid=siteid, deadline=deadline,
                                                            online_time_trial=online_time_trial,
                                                            createtime=createtime, name=name, version_id=version_id,
                                                            classifyId=classifyId)

            # 行政组
            KfModel(kf_dbcon).modify_t2d_group(siteid)
            # 用户表逻辑
            group_data = KfModel(kf_dbcon).get_t2d_group(siteid)
            # 行政组id
            gid = group_data[0]['id']
            KfModel(kf_dbcon).modify_t2d_user(name=accountconf_username, nickname='admin', externalname='admin',
                                              password=accountconf_pwd, siteid=siteid, userid=userid, gid=gid)
            KfModel(kf_dbcon).modify_t2d_user(name='kefu01', nickname='kefu01', externalname='kefu01',
                                              password=accountconf_pwd,
                                              siteid=siteid, userid=userid_kefu01, gid=gid)
            KfModel(kf_dbcon).modify_t2d_user(name='kefu02', nickname='kefu02', externalname='kefu02',
                                              password=accountconf_pwd,
                                              siteid=siteid, userid=userid_kefu02, gid=gid)
            KfModel(kf_dbcon).modify_t2d_user(name='kefu03', nickname='kefu03', externalname='kefu03',
                                              password=accountconf_pwd,
                                              siteid=siteid, userid=userid_kefu03, gid=gid)
            KfModel(kf_dbcon).modify_t2d_user(name='ntalker_steven', nickname='ntalker_steven',
                                              externalname='ntalker_steven',
                                              password=passIndex_ntalker_steven, siteid=siteid,
                                              userid=userid_ntalker_steven,
                                              gid=gid)
            KfModel(kf_dbcon).modify_t2d_user(name='ntalker_maliqun', nickname='ntalker_maliqun',
                                              externalname='ntalker_maliqun', password=passIndex_ntalker_maliqun,
                                              siteid=siteid,
                                              userid=userid_ntalker_maliqun, gid=gid)
            KfModel(kf_dbcon).modify_t2d_user(name='ntalker_lizhipeng', nickname='ntalker_lizhipeng',
                                              externalname='ntalker_lizhipeng', password=passIndex_ntalker_lizhipeng,
                                              siteid=siteid, userid=userid_ntalker_lizhipeng, gid=gid)
            KfModel(kf_dbcon).modify_t2d_user(name='ralf', nickname='ralf', externalname='ralf',
                                              password=passIndex_ralf,
                                              siteid=siteid, userid=userid_ralf, gid=gid)
            # 接待组逻辑
            syssetting_data = KfModel(kf_dbcon).get_t2d_syssetting(siteid, 'embed')
            if syssetting_data == False:
                KfModel(kf_dbcon).modify_t2d_syssetting(settingid=settingid, settingname=settingname, siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_syssetting(settingid=settingid2, settingname=settingname2, siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_syssetting(settingid=settingid3, settingname=settingname3, siteid=siteid)
            syssetting_mode_data = KfModel(kf_dbcon).get_t2d_syssetting_mode(siteid, 'icon')
            if syssetting_mode_data == False:
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(settingid=settingid, mode='icon', siteid=siteid,
                                                             modeid=iconid)
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(settingid=settingid2, mode='icon', siteid=siteid,
                                                             modeid=iconid2)
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(settingid=settingid3, mode='icon', siteid=siteid,
                                                             modeid=iconid3)
            syssetting_mode2 = KfModel(kf_dbcon).get_t2d_syssetting_mode(siteid, 'list')
            if syssetting_mode2 == False:
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(modeid=listid, settingid=settingid, mode='list',
                                                             siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(modeid=listid2, settingid=settingid2, mode='list',
                                                             siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(modeid=listid3, settingid=settingid3, mode='list',
                                                             siteid=siteid)
            syssetting_mode3 = KfModel(kf_dbcon).get_t2d_syssetting_mode(siteid, 'list')
            if syssetting_mode3 == False:
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(modeid=toolbarid, settingid=settingid, mode='toolbar',
                                                             siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(modeid=toolbarid2, settingid=settingid2, mode='toolbar',
                                                             siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_syssetting_mode(modeid=toolbarid3, settingid=settingid3, mode='toolbar',
                                                             siteid=siteid)
            chosenuser = KfModel(kf_dbcon).get_t2d_chosenuser(siteid)
            if chosenuser == False:
                KfModel(kf_dbcon).modify_t2d_chosenuser(settingid=settingid, iconid=iconid, groupid=groupid,
                                                        siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_chosenuser(settingid=settingid2, iconid=iconid2, groupid=groupid2,
                                                        siteid=siteid)
                KfModel(kf_dbcon).modify_t2d_chosenuser(settingid=settingid3, iconid=iconid3, groupid=groupid3,
                                                        siteid=siteid)

            t_wdk_sit_data = KfModel(kf_dbcon).get_t_wdk_sit(siteid)
            if t_wdk_sit_data == False:
                KfModel(kf_dbcon).modify_t_wdk_sit(siteid, fuwu_lists)

            # 检查企业id版本
            version = checkversion(siteid)
            # 路由
            route_url = AliModel().get_siteid_routing(siteid)
            if route_url == False and version:
                AliModel().modify_t2d_route_url(siteid=siteid, scripturl=scripturl, downturl=downturl,
                                                updateurl=updateurl, apiurl=apiurl)
            # letao库
            site_list = LetaoModel(letao_dbcon).get_t2d_site(siteid)
            if site_list == False and version:
                LetaoModel(letao_dbcon).modify_t2d_site(siteid)
            # 功能开关
            if version == 'b2b':
                functionset = Functionset(kf_dbcon, siteid, 1)
            else:
                functionset = Functionset(kf_dbcon, siteid, 0)
            func_error = ''
            for v in func_lists:
                func_code = str(v['func_list__function__func_code'])
                func_val = str(v['func_list__select_value'])
                is_func = hasattr(functionset, func_code)
                if is_func == False:
                    func_error = func_error + func_code + '开通方法不存在,'
                else:
                    func = functionset.__getattribute__(func_code)
                    if func_code == str('xbot'):
                        func_data = func(func_val, host)
                    else:
                        func_data = func(func_val)
                    if func_data == False:
                        func_error = func_error + func_code + '开通失败,'
            if func_error:
                return {'status': False, 'error': func_error}
        # 更新configjs
        configjs_obj = Configjs(kf_dbcon)
        configjs_data1 = configjs_obj.configjs(siteid)
        if configjs_data1 == False:
            kf_dbcon.rollback()
            return {'status': False, 'error': '更新configjs 失败'}
        kf_commit = kf_dbcon.commit()
        if kf_commit == False:
            kf_dbcon.rollback()
            data = {'status': False, 'error': '提交kf库失败'}
        else:
            # 推送cdn
            # cdn_obj = Cdn(oa_dbcon)
            # cdn_obj.pushcdn_b2b(siteid)
            data = {'status': True, 'error': 'null'}
    except Exception as e:
        kf_dbcon.rollback()
        data = {'status': False, 'error': '异常错误'}
    return data


# 删除站点逻辑
def del_siteid_logic(kf_dbcon, siteid):
    # 检查企业id版本
    version = checkversion(siteid)
    if version == 'b2b':
        try:
            siteid = siteid.split('_')[0] + '_%'
            sql = 'DELETE from `t2d_enterpriseinfo` where siteid like "%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_group` where siteid like "%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_user` where siteid like "%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_syssetting` where siteid like "%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_syssetting_mode` where siteid like "%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_chosenuser` where siteid like "%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_enterpriseinfo_extend` where siteid like "%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            kf_dbcon.commit()
            return True
        except Exception as e:
            kf_dbcon.rollback()
            return False
    else:
        try:
            sql = 'DELETE from `t2d_enterpriseinfo` where siteid="%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_group` where siteid="%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_user` where siteid="%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_syssetting` where siteid="%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_syssetting_mode` where siteid="%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_chosenuser` where siteid="%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            sql = 'DELETE from `t2d_enterpriseinfo_extend` where siteid="%s"' % (siteid)
            kf_dbcon.add_up_de(sql)
            kf_dbcon.commit()
            return True
        except Exception as e:
            kf_dbcon.rollback()
            return False


# 关闭站点逻辑
def close_siteid_logic(kf_dbcon, siteid):
    try:
        version = checkversion(siteid)
        if version == 'b2b':
            KfModel(kf_dbcon).active_t2d_user(siteid=siteid, active=0, is_son=True)
        else:
            KfModel(kf_dbcon).active_t2d_user(siteid=siteid, active=0)
        kf_dbcon.commit()
        return True
    except Exception as e:
        kf_dbcon.rollback()
        return False

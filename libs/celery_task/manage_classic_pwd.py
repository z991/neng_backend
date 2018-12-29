from ldap_server.configs import MONTH_KEY
from libs.basemodel import BaseModelHelp
import time
from libs.classic_service.basehelp import *
from libs.email_ali import *
from libs.sms import *

# 经典版密码定时更换管理
class classic_pwd:

    #每两周执行一次修改密码
    def week_pwd(self):
        duanxin_promptsuccess = {18001220003: '霍飞',
                                 13241388585: '王丽颖',
                                 18701636870: '刘晓',
                                 18501233134: '王云飞',
                                 15712938695: '杨晓',
                                 18813004324: '徐浩然',
                                 13121867233: '李玉岩',
                                 18810691453: '段会',
                                 18330021318: '李慧',
                                 13161487200: '丁泽漪'}
        youjian_promptsuccess = {'guojifa@xiaoneng.cn': '郭吉发',
                                 'huofei@xiaoneng.cn': '霍飞',
                                 'wangliying@xiaoneng.cn': '王丽颖',
                                 'liuxiao@xiaoneng.cn': '刘晓',
                                 'wangyunfei@xiaoneng.cn': '王云飞',
                                 'yangxiao@xiaoneng.cn': '杨晓',
                                 'xuhaoran@xiaoneng.cn': '徐浩然',
                                 'liyuyan@xiaoneng.cn': '李玉岩',
                                 'duanhuili@xiaoneng.cn': '段会',
                                 'lihui@xiaoneng.cn': '李慧',
                                 'yunwei@xiaoneng.cn': '运维',
                                 'dingzeyi@xiaoneng.cn': '丁泽漪'}
        youjian_prompterror = {'guojifa@xiaoneng.cn': '郭吉发',
                               'yunwei@xiaoneng.cn': '运维'}
        duanxin_prompterror = {13311071024: '郭吉发',
                               18511583871: '邱瑞杰'}
        ntalker_maliqun = md5Encode("ntalker_maliqun" + MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
        ntalker_maliqun_pwd = ntalker_maliqun[0:8]
        db_con_list = BaseModelHelp().get_db_list_con('kf')
        error_str = ''
        for key in db_con_list:
            try:
                user_sql = f'update t2d_user set password="{ntalker_maliqun_pwd}" where userid like "%ISME9754_T2D_ntalker_maliqun"'
                key.add_up_de_commit(user_sql)
            except:
                error_str += key + ','
                continue

        error_tip = f"修改(maliqun)密码异常需运维和开发者检测,异常信息：{error_str}连接数据库失败。【小能科技】"
        success_tip = f"测试账号(maliqun)密码更换为({ntalker_maliqun_pwd})，谨慎保管！【小能科技】"
        if error_str:
            for key in duanxin_prompterror:
                Sms().send(key, error_tip)
            for key in youjian_prompterror:
                Email_base().email(key, '小能系统账号密码更换', '小能系统账号密码更换', error_tip)
        for key in duanxin_promptsuccess:
            Sms().send(key, success_tip)
        for key in youjian_promptsuccess:
            Email_base().email(key, '小能系统账号密码更换', '小能系统账号密码更换', success_tip)

    #每天执行修改密码
    def day_pwd(self):
        duanxin_promptsuccess_ntalker_steven = {13911101998: 'steven',
                                        18601293995: '任斌',
                                        13522070301: '马立群',
                                        13552690112: '赵林海',
                                        15010060738: '杜鹏飞',
                                        18911207028: '崔雨涵', }
        youjian_promptsuccess_ntalker_steven = {'stevengou@xiaoneng.cn': 'steven',
                                        'renbin@xiaoneng.cn': '任斌',
                                        'maliqun@xiaoneng.cn': '马立群',
                                        'zhaolinhai@xiaoneng.cn': '赵林海',
                                        'dupengfei@xiaoneng.cn': '杜鹏飞',
                                        'cuiyuhan@xiaoneng.cn': '崔雨涵',
                                        'guojifa@xiaoneng.cn': '郭吉发',
                                        'yunwei@xiaoneng.cn': '运维'}
        duanxin_promptsuccess_ntalker_lizhipeng = {15810399849: '李自飞',
                                           13810706710: '李先磊'}
        youjian_promptsuccess_ntalker_lizhipeng = {'lizifei@xiaoneng.cn': '李自飞',
                                           'lixianlei@xiaoneng.cn': '李先磊',
                                           'guojifa@xiaoneng.cn': '郭吉发',
                                           'yunwei@xiaoneng.cn': '运维'}
        duanxin_promptsuccess_ralf = {15010060738: '杜鹏飞'}
        youjian_promptsuccess_ralf = {'dupengfei@xiaoneng.cn': '杜鹏飞',
                                      'guojifa@xiaoneng.cn': '郭吉发',
                                      'yunwei@xiaoneng.cn': '运维'}
        youjian_prompterror = {'guojifa@xiaoneng.cn': '郭吉发',
                               'yunwei@xiaoneng.cn': '运维'}
        duanxin_prompterror = {13311071024: '郭吉发',
                               18511583871: '邱瑞杰'}
        ntalker_steven = md5Encode("ntalker_steven" + MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
        ntalker_steven_pwd = ntalker_steven[0:8]
        ntalker_lizhipeng = md5Encode("ntalker_lizhipeng" + MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
        ntalker_lizhipeng_pwd = ntalker_lizhipeng[0:8]
        ralf = md5Encode("ralf" + MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
        ralf_pwd = ralf[0:8]
        db_con_list = BaseModelHelp().get_db_list_con('kf')
        error_str = ''
        for key in db_con_list:
            try:
                user_sql = f'update t2d_user set password="{ntalker_steven_pwd}" where userid like "%ISME9754_T2D_ntalker_steven"'
                key.add_up_de_commit(user_sql)
                user_sql = f'update t2d_user set password="{ntalker_lizhipeng_pwd}" where userid like "%ISME9754_T2D_ntalker_lizhipeng"'
                key.add_up_de_commit(user_sql)
                user_sql = f'update t2d_user set password="{ralf_pwd}" where userid like "%ISME9754_T2D_ralf"'
                key.add_up_de_commit(user_sql)
            except:
                error_str += key + ','
                continue

        error_tip = f"修改(maliqun)密码异常需运维和开发者检测,异常信息：{error_str}连接数据库失败。【小能科技】"
        success_tip_ntalker_steven = f"系统账号(ntalker_steven)密码更换为({ntalker_steven_pwd})，谨慎保管！【小能科技】"
        success_tip_ntalker_lizhipeng = f"系统账号(ntalker_lizhipeng)密码更换为({ntalker_lizhipeng_pwd})，谨慎保管！【小能科技】"
        success_tip_ralf = f"系统账号(ralf)密码更换为({ralf_pwd})，谨慎保管！【小能科技】"
        if error_str:
            for key in duanxin_prompterror:
                Sms().send(key, error_tip)
            for key in youjian_prompterror:
                Email_base().email(key, '小能系统账号密码更换', '小能系统账号密码更换', error_tip)
        #ntalker_steven
        for key in duanxin_promptsuccess_ntalker_steven:
            Sms().send(key, success_tip_ntalker_steven)
        for key in youjian_promptsuccess_ntalker_steven:
            Email_base().email(key, '小能系统账号密码更换', '小能系统账号密码更换', success_tip_ntalker_steven)
        # ntalker_lizhipeng
        for key in duanxin_promptsuccess_ntalker_lizhipeng:
            Sms().send(key, success_tip_ntalker_steven)
        for key in youjian_promptsuccess_ntalker_lizhipeng:
            Email_base().email(key, '小能系统账号密码更换', '小能系统账号密码更换', success_tip_ntalker_lizhipeng)
        # ralf
        for key in duanxin_promptsuccess_ralf:
            Sms().send(key, success_tip_ntalker_steven)
        for key in youjian_promptsuccess_ralf:
            Email_base().email(key, '小能系统账号密码更换', '小能系统账号密码更换', success_tip_ralf)

"""
function：Functionset 功能开关
describe：功能开关操作类封装
date：20171127
author：gjf
version:1.09
"""
# coding=utf-8
import requests
from libs.functionset import Robot,New_ticket


class Functionset:
    """
    function:__init__
    describe:构造函数初始连接数据库kf库
    param: pymysql.cursors.Cursor @dbcon kf库
    """

    def __init__(self, dbcon,siteid,linkage=0):
        self.dbcon = dbcon
        self.siteid = siteid
        self.linkage = linkage
        if self.siteid:
            self.siteid_like = self.siteid.split('_')[0]+'_%'

    """
    function:erpserver
    describe:erp显示功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def erpserver(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set erpserver='%s' where siteid like '%s'" % (switch,self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set erpserver='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:iscommodity
    describe:商品接口设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def iscommodity(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set iscommodity='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set iscommodity='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:isweixin
    describe:微信设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def isweixin(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set isweixin='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set isweixin='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:autoconnect
    describe:连接客服逻辑功能开通和关闭 直接连接:1,输入信息后连接:0
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def autoconnect(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set autoconnect='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set autoconnect='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:iserp
    describe:开启erp功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def iserp(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set iserp='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set iserp='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:ticket
    describe:工单设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def ticket(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set ticket='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set ticket='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    #新工单
    def new_ticket(self, switch):
        if int(switch) == 1:
            data = New_ticket(self.dbcon).on_ticket(self.siteid)
            sql = "update t2d_enterpriseinfo set ticket='%s' where siteid='%s'" % (2, self.siteid)
            data = self.dbcon.add_up_de(sql)
            if data:
                return True
            else:
                return False
        else:
            data = New_ticket(self.dbcon).off_ticket(self.siteid)
            if data:
                sql = "update t2d_enterpriseinfo set ticket='%s' where siteid='%s'" % (0, self.siteid)
                data = self.dbcon.add_up_de(sql)
                if data:
                    return True
                else:
                    return False
            else:
                return True


    """
    function:smarteye
    describe:帮助中心设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def smarteye(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set smarteye='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set smarteye='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:enable_artificialgreeting
    describe:默认欢迎语功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def enable_artificialgreeting(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set enable_artificialgreeting='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set enable_artificialgreeting='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:changecsr
    describe:更换客服功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def changecsr(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set changecsr='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set changecsr='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:xiaonengver
    describe:小能版权信息功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def xiaonengver(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set xiaonengver='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set xiaonengver='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False


    """
    function:watchqueue
    describe:客户端查看排队信息功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def watchqueue(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set watchqueue='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set watchqueue='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:linechannel
    describe:二维码功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def linechannel(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set linechannel='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set linechannel='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:autoexpansion
    describe:是否展开侧边栏功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def autoexpansion(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set autoexpansion='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set autoexpansion='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:isnoim
    describe:更改IM连接级别功能开通和关闭
             进入网页就加载im服务,访客关闭聊窗,收到客服发送消息后,弹tip:0,
             关闭im服务,访客关闭聊窗,收不到客服发送的消息:1,
             打开聊窗后,再加载im服务,访客关闭聊窗,收到客服发送消息后,弹tip:2,
             进入网页就加载im服务,访客关闭聊窗,收到客服发送消息后,直接打开聊窗:3
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def isnoim(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set isnoim='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set isnoim='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:transferfiles
    describe:访客端是否显示上传文件按钮功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def transferfiles(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set transferfiles='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set transferfiles='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:close_im_flash
    describe:IM的flash连接功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def close_im_flash(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set close_im_flash='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set close_im_flash='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)

    """
    function:close_tchat_flash
    describe:tchat的flash连接功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def close_tchat_flash(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set close_tchat_flash='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set close_tchat_flash='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:resize_chat
    describe:聊天窗口是否可变换大小功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def resize_chat(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set resize_chat='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set resize_chat='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:drag_chat
    describe:聊天窗口是否可拖动功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def drag_chat(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set drag_chat='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set drag_chat='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:enable_robotgreeting
    describe:是否启用机器人1.0欢迎语开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def enable_robotgreeting(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set enable_robotgreeting='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set enable_robotgreeting='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:notrail
    describe:轨迹调用开通和关闭 进入网页就加载轨迹服务:0,关闭轨迹服务:1,打开聊窗后,再加载轨迹服务:2
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    #听到这音乐、我一脚蹬开了身边的牛、自己耕完了200亩地、、、
    def notrail(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set notrail='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set notrail='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:captureimage
    describe:访客端截图插件功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def captureimage(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set captureimage='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set captureimage='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:sessioncarry
    describe:会话携带功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def sessioncarry(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set sessioncarry='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set sessioncarry='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:viewchatrecord
    describe:前端查看聊天记录功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def viewchatrecord(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set viewchatrecord='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set viewchatrecord='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:enable_entrance
    describe:新版邀请功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def enable_entrance(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set enable_entrance='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set enable_entrance='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:androidtransf
    describe:WAP图片上传功能（安卓）功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def androidtransf(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set androidtransf='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set androidtransf='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:othertransf
    describe:WAP图片上传功能（非安卓）功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def othertransf(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set othertransf='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set othertransf='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    """
    function:sessionmode
    describe:是否开通公平模式功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """

    def sessionmode(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set sessionmode='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set sessionmode='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 小能使用模式
    def mode(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set mode='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set mode='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    def sessionhelp(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set sessionhelp='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set sessionhelp='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # WAP聊窗功能开关功能开通和关闭 关闭:0,开通:1
    def wap(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set wap='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set wap='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 打开链接方式功能开通和关闭 关闭:0,开通:1
    def waphref(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set waphref='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set waphref='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 聊天记录是否可导出功能开通和关闭 关闭:0,开通:1
    def chatingrecord(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set chatingrecord='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set chatingrecord='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 敏感词开关功能开通和关闭 关闭:0,开通:1
    def filter(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set filter='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set filter='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 会话接管功能开通和关闭 关闭:0,开通:1
    def sessiontakeover(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set sessiontakeover='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set sessiontakeover='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 接待时间功能开通和关闭 关闭:0,开通:1
    def isrecep_time(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set isrecep_time='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set isrecep_time='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 会话断开时间功能 单位秒
    def contime(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set contime='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set contime='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 客服坐席数功能 单位/人
    def kfsum(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set kfsum='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo set kfsum='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # qq功能开通和关闭 关闭:0,开通:1
    def is_qq(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set is_qq='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set is_qq='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # 微博功能开通和关闭 关闭:0,开通:1
    def is_weibo(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set is_weibo='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set is_weibo='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # （教育版）咨询接待-邀请会话功能开通和关闭 关闭:0,开通:1
    def reversechat(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set reversechat='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set reversechat='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # （（教育版）KPI-邀请会话功能开通和关闭 关闭:0,开通:1
    def isyqhh(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set isyqhh='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set isyqhh='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # （教育版）数据分析 - 运营报表功能开通和关闭 关闭:0,开通:1
    def ishhlx(self, switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set ishhlx='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set ishhlx='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    # xbot机器人开关 关闭:0,开通:1
    def xbot(self, switch, host):
        if int(switch) == 1:
            robot = Robot(self.dbcon)
            robot_re = robot.on_xbot(self.siteid, host)
            if robot_re == False:
                return False
            else:
                return True
        else:
            return True

    #云问机器人
    def yunwen(self, switch):
        if int(switch) == 1:
            robot = Robot(self.dbcon)
            robot_re = robot.on_yunwen(self.siteid)
            if robot_re == False:
                return False
            else:
                return True
        else:
            return True

    def coop(self, switch):
        return True

    #企业logo
    def logo(self,switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set logo='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set logo='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    #xpush
    def xpush(self,switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo set isnoim=0 where siteid like '%s'" % (self.siteid_like)
            data = self.dbcon.add_up_de(sql)
            sql = "update t2d_enterpriseinfo_extend set usexpush='%s',xpushpolltimeout=30 where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set usexpush='%s',xpushpolltimeout=30 where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False

    #移动云
    def mobile_cloud(self,switch):
        if self.linkage:
            sql = "update t2d_enterpriseinfo_extend set mobile_cloud_online='%s' where siteid like '%s'" % (switch, self.siteid_like)
            data = self.dbcon.add_up_de(sql)
        else:
            sql = "update t2d_enterpriseinfo_extend set mobile_cloud_online='%s' where siteid='%s'" % (switch, self.siteid)
            data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False




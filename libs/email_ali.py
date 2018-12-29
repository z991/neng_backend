# -*- coding:utf-8 -*-
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header
from ldap_server.configs import EMAIL_USERNAME,EMAIL_PWD


class Email_base:

    def __init__(self):
        # 发件人地址，通过控制台创建的发件人地址
        self.email_username = EMAIL_USERNAME
        # 发件人密码，通过控制台创建的发件人密码
        self.email_pwd = EMAIL_PWD

    def email(self,rcptto,theme,nickname,content):

        # 自定义的回复地址
        replyto = ''

        # 收件人地址或是地址列表，支持多个收件人，最多30个
        # rcptto = ['***', '***']
        # rcptto = 'guojifa@xiaoneng.cn'

        #自定义邮件主题
        #theme = '自定义信件主题'

        #自定义发信昵称
        #nickname = '自定义发信昵称'

        #自定义HTML邮件内容
        # content = '自定义HTML邮件内容'

        # 构建alternative结构
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(theme).encode()
        msg['From'] = '%s <%s>' % (Header(nickname).encode(), self.email_username)
        #msg['To'] = rcptto
        #msg['Reply-to'] = replyto
        msg['Message-id'] = email.utils.make_msgid()
        msg['Date'] = email.utils.formatdate()
        # 构建alternative的text/plain部分
        textplain = MIMEText('自定义TEXT纯文本部分', _subtype='plain', _charset='UTF-8')
        msg.attach(textplain)
        # 构建alternative的text/html部分
        texthtml = MIMEText(content, _subtype='html', _charset='UTF-8')
        msg.attach(texthtml)
        # 发送邮件
        try:
            client = smtplib.SMTP()
            # python 2.7以上版本，若需要使用SSL，可以这样创建client
            # client = smtplib.SMTP_SSL()
            # SMTP普通端口为25或80
            client.connect('smtpdm.aliyun.com', 25)
            # 开启DEBUG模式
            client.set_debuglevel(0)
            client.login(self.email_username, self.email_pwd)
            # 发件人和认证地址必须一致
            # 备注：若想取到DATA命令返回值,可参考smtplib的sendmaili封装方法:
            #      使用SMTP.mail/SMTP.rcpt/SMTP.data方法
            client.sendmail(self.email_username, rcptto, msg.as_string())
            client.quit()
            return True
        except Exception as e:
            print(e)
            return False

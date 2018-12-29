#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.header import Header
from email.mime.text import MIMEText

sender = 'zhouzichen@xiaoneng.cn'
mail_host = "smtp.exmail.qq.com"
mail_user = "zhouzichen@xiaoneng.cn"
mail_pass = "0408Inlove"


def send_mail(email, url):
    mail_msg = """
    <p>LDAP账号管理中心-账户密码重置</p>
    <p><a href={}>重置链接</a></p>
    """

    message = MIMEText(mail_msg.format(url), 'html', 'utf-8')

    message['From'] = Header("LDAP账号管理中心", 'utf-8')
    message['To'] = Header(email, 'utf-8')

    subject = '账号重置邮件'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, email, message.as_string())
        return True
    except smtplib.SMTPException:
        return False

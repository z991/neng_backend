#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from ldap_server.configs import MAIL_PASS, MAIL_USER, MAIL_HOST, SENDER


def send_mail(email, code):

    mail_msg = """
    <p>LDAP账号管理中心-账户密码重置</p><br />
    <p>验证码: {}</p>
    """

    message = MIMEText(mail_msg.format(code), 'html', 'utf-8')

    message['From'] = Header(SENDER, 'utf-8')
    message['To'] = Header(email, 'utf-8')

    subject = '账号重置邮件'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(MAIL_HOST)
        smtpObj.login(MAIL_USER, MAIL_PASS)
        smtpObj.sendmail(SENDER, email, message.as_string())
        return True
    except smtplib.SMTPException:
        return False

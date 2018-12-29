import pymysql
from libs.environment import ENV
current_env = ENV()

db = pymysql.connect(current_env.get_config("DB_HOST"),
                     current_env.get_config("DB_USER"),
                     current_env.get_config("DB_PASSWORD"),
                     current_env.get_config("DB_NAME"))
cursor = db.cursor()
sql = 'select * from setup_loginldapconfig'
cursor.execute(sql)
reslist = cursor.fetchall()
try:
    loginconfig = reslist[0]
    auth_ldap_bind_dn = loginconfig[1]
    auth_ldap_bind_password = loginconfig[2]
    user_ldapsearch = loginconfig[3]
    user_scope_subtree = loginconfig[4]
    group_ldapsearch = loginconfig[5]
    group_scope_subtree = loginconfig[6]
    is_active = loginconfig[7]
    is_staff = loginconfig[8]
    is_superuser = loginconfig[9]
    ldap_server_url = loginconfig[10]
    login_model = loginconfig[11]
    ldap_name = loginconfig[12]
except:
    login_model = 2
    auth_ldap_bind_dn = ""
    auth_ldap_bind_password = ""
    user_ldapsearch = ""
    user_scope_subtree = ""
    group_ldapsearch = ""
    group_scope_subtree = ""
    is_active = ""
    is_staff = ""
    is_superuser = ""
    ldap_server_url = ""
    ldap_name = ""
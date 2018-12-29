from applications.setup.models import LoginLdapConfig


def get_login_model():
    try:
        login_mode = LoginLdapConfig.objects.get(ldap="oa")
    except:
        login_mode = None
    return login_mode


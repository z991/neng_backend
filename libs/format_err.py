# __author__='gzh'


# 将异常的描述转化为字符串
def format_error(err_list):
    error_dict = {}
    for index, data in enumerate(err_list):
        error_dict[index] = data
    return str(error_dict)

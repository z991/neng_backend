import xlrd


def syn_industry(file_contents=None, col_name_index=0, sheet_name=u'industry'):
    """
        获取Excel表格中的数据
        参数: file_excel：Excel文件路径
             col_name_index：表头列名所在行的索引
             sheet_name：Sheet1名称
    """
    try:
        data = xlrd.open_workbook(file_contents=file_contents)
        table = data.sheet_by_name(sheet_name)
        n_rows = table.nrows  # 行数
        row_data = []
        for row_num in range(1, n_rows):
            row = table.row_values(row_num)
            row_data.append(row)
        return row_data
    except Exception as e:
        return False

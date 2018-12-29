import csv
import xlwt
import datetime
import codecs
from django.http import HttpResponse, JsonResponse


class Excel_export:
    """
    导出类
    title = {"siteid":"企业id","name":"企业名称"}
    content = [{"siteid":"kf_123","name":"哈喽"},{"siteid":"kf_1234","name":"哈喽1"}]
    """

    def __init__(self, filename=str, title=dict, content=dict):
        self.filename = filename
        self.title = title
        self.content = content
        self.today = datetime.date.today()

    def export_xls(self):
        filename = f"attachment; filename={self.filename}_{self.today}.xls"
        # 设置HTTPResponse的类型
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = filename
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        ws = wb.add_sheet('sheet1')
        row_num = 0
        col_num = 0
        title_list = []
        # 写入文件标题
        for k in self.title:
            ws.write(row_num, col_num, self.title[k])
            col_num = col_num+1
            title_list.append(k)

        for key in self.content:
            row_num = row_num+1
            for col_num in range(len(title_list)):
                ws.write(row_num, col_num, key[title_list[col_num]])
        wb.save(response)
        return response

    def export_csv(self):
        filename = f"attachment; filename={self.filename}_{self.today}.csv"
        # 设置HTTPResponse的类型
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = filename
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response)
        title_list = []
        title = []
        for k in self.title:
            title_list.append(k)
            title.append(self.title[k])
        writer.writerow(title)
        if self.content != False:
            for key in self.content:
                content = []
                for k in title_list:
                    content.append(key[k])
                writer.writerow(content)
        return response

class Excel_import:
    """
    导入类

    """


    def __init__(self):
        pass
import  datetime
import xlrd
import os
from xlutils.copy import copy

class Logger:
    def __init__(self, config):
        self.log_path = config["output_path"]


    def logger_xls(self,msg,sendGptMsg):
        # 对话日志写入 excel
        with open(os.path.join(self.log_path,str(datetime.date.today()) + '.txt'), 'a', encoding='utf-8') as a:
            a.write(str(datetime.datetime.now()) + "::发送::" + sendGptMsg + '\n')
            a.flush()
            # self.write_excel_xls_append({
            #     'datetime': str(datetime.datetime.now()),
            #     'user': msg['name'],
            #     'type': msg['type'],
            #     'num': msg['num'],
            #     'action': msg['action'],
            #     'msg': msg['msg'],
            #     'price': msg['price']
            # })


    def logger_receive(self,responseText):
        with open(os.path.join(self.log_path,str(datetime.date.today()) + '.txt'), 'a', encoding='utf-8') as a:
            a.write(str(datetime.datetime.now()) + "::接收::" + responseText + '\n')
            a.flush()
            # self.write_excel_xls_append({
            #     'datetime': str(datetime.datetime.now()),
            #     'user': 'gpt35',
            #     'type': '',
            #     'num': '',
            #     'action': '说',
            #     'msg': responseText,
            #     'price': 0
            # })

    # 记录弹幕上下文到 excel
    def write_excel_xls_append(self,value):
        workbook = xlrd.open_workbook(self.log_path)  # 打开工作簿
        sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
        rows_old = 0
        sheetName = str(datetime.date.today())
        if sheetName in sheets:
            worksheet = workbook.sheet_by_name(sheetName)
            rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
        new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
        if sheetName not in sheets:
            new_workbook.add_sheet(sheetName)
        new_worksheet = new_workbook.get_sheet(sheetName)  # 获取转化后工作簿中的第一个表格
        new_worksheet.write(rows_old, 0, value['datetime'])
        new_worksheet.write(rows_old, 1, value['user'])
        new_worksheet.write(rows_old, 2, value['type'])
        new_worksheet.write(rows_old, 3, value['num'])
        new_worksheet.write(rows_old, 4, value['action'])
        new_worksheet.write(rows_old, 5, value['msg'])
        new_worksheet.write(rows_old, 6, value['price'])
        new_workbook.save(self.log_path)  # 保存工作簿
        if self.config['env'] == 'dev':
            print("xls格式表格【追加】写入数据成功！")

    # 模拟 SSE 键盘输入，供 obs 抓取字幕
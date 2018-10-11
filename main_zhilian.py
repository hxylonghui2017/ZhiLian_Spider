from selenium import webdriver
from bs4 import BeautifulSoup
import xlwt
import csv
import requests

#url = 'https://xiaoyuan.zhaopin.com/full/538/0_0_160000_1_0_0_0_1_0'
#url = 'https://sou.zhaopin.com/?pageSize=60&jl=765&sf=10001&st=15000&kw=java&kt=3&=10001'
def get_content(arcurl):
    browser = webdriver.Firefox()
    browser.get(arcurl)
    html = browser.page_source
    browser.close()
    return html

def get_content_requests(arcul):
    headers = {
        'Host': 'sou.zhaopin.com',
        'Referer': 'https://i.zhaopin.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6756.400 QQBrowser/10.2.2457.400',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    response = requests.get(arcul, headers = headers)
    response.encoding = response.apparent_encoding
    if response.status_code == 200:
        return response.text
    else:
        print("find error, link agin")
        get_content_requests(arcul)

def parse_page_shezhao(html):
    #print(html)
    soup = BeautifulSoup(html, "lxml")
    message = []
    message_dict = []
    div_list = soup.select('#listContent > div')
    for div in div_list:
        messdict = {}
        div_infobox = div.select('div.listItemBox > div.infoBox')
        if len(div_infobox) > 0:
            nameBox = div_infobox[0].select('.nameBox > div.jobName')
            if len(nameBox) > 0:
                jobname = nameBox[0].get_text()
                job_link = nameBox[0].select('a')[0].attrs['href']
            companyBox = div_infobox[0].select('.nameBox > div.commpanyName')
            if len(companyBox) > 0:
                company_name = companyBox[0].get_text()
                company_link = companyBox[0].select('a')[0].attrs['href']
            jobDesc = div_infobox[0].select('.descBox > div.jobDesc')
            if len(jobDesc) > 0:
                jobadr = jobDesc[0].get_text()
                job_saray = jobDesc[0].select('p.job_saray')[0].get_text()
                job_demand = jobDesc[0].select('.job_demand')[0].get_text()
            commpanyDesc = div_infobox[0].select('.descBox > div.commpanyDesc')
            if len(commpanyDesc) > 0:
                jobadr += " " + commpanyDesc[0].get_text()
                company_desc = commpanyDesc[0].get_text()
            job_welfare = div_infobox[0].select('div > div.job_welfare > div')
            desc = ""
            for xvar in job_welfare:
                desc += xvar.get_text() + "; "
            commpanyStatus = div_infobox[0].select('div > div.commpanyStatus')
            desc += "【" + commpanyStatus[0].get_text() + "】"
            # ['职位链接', '职位', '薪资', '基本要求', '职责描述', '公司', '公司规模', '公司链接']
        messdict['职位链接'] = job_link
        messdict['职位']=jobname
        messdict['薪资']=job_saray
        messdict['基本要求'] = job_demand
        messdict['职责描述'] = desc
        messdict['公司'] = company_name
        messdict['公司规模'] = company_desc
        messdict['公司链接'] = company_link
        # messdict['相关性质'] = jobadr
        # messdict['职责描述'] = desc
        message.append([job_link, jobname, company_name, company_link, jobadr, desc])
        message_dict.append(messdict)
    return message, message_dict

def parse_page(html):
    soup = BeautifulSoup(html, "lxml")
    message = []
    for li in soup.select('.searchResultListUl > li'):
        names = li.select('div.searchResultItemDetailed > p.searchResultJobName > a')
        if len(names) > 0:
            jobname = names[0].get_text()
            job_link = names[0]['href']
        company_names = li.select('div.searchResultItemDetailed > p.searchResultCompanyname')
        if len(company_names) > 0:
            company_name = company_names[0].get_text()
        jobadrs = li.select('div.searchResultItemDetailed > p.searchResultJobAdrNum > span')
        if len(jobadrs) > 0:
            jobadr = ""
            for j in jobadrs:
                jobadr += j.get_text().replace("\n", '') + "；"
        companyinfos = li.select('div.searchResultItemDetailed > p.searchResultCompanyInfodetailed > span')
        if len(companyinfos) > 0:
            for c in companyinfos:
                jobadr += c.get_text().replace("\n", '') + "；"
        descriptions = li.select('div.searchResultItemDetailed > p.searchResultJobdescription')
        if len(descriptions) > 0:
            desc = ""
            for d in descriptions:
                desc += d.get_text().replace(' ','').replace("\n", '')
        message.append([job_link,jobname,company_name,jobadr,desc])
    return message

def excel_write(filename, html):
    # 创建excel文件，声明编码为utf-8
    wb = xlwt.Workbook(encoding='utf-8')
    # 创建表格
    ws = wb.add_sheet('sheet1')
    # 表头信息
    headData = ['LINK_URL', '职位', '公司', '公司链接', '相关性质', '职责描述']
    # 写入表头信息
    for colnum in range(0, len(headData)):
        ws.write(0, colnum, headData[colnum], xlwt.easyxf('font: bold on'))
    # 从第2行开始写入
    index = 1
    #for item in parse_page(html):
    items, others = parse_page_shezhao(html)
    for item in items:
        print(item)
        for i in range(0, len(headData)):
            # .write（行，列，数据）
            ws.write(index, i, item[i])
        index += 1
    # 保存excel
    wb.save(filename)

def write_csv_headers(path, headers):
    with open(path, 'a', encoding='gb18030', newline='') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()

def write_csv_rows(path, headers, rows):
   '''
   写入行
   '''
   with open(path, 'a', encoding='gb18030', newline='') as f:
       f_csv = csv.DictWriter(f, headers)
       f_csv.writerows(rows)

def csv_write(csv_name, headers, html):
    write_csv_headers(csv_name, headers)
    items, others = parse_page_shezhao(html)
    print(others)
    write_csv_rows(csv_name, headers, others)

def main():
    filename = input("请输入存储文件名：\n")
    while True:
        url = input("请输入URL：\n")
        if not url=="end":
            html = get_content(url)
            # html = get_content_requests(url)
            csv_name = filename + '.csv'
            headers = ['职位链接', '职位', '薪资',  '基本要求', '职责描述', '公司', '公司规模', '公司链接']
            csv_write(csv_name, headers, html)
        else:
            break

    #excel_name = filename + ".xls"
    #excel_write("智联招聘岗位爬虫结果.xls", html)
    #excel_write(excel_name, html)

if __name__=="__main__":
    main()
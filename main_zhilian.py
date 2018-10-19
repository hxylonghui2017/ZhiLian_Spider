from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import xlwt
import csv
import requests
import time
import re

#url = 'https://xiaoyuan.zhaopin.com/full/538/0_0_160000_1_0_0_0_1_0'
#url = 'https://sou.zhaopin.com/?pageSize=60&jl=765&sf=10001&st=15000&kw=java&kt=3&=10001'

search_url = 'https://i.zhaopin.com/'
# main_browser = webdriver.Firefox()
# wait = WebDriverWait(main_browser, 10)
def create_browser():
    main_browser = webdriver.Firefox()
    wait = WebDriverWait(main_browser, 10)
    return main_browser, wait

def next_page(main_browser, wait, max_page):
    try:
        page_click = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pagination_content"]/div/button[2]'))
            )
        page_click.click()
        # print(main_browser.current_url)
        re_url = main_browser.current_url
        pattern = re.compile('/?p=(.*?)&', re.S)
        find = pattern.findall(re_url)
        if len(find) > 0:
            #print(int(find[0]))
            if int(find[0])>max_page:
                return None
        return main_browser.page_source
    except TimeoutException:
        return None

def search_key(keyword, main_browser, wait, url=search_url):
    print("正在搜索："+ keyword)
    try:
        main_browser.get(url)
        # input = browser.find_element_by_class_name('zp-search-input')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.zp-search-input'))
        )
        # btn_search = browser.find_element_by_class_name('zp-search-btn')
        btn_search = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.zp-search-btn'))
        )
        input.send_keys(keyword)
        time.sleep(1)
        btn_search.click()
        #处理多个标签页
        handle = main_browser.current_window_handle
        handles = main_browser.window_handles
        if len(handles) > 1:
            for h in handles:
                if h != handle:
                    main_browser.switch_to_window(h)
                    time.sleep(1)
                    #print(main_browser.page_source)
                    return main_browser.page_source
        else:
            return main_browser.page_source
    except TimeoutException:
        return search_key(keyword)

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
    # print(len(div_list))
    for div in div_list:
        messdict = {}
        job_l = ""
        jobname = ""
        job_saray = ""
        job_demand = ""
        desc = ""
        company_name = ""
        company_desc = ""
        company_link = ""
        jobadr = ""
        div_infobox = div.select('div.contentpile__content__wrapper__item > div.contentpile__content__wrapper__item__info')
        if len(div_infobox) > 0:
            nameBox = div_infobox[0].select('.nameBox > div.jobName')
            if len(nameBox) > 0:
                jobname = nameBox[0].get_text()
                job_l = nameBox[0].select('a')[0].attrs['href']
                # print(job_l)
                # print(job_l)
            companyBox = div_infobox[0].select('.nameBox > div.commpanyName')
            if len(companyBox) > 0:
                company_name = companyBox[0].get_text()
                company_link = companyBox[0].select('a')[0].attrs['href']
            jobDesc = div_infobox[0].select('.descBox > div.jobDesc')
            if len(jobDesc) > 0:
                jobadr = jobDesc[0].get_text()
                job_saray = jobDesc[0].select('p.contentpile__content__wrapper__item__info__box__job__saray')[0].get_text()
                job_demand = jobDesc[0].select('.contentpile__content__wrapper__item__info__box__job__demand')[0].get_text()
            commpanyDesc = div_infobox[0].select('.descBox > div.contentpile__content__wrapper__item__info__box__job__comdec')
            if len(commpanyDesc) > 0:
                jobadr += " " + commpanyDesc[0].get_text()
                company_desc = commpanyDesc[0].get_text()
            job_welfare = div_infobox[0].select('div > div.job_welfare > div')
            desc = ""
            for xvar in job_welfare:
                desc += xvar.get_text() + "; "
            commpanyStatus = div_infobox[0].select('div > div.contentpile__content__wrapper__item__info__box__status')
            desc += "【" + commpanyStatus[0].get_text() + "】"
            # ['职位链接', '职位', '薪资', '基本要求', '职责描述', '公司', '公司规模', '公司链接']
        messdict['职位链接'] = job_l
        messdict['职位']=jobname
        messdict['薪资']=job_saray
        messdict['基本要求'] = job_demand
        messdict['职责描述'] = desc
        messdict['公司'] = company_name
        messdict['公司规模'] = company_desc
        messdict['公司链接'] = company_link
        # messdict['相关性质'] = jobadr
        # messdict['职责描述'] = desc
        message.append([job_l, jobname, company_name, company_link, jobadr, desc])
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

def csv_write(csv_name, headers, html, writeheader = True):
    if writeheader:
        write_csv_headers(csv_name, headers)
    items, others = parse_page_shezhao(html)
    #print(others)
    write_csv_rows(csv_name, headers, others)

def main():
    filename = input("请输入搜索关键词：\n").replace(' ','_')
    # print(search_key('python'))
    max_page = int(input('请输入存储页数：\n'))
    b, w = create_browser()
    html = search_key(filename, b, w)
    csv_name = filename + '.csv'
    headers = ['职位链接', '职位', '薪资', '基本要求', '职责描述', '公司', '公司规模', '公司链接']
    csv_write(csv_name, headers, html)
    while True:
        # b.close()
        time.sleep(1)
        html = next_page(b, w, max_page)
        if not html:
            break
        else:
            csv_write(csv_name, headers, html, False)
    b.quit()

def main2():
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
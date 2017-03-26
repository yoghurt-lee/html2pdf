#coding:utf-8
import urlparse as uparse
from urlparse import urlparse
import myrequests,re
from bs4 import BeautifulSoup
import pdfkit

class spider(object):
    model = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
    {0}
    </body>
    </html>
    '''
    def __init__(self,url,name):
        d = urlparse(url)
        self.name = name
        self.domain = "{0}://{1}".format(d.scheme,d.netloc)
        self.url = url

    def crawler(self,url):
        return myrequests.get(url).content

    def html2pdf(self):
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'cookie': [
                ('cookie-name1', 'cookie-value1'),
                ('cookie-name2', 'cookie-value2'),
            ],
            'outline-depth': 10,
        }
        try:
            self.htmls = self.get_htmls()
            pdfkit.from_file(self.htmls,self.name+'.pdf',options)
        except Exception as e:
            print str(e)
        finally:
            self.__remove()

    def get_htmls(self):
        pass

    def __remove(self):
        import os
        for filename in self.htmls:
            os.remove(filename)


class Python(spider):
    def menu(self,content):
        soup = BeautifulSoup(content,"html.parser")
        soup = soup.findAll('ul',{'class':'uk-nav uk-nav-side'})[1]
        List = soup.findAll('a')
        for element in List:
            url = uparse.urljoin(self.domain,element.get('href'))
            yield url

    def body(self,content):
        try:
            soup = BeautifulSoup(content,"html.parser")
            body = soup.findAll('div',{'class':'x-wiki-content'})[0]
            title = soup.find('h4').string.strip()
            center_tag = soup.new_tag('center')
            title_tag = soup.new_tag('h1')
            title_tag.string = title
            #insert(index,tag)参数:向body中插入tag标签,第一个参数是插入到网页中第index个标签处,第二个参数这里插入的是'bs4.element.Tag'类型
            center_tag.insert(1,title_tag)
            body.insert(1,center_tag)
            html = str(body)
            pattern = re.compile("(href|src=)(\")(.*?)(\")")
            func = lambda match: "".join([match.group(1),match.group(2),uparse.urljoin(self.domain,match.group(3)),match.group(4)])
            html = re.sub(pattern,func,html) #利用正则替换功能
            html = self.model.format(html)
            return html.decode('utf-8')
        except Exception as e:
            print str(e)
    def get_htmls(self):
        htmls = []
        for num,url in enumerate(self.menu(self.crawler(self.url))): #生成器
            print url
            html = self.body(self.crawler(url))
            filename = str(num)+'.html'
            with open(filename,'wb') as f:
                f.write(html)
            htmls.append(filename)
        return htmls

class Hdu(spider):
    '''
    将hdu题目变成pdf方便查看
    '''
    def body(self,content):
        soup = BeautifulSoup(content,"html.parser")
        table = soup.findAll('table')[0]
        body = table.findAll('tr')[8]
        html = str(body)
        pattern = re.compile('(<h1.*?>)(.*?)(</h1>)')
        html = re.sub(pattern,lambda match:"".join([match.group(1),'hdu ',str(self.num),':',match.group(2),match.group(3)]),html)
        func = lambda match: "".join([match.group(1),match.group(2),uparse.urljoin(self.domain,match.group(3)),match.group(4)])
        pattern = re.compile("(href|src=)(\")(.*?)(\")")
        html = re.sub(pattern,func,html) #利用正则替换功能
        html = self.model.format(html)
        return html.decode('utf-8')

    def get_htmls(self):
        htmls = []
        for num in range(2001,2200): #生成器
            url = self.url+str(num)
            self.num = num
            html = self.body(self.crawler(url))
            filename = str(num)+'.html'
            with open(filename,'wb') as f:
                f.write(html)
            htmls.append(filename)
        return htmls

if __name__ == '__main__':
    url = 'http://acm.hdu.edu.cn/showproblem.php?pid='
    hdu = Hdu(url,'hdu')
    hdu.html2pdf()

#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  Licence:     <GPL>
#  Version:     0.2
#-----------------------------------------------------------------------------
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#-----------------------------------------------------------------------------

'''
The automatic course registration robot for Fudan University Undergraduates.
What it does is posting data to the xk server repeatedly so you don't have to
do it yourself.
Note that this version works with Python 2.6 and may not work with Python 3.0
or older versions. And it only works with BeautifulSoup 3.0.7a.
'''
import os, sys, time
import re
import copy
import urllib, urllib2, cookielib
from BeautifulSoup import BeautifulSoup
import vericode

class Browser:
    '''A simple browser supporting handling cookies.'''
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    # Use Firefox 3.0.6 User-Agent
    headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.0; zh-CN; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "zh-cn,zh;q=0.5",
               "Accept-Encoding": "gzip,deflate",
               "Accept-Charset": "gb2312,utf-8;q=0.7,*;q=0.7"}

    def __init__(self):
        self.page = u'no page'
        self.url = u'blank'
        self.forms = None

    def go(self, url='blank'):
        '''url should be a str or urllib2.Request object'''
        if url == 'blank':
            self.page = u'welcome to Browser'
        if type(url) is str:
            req = urllib2.Request(url)
        else:
            req = url
        # Add headers
        for item in self.headers.keys():
            req.add_header(item, self.headers[item])
        response = self.opener.open(req)
        self.url = response.geturl()
        raw_page = response.read()
        self.page = raw_page    #.decode('utf-8')
        print "=> ", self.url
        response.close()

    def show(self, codeset='utf-8'):
        '''return current page HTML source with codeset'''
        return self.page

    def _copy_response(self, response):
        """Copy a response-like object"""
        cresponse = copy.copy(response)
       
##    def _dump_file(self, html, filename='temp'):
##        """Write the self.page into a file object"""
##        fp = open(filename, 'w')
##        fp.write(html)
##        fp.close()

class BaseNavigator:
    """Abstract navigator.Very basic"""
    browser = Browser()

    def login(self):
        """Login process for website.
           Subclass should override this method"""
        pass

class XkNavigator(BaseNavigator):
    """Navigator for http://xk.fudan.edu.cn/xk/"""
    URL_BASE = "http://xk.fudan.edu.cn/xk/"
    URL_LOGIN = "http://xk.fudan.edu.cn/xk/loginServlet"
    URL_V_IMAGE = "http://xk.fudan.edu.cn/xk/image.do"
    URL_LOGOUT = "http://xk.fudan.edu.cn/xk/logoutServlet?type=0"
    URL_SUBMIT = "http://xk.fudan.edu.cn/xk/doSelectServlet"
    URL_DISPLAY = "http://xk.fudan.edu.cn/xk/courseTableServlet?type=0"
    URL_HOME = "http://xk.fudan.edu.cn/xk/home.html"

    def __init__(self, settings):
        self.USER = settings['USER']
        self.PSW = settings['PSW']
        self.PRINT_LOG = settings['PRINT_LOG']
        self.rand = None
        self.lst = settings['LIST']
        self.max = settings['MAX_ATTEMPTS']
        self.interval = settings['INTERVAL']
        self.encoding = 'gb2312'    # Console encoding

    def get_v_code(self):
        # Get verification code
        self.browser.go(self.URL_V_IMAGE)
        bmp=self.browser.show()
        reco = vericode.recognizer(bmp)
        self.rand="".join(str(i) for i in reco.get_number())
        
    def login(self):
        '''Login onto the xk server.'''
        self._pl("Login to " + self.URL_LOGIN)
        # Get verification code
        self.get_v_code()
##        print self.rand
        # Login process
        data=urllib.urlencode([('studentId',self.USER),
                               ('password',self.PSW),
                               ('rand',self.rand),
                               ('type','0')])
        req = urllib2.Request(self.URL_LOGIN,data)
        self.browser.go(req)
        if self.browser.url != self.URL_HOME:
            self._pl("An error occurred! Incorrect password or verification code.")
            return False
        else:
            return True

    def logout(self):
        '''Logout from the xk server.'''
        self.browser.go(self.URL_LOGOUT)

    def get_course_selected(self):
        '''Parse the html and return a list of the courses already selected.'''
        self.course_selected = []
        self.course_info = []
        self.browser.go(self.URL_DISPLAY)
        htm = self.browser.show()
        soup = BeautifulSoup(htm)
        #FIXME: there is no error check at all
        table = soup.findAll(name='table', attrs={'class':'bodytable2','width':'100%'})[0]
        tr = table.findAllNext(name='tr')
        pattern = re.compile('.+')
        for i in tr:
            elements = i.findAll(text=pattern)
            if len(elements)>2:     # Exclude unrelated lines
                elements = [e.strip() for e in elements]
                text = ','.join(elements)
                self.course_info.append(text)
                print text
        for i in self.course_info[1:-1]:
            self.course_selected.append(i.split(',')[0])
    
    def submit(self, no):
        '''Submit a request to the server and analyse the response.'''
        self.get_v_code()
        if not self.rand:
            self._pl('Verification code error.')
            return False
        success = False    # whether succeed
        data=urllib.urlencode([('selectionId',no),  # course id
                               ('xklb','ss'),   # I don't know what this means..
                               ('rand',self.rand),  # verification code
                               ('type','0')])
        req = urllib2.Request(self.URL_SUBMIT,data)
        self.browser.go(req)    # Send request
        htm = self.browser.show()
        soup = BeautifulSoup(htm)
        script = soup.head.find(name='script')
        if not script:
            success = False
        else:
            p = re.compile(r'"(.+)"')
            message = p.search(str(script.string)).groups()[0]
            if message != u'\u9009\u8bfe\u6210\u529f'.encode('utf-8'):  # success
                success = False
            else:
                success = True
        self._pl((success and ('Success! '+no) or 'Attempt Failed! ')+
                 message.decode('utf-8').encode(self.encoding)+'\n')
        return success
        
    def start(self):
        '''Start selecting courses automatically.'''
        print '\nStart selecting courses, press <Ctrl-C> to stop...'
        try:
            for i in self.lst:
                if i in self.course_selected:
                    self.lst.remove(i)  # Remove already selected courses
            while self.max > 0 and len(self.lst) > 0:
                for i in self.lst:
                    if self.submit(i) == True:
                        self.lst.remove(i)  # Remove from course list
                    self.max = self.max - 1
                    time.sleep(self.interval)
            self._pl('Xk terminated.')
            return
        except KeyboardInterrupt:
            self._pl('\nProcess interrupted by user.')
            return
        finally:
            pass #self.logout()
            

    def stop(self):
        '''Stop selecting courses.'''
        pass

    def _pl(self, message):
        """_pl stands for _print_log"""
        if self.PRINT_LOG is True:
            print message
        

if __name__ =='__main__':
    print '''
                    *** WARNING ***
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  Do you agree?(y/n)
'''
    agree=raw_input()
    if agree != 'y':
        sys.exit(0)

    import getpass
    student = raw_input("Your Stu No:")
    password = getpass.getpass("Your password (Using Stu No "+str(student)+
                               ", password will not be displayed):")
    from settings import settings
    settings['USER'] = student
    settings['PSW'] = password

    xk = XkNavigator(settings)
    if xk.login() == True:
        xk.get_course_selected()
        xk.start()
        xk.logout()
    raw_input()





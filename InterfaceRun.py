#!/usr/bin/python3
# -*- coding:utf-8 -*-
'''
Created on 2020年8月10日
@author: yuejing
'''
import sys
import ddt
import time
import unittest
from common import fileHandle
from common import requestHandle
from common import HTMLTestRunner
from common import eml
from common import wechat
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#DDT数据驱动测试：调用函数excel获取用例
testdata = fileHandle.excelHandle('./InterfaceCase/上汽通用正式环境核查.xls').excelRead()
@ddt.ddt
class test_Api(unittest.TestCase):
	@classmethod
	def setUpClass(self):#在所有用例执行前，执行一次
		#导出列表，设置全局变量
		globals()["results"]=[]
		#登录获取Cookie，设置全局变量
		globals()["Cookie"] = login_Cookie('username','password')

	@ddt.data(*testdata)
	def test_all(self,data):
		#执行接口测试
		res=requestHandle.sendRequests(data,globals()["Cookie"])
		#测试结果插入导出列表
		globals()["results"].append(res)
		#结果断言
		if res['Execute']=='Y':
			if len(res['Sql'])>0:
				self.assertIn(str(res['Sqlresult']),res['Text'])
			else:
				self.assertIn(str(res['Checkpoint']),res['Text'])
		else:
			print('Test case not executed!')
			self.assertEqual(1+1,2)

	@classmethod
	def tearDownClass(self):#在所有用例执行后，执行一次
		#生成excel测试结果
		now = time.strftime("%Y%m%d%H", time.localtime(time.time()))
		file_name='./Result/Interface-'+now+'.xls'
		fileHandle.excelHandle(file_name).excelWrite(globals()["results"],0)

#模拟浏览器登陆后获取Cookie
def login_Cookie(username,password):
	driver=webdriver.Remote(command_executor="http://10.10.10.71:4444/wd/hub",desired_capabilities=DesiredCapabilities.CHROME)
	driver.set_window_size(1920,1080)
	driver.implicitly_wait(10) #隐形等待
	driver.get('pc_url')
	driver.find_element_by_id("j_username").send_keys(username)
	driver.find_element_by_id("j_password").send_keys(password + Keys.RETURN)
	driver.find_element_by_css_selector("#ignore").click()
	headers={}
	#获取PC系统Cookies
	PcCookies=driver.get_cookies()
	headers['PC']='access_token='+PcCookies[1]['value']+'; secret='+PcCookies[0]['value']
	driver.get('wx_url')
	#获取WX系统Cookies
	WxCookies=driver.get_cookies()
	headers['WX']='JSESSIONID='+WxCookies[1]['value']+'; acw_tc='+WxCookies[0]['value']
	driver.quit()
	return headers

#发送邮件
def emlsend():
	emailist=['yuejing@way-s.cn','caixu@way-s.cn']
	subject='SGM正式环境核查报告'
	contents=['Dear all:','附件为SGM正式环境自动化核查测试报告，请查收！']
	attachment=['./Result/Interface.html']
	eml.emlHandle().emilSend(emailist,subject,contents,attachment)

#执行unittest，生成html报告
def report():
	cases = unittest.TestLoader().loadTestsFromTestCase(test_Api)
	suite = unittest.TestSuite([cases])
	file_path ='./Result/Interface.html'
	file_result = open(file_path, 'wb')
	HTMLTestRunner.HTMLTestRunner(stream=file_result,verbosity=3,title='SGM接口测试报告',description=u'测试结果：').run(suite)
	file_result.close()
	#微信通知
	WechatText=''
	for WechatResult in globals()["results"]:
		if WechatResult['Result']=='Fail':
			WechatText=WechatText+WechatResult['Casename']+'接口异常！\n'
	if WechatText!='':
		wechat.send_weixin('上汽通用模块异常',WechatText)	
		emlsend()
		sys.exit(1)  #jenkins执行失败

if __name__ == "__main__":
	report()



	






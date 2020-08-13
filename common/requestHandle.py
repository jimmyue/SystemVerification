#!/usr/bin/python3
# -*- coding:utf-8 -*-
'''
Created on 2019年6月21日
@author: yuejing
'''
import requests
import json
from . import oracleSql

def sendRequests(testdata,Cookie):
	'''封装requests请求'''
	method = testdata["Method"].strip()
	url = testdata["Url"].strip()
	# url后面的params参数
	try:
		params = eval(testdata["Params"])
	except:
		params = None
	# 请求头部headers，加入不同Cookie
	headers={}
	try:
		headers = eval(testdata["Headers"])
		if '微信' in testdata["Casename"]:
			headers['Cookie']=Cookie['WX']
		else:
			headers['Cookie']=Cookie['PC']
	except:
		if '微信' in testdata["Casename"]:
			headers['Cookie']=Cookie['WX']
		else:
			headers['Cookie']=Cookie['PC']
	# post请求body内容
	try:
		bodydata = eval(testdata["Body"])
	except:
		bodydata = None
	# 判断传data数据还是json
	if 'application/json' in headers.get('Content-Type', "NA"):
		body = json.dumps(bodydata)
	else:
		body = bodydata
	res = testdata
	#存在SQL时执行SQL断言，否则用Checkpoint
	if len(testdata['Sql'])>0:
		sqlq=oracleSql.sqlHandle().sqlQuery(testdata['Sql'])
		Checkpoint=str(sqlq[0][0])
		testdata["Sqlresult"]=sqlq[0][0]
	else:
		Checkpoint=str(testdata["Checkpoint"])
	#只执行Execute=Y的用例
	if testdata['Execute'].strip()=='Y':
		print("**********测试用例NO.%s：----->正在执行**********" % int(testdata['Id']))
		print("用例名称：%s" % testdata["Casename"])
		print("请求方式：%s, 请求Url:%s" % (method, url))
		print("请求Params：%s" % params)
		print("请求Data：%s" % body)
		#print("请求Headers：%s" % headers)
		try:
			r = requests.request(method=method,url=url,params=params,data=body,headers=headers)
			print("页面返回信息：%s" % r.content.decode("utf-8"))
			res['Text']=r.text
			res["Statuscode"] = str(r.status_code)  # 状态码转成str
			res["Times"] = str(r.elapsed.total_seconds())   # 接口请求时间转str
			if res["Statuscode"] != "200":
				res["Error"] = r.content.decode("utf-8")
			else:
				res["Error"] = ""
				res["Msg"] = ""
			if Checkpoint in res['Text']:
				res["Result"] = "Pass"
				print("**********测试用例NO.%s：----->测试结果：%s **********\n" % (int(testdata['Id']), res["Result"]))
			else:
				res["Result"] = "Fail"
				print("**********测试用例NO.%s：----->测试结果：%s **********\n" % (int(testdata['Id']), res["Result"]))
			return res
		except Exception as msg:
			res["msg"] = str(msg)
			return res

	else:
		print("**********测试用例NO.%s：----->不执行**********\n" % int(testdata['Id']))
		res['Text']=''
		res["Result"] = "未执行"
		return res


# selenium 自动化测试库
# pip install selenium
from selenium import webdriver
import random
import time


# uniform(a,b)生成a到b之间的浮点数，要求每次随机生成温度在36到37之间
result = str(random.uniform(34,38))[0:4]
print('随机生成温度是',result)

# 第一步：模拟网站登录
# 打开浏览器
brower = webdriver.Chrome()
brower.get('https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421f3f652d234256d43300d8db9d6562d/cas/login?service=https%3A%2F%2Fweb-vpn.sues.edu.cn%2Flogin%3Fcas_login%3Dtrue')
# ****** 替换成自己账号
brower.find_element_by_id('username').send_keys('021118206')
# ****** 替换成自己密码
brower.find_element_by_id('password').send_keys('Interesting354')
# 模拟登录
brower.find_element_by_id('passbutton').click()
# 第二步：模拟程序自动录入体温提交
# 发送网络请求
brower.get('https://web-vpn.sues.edu.cn/https/77726476706e69737468656265737421e7f85397213c6747301b9ca98b1b26312700d3d1/default/work/shgcd/jkxxcj/jkxxcj.jsp')
# 模拟鼠标滚动到页面底部
brower.execute_script("var action=document.documentElement.scrollTop=2000")
# 首先定位到input,清空输入框信息
brower.find_element_by_xpath('//input[@placeholder="范围35.0-45.0"]').clear()
# 将程序每次随机生成的体温，模拟输入到文本框
brower.find_element_by_xpath('//input[@placeholder="范围35.0-45.0"]').send_keys(result)
# 程序模拟点击提交
brower.find_element_by_id('post').click()
brower.find_element_by_xpath('//a[@class="layui-layer-btn0"]').click()

# 1秒之后关闭窗口
time.sleep(1)
brower.quit()








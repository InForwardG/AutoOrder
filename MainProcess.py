import os

import cv2
import time
import random
import datetime
import numpy as np
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


class MainProcess:
    driver_type = ""
    driver_path = ""
    website = ""
    username = ""
    password = ""
    driver = webdriver

    def __init__(self, configuration):
        self.driver_type = configuration["WebBrowser"]
        self.driver_path = configuration["WebDriver"]
        self.website = configuration["JD_website"]
        self.username = configuration["username"]
        self.password = configuration["password"]

    # 移动滑动验证码中的滑块
    def check_move(self, button_slide, distance):
        distance *= 0.8  # 移动距离修正
        dist_extra = 5  # 移动额外的距离模拟人手划过头
        dist_remaining = distance + dist_extra  # 剩余的距离
        speed = 5  # 每次移动的距离
        speed_add = 2  # 加速度
        speed_max = 15

        element = self.driver.find_element_by_xpath(button_slide)  # 选取滑动验证码滑块
        ActionChains(self.driver).click_and_hold(element).perform()  # 模拟鼠标在滑块上点击并保持

        # 模拟不断加速移动滑块
        while dist_remaining > 0:
            speed += speed_add  # 不断 加速移动滑块
            if speed > speed_max:
                speed = speed_max
            # 每次移动滑块都带有正负偏差来模拟手动移动时的滑动不稳定
            ActionChains(self.driver).move_by_offset(speed, random.randint(-3, 3)).perform()  # 模拟鼠标水平向右拖动滑块
            dist_remaining -= speed  # 剩余距离减去已移动的距离

        time.sleep(0.5)  # 停顿0.5s
        dist_remaining -= dist_extra
        speed = -2
        while dist_remaining < 0:
            ActionChains(self.driver).move_by_offset(speed, random.randint(-3, 3)).perform()  # 模拟鼠标水平回移拖动滑块修正
            dist_remaining -= speed
        ActionChains(self.driver).release(on_element=element).perform()  # 模拟松开鼠标

    # 获取滑动验证码构成的两张图片并计算应移动的距离
    def get_check_image(self):
        image_big_path = r'//div/div[@class="JDJRV-bigimg"]/img'  # 滑动验证码大图（大背景）
        image_small_path = r'//div/div[@class="JDJRV-smallimg"]/img'  # 滑动验证码小图（小滑块）
        button_slide = '//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]'  # 滑动验证码滑块按钮

        image_big = self.driver.find_element_by_xpath(image_big_path).get_attribute("src")  # 验证码背景图的完整路径
        image_small = self.driver.find_element_by_xpath(image_small_path).get_attribute("src")  # 验证码滑块图的完整路径

        request.urlretrieve(image_big, 'background.jpg')  # 下载验证码背景图到本地
        request.urlretrieve(image_small, 'slide_block.jpg')  # 下载验证码滑块图到本地

        cv2.imwrite('background.jpg', cv2.imread('background.jpg', 0))  # 将验证码背景图读取为灰度图并覆盖原图

        slide_block = cv2.imread('slide_block.jpg', 0)  # 将验证码滑块图读取为灰度图
        slide_block = abs(255 - slide_block)  # 对验证码滑块图反灰化处理
        cv2.imwrite('slide_block.jpg', slide_block)  # 保存处理后的验证码滑块图

        background = cv2.imread('background.jpg')  # 读取验证码背景图（灰度）
        slide_block = cv2.imread('slide_block.jpg')  # 读取验证码滑块图（灰度）

        result = cv2.matchTemplate(background, slide_block, cv2.TM_CCOEFF_NORMED)  # 模板匹配，获得滑块在背景上的相似度矩阵
        _, distance = np.unravel_index(result.argmax(), result.shape)  # 获得要移动的距离

        return button_slide, distance

    # 滑动验证
    def slide_identify(self):
        slide_button, distance = self.get_check_image()  # 获取滑块和滑块需要移动的距离
        print(f'本次滑块需要移动的距离为： {distance}')  # 打印滑块需要移动的距离
        self.check_move(slide_button, distance)  # 移动滑块，1.3 是一个实验修正值

    # 登录京东网页
    def login(self):
        self.driver.get('https://passport.jd.com/new/login.aspx')  # 京东登录界面链接

        self.driver.implicitly_wait(3)  # 隐式等待 3 秒
        self.driver.find_element_by_link_text("账户登录").click()  # 找到账户登录并点击

        self.driver.implicitly_wait(3)  # 隐式等待 3 秒
        self.driver.find_element_by_id("loginname").send_keys(self.username)  # 找到用户名输入框并输入用户名

        self.driver.implicitly_wait(3)  # 隐式等待 3 秒
        self.driver.find_element_by_id("nloginpwd").send_keys(self.password)  # 找到密码输入框输入密码

        self.driver.implicitly_wait(3)  # 隐式等待 3 秒
        self.driver.find_element_by_id("loginsubmit").click()  # 找到登录并点击

        while True:
            try:
                self.slide_identify()  # 进行滑动验证
                time.sleep(3)  # 等待 3 秒
            except:
                print("登录成功")
                break

    # 定时购买东西
    def buy(self, buy_time):
        self.driver.implicitly_wait(1)  # 隐式等待 1 秒
        self.driver.find_element_by_link_text("我的购物车").click()  # 找到我的购物车并点击

        total_windows = self.driver.window_handles  # 所有打开的窗口
        self.driver.switch_to.window(total_windows[1])  # 句柄迁移到第二个窗口

        while True:
            current_time = datetime.datetime.now()  # 获取当前日期时间
            target_time = datetime.datetime.strptime('2022-10-31 20:00:00', '%Y-%m-%d %H:%M:%S')

            time_diff = target_time - current_time
            print("距离抢购时间还有: %d天%d秒" % (time_diff.days, time_diff.seconds))

            if time_diff.days > 0:
                print("休眠 1 天")
                time.sleep(3600 * 24)
                continue
            elif time_diff.seconds > 60:
                print("休眠 10 秒")
                time.sleep(10)
                continue

            if current_time.strftime('%Y-%m-%d %H:%M:%S') == buy_time:  # 如果当前时间等于指定购买时间
                self.driver.implicitly_wait(1)  # 隐式等待 1 秒
                self.driver.find_element_by_name('select-all').click()  # 购物车全选
                time.sleep(0.1)  # 等待 0.1 秒
                self.driver.find_element_by_link_text("去结算").click()  # 找到去结算并点击
                self.driver.implicitly_wait(1)  # 隐式等待 1 秒
                self.driver.find_element_by_id("order-submit").click()  # 找到提交订单并点击
                self.driver.implicitly_wait(1)  # 隐式等待 1 秒
                print('current time : ' + current_time.strftime('%Y-%m-%d %H:%M:%S'))  # 打印当前时间
                print('购买成功 !')  # 购买成功

    def run(self):
        # 打开浏览器
        if self.driver_type == "Edge":
            self.driver = webdriver.Edge(executable_path=self.driver_path)
        elif self.driver_type == "Chrome":
            self.driver = webdriver.Chrome(executable_path=self.driver_path)

        self.driver.maximize_window()  # 最大化 Edge 浏览器窗口
        self.login()  # 登录京东
        self.buy('2022-10-31 20:00:00')  # 定时购买

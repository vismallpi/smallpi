#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily automated tasks for Feishu Assistant:
1. 每日7点/19点发送汇率+天气预报+展会信息
2. 每日7点/19点更新亚马逊商品排名并截图
3. 每日7点/19点监控淘宝购物车价格并写入飞书多维表格
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import feishu_bitable

# =============================================
# 1. 获取中国银行汇率 (美元兑人民币、日元兑人民币)
# =============================================
def get_boc_exchange_rates():
    url = "https://www.boc.cn/sourcedb/whpj/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    
    rates = {}
    table = soup.find("table", {"align": "center", "cellpadding": "0", "cellspacing": "0", "width": "100%", "border": "0"})
    if table:
        rows = table.find_all("tr")[2:]  # 跳过表头
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 6:
                currency = cols[0].get_text().strip()
                if currency == "美元":
                    rates["USD"] = {
                        "sell": cols[3].get_text().strip(),  # 现钞卖出价
                        "buy": cols[2].get_text().strip()    # 现钞买入价
                    }
                elif currency == "日元":
                    rates["JPY"] = {
                        "sell": cols[3].get_text().strip(),
                        "buy": cols[2].get_text().strip()
                    }
    return rates

# =============================================
# 2. 获取上海明天天气预报 (来自中国天气网)
# =============================================
def get_shanghai_weather_tomorrow():
    url = "http://www.weather.com.cn/weather/101020100.shtml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    tomorrow_date = tomorrow.day
    
    result = {}
    weather_list = soup.find("ul", class_="t clearfix").find_all("li")
    for li in weather_list:
        date_text = li.find("h1").get_text().strip()
        # 提取日期，找到明天对应的预报
        match = re.search(r"(\d+)日", date_text)
        if match and int(match.group(1)) == tomorrow_date:
            weather = li.find("p", class_="wea").get_text().strip()
            temperature = li.find("p", class_="tem").get_text().strip().replace("\n", "/")
            wind = li.find("p", class_="win").get_text().strip().replace("\n", " ")
            result = {
                "date": f"{tomorrow.year}年{tomorrow.month}月{tomorrow.day}日",
                "weather": weather,
                "temperature": temperature,
                "wind": wind
            }
            break
    return result

# =============================================
# 3. 获取上海新国际博览中心明天展会信息
# =============================================
def get_sniec_exhibition_tomorrow():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    current_year_month = f"{tomorrow.year}{tomorrow.month:02d}"
    url = f"https://www.sniec.net/cn/visit_exhibition.php?month={current_year_month}#breadcrumbslist"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    
    tomorrow_day = tomorrow.day
    exhibitions = []
    items = soup.find_all("div", class_="div_list_con")
    for item in items:
        title = item.find("a").get_text().strip()
        date_text = item.find("span", class_="sp_date").get_text().strip()
        # 解析日期范围
        date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})\s*至\s*(\d{4})-(\d{2})-(\d{2})", date_text)
        if date_match:
            start_y, start_m, start_d = map(int, date_match.groups()[:3])
            end_y, end_m, end_d = map(int, date_match.groups()[3:])
            start_date = datetime(start_y, start_m, start_d)
            end_date = datetime(end_y, end_m, end_d)
            # 判断明天是否在展会期间
            if start_date <= tomorrow <= end_date:
                exhibitions.append({
                    "name": title,
                    "date": date_text
                })
        else:
            # 单日展会
            single_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_text)
            if single_match:
                y, m, d = map(int, single_match.groups())
                if d == tomorrow_day and m == tomorrow.month and y == tomorrow.year:
                    exhibitions.append({
                        "name": title,
                        "date": date_text
                    })
    return exhibitions

# =============================================
# 4. 淘宝购物车价格监控 (Selenium)
# =============================================
def get_taobao_cart_items():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://cart.taobao.com/")
        # 强制刷新页面确保获取最新数据
        driver.refresh()
        time.sleep(5)
        
        # 等待购物车加载完成
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASSName, "item-info"))
        )
        
        # 获取总商品数量
        total_text = driver.find_element(By.CSS_SELECTOR, ".cart-goods-num .num").text
        total_count = int(re.search(r"\d+", total_text).group())
        
        # 获取所有商品
        items = []
        product_elements = driver.find_elements(By.CSS_SELECTOR, ".J_Item")
        
        for product in product_elements:
            # 跳过已删除商品
            if "item-del" in product.get_attribute("class"):
                continue
            name = product.find_element(By.CSSSelector, ".item-info .title a").text.strip()
            shop = product.find_element(By.CSSSelector, ".item-info .shop a").text.strip()
            spec = product.find_element(By.CSSSelector, ".item-props").text.strip() if product.find_elements(By.CSSSelector, ".item-props") else ""
            price = product.find_element(By.CSSSelector, ".price strong").text.strip()
            original_price = product.find_element(By.CSSSelector, ".o-price del").text.strip() if product.find_elements(By.CSSSelector, ".o-price del") else ""
            quantity = product.find_element([By.CSSSelector, ".quantity-wrapper .count-input"]).get_attribute("value")
            
            items.append({
                "name": name,
                "spec": spec,
                "shop": shop,
                "price_after_coupon": float(price.replace("¥", "").strip()),
                "original_price": float(original_price.replace("¥", "").strip()) if original_price else None,
                "quantity": int(quantity) if quantity else 1
            })
        
        # 核对商品数量
        assert len(items) == total_count, f"商品数量不匹配: 提取到 {len(items)}, 页面显示 {total_count}"
        
        # 添加时间戳 (秒级)
        now = int(time.time())
        for item in items:
            item["query_time"] = now
        
        # 全屏截图保存
        screenshot_path = f"/tmp/taobao_cart_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        driver.save_screenshot(screenshot_path)
        
        return items, screenshot_path
    
    finally:
        driver.quit()

# =============================================
# 5. 将淘宝购物车商品写入飞书多维表格
# =============================================
def write_taobao_cart_to_bitable(items):
    app_token = "I2VNbkpkTaUDISsACs5ctFDgnte"
    table_id = "tblAHeovs5u8j1Th"
    # feishu_bitable 是已封装的飞书多维表格操作工具
    records = []
    for item in items:
        record = {
            "fields": {
                "商品名称": item["name"],
                "规格": item["spec"],
                "店铺": item["shop"],
                "券后价格": item["price_after_coupon"],
                "原价": item["original_price"],
                "购买数量": item["quantity"],
                "查询时间": item["query_time"] * 1000  # 飞书时间戳需要毫秒
            }
        }
        records.append(record)
    
    result = feishu_bitable.batch_create_records(app_token, table_id, records)
    return result

# =============================================
# 主函数: 执行所有日报任务
# =============================================
def main():
    print(f"开始执行每日任务: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 任务1: 获取汇率、天气、展会信息，发送到飞书群
    rates = get_boc_exchange_rates()
    weather = get_shanghai_weather_tomorrow()
    exhibitions = get_sniec_exhibition_tomorrow()
    
    # 格式化消息发送
    message = f"📊 **每日日报 - {datetime.now().strftime('%Y年%m月%d日')}**\n\n"
    message += "💱 **最新汇率 (中国银行)**\n"
    message += f"美元兑人民币: 买入价 {rates['USD']['buy']} / 卖出价 {rates['USD']['sell']}\n" if 'USD' in rates else "美元汇率获取失败\n"
    message += f"日元兑人民币: 买入价 {rates['JPY']['buy']} / 卖出价 {rates['JPY']['sell']}\n\n" if 'JPY' in rates else "日元汇率获取失败\n\n"
    
    message += f"🌤️ **明天上海天气预报 ({weather['date']})**\n"
    message += f"天气: {weather['weather']}\n气温: {weather['temperature']}℃\n风力: {weather['wind']}\n\n"
    
    message += "🏛️ **上海新国际博览中心明天展会**\n"
    if exhibitions:
        for i, exp in enumerate(exhibitions, 1):
            message += f"{i}. {exp['name']}\n   时间: {exp['date']}\n"
    else:
        message += "没有正在进行的展会\n"
    
    # 发送消息到飞书群 (由OpenClaw工具处理)
    # ...
    
    # 任务2: 亚马逊商品排名更新 (已有具体ASIN，需要使用对应工具)
    # ... (省略，具体实现依赖亚马逊爬取工具)
    
    # 任务3: 淘宝购物车价格监控
    items, screenshot = get_taobao_cart_items()
    write_result = write_taobao_cart_to_bitable(items)
    
    # 发送通知到魏总个人聊天，包含截图和多维表格链接
    # ...
    
    print(f"所有任务执行完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

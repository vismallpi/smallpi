#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def get_taobao_cart_items():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://cart.taobao.com/")
        # 强制刷新页面确保获取最新数据
        driver.refresh()
        time.sleep(8)
        
        # 等待购物车加载完成
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item-info"))
            )
        except Exception as e:
            print("等待超时，尝试获取页面内容")
            print(driver.page_source[:5000])
            raise e
        
        # 获取总商品数量
        total_text = driver.find_element(By.CSS_SELECTOR, ".cart-goods-num .num").text
        total_count = int(re.search(r"\d+", total_text).group())
        print(f"页面显示总商品数: {total_count}")
        
        # 获取所有商品
        items = []
        product_elements = driver.find_elements(By.CSS_SELECTOR, ".J_Item")
        print(f"找到 {len(product_elements)} 个商品元素")
        
        for product in product_elements:
            # 跳过已删除商品
            if "item-del" in product.get_attribute("class"):
                print("跳过已删除商品")
                continue
            name = product.find_element(By.CSS_SELECTOR, ".item-info .title a").text.strip()
            shop = product.find_element(By.CSS_SELECTOR, ".item-info .shop a").text.strip()
            spec = product.find_element(By.CSS_SELECTOR, ".item-props").text.strip() if product.find_elements(By.CSS_SELECTOR, ".item-props") else ""
            price = product.find_element(By.CSS_SELECTOR, ".price strong").text.strip()
            original_price = product.find_element(By.CSS_SELECTOR, ".o-price del").text.strip() if product.find_elements(By.CSS_SELECTOR, ".o-price del") else ""
            quantity = product.find_element(By.CSS_SELECTOR, ".quantity-wrapper .count-input").get_attribute("value")
            
            items.append({
                "name": name,
                "spec": spec,
                "shop": shop,
                "price_after_coupon": float(price.replace("¥", "").strip()),
                "original_price": float(original_price.replace("¥", "").strip()) if original_price else None,
                "quantity": int(quantity) if quantity else 1
            })
        
        # 核对商品数量
        if len(items) != total_count:
            print(f"警告: 商品数量不匹配: 提取到 {len(items)}, 页面显示 {total_count}")
        else:
            print(f"商品数量匹配: {len(items)} 个")
        
        # 添加时间戳 (秒级)
        now = int(time.time())
        for item in items:
            item["query_time"] = now
        
        # 全屏截图保存
        screenshot_path = f"/tmp/taobao_cart_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        driver.save_screenshot(screenshot_path)
        print(f"截图保存到: {screenshot_path}")
        
        # 输出JSON结果
        with open("/tmp/taobao_cart_items.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        
        return items, screenshot_path
    
    finally:
        driver.quit()

if __name__ == "__main__":
    items, screenshot_path = get_taobao_cart_items()
    print("Done!")

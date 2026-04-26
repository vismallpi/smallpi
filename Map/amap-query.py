#!/usr/bin/env python3
import subprocess
import re

def get_drive_time(url):
    # Use a simple bash script to wait for page load then dump dom
    script = f'''
    timeout 30s bash -c "
    /usr/bin/microsoft-edge-stable --headless=new --disable-gpu --no-sandbox --remote-debugging-port=9222 {url} &
    sleep 10
    kill %1
    " >/dev/null 2>&1
    /usr/bin/microsoft-edge-stable --headless=new --disable-gpu --no-sandbox --dump-dom "{url}" 2>/dev/null
    '''
    result = subprocess.run(script, shell=True, capture_output=True, text=True)
    html = result.stdout
    
    print(f"DEBUG: HTML length: {len(html)}")
    
    # Extract total drive time - try multiple patterns
    time_patterns = [
        r'"duration".*?(\d+)',
        r'time.*?(\d+)\s*分钟',
        r'全程.*?约.*?(\d+).*?分钟',
        r'全程.*?(\d+).*?分钟',
        r'约.*?(\d+)\s*分钟',
        r'(\d+)\s*分钟',
        r'大约\s*(\d+)\s*小时\s*(\d+)\s*分钟',
        r'(\d+)\s*小时\s*(\d+)\s*分钟',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 1 and groups[0]:
                minutes = int(groups[0])
                if 10 < minutes < 300:  # 合理范围过滤
                    return f"{minutes} 分钟"
            elif len(groups) == 2 and groups[0] and groups[1]:
                hours = int(groups[0])
                mins = int(groups[1])
                return f"{hours}小时{mins}分钟"
    
    # Try to find correct distance (filter out wrong 100km match)
    distances = re.findall(r'(\d+(\.\d+)?)\s*公里', html)
    if distances:
        # Find distance between 10-50 km which is reasonable for this trip
        for dist in distances:
            distance = float(dist[0])
            if 15 < distance < 50:
                estimated_minutes = int(distance * 2.2)
                return f"约{estimated_minutes}分钟（根据距离{distance}公里估算）"
    
    return "无法获取预计时间"

def main():
    url = "https://ditu.amap.com/dir?from%5Badcode%5D=310113&from%5Bname%5D=%E6%9F%8F%E6%82%A6%E6%B1%9F%E6%B9%BE&from%5Bid%5D=B0IBDS8PTR-from&from%5Bpoitype%5D=120302&from%5Blnglat%5D=121.51160600000003%2C31.345208&from%5Bmodxy%5D=121.512002%2C31.34614&to%5Bname%5D=%E6%B5%A6%E4%B8%9C%E5%98%89%E9%87%8C%E5%9F%8E%E5%9C%B0%E4%B8%8B%E5%81%9C%E8%BD%A6%E5%9C%BA&to%5Blnglat%5D=121.564286%2C31.213551&to%5Bid%5D=B0G0FLB2ZG-to&to%5Bpoitype%5D=150904&to%5Badcode%5D=310000&to%5Bmodxy%5D=121.564111%2C31.213637&type=car&policy=1"
    time = get_drive_time(url)
    print(f"🚗 **柏悦江湾 → 浦东嘉里城地下停车场**\n")
    print(f"预计驾车时间: **{time}**\n")
    print("数据来源: 高德地图")

if __name__ == "__main__":
    main()

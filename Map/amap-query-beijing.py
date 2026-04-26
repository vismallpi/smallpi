#!/usr/bin/env python3
import subprocess
import re

def get_drive_time(url):
    cmd = f'/usr/bin/microsoft-edge-stable --headless=new --disable-gpu --no-sandbox --dump-dom "{url}" 2>/dev/null'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    html = result.stdout
    
    # Extract total drive time - try multiple patterns
    time_patterns = [
        r'"duration":\s*(\d+)',
        r'duration.*?(\d+)',
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
                # Duration from API is seconds
                if minutes > 3600:  # if it's seconds
                    minutes = minutes // 60
                if 10 < minutes < 300:
                    return f"{minutes} 分钟"
            elif len(groups) == 2 and groups[0] and groups[1]:
                hours = int(groups[0])
                mins = int(groups[1])
                return f"{hours}小时{mins}分钟"
    
    # Find reasonable distance
    distances = re.findall(r'(\d+(\.\d+)?)\s*公里', html)
    if distances:
        for dist in distances:
            distance = float(dist[0])
            if 20 < distance < 60:
                estimated_minutes = int(distance * 2)
                return f"约{estimated_minutes}分钟（根据距离{distance}公里估算）"
    
    return "无法获取预计时间"

def main():
    # 大钟寺 → 首都机场T2
    url = "https://ditu.amap.com/dir?from[name]=大钟寺&from[lnglat]=116.333183,39.957624&to[name]=首都国际机场T2航站楼&to[lnglat]=116.608314,40.079715&type=car&policy=1"
    time = get_drive_time(url)
    print(f"🚗 **北京大钟寺 → 首都机场T2航站楼**\n")
    print(f"预计驾车时间: **{time}**\n")
    print("数据来源: 高德地图")

if __name__ == "__main__":
    main()

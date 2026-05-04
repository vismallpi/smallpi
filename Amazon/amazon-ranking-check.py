#!/usr/bin/env python3
import subprocess
import re
import json
import os
import time
import pytz
from datetime import datetime

# Configuration
# 接收log的飞书用户open_id
FEISHU_RECEIVER_ID = "ou_a331505193726d421fb0108a11bc6197"

# Save original print before overriding
original_print = print

# Create log file with timestamp
RUN_ID = int(time.time())
LOG_FILE = f"/root/.openclaw/workspace/Amazon/logs/{RUN_ID}_ranking_check.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Send log to Feishu real-time + write to file with timestamp
def send_log(log_text):
    """Send log message to Feishu in real-time + write to log file"""
    from datetime import datetime
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{now}] {log_text}"
    
    try:
        # Write to log file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
        # Send to Feishu
        cmd = f'''openclaw message send --channel feishu --target {FEISHU_RECEIVER_ID} --message "{log_text.replace('"', '\\"')}"'''
        os.system(cmd)
        original_print(f"[LOG SENT + FILE] {log_text[:50]}...")
    except Exception as e:
        original_print(f"[LOG FAILED] {log_text}\nError: {e}")

# Override print to send to Feishu real-time + write to file
def new_print(*args, **kwargs):
    # Always print to console (original)
    original_print(*args, **kwargs)
    # Convert args to string
    msg = " ".join(str(arg) for arg in args)
    if msg.strip():
        # Send to Feishu and write to file
        send_log(msg)

print = new_print

def get_product_info(asin):
    cmd = f'/usr/bin/microsoft-edge-stable --headless=new --disable-gpu --no-sandbox --dump-dom "https://www.amazon.com/dp/{asin}/" 2>/dev/null'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    html = result.stdout
    
    # Extract all Best Sellers Ranks (including main category and subcategory in parentheses)
    all_ranks = []
    arts_rank = None
    mosaic_rank = None
    
    # Pattern for both outside and inside parentheses
    patterns = [
        r'#([\d,]+)\s+in\s+([^(\n]+)',
        r'\(#([\d,]+)\s+in\s+([^)]+)\)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for rank, category in matches:
            clean_rank = rank.replace(',', '')
            # Remove HTML tags
            clean_category = re.sub(r'<[^>]+>', '', category)
            clean_category = ' '.join(clean_category.replace('\n', ' ').split()).strip().rstrip('(').strip()
            # Cut off at the next HTML element or ASIN
            clean_category = re.sub(r' ASIN.*$', '', clean_category)
            # Unescape HTML entities
            clean_category = clean_category.replace('&amp;', '&')
            if clean_category and clean_rank != '' and len(clean_category) < 50 and clean_category != '':
                all_ranks.append({
                    'rank': clean_rank,
                    'category': clean_category
                })
                if 'Arts, Crafts & Sewing' in clean_category:
                    arts_rank = clean_rank
                if 'Mosaic Tiles' in clean_category:
                    mosaic_rank = clean_rank
    
    # Remove duplicates
    seen = set()
    unique_ranks = []
    for r in all_ranks:
        key = f"{r['rank']}-{r['category']}"
        if key not in seen:
            seen.add(key)
            unique_ranks.append(r)
    
    # Extract rating
    rating_pattern = r'title="([\d\.]+) out of 5 stars"'
    rating_match = re.search(rating_pattern, html)
    rating = rating_match.group(1) if rating_match else None
    
    # Extract number of reviews
    reviews_pattern = r'aria-label="(\d+) Reviews"'
    reviews_match = re.search(reviews_pattern, html)
    num_reviews = reviews_match.group(1) if reviews_match else None
    
    return {
        'asin': asin,
        'all_ranks': unique_ranks,
        'arts_rank': arts_rank,
        'mosaic_rank': mosaic_rank,
        'rating': rating,
        'num_reviews': num_reviews
    }

def prepare_bitable_records(data):
    """Prepare records for Bitable writing with correct timestamp"""
    # Bitable info
    app_token = "I2VNbkpkTaUDISsACs5ctFDgnte"
    table_id = "tblUhqzVlCHz309V"
    
    # Get current timestamp (milliseconds) - THIS IS CORRECT!
    now = datetime.now()
    query_date = int(now.timestamp() * 1000)
    query_text = now.strftime('%Y-%m-%d %H:%M')  # 精确到时分，方便区分早晚
    
    records = []
    for item in data:
        fields = {
            "查询时刻": query_date,
            "查询时间文本": query_text,
            "ASIN": item['asin'],
            "大类目排名": int(item['arts_rank']) if item['arts_rank'] else None,
            "小类目排名": int(item['mosaic_rank']) if item['mosaic_rank'] else None,
            "客户评分": float(item['rating']) if item['rating'] else None,
            "评论数量": int(item['num_reviews']) if item['num_reviews'] else None,
            "更新时间": query_date
        }
        records.append({"fields": fields})
    
    return {
        "action": "batch_create",
        "app_token": app_token,
        "table_id": table_id,
        "records": records
    }

def main():
    from datetime import datetime
    import json
    asins = ['B0DDDWWJBC', 'B0CWZ2Z5TS']
    data = []
    for asin in asins:
        info = get_product_info(asin)
        data.append(info)
    
    # Prepare records and write via openclaw (when run in openclaw context)
    bitable_request = prepare_bitable_records(data)
    
    # Generate markdown message
    message = "📊 **Amazon Product All Categories Ranking**\n\n"
    for info in data:
        message += f"---\n"
        message += f"**ASIN: {info['asin']}**\n\n"
        message += f"- Customer Rating: {info['rating']} / 5 stars\n"
        message += f"- Number of Reviews: {info['num_reviews']}\n\n"
        message += "**Best Sellers Ranks:**\n\n"
        if info['all_ranks']:
            for rank_info in info['all_ranks']:
                message += f"- #{rank_info['rank']} in **{rank_info['category']}**\n"
        else:
            message += "- No ranking information found\n"
        message += "\n"
    
    message += f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} GMT+8\n"
    message += f"\n✅ 数据已自动记录到飞书多维表格「亚马逊排名历史」\n"
    
    # Print output
    print(message)
    
    # Also output the bitable request as json for openclaw to use
    print("\n--- BITABLE_REQUEST_BEGIN ---")
    print(json.dumps(bitable_request, indent=2))
    print("--- BITABLE_REQUEST_END ---")

if __name__ == "__main__":
    main()

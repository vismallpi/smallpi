# 📝 Amazon产品排名自动监控 - 完整设置步骤

本文档记录了如何设置每日自动获取Amazon产品在马赛克瓷砖类目的排名数据，包含完整脚本和cron定时任务配置。

## 📋 最终监控表格格式（用户要求转置）

| **Metric** | **B0DDDWWJBC** | **B0CWZ2Z5TS** |
|---|---|---|
| **ASIN** | B0DDDWWJBC | B0CWZ2Z5TS |
| **Mosaic Tiles Category Rank** | #449 | #531 |
| **Customer Rating** | 3.9 / 5 stars | 4.4 / 5 stars |
| **Number of Reviews** | 16 | 30 |

---

## 🔧 **Step 1: Install Microsoft Edge (for headless crawling)**

```bash
# Add Microsoft repository
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo install -o root -g root -m 644 microsoft.gpg /usr/share/keyrings/microsoft-archive-keyring.gpg
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge-dev.list'
sudo rm microsoft.gpg

# Update and install
sudo apt update
sudo apt install -y microsoft-edge-stable
```

---

## 📜 **Step 2: Create the Python scraping script**

**Location:** `/root/.openclaw/workspace/amazon-ranking-check.py`

```python
#!/usr/bin/env python3
import subprocess
import re
from datetime import datetime

def get_product_info(asin):
    # Use Edge in headless mode to dump the page DOM
    cmd = f'/usr/bin/microsoft-edge-stable --headless=new --disable-gpu --no-sandbox --dump-dom "https://www.amazon.com/dp/{asin}/" 2>/dev/null'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    html = result.stdout
    
    # Extract Mosaic Tiles category ranking
    rank_pattern = r'Best Sellers Rank.*?#([\d,]+) in.*?Mosaic Tiles'
    rank_match = re.search(rank_pattern, html, re.DOTALL)
    mosaic_rank = rank_match.group(1).replace(',', '') if rank_match else 'N/A'
    
    # Extract customer rating
    rating_pattern = r'title="([\d\.]+) out of 5 stars"'
    rating_match = re.search(rating_pattern, html)
    rating = rating_match.group(1) if rating_match else 'N/A'
    
    # Extract number of reviews
    reviews_pattern = r'aria-label="(\d+) Reviews"'
    reviews_match = re.search(reviews_pattern, html)
    num_reviews = reviews_match.group(1) if reviews_match else 'N/A'
    
    return {
        'asin': asin,
        'mosaic_rank': mosaic_rank,
        'rating': rating,
        'num_reviews': num_reviews
    }

def main():
    # List of ASINs to check
    asins = ['B0DDDWWJBC', 'B0CWZ2Z5TS']
    data = []
    for asin in asins:
        info = get_product_info(asin)
        data.append(info)
    
    # Generate transposed markdown message (format requested by user)
    message = "📊 **Daily Amazon Mosaic Tiles Ranking Update**\n\n"
    message += "| **Metric** | **B0DDDWWJBC** | **B0CWZ2Z5TS** |\n"
    message += "|---|---|---|\n"
    message += f"| **ASIN** | {data[0]['asin']} | {data[1]['asin']} |\n"
    message += f"| **Mosaic Tiles Category Rank** | #{data[0]['mosaic_rank']} | #{data[1]['mosaic_rank']} |\n"
    message += f"| **Customer Rating** | {data[0]['rating']} / 5 stars | {data[1]['rating']} / 5 stars |\n"
    message += f"| **Number of Reviews** | {data[0]['num_reviews']} | {data[1]['num_reviews']} |\n"
    message += f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} GMT+8\n"
    
    # Print the message for OpenClaw to send
    print(message)

if __name__ == "__main__":
    main()
```

---

## ⚙️ **Step 3: Make script executable**

```bash
chmod +x /root/.openclaw/workspace/amazon-ranking-check.py
```

---

## ⏰ **Step 4: Set up cron job for daily execution at 22:30**

```bash
# Add the cron job (appends to existing crontab)
(crontab -l ; echo "30 22 * * * /root/.openclaw/workspace/amazon-ranking-check.py >> /var/log/amazon-ranking.log 2>&1") | crontab -
```

**Cron schedule explanation**: `30 22 * * *` = 
- `30` = 30 minutes
- `22` = 22:00 (10 PM)
- `* * *` = every day, every month, every day of week

---

## ✅ **Step 5: Verify the cron job was created**

```bash
crontab -l
```

You should see the line:
```
30 22 * * * /root/.openclaw/workspace/amazon-ranking-check.py >> /var/log/amazon-ranking.log 2>&1
```

---

## 💡 **Key Points:**

1.  **Why use headless Edge?** Amazon blocks simple curl requests with CAPTCHA, but headless browser can bypass this (most of the time)
2.  **Regex extraction**: We use regular expressions to pull the specific data we need from the full HTML dump
3.  **Logging**: All output is logged to `/var/log/amazon-ranking.log` for debugging if something fails
4.  **Format**: The table is transposed with metrics as rows instead of columns for better readability on mobile
5.  **Automation**: Once set up, cron runs it automatically every day without any manual intervention

---

## 📊 **Current Data (as of 2026-03-24):**

| **Metric** | **B0DDDWWJBC** | **B0CWZ2Z5TS** |
|---|---|---|
| **ASIN** | B0DDDWWJBC | B0CWZ2Z5TS |
| **Mosaic Tiles Category Rank** | #449 | #531 |
| **Customer Rating** | 3.9 / 5 stars | 4.4 / 5 stars |
| **Number of Reviews** | 16 | 30 |

---

## 📝 Notes for future:

- This document will be used to collect training materials for "小龙虾"
- Each different skill/task can be added to separate documents with clear naming
- Current document: **Amazon产品排名自动监控** - for automated daily ranking check task

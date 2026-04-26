# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Daily combined task: Send exchange rates + tomorrow's exhibition/weather forecast
- Frequency: every day at 7:00 AM GMT+8 and 7:00 PM GMT+8
- Content to send:
  1. 当日最新美元兑人民币、日元兑人民币汇率（来自中国银行官网，表格展示）
  2. 明天上海的天气预报（预警用，数据源：中国天气网）
  3. 明天在上海新国际博览中心（SNIEC）正在进行的展会信息（提前预警），说明：展会时间显示为区间时代表区间内每天都正常开展
- Sources:
  - Exchange rate: https://www.boc.cn/sourcedb/whpj/
  - Exhibitions: https://www.sniec.net/cn/visit_exhibition.php?month={{current_year_month}}#breadcrumbslist (check next month if tomorrow is in next month)
  - Weather: http://www.weather.com.cn/weather/101020100.shtml (China Weather Network, Shanghai)
- Post to: 当前群聊 (chat_id: oc_8fbfbbc914440f5be361a878c0e10d20)

## Daily automatic tasks: Product page screenshot + Amazon category ranking update
- Frequency: every day at 7:00 AM GMT+8 and 7:00 PM GMT+8
- Tasks:
  1. 商品页面截图
  2. 亚马逊类目排名更新
- Post to:
  1. 当前个人聊天 (魏总: ou_a331505193726d421fb0108a11bc6197)

## Daily automatic tasks: Taobao shopping cart price monitoring (Mosaic materials)
- Frequency: every day at 7:00 AM GMT+8 and 7:00 PM GMT+8
- Tasks:
  1. 打开淘宝购物车页面 https://cart.taobao.com/，**强制刷新页面**，确保获取最新session和最新购物车数据（避免旧界面缓存）
  2. **严格规则**: 
     - 只提取「猜你喜欢」上方真正购物车内的商品，猜你喜欢推荐区域商品不需要记录
     - **必须从页面顶部第一个商品开始，从上到下逐个清点计数**，不能遗漏任何一个商品
     - 提取完成后，必须核对商品数量和页面顶部显示的"全部商品(X)"数量一致，确认数量匹配后才能继续写入
  3. 每个商品提取：商品名称、规格、店铺、券后价格、原价、购买数量，添加**精确到分钟**的当前北京时间查询时间戳（飞书日期字段需要**秒级时间戳**，不能使用毫秒级）
  4. 将所有商品信息写入飞书多维表格"马赛克原料"数据表
  5. 对购物车页面进行全屏截图
  6. **必须**：监控完成后发送通知，内容必须包含：全屏截图 + 更新完成提示 + **完整的多维表格链接**，不能遗漏链接
- Feishu Bitable target:
  - App token: I2VNbkpkTaUDISsACs5ctFDgnte
  - Table ID: tblAHeovs5u8j1Th
  - Full URL: https://fqjt33o3gr7.feishu.cn/base/I2VNbkpkTaUDISsACs5ctFDgnte?table=tblAHeovs5u8j1Th
- Post to:
  1. 当前个人聊天 (魏总: ou_a331505193726d421fb0108a11bc6197)

## Daily automatic task: Force push workspace to GitHub
- Frequency: every day at 7:00 AM GMT+8 and 7:00 PM GMT+8
- Tasks:
  1. cd /root/.openclaw/workspace
  2. git add .
  3. git commit -a -m "Auto backup: $(date +'%Y-%m-%d %H:%M') workspace backup"
  4. git push -f origin master
  5. 推送完成后发送通知确认

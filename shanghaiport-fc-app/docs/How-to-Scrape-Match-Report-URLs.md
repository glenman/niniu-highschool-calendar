# 如何抓取上海海港赛事报告链接

本文档说明如何从fbref.com抓取上海海港某个赛季的所有比赛报告URL，并生成对应的JSON文件。

## 前置要求

1. **Chrome浏览器**：需要支持远程调试功能
2. **Node.js**：版本 >= 22（需要内置WebSocket支持）
3. **agent-browser工具**：用于浏览器自动化
4. **访问权限**：能够访问fbref.com

## 快速开始

只需一句指令：

```
给我生成上海海港2023赛季的赛事报告链接
```

系统会自动完成所有步骤，生成 `data/2023-match_urls.json` 文件。

## 手动操作步骤

如果需要手动操作，请按以下步骤执行：

### 步骤1：启动Chrome远程调试

在终端中运行：

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# 或者使用headless模式
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --headless
```

### 步骤2：访问fbref.com

使用浏览器或agent-browser访问fbref.com，找到上海海港的赛季页面：

```bash
agent-browser --cdp 9222 open "https://fbref.com/en/squads/c48512d3/2023/Shanghai-Port-Stats"
```

如果遇到Cloudflare验证，需要在真实浏览器窗口中手动完成验证。

### 步骤3：提取比赛列表

访问赛季的比分和赛程页面：

```bash
agent-browser --cdp 9222 open "https://fbref.com/en/squads/c48512d3/2023/matchlogs/all_comps/schedule/Shanghai-Port-Scores-and-Fixtures-All-Competitions"
```

### 步骤4：获取Match Report链接

使用Node.js脚本通过CDP提取所有Match Report链接：

```javascript
// 保存为 extract_match_urls.mjs
const wsUrl = 'ws://localhost:9222/devtools/page/PAGE_ID'; // 替换PAGE_ID

const jsCode = `
const links = Array.from(document.querySelectorAll('a')).filter(link =>
    link.textContent.trim() === 'Match Report' &&
    link.href.includes('/matches/')
);
JSON.stringify(links.map(link => link.href));
`;

const ws = new WebSocket(wsUrl);
ws.onopen = () => {
  ws.send(JSON.stringify({
    id: 1,
    method: 'Runtime.evaluate',
    params: { expression: jsCode, returnByValue: true }
  }));
};
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response.result.result.value);
  ws.close();
};
```

运行脚本：

```bash
node extract_match_urls.mjs > match_urls.json
```

### 步骤5：生成最终JSON文件

将URL列表与日期匹配，生成标准格式的JSON文件：

```json
{
  "team": "Shanghai Port FC",
  "season": 2023,
  "competition": "All Competitions (Chinese Super League)",
  "data_source": "fbref.com",
  "last_updated": "2026-03-27",
  "match_urls": [
    {
      "date": "2023-04-15",
      "match_report_url": "https://fbref.com/en/matches/..."
    },
    ...
  ]
}
```

## 自动化脚本

我们提供了一个完整的自动化脚本 `scripts/scrape_match_urls.sh`：

```bash
#!/bin/bash

# 使用方法
SEASON=${1:-2023}

# 步骤1：启动Chrome远程调试
# （需要手动启动，或者使用headless模式）

# 步骤2-5：自动提取和生成JSON
node scripts/extract_match_urls.mjs $SEASON
python3 scripts/merge_match_data.py $SEASON

echo "✓ 生成完成: data/${SEASON}-match_urls.json"
```

使用方法：

```bash
./scripts/scrape_match_urls.sh 2023
./scripts/scrape_match_urls.sh 2024
./scripts/scrape_match_urls.sh 2025
```

## URL格式说明

fbref.com的Match Report URL格式：

```
https://fbref.com/en/matches/{MATCH_ID}/{TEAM1}-{TEAM2}-{DATE}-Chinese-Super-League
```

示例：
```
https://fbref.com/en/matches/13f114b6/Wuhan-Three-Towns-Shanghai-Port-April-15-2023-Chinese-Super-League
```

## 注意事项

### Cloudflare验证

fbref.com使用Cloudflare反爬虫保护，可能需要：

1. **手动验证**：第一次访问时在浏览器窗口中完成人机验证
2. **保持会话**：使用CDP保持浏览器会话，避免重复验证
3. **限制频率**：不要频繁请求，建议每次抓取间隔几秒钟

### 数据完整性

- 确保抓取了所有比赛的URL（通常一个赛季30场比赛）
- 检查日期和URL是否正确匹配
- 验证JSON格式是否正确

### 错误处理

常见错误：

1. **Cloudflare验证失败**：在真实浏览器窗口中手动完成验证
2. **WebSocket连接失败**：检查Chrome远程调试端口是否正确（默认9222）
3. **找不到Match Report链接**：确保页面已完全加载

## 技术栈

- **浏览器自动化**：Chrome DevTools Protocol (CDP)
- **数据提取**：JavaScript DOM操作
- **数据格式**：JSON
- **工具**：Node.js, agent-browser

## 文件结构

```
shanghaiport-fc-app/
├── data/
│   ├── 2023-match_urls.json  # 2023赛季比赛URL
│   ├── 2024-match_urls.json  # 2024赛季比赛URL
│   └── ...
├── docs/
│   └── How-to-Scrape-Match-Report-URLs.md  # 本文档
└── scripts/
    ├── extract_match_urls.mjs  # URL提取脚本
    ├── merge_match_data.py     # 数据合并脚本
    └── scrape_match_urls.sh    # 完整流程脚本
```

## 参考资料

- [FBref上海海港页面](https://fbref.com/en/squads/c48512d3/Shanghai-Port-Stats)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [agent-browser工具](https://github.com/example/agent-browser)

## 更新日志

- 2026-03-27：初始版本，支持2023赛季数据抓取
- 2026-03-27：添加自动化脚本和详细文档

---

如有问题或建议，请联系小龙虾。

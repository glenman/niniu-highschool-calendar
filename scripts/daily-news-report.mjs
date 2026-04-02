#!/usr/bin/env node

/**
 * 每日新闻收集与报告生成脚本
 * 功能：从多个新闻源抓取热点新闻，生成报告到飞书云文档
 * 运行时间：每天早上 6:00
 */

const NEWS_SOURCES = {
  politics: [
    { name: 'AP News', url: 'https://apnews.com', type: '时政' },
    { name: 'CNBC Politics', url: 'https://www.cnbc.com/politics/', type: '时政' },
  ],
  finance: [
    { name: 'CNBC Markets', url: 'https://www.cnbc.com/markets/', type: '财经' },
    { name: 'CNBC Business', url: 'https://www.cnbc.com/business/', type: '财经' },
  ]
};

// 格式化日期
function formatDate() {
  const now = new Date();
  const options = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Shanghai'
  };
  return now.toLocaleDateString('zh-CN', options);
}

// 生成报告标题
function generateTitle() {
  const now = new Date();
  const dateStr = now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  });
  return `📰 每日国际新闻概要 - ${dateStr}`;
}

// 这里的新闻数据将由 OpenClaw agent 通过 web_fetch 获取
// 脚本本身只是定义结构和格式

console.log(JSON.stringify({
  action: 'generate_report',
  title: generateTitle(),
  date: formatDate(),
  sources: NEWS_SOURCES,
  targetNewsCount: 20
}));

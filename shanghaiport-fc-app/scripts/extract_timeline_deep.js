#!/usr/bin/env node
const fs = require('fs');

console.log('========================================');
console.log('深度提取比赛事件时间线');
console.log('========================================\n');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');

// 策略: 直接在原始HTML文本中查找事件模式

const events = [];

// 1. 查找所有包含"Goal"的行
console.log('【1】查找Goal关键词附近的文本...\n');

const goalMatches = html.matchAll(/(\d+(?:\+\d+)?')[^"]{0,200}Goal[^"]{0,200}/g);
for (const match of goalMatches) {
  const fullText = match[0];
  const timeMatch = fullText.match(/(\d+(?:\+\d+)?')/);
  const time = timeMatch ? timeMatch[1] : '';
  
  // 提取球员名
  const playerMatch = fullText.match(/([A-Z][a-z]+ [A-Z][a-z'·]+)(?:[^A-Z]|$)/);
  const player = playerMatch ? playerMatch[1].replace(/·/g, ' ') : '';
  
  // 判断球队
  const isHome = fullText.includes('Shanghai Port') || 
                 fullText.includes('Wu Lei') || 
                 fullText.includes('Wang Shenchao') ||
                 fullText.includes('Oscar') ||
                 fullText.includes('Lü Wenjun');
  
  const team = isHome ? '主队' : '客队';
  
  if (time && player) {
    events.push({
      time,
      type: '进球',
      player,
      team,
      raw: fullText.substring(0, 100)
    });
  }
}

// 2. 查找黄牌
console.log('【2】查找Yellow Card...\n');

const yellowMatches = html.matchAll(/(\d+(?:\+\d+)?')[^"]{0,200}Yellow[^"]{0,200}/g);
for (const match of yellowMatches) {
  const fullText = match[0];
  const timeMatch = fullText.match(/(\d+(?:\+\d+)?')/);
  const time = timeMatch ? timeMatch[1] : '';
  
  const playerMatch = fullText.match(/([A-Z][a-z]+ [A-Z][a-z'·]+)/);
  const player = playerMatch ? playerMatch[1].replace(/·/g, ' ') : '';
  
  const isHome = fullText.includes('Shanghai Port');
  const team = isHome ? '主队' : '客队';
  
  if (time && player) {
    events.push({
      time,
      type: '黄牌',
      player,
      team,
      raw: fullText.substring(0, 100)
    });
  }
}

// 3. 查找换人
console.log('【3】查找Substitution...\n');

const subMatches = html.matchAll(/(\d+(?:\+\d+)?')[^"]{0,300}(?:substitute|Substitute|substituted)[^"]{0,300}/gi);
for (const match of subMatches) {
  const fullText = match[0];
  const timeMatch = fullText.match(/(\d+(?:\+\d+)?')/);
  const time = timeMatch ? timeMatch[1] : '';
  
  // 提换人和被换球员
  const playersMatch = fullText.match(/([A-Z][a-z]+ [A-Z][a-z'·]+)[^A-Z]+for[^A-Z]+([A-Z][a-z]+ [A-Z][a-z'·]+)/);
  const playerIn = playersMatch ? playersMatch[1].replace(/·/g, ' ') : '';
  const playerOut = playersMatch ? playersMatch[2].replace(/·/g, ' ') : '';
  
  const isHome = fullText.includes('Shanghai Port');
  const team = isHome ? '主队' : '客队';
  
  if (time && playerIn && playerOut) {
    events.push({
      time,
      type: '换人',
      player: `${playerIn} 替换 ${playerOut}`,
      team,
      raw: fullText.substring(0, 100)
    });
  }
}

// 去重
const uniqueEvents = [];
const eventKeys = new Set();

events.forEach(e => {
  const key = `${e.time}-${e.type}-${e.player}`;
  if (!eventKeys.has(key)) {
    eventKeys.add(key);
    uniqueEvents.push(e);
  }
});

// 按时间排序
uniqueEvents.sort((a, b) => {
  const parseTime = (t) => {
    const parts = t.replace("'", '').split('+');
    return parseInt(parts[0]) + (parts[1] ? parseInt(parts[1]) / 100 : 0);
  };
  return parseTime(a.time) - parseTime(b.time);
});

// 显示结果
console.log('========================================');
console.log(`找到 ${uniqueEvents.length} 个比赛事件`);
console.log('========================================\n');

if (uniqueEvents.length > 0) {
  uniqueEvents.forEach((e, idx) => {
    console.log(`${idx + 1}. [${e.time}] [${e.type}] [${e.team}]`);
    console.log(`   球员: ${e.player}`);
    console.log(`   原文: ${e.raw}`);
    console.log('');
  });
  
  // 保存CSV
  const csvRows = [];
  csvRows.push(['序号', '时间', '事件类型', '球队', '球员', '原文片段']);
  
  uniqueEvents.forEach((e, idx) => {
    csvRows.push([
      idx + 1,
      e.time,
      e.type,
      e.team,
      e.player,
      e.raw.replace(/"/g, '""')
    ]);
  });
  
  const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  fs.writeFileSync('./data/match_events_timeline.csv', '\ufeff' + csvContent, 'utf8');
  
  console.log('========================================');
  console.log(`✓ 已保存: data/match_events_timeline.csv`);
  console.log('========================================\n');
  
  // 分类汇总
  const byType = {};
  uniqueEvents.forEach(e => {
    byType[e.type] = (byType[e.type] || 0) + 1;
  });
  
  console.log('事件分类:');
  Object.entries(byType).forEach(([type, count]) => {
    console.log(`  ${type}: ${count}个`);
  });
  
} else {
  console.log('⚠️  未找到任何事件\n');
  console.log('建议:');
  console.log('1. HTML可能是JavaScript渲染后的内容');
  console.log('2. 事件信息可能在<script>标签中');
  console.log('3. 需要查看原始HTML结构');
  
  // 尝试查找JSON数据
  const jsonMatches = html.match(/<script[^>]*>[\s\S]*?(\{[\s\S]*?"events"[\s\S]*?\})[\s\S]*?<\/script>/gi);
  if (jsonMatches) {
    console.log('\n找到可能的JSON数据区域，正在提取...');
  }
}

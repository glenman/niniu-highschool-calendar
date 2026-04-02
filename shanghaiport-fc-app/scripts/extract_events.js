#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

console.log('提取比赛事件（进球、换人、黄牌）\n');
console.log('='.repeat(80));

const events = [];

// 在HTML文本中查找特定模式
const text = $('body').text();

// 查找所有包含时间的行
const lines = text.split('\n');

lines.forEach((line, index) => {
  const trimmed = line.trim();
  
  // 查找进球 - 格式通常是 "时间 · 球员名 Goal"
  if (trimmed.match(/\d+'/)) {
    const timeMatch = trimmed.match(/(\d+'\d*)/);
    if (timeMatch) {
      const time = timeMatch[1];
      
      // 检查是否包含Goal或进球相关关键词
      if (trimmed.toLowerCase().includes('goal') || 
          trimmed.includes('Wu Lei') ||
          trimmed.includes('Wang Shenchao') ||
          trimmed.includes('Wang Yi Denny')) {
        
        // 提取球员名
        const playerMatch = trimmed.match(/([A-Z][a-z]+ [A-Z][a-z']+)/);
        const player = playerMatch ? playerMatch[1] : '';
        
        if (player) {
          events.push({
            time: time,
            player: player,
            type: '进球',
            raw: trimmed.substring(0, 100)
          });
        }
      }
      
      // 检查是否是换人
      if (trimmed.toLowerCase().includes('substitute') || 
          trimmed.toLowerCase().includes('substituted')) {
        events.push({
          time: time,
          type: '换人',
          raw: trimmed.substring(0, 100)
        });
      }
      
      // 检查是否是黄牌
      if (trimmed.toLowerCase().includes('yellow')) {
        const playerMatch = trimmed.match(/([A-Z][a-z]+ [A-Z][a-z']+)/);
        const player = playerMatch ? playerMatch[1] : '';
        
        events.push({
          time: time,
          player: player,
          type: '黄牌',
          raw: trimmed.substring(0, 100)
        });
      }
    }
  }
});

// 去重
const uniqueEvents = [];
const eventKeys = new Set();

events.forEach(e => {
  const key = `${e.time}-${e.type}-${e.player || ''}`;
  if (!eventKeys.has(key)) {
    eventKeys.add(key);
    uniqueEvents.push(e);
  }
});

// 按时间排序
uniqueEvents.sort((a, b) => {
  const minA = parseInt(a.time.replace("'", ''));
  const minB = parseInt(b.time.replace("'", ''));
  return minA - minB;
});

console.log(`\n找到 ${uniqueEvents.length} 个比赛事件:\n`);

uniqueEvents.forEach((e, idx) => {
  console.log(`${idx + 1}. ${e.time} - [${e.type}] ${e.player || ''}`);
  console.log(`   详情: ${e.raw}`);
  console.log('');
});

// 保存到文件
const csvContent = '时间,类型,球员,详情\n' + 
  uniqueEvents.map(e => 
    `"${e.time}","${e.type}","${e.player || ''}","${e.raw.replace(/"/g, '""')}"`
  ).join('\n');

fs.writeFileSync('./data/match_events.csv', '\ufeff' + csvContent, 'utf8');

console.log('='.repeat(80));
console.log(`\n✓ 已保存到: data/match_events.csv`);
console.log(`  共 ${uniqueEvents.length} 个事件\n`);

// 显示进球汇总
const goals = uniqueEvents.filter(e => e.type === '进球');
if (goals.length > 0) {
  console.log('进球汇总:');
  goals.forEach(g => {
    console.log(`  ${g.time} - ${g.player}`);
  });
}

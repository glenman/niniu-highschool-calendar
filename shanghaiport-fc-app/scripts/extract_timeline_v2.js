#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('========================================');
console.log('比赛事件时间线提取 - 专业版');
console.log('========================================\n');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

const events = [];

// 策略1: 查找所有包含时间的div
console.log('【策略1】查找时间+事件描述\n');

$('div').each((i, elem) => {
  const $div = $(elem);
  const text = $div.text().trim();
  
  // 匹配时间格式: 20', 45+2', 90+2'等
  const timeMatch = text.match(/(\d+(?:\+\d+)')/);
  
  if (timeMatch) {
    const time = timeMatch[1];
    const remainingText = text.replace(timeMatch[0], '').trim();
    
    // 检测进球
    if (remainingText.toLowerCase().includes('goal') || 
        remainingText.includes('Wu Lei') ||
        remainingText.includes('Wang Shenchao') ||
        remainingText.includes('Wang Yi Denny')) {
      
      // 提取球员名
      const playerPatterns = [
        /([A-Z][a-z]+(?: [A-Z][a-z']+)?)/g
      ];
      
      let players = [];
      playerPatterns.forEach(pattern => {
        const matches = remainingText.match(pattern);
        if (matches) {
          players = players.concat(matches);
        }
      });
      
      // 过滤掉常见的非球员词
      players = players.filter(p => 
        !['Goal', 'Assist', 'Yellow', 'Red', 'Card', 'Substitute', 'The', 'Match', 'Team', 'Port', 'Wuhan'].includes(p)
      );
      
      if (players.length > 0) {
        events.push({
          time: time,
          type: '进球',
          player: players[0],
          team: text.includes('Shanghai Port') || text.includes('Wu Lei') || text.includes('Wang Shenchao') ? '主队' : '客队',
          detail: remainingText.substring(0, 80)
        });
      }
    }
    
    // 检测黄牌
    if (remainingText.toLowerCase().includes('yellow')) {
      const playerMatch = remainingText.match(/([A-Z][a-z]+ [A-Z][a-z']+)/);
      if (playerMatch) {
        events.push({
          time: time,
          type: '黄牌',
          player: playerMatch[1],
          team: text.includes('Shanghai Port') ? '主队' : '客队',
          detail: remainingText.substring(0, 80)
        });
      }
    }
    
    // 检测换人
    if (remainingText.toLowerCase().includes('substitute') || 
        remainingText.toLowerCase().includes('substituted') ||
        remainingText.includes('for')) {
      
      const inMatch = remainingText.match(/([A-Z][a-z]+ [A-Z][a-z']+).*?for ([A-Z][a-z]+ [A-Z][a-z']+)/);
      if (inMatch) {
        events.push({
          time: time,
          type: '换人',
          player: inMatch[1] + ' 替 ' + inMatch[2],
          team: text.includes('Shanghai Port') ? '主队' : '客队',
          detail: remainingText.substring(0, 80)
        });
      }
    }
  }
});

// 策略2: 在整个body文本中查找事件
console.log('【策略2】全文搜索事件模式\n');

const bodyText = $('body').text();

// 更精确的进球匹配
const goalPattern = /(\d+(?:\+\d+)?')\s*([^\n]*?(?:Goal|进球)[^\n]*)/g;
let match;

while ((match = goalPattern.exec(bodyText)) !== null) {
  const time = match[1];
  const detail = match[2].trim();
  
  // 提取球员名
  const playerMatch = detail.match(/([A-Z][a-z]+ [A-Z][a-z']+)/);
  const player = playerMatch ? playerMatch[1] : '';
  
  if (player && !events.find(e => e.time === time && e.type === '进球')) {
    events.push({
      time: time,
      type: '进球',
      player: player,
      team: detail.includes('Wu Lei') || detail.includes('Wang Shenchao') ? '主队' : '客队',
      detail: detail.substring(0, 80)
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

if (uniqueEvents.length === 0) {
  console.log('⚠️  未找到事件，尝试更激进的搜索...\n');
  
  // 策略3: 直接在原始HTML中查找
  const rawHtml = html;
  
  // 查找所有时间标记
  const allTimes = rawHtml.match(/\d+'/g) || [];
  console.log(`HTML中共有 ${allTimes.length} 个时间标记`);
  
  // 查找可能的球员名
  const knownPlayers = [
    'Wu Lei', 'Wang Shenchao', 'Wang Yi Denny',
    'Matías Vargas', 'Oscar', 'Lü Wenjun',
    'Pedro', 'Liu Ruofan'
  ];
  
  knownPlayers.forEach(player => {
    if (rawHtml.includes(player)) {
      console.log(`✓ 找到球员: ${player}`);
      
      // 查找这个球员附近的时间
      const playerIndex = rawHtml.indexOf(player);
      const nearbyText = rawHtml.substring(Math.max(0, playerIndex - 200), playerIndex + 200);
      const nearbyTime = nearbyText.match(/(\d+)'/);
      
      if (nearbyTime) {
        console.log(`  附近时间: ${nearbyTime[1]}'`);
      }
    }
  });
  
} else {
  // 显示所有事件
  uniqueEvents.forEach((e, idx) => {
    console.log(`${idx + 1}. [${e.time}] [${e.type}] [${e.team}] ${e.player}`);
    console.log(`   详情: ${e.detail}`);
    console.log('');
  });
  
  // 保存到CSV
  const csvRows = [];
  csvRows.push(['序号', '时间', '类型', '球队', '球员', '详情']);
  
  uniqueEvents.forEach((e, idx) => {
    csvRows.push([
      idx + 1,
      e.time,
      e.type,
      e.team,
      e.player,
      e.detail
    ]);
  });
  
  const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  fs.writeFileSync('./data/match_timeline.csv', '\ufeff' + csvContent, 'utf8');
  
  console.log('========================================');
  console.log(`✓ 已保存到: data/match_timeline.csv`);
  console.log('========================================\n');
  
  // 分类汇总
  const goals = uniqueEvents.filter(e => e.type === '进球');
  const yellows = uniqueEvents.filter(e => e.type === '黄牌');
  const subs = uniqueEvents.filter(e => e.type === '换人');
  
  console.log('事件汇总:');
  console.log(`  进球: ${goals.length}个`);
  console.log(`  黄牌: ${yellows.length}张`);
  console.log(`  换人: ${subs.length}次`);
  
  if (goals.length > 0) {
    console.log('\n进球详情:');
    goals.forEach(g => {
      console.log(`  ${g.time} - ${g.player} (${g.team})`);
    });
  }
}

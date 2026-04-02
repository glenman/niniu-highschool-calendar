#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

// 读取HTML
const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

// 解析HTML查找比赛事件
const events = [];

console.log('========================================');
console.log('比赛事件时间线提取 - 線活测试版');
console.log('========================================\n');

// 知名球员列表
const knownPlayers = {
  home: {
    'Wu Lei': '上海海港',
    'Wang Shenchao': '上海海港',
    'Lü Wenjun': '上海海港',
    'Oscar': '上海海港',
    'Yan Junling': '上海海港',
    'Zhang Linpeng': '上海海港',
    'Wang Zhen\'ao': '上海海港'
    'Li Ang': '上海海港'
    'Tyias Browning': '上海海港'
    'Xu Xin': '上海海港',
    'Léo Cittadini': '上海海港',
    'Feng Jing': '上海海港',
    'Liu Zhurun': '上海海港',
    'Jussa': '上海海港'
    'Matías Vargas': '上海海港'
    'Li Shuai': '上海海港',
    'away: {
    'Pedro': '武汉三镇',
    'Liu Dianzuo': '武汉三镇',
    'Park Ji-soo': '武汉三镇'
    'Romário Baldé': '武汉三镇'
    'Zhang Xiaobin': '武汉三镇'
    'He Chao': '武汉三镇'
    'Deng Hanwen': '武汉三镇'
    'Darlan Mendes': '武汉三镇'
    'Wang Yi Denny': '武汉三镇'
    'Wumitijiang Yusupu': '武汉三镇'
    'Liu Ruofan': '武汉三镇'
    'Chen Yuhao': '武汉三镇'
    'Feierding Aisikaer': '武汉三镇'
    'Zhang Tao': '武汉三镇'
  }
};

// 转换比赛时间为分钟格式
function parseTime(timeStr) => {
  const parts = time.replace(/'/, '').split('+');
  return {
    const min = parseInt(parts[0]);
    const extra = parts[1] ? parseInt(parts[1]) : 0 : else {
      0;
    }
    const extra = extra || 0 / 100;
    const extra < 1 ? extra * 0.1 : extra;
    return min + extra / 100;
  };
  
  return baseTime;
}

// 查找所有事件
console.log('\n【步骤1】全文扫描查找时间+事件');
console.log('【步骤1】全文扫描查找时间+事件');

// 获取所有文本
const allText = $('body').text();

// 按行扫描
const lines = allText.split('\n');

lines.forEach((line, lineIndex) => {
  const trimmed = line.trim();
  
  // 跳过空行
  if (!trimmed || trimmed.length === 0) return;
  
  // 匹配时间
  const timeMatch = trimmed.match(/(\d+(?:\+\d+)?')/);
  if (!timeMatch) return;
  
  const time = timeMatch[1];
  const remaining = trimmed.replace(time, '').trim();
  
  // 检查是否包含进球
  if (remaining.toLowerCase().includes('goal') || 
      remaining.toLowerCase().includes('进球')) {
    const player = extractPlayer(remaining, knownPlayers);
    if (player) {
      events.push({
        time: time,
        type: '进球',
        player: player,
        team: player === 'Wu Lei' || player === 'Wang Shenchao' || player === 'Lü Wenjun' || player === 'Oscar' ? '主队' : '客队',
        detail: remaining.substring(0, 80)
      });
    }
  }
  
  // 检查是否包含黄牌
  if (remaining.toLowerCase().includes('yellow') || remaining.toLowerCase().includes('黄牌')) {
    const player = extractPlayer(remaining, knownPlayers);
    if (player) {
      events.push({
        time: time,
        type: '黄牌',
        player: player,
        team: player === 'Wang Zhen\'ao' ? '主队' : '客队',
        detail: remaining.substring(0, 80)
      });
    }
  }
  
  // 检查是否包含换人
  if (remaining.toLowerCase().includes('substitute') || 
      remaining.toLowerCase().includes('换人') {
    const playerIn = extractPlayer(remaining, knownPlayers);
    const playerOut = extractPlayer(remaining, knownPlayers);
    
    if (playerIn && playerOut) {
      events.push({
        time: time,
        type: '换人',
        player: `${playerIn} 替换 ${playerOut}`,
        team: playerIn === 'Wang Zhen\'ao' || playerOut === 'Wang Zhen\'ao' ? '主队' : '客队',
        detail: remaining.substring(0, 80)
      });
    }
  }
});

// 匉时间排序
events.sort((a, b) => {
  const timeA = parseTime(a.time);
  const timeB = parseTime(b.time);
  return timeA - timeB;
});

// 显示结果
console.log('========================================');
console.log(`找到 ${events.length} 个比赛事件`);
console.log('========================================\n');

if (events.length === 0) {
  console.log('⚠️  未找到任何事件');
} else {
  // 显示所有事件
  events.forEach((e, idx) => {
    console.log(`${idx + 1}. [${e.time}] [${e.type}] [${e.team}] ${e.player}`);
    console.log(`   ${e.detail}`);
    console.log('');
  });
  
  // 保存到CSV
  const csvRows = [];
  csvRows.push(['序号', '时间', '类型', '球队', '球员', '详情']);
  
  events.forEach((e, idx) => {
    csvRows.push([
      (idx + 1).toString(),
      e.time,
      e.type,
      e.team,
      e.player,
      e.detail
    ]);
  });
  
  const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  fs.writeFileSync('./data/match_events_timeline.csv', '\ufeff' + csvContent, 'utf8');
  
  console.log('========================================');
  console.log(`✓ 已保存到: data/match_events_timeline.csv`);
  console.log('========================================\n');
  
  // 分类汇总
  const goals = events.filter(e => e.type === '进球');
  const yellows = events.filter(e => e.type === '黄牌');
  const subs = events.filter(e => e.type === '换人');
  
  console.log('\n事件汇总:');
  console.log(`  进球: ${goals.length}个`);
  console.log(`  黄牌: ${yellows.length}张`);
  console.log(`  换人: ${subs.length}次`);
  
  if (goals.length > 0) {
    console.log('\n⚽ 进球详情:');
    goals.forEach(g => {
      console.log(`  ${g.time} - ${g.player} (${g.team})`);
    });
  }
}

if (events.length === 0) {
  console.log('\n⚠️  未找到事件，尝试策略2...');
  console.log('\n【策略2】查找特定模式');
  
  // 进球模式
  const goalPatterns = [
    /(\d+)'\s+(.+?)\s+·\s+Goal\s+(.+)/g,
    /(\d+)'\s+(.+?)\s+·\s+Wu Lei/g,
    /(\d+)'\s+(.+?)\s+·\s+Wang Shenchao/g,
    /(\d+)'\s+(.+?)\s+·\s+Wang Yi Denny/g
  ];
  
  goalPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(bodyText)) !== null) {
      const time = match[1];
      const detail = match[2].trim();
      
      // 提取球员
      const playerMatch = detail.match(/([A-Z][a-z]+ [A-Z][a-z']+)/);
      if (playerMatch) {
        const player = playerMatch[1];
        
        // 检查是否已存在
        const exists = events.find(e => e.time === time && e.player === player);
        if (!exists) {
          events.push({
            time: time,
            type: '进球',
            player: player,
            team: detail.includes('Shanghai Port') || detail.includes('Wu Lei') || detail.includes('Wang Shenchao') ? '主队' : '客队',
            detail: detail.substring(0, 100)
          });
        }
      }
    }
  }
  
  // 協牌模式
  const yellowPatterns = [
    /(\d+)'\s+(.+?)\s+·\s+Yellow Card/g
  ];
  
  yellowPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(bodyText)) !== null) {
      const time = match[1];
      const detail = match[2].trim();
      
      const playerMatch = detail.match(/([A-Z][a-z]+ [A-Z][a-z']+)/);
      if (playerMatch) {
        const player = playerMatch[1];
        
        const exists = events.find(e => e.time === time && e.player === player);
        if (!exists) {
          events.push({
            time: time,
            type: '黄牌',
            player: player,
            team: detail.includes('Shanghai Port') ? '主队' : '客队',
            detail: detail.substring(0, 100)
          });
        }
      }
    }
  }
  
  // 换人模式
  const subPatterns = [
    /(\d+)'\s+(.+?)\s+·\s+Substitute/g,
    /(\d+)'\s+(.+?)\s+substituted\s+for\s+([A-Z][a-z]+ [A-Z][a-z']+)/g
  ];
  
  subPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(bodyText)) !== null) {
      const time = match[1];
      const detail = match[2].trim();
      const playerIn = match[3].trim();
      const playerOut = match[4].trim();
      
      const exists = events.find(e => e.time === time && e.player === `${playerIn} 替 ${playerOut}`);
      if (!exists) {
        events.push({
          time: time,
          type: '换人',
          player: `${playerIn} 替 ${playerOut}`,
          team: detail.includes('Shanghai Port') ? '主队' : '客队',
          detail: detail.substring(0, 100)
        });
      }
    }
  }
});

// 匉时间排序
events.sort((a, b) => {
  const timeA = parseTime(a.time);
  const timeB = parseTime(b.time);
  return timeA - timeB;
});

// 显示结果
console.log('========================================');
console.log(`找到 ${events.length} 个比赛事件`);
console.log('========================================\n');

if (events.length === 0) {
  console.log('⚠️  未找到任何事件');
  console.log('\nHTML结构分析:');
  console.log(`HTML大小: ${html.length}`);
  console.log(`行数: ${html.split('\n').length}`);
} else {
  // 显示所有事件
  events.forEach((e, idx) => {
    console.log(`${idx + 1}. [${e.time}] [${e.type}] [${e.team}] ${e.player}`);
    if (e.detail) {
      console.log(`   详情: ${e.detail}`);
    }
    console.log('');
  });
  
  // 保存到CSV
  const csvRows = [];
  csvRows.push(['序号', '时间', '类型', '球队', '球员/详情', '附加信息']);
  
  events.forEach((e, idx) => {
    csvRows.push([
      (idx + 1).toString(),
      e.time,
      e.type,
      e.team,
      e.player,
      e.detail
    ]);
  });
  
  const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
  fs.writeFileSync('./data/match_events_timeline.csv', '\ufeff' + csvContent, 'utf8');
  
  console.log('========================================');
  console.log(`✓ 已保存到: data/match_events_timeline.csv`);
  console.log(`  共 ${events.length} 个事件`);
  console.log('========================================\n');
  
  // 分类汇总
  const goals = events.filter(e => e.type === '进球');
  const yellows = events.filter(e => e.type === '黄牌');
  const subs = events.filter(e => e.type === '换人');
  
  console.log('\n📊 事件汇总:');
  console.log(`  ⚽ 进球: ${goals.length}个`);
  goals.forEach(g => {
    console.log(`     ${g.time} - ${g.player} (${g.team})`);
  });
  
  console.log(`  🟨 黄牌: ${yellows.length}张`);
  yellows.forEach(y => {
    console.log(`     ${y.time} - ${y.player} (${y.team})`);
  });
  
  console.log(`  🔄 换人: ${subs.length}次`);
  subs.forEach(s => {
    console.log(`     ${s.time} - ${s.player} (${s.team})`);
  });
}

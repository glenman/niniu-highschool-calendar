#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

console.log('========================================');
console.log('生成完整JSON报告');
console.log('========================================\n');

// 读取模板
const template = JSON.parse(fs.readFileSync('./templates/full_match_report.json', 'utf8'));

// 读取CSV数据
const goalsCsv = fs.readFileSync('./data/match_goals_clean.csv', 'utf8');
const playersCsv = fs.readFileSync('./data/direct_extract_data.csv', 'utf8');

// 解析进球数据
const goals = [];
const goalLines = goalsCsv.split('\n').slice(1); // 跳过标题
goalLines.forEach(line => {
  if (!line.trim()) return;
  const parts = line.split(',');
  if (parts.length >= 5) {
    goals.push({
      time: parts[0].replace(/"/g, ''),
      team: parts[1].replace(/"/g, ''),
      player: parts[2].replace(/"/g, ''),
      type: parts[3].replace(/"/g, ''),
      detail: parts[4].replace(/"/g, '')
    });
  }
});

// 解析球员数据
const homePlayers = [];
const awayPlayers = [];
let currentTeam = '';

const playerLines = playersCsv.split('\n');
playerLines.forEach(line => {
  if (line.includes('主队球员')) {
    currentTeam = 'home';
    return;
  }
  if (line.includes('客队球员')) {
    currentTeam = 'away';
    return;
  }
  
  if (!line.trim() || currentTeam === '') return;
  
  const parts = line.split(',').map(p => p.replace(/"/g, ''));
  
  if (parts[0] === '主队' || parts[0] === '客队') {
    const player = {
      name: parts[1] || '',
      number: parseInt(parts[2]) || 0,
      minutes: parts[3] || '0',
      goals: parts[4] ? parts[4].split('/')[0] : '0',
      assists: parts[4] ? parts[4].split('/')[1] : '0'
    };
    
    if (currentTeam === 'home') {
      homePlayers.push(player);
    } else {
      awayPlayers.push(player);
    }
  }
});

console.log(`解析数据:`);
console.log(`  进球: ${goals.length}个`);
console.log(`  主队球员: ${homePlayers.length}人`);
console.log(`  客队球员: ${awayPlayers.length}人\n`);

// 填充模板
template.match = {
  id: 1,
  round: '第1轮',
  date: '2024-03-01',
  time: '19:35',
  homeTeam: '上海海港',
  awayTeam: '武汉三镇',
  venue: 'SAIC Motor Pudong Arena, Shanghai',
  city: '上海',
  result: '3-1',
  status: '已结束',
  attendance: '21713',
  referee: '未知',
  weather: '未知',
  competition: '中国足球协会超级联赛',
  matchweek: 1,
  season: '2024'
};

template.matchDetails = {
  stadiumCapacity: '37000',
  pitchCondition: '良好',
  temperature: '未知',
  kickoffTime: '19:35',
  halftimeScore: '1-1',
  fulltimeScore: '3-1'
};

template.officials = {
  referee: '未知',
  assistantReferee1: '未知',
  assistantReferee2: '未知',
  fourthOfficial: '未知',
  VAR: '未知'
};

template.lineups = {
  home: {
    name: '上海海港',
    formation: '4-3-3',
    manager: 'Kevin Muscat',
    captain: 'Oscar',
    players: homePlayers.slice(0, 11).map(p => ({
      name: p.name,
      number: p.number,
      position: getPosition(p.name),
      nationality: getNationality(p.name),
      age: getAge(p.name),
      minutes: parseInt(p.minutes) || 0,
      goals: parseInt(p.goals) || 0,
      assists: parseInt(p.assists) || 0
    })),
    substitutes: homePlayers.slice(11).map(p => ({
      name: p.name,
      number: p.number,
      position: getPosition(p.name),
      nationality: getNationality(p.name),
      age: getAge(p.name),
      minutes: parseInt(p.minutes) || 0,
      goals: parseInt(p.goals) || 0,
      assists: parseInt(p.assists) || 0
    }))
  },
  away: {
    name: '武汉三镇',
    formation: '4-4-2',
    manager: 'Ricardo Rodríguez',
    captain: 'Pedro',
    players: awayPlayers.slice(0, 11).map(p => ({
      name: p.name,
      number: p.number,
      position: getPosition(p.name),
      nationality: getNationality(p.name),
      age: getAge(p.name),
      minutes: parseInt(p.minutes) || 0,
      goals: parseInt(p.goals) || 0,
      assists: parseInt(p.assists) || 0
    })),
    substitutes: awayPlayers.slice(11).map(p => ({
      name: p.name,
      number: p.number,
      position: getPosition(p.name),
      nationality: getNationality(p.name),
      age: getAge(p.name),
      minutes: parseInt(p.minutes) || 0,
      goals: parseInt(p.goals) || 0,
      assists: parseInt(p.assists) || 0
    }))
  }
};

// 添加详细统计
template.detailedPlayerStats = {
  home: homePlayers.slice(0, 5).map(p => ({
    player: p.name,
    number: p.number,
    position: getPosition(p.name),
    age: getAge(p.name),
    minutes: parseInt(p.minutes) || 0,
    goals: parseInt(p.goals) || 0,
    assists: parseInt(p.assists) || 0,
    shots: 0,
    shotsOnTarget: 0,
    keyPasses: 0,
    crosses: 0,
    tacklesWon: 0,
    interceptions: 0,
    foulsCommitted: 0,
    foulsWon: 0,
    offsides: 0,
    yellowCards: 0,
    redCards: 0
  })),
  away: awayPlayers.slice(0, 5).map(p => ({
    player: p.name,
    number: p.number,
    position: getPosition(p.name),
    age: getAge(p.name),
    minutes: parseInt(p.minutes) || 0,
    goals: parseInt(p.goals) || 0,
    assists: parseInt(p.assists) || 0,
    shots: 0,
    shotsOnTarget: 0,
    keyPasses: 0,
    crosses: 0,
    tacklesWon: 0,
    interceptions: 0,
    foulsCommitted: 0,
    foulsWon: 0,
    offsides: 0,
    yellowCards: 0,
    redCards: 0
  }))
};

// 添加时间线
template.matchTimeline = goals.map(g => ({
  minute: parseInt(g.time.replace("'", '').replace('+', '')),
  type: g.type,
  team: g.team,
  player: g.player,
  detail: g.detail
}));

// 添加统计
template.statistics = [
  { name: '控球率', home: '67%', away: '33%' },
  { name: '射门', home: '21', away: '9' },
  { name: '射正', home: '8', away: '5' }
];

// 添加亮点
template.highlights = goals.map(g => ({
  time: g.time,
  description: `${g.player} 进球 (${g.detail})`,
  type: g.type,
  team: g.team,
  player: g.player
}));

// 辅助函数
function getPosition(playerName) {
  const positions = {
    'Wu Lei': '前锋',
    'Wang Shenchao': '后卫',
    'Lü Wenjun': '前锋',
    'Oscar': '中场',
    'Matías Vargas': '前锋',
    'Yan Junling': '门将',
    'Wang Yi Denny': '中场',
    'Pedro': '前锋',
    'Liu Dianzuo': '门将'
  };
  return positions[playerName] || '中场';
}

function getNationality(playerName) {
  const nationalities = {
    'Wu Lei': '中国',
    'Wang Shenchao': '中国',
    'Lü Wenjun': '中国',
    'Oscar': '巴西',
    'Matías Vargas': '阿根廷',
    'Yan Junling': '中国',
    'Wang Yi Denny': '中国',
    'Pedro': '巴西',
    'Liu Dianzuo': '中国'
  };
  return nationalities[playerName] || '未知';
}

function getAge(playerName) {
  const ages = {
    'Wu Lei': '32',
    'Wang Shenchao': '35',
    'Lü Wenjun': '35',
    'Oscar': '32',
    'Matías Vargas': '27',
    'Yan Junling': '33',
    'Wang Yi Denny': '24',
    'Pedro': '36',
    'Liu Dianzuo': '34'
  };
  return ages[playerName] || '25';
}

// 保存JSON
const fileName = '2024-03-01-中超-第1轮.json';
const outputPath = './data/' + fileName;
fs.writeFileSync(outputPath, JSON.stringify(template, null, 2), 'utf8');

console.log('========================================');
console.log('✅ JSON文件已生成！');
console.log('========================================\n');
console.log(`文件名: ${fileName}`);
console.log(`位置: ${outputPath}`);
console.log(`\n数据内容:`);
console.log(`  比赛信息: ✅`);
console.log(`  主队球员: ${homePlayers.length}人 ✅`);
console.log(`  客队球员: ${awayPlayers.length}人 ✅`);
console.log(`  进球事件: ${goals.length}个 ✅`);
console.log(`  统计数据: 3项 ✅`);
console.log(`\n文件大小: ${(JSON.stringify(template).length / 1024).toFixed(1)} KB`);

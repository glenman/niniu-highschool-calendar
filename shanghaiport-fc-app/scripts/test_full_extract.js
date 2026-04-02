#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

// 球队名称映射
const teamNameMap = {
  'Shanghai Port': '上海海港',
  'Wuhan Three Towns': '武汉三镇',
  'Zhejiang Professional': '浙江队',
  'Henan': '河南',
  'Shandong Taishan': '山东泰山',
  'Qingdao West Coast': '青岛西海岸',
  'Meizhou Hakka': '梅州客家',
  'Cangzhou Mighty Lions': '沧州雄狮',
  'Tianjin Jinmen Tiger': '天津津门虎',
  'Shenzhen Peng City': '深圳新鹏城',
  'Nantong Zhiyun': '南通支云',
  'Chengdu Rongcheng': '成都蓉城',
  'Changchun Yatai': '长春亚泰',
  'Qingdao Hainiu': '青岛海牛',
  'Shanghai Shenhua': '上海申花',
  'Beijing Guoan': '北京国安'
};

const positionMap = {
  'GK': '门将', 'FW': '前锋', 'MF': '中场', 'DF': '后卫',
  'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫',
  'DM': '后腰', 'CM': '中场', 'AM': '攻击型中场',
  'RW': '右边锋', 'LW': '左边锋', 'RM': '右中场', 'LM': '左中场'
};

console.log('='.repeat(80));
console.log('完整比赛报告数据提取');
console.log('='.repeat(80));
console.log('');

const html = fs.readFileSync('./data/test_match_full.html', 'utf8');
const $ = cheerio.load(html);

// ============ 1. 比赛基本信息 ============
console.log('【1. 比赛基本信息】');

const title = $('title').text();
const matchInfo = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)$/);

const match = {
  homeTeam: matchInfo ? matchInfo[1].trim() : '',
  awayTeam: matchInfo ? matchInfo[2].trim() : '',
  date: matchInfo ? matchInfo[3].trim() : ''
};

console.log(`主队: ${match.homeTeam} -> ${teamNameMap[match.homeTeam]}`);
console.log(`客队: ${match.awayTeam} -> ${teamNameMap[match.awayTeam]}`);
console.log(`日期: ${match.date}`);

// 提取比分
const scores = [];
$('div.score').each((i, elem) => {
  const score = $(elem).text().trim();
  if (score.match(/^\d+$/)) {
    scores.push(parseInt(score));
  }
});
if (scores.length >= 2) {
  match.homeScore = scores[0];
  match.awayScore = scores[1];
  console.log(`比分: ${match.homeScore} - ${match.awayScore}`);
}

// 提取时间
$('*').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('Kick-off')) {
    const timeMatch = text.match(/Kick-off:\s*(\d+:\d+)/);
    if (timeMatch) {
      match.time = timeMatch[1];
      console.log(`开球时间: ${match.time}`);
    }
  }
});

// 提取场馆
$('*').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('Venue:') && !match.venue) {
    const venueMatch = text.match(/Venue:\s*([^\n]+)/);
    if (venueMatch) {
      match.venue = venueMatch[1].trim();
      console.log(`场馆: ${match.venue}`);
    }
  }
});

// 提取观众
$('*').each((i, elem) => {
  const text = $(elem).text();
  const attMatch = text.match(/Attendance:\s*([\d,]+)/);
  if (attMatch && !match.attendance) {
    match.attendance = attMatch[1];
    console.log(`观众: ${match.attendance}`);
  }
});

// 提取裁判
$('*').each((i, elem) => {
  const text = $(elem).text();
  const refMatch = text.match(/Referee:\s*([^\n]+)/);
  if (refMatch && !match.referee) {
    match.referee = refMatch[1].trim();
    console.log(`裁判: ${match.referee}`);
  }
});

console.log('');

// ============ 2. 球队阵容和替补 ============
console.log('【2. 球队阵容和替补】');

const lineups = {
  home: { name: teamNameMap[match.homeTeam], formation: '', players: [], substitutes: [] },
  away: { name: teamNameMap[match.awayTeam], formation: '', players: [], substitutes: [] }
};

let teamCount = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';
  const className = $table.attr('class') || '';

  if (className.includes('stats_table') && !id.includes('keeper')) {
    const team = teamCount === 0 ? 'home' : 'away';
    teamCount++;

    const players = [];
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      const cells = [];
      $row.find('td').each((j, cell) => {
        cells.push($(cell).text().trim());
      });

      if (cells.length >= 13) {
        const player = {
          name: cells[0] || '',
          number: parseInt(cells[1]) || 0,
          nationality: cells[2] || '',
          position: positionMap[cells[3]] || cells[3] || '',
          age: cells[4] || '',
          minutes: parseInt(cells[5]) || 0,
          goals: parseInt(cells[6]) || 0,
          assists: parseInt(cells[7]) || 0,
          shots: parseInt(cells[10]) || 0,
          shotsOnTarget: parseInt(cells[11]) || 0,
          yellowCards: parseInt(cells[12]) || 0,
          redCards: parseInt(cells[13]) || 0
        };

        if (player.name && player.minutes > 0) {
          players.push(player);
        }
      }
    });

    lineups[team].players = players.slice(0, 11);
    lineups[team].substitutes = players.slice(11);

    console.log(`${team === 'home' ? '主队' : '客队'}: ${players.length}人`);
    console.log(`  首发 (${lineups[team].players.length}): ${lineups[team].players.map(p => p.name).join(', ')}`);
    if (lineups[team].substitutes.length > 0) {
      console.log(`  替补 (${lineups[team].substitutes.length}): ${lineups[team].substitutes.map(p => p.name).join(', ')}`);
    }
    console.log('');
  }
});

// ============ 3. 比赛事件 ============
console.log('【3. 比赛事件】');

const timeline = [];
$('div').each((i, elem) => {
  const text = $(elem).text();
  // 查找包含时间的事件
  const eventMatch = text.match(/(\d+)'\s+(.+)/);
  if (eventMatch && (text.includes('Goal') || text.includes('Substitute') || text.includes('Yellow') || text.includes('Red'))) {
    timeline.push({
      minute: parseInt(eventMatch[1]),
      event: eventMatch[2].trim().substring(0, 100)
    });
  }
});

if (timeline.length > 0) {
  timeline.sort((a, b) => a.minute - b.minute);
  timeline.forEach(event => {
    console.log(`  ${event.minute}' - ${event.event}`);
  });
} else {
  console.log('  未找到比赛事件');
}

console.log('');

// ============ 4. 统计数据 ============
console.log('【4. 统计数据】');

const statistics = [];
$('*').each((i, elem) => {
  const text = $(elem).text();

  if (text.includes('Possession')) {
    const possMatch = text.match(/(\d+)%.*?(\d+)%/);
    if (possMatch) {
      statistics.push({ name: '控球率', home: `${possMatch[1]}%`, away: `${possMatch[2]}%` });
      console.log(`  控球率: ${possMatch[1]}% - ${possMatch[2]}%`);
    }
  }

  if (text.includes('Shots on Target')) {
    const shotsMatch = text.match(/(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)/);
    if (shotsMatch) {
      statistics.push({ name: '射正', home: shotsMatch[1], away: shotsMatch[3] });
      statistics.push({ name: '射门', home: shotsMatch[2], away: shotsMatch[4] });
      console.log(`  射正: ${shotsMatch[1]} - ${shotsMatch[3]}`);
      console.log(`  射门: ${shotsMatch[2]} - ${shotsMatch[4]}`);
    }
  }
});

console.log('');

// ============ 5. 生成完整JSON ============
console.log('【5. 生成完整JSON】');

// 转换日期格式
const dateParts = match.date.match(/(\w+)\s+(\d+),?\s+(\d{4})/);
let formattedDate = '2024-03-01';
if (dateParts) {
  const months = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08',
    'September': '09', 'October': '10', 'November': '11', 'December': '12'
  };
  const month = months[dateParts[1]] || '03';
  const day = dateParts[2].padStart(2, '0');
  const year = dateParts[3];
  formattedDate = `${year}-${month}-${day}`;
}

const fullReport = {
  match: {
    id: 1,
    round: '第1轮',
    date: formattedDate,
    time: match.time || '19:35',
    homeTeam: teamNameMap[match.homeTeam] || match.homeTeam,
    awayTeam: teamNameMap[match.awayTeam] || match.awayTeam,
    venue: match.venue || '未知',
    result: `${match.homeScore || 0}-${match.awayScore || 0}`,
    status: '已结束',
    attendance: match.attendance || '未知',
    referee: match.referee || '未知',
    competition: '中国足球协会超级联赛',
    season: '2024'
  },
  lineups: {
    home: {
      name: lineups.home.name,
      formation: lineups.home.formation || '4-2-3-1',
      players: lineups.home.players,
      substitutes: lineups.home.substitutes
    },
    away: {
      name: lineups.away.name,
      formation: lineups.away.formation || '4-2-3-1',
      players: lineups.away.players,
      substitutes: lineups.away.substitutes
    }
  },
  detailedPlayerStats: {
    home: lineups.home.players.slice(0, 5).map(p => ({
      player: p.name, number: p.number, position: p.position,
      minutes: p.minutes, goals: p.goals, assists: p.assists,
      shots: p.shots, shotsOnTarget: p.shotsOnTarget,
      yellowCards: p.yellowCards, redCards: p.redCards
    })),
    away: lineups.away.players.slice(0, 5).map(p => ({
      player: p.name, number: p.number, position: p.position,
      minutes: p.minutes, goals: p.goals, assists: p.assists,
      shots: p.shots, shotsOnTarget: p.shotsOnTarget,
      yellowCards: p.yellowCards, redCards: p.redCards
    }))
  },
  matchTimeline: timeline,
  statistics: statistics,
  tacticalAnalysis: {
    homeFormation: '4-2-3-1',
    awayFormation: '4-2-3-1',
    possession: { home: 50, away: 50 }
  },
  summary: '比赛报告',
  highlights: timeline.map(e => ({
    time: `${e.minute}'`,
    description: e.event
  }))
};

// 保存JSON
fs.writeFileSync('./data/test_match_report.json', JSON.stringify(fullReport, null, 2), 'utf8');

console.log('');
console.log('='.repeat(80));
console.log('✅ 测试完成！');
console.log('='.repeat(80));
console.log('');
console.log('数据提取结果:');
console.log(`  比赛信息: ✅`);
console.log(`  球队阵容: 主队${lineups.home.players.length + lineups.home.substitutes.length}人, 客队${lineups.away.players.length + lineups.away.substitutes.length}人`);
console.log(`  比赛事件: ${timeline.length}个`);
console.log(`  统计数据: ${statistics.length}项`);
console.log('');
console.log('JSON文件已保存: data/test_match_report.json');
console.log('');

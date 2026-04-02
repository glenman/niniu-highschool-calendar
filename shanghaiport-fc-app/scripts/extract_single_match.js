#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('='.repeat(80));
console.log('单场比赛数据提取测试');
console.log('='.repeat(80));
console.log('');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

// ============ 1. 比赛基本信息 ============
console.log('【1. 比赛基本信息】');

const title = $('title').text();
console.log('页面标题:', title);

const matchInfo = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)$/);
if (matchInfo) {
  console.log('主队:', matchInfo[1].trim());
  console.log('客队:', matchInfo[2].trim());
  console.log('日期:', matchInfo[3].trim());
}

// 提取比分
const scores = [];
$('div.score').each((i, elem) => {
  const score = $(elem).text().trim();
  if (score.match(/^\d+$/)) {
    scores.push(parseInt(score));
  }
});
if (scores.length >= 2) {
  console.log('比分:', `${scores[0]} - ${scores[1]}`);
}

// 提取场馆、观众、裁判
const body = $('body').text();

const venueMatch = body.match(/Venue:\s*([^\n]+)/);
if (venueMatch) {
  console.log('场馆:', venueMatch[1].trim());
}

const attMatch = body.match(/Attendance:\s*([\d,]+)/);
if (attMatch) {
  console.log('观众:', attMatch[1]);
}

const refMatch = body.match(/Referee:\s*([^\n]+)/);
if (refMatch) {
  console.log('裁判:', refMatch[1].trim());
}

console.log('');

// ============ 2. 球队阵容和替补 ============
console.log('【2. 球队阵容和替补】');

const teams = [
  { name: 'Shanghai Port', players: [] },
  { name: 'Wuhan Three Towns', players: [] }
];

let teamIndex = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';
  const className = $table.attr('class') || '';

  if (className.includes('stats_table') && !id.includes('keeper')) {
    const team = teamIndex < 1 ? teams[0] : teams[1];
    teamIndex++;

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
          position: cells[3] || '',
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
          team.players.push(player);
        }
      }
    });

    console.log(`${team.name}: ${team.players.length}人`);
    console.log(`  首发: ${team.players.slice(0, 11).map(p => `${p.name}(#${p.number})`).join(', ')}`);
    if (team.players.length > 11) {
      console.log(`  替补: ${team.players.slice(11).map(p => `${p.name}(#${p.number})`).join(', ')}`);
    }
    console.log('');
  }
});

// ============ 3. 比赛事件 ============
console.log('【3. 比赛事件】');

const events = [];
$('div').each((i, elem) => {
  const text = $(elem).text();

  // 查找事件行
  if (text.match(/\d+'\s+(Goal|Yellow|Substitute)/)) {
    const lines = text.split('\n');
    lines.forEach(line => {
      const eventMatch = line.match(/(\d+'\d*)\s+(.+)/);
      if (eventMatch) {
        const minute = eventMatch[1];
        const event = eventMatch[2].trim();

        if (event.includes('Goal')) {
          events.push({ minute, type: '进球', event });
        } else if (event.includes('Yellow')) {
          events.push({ minute, type: '黄牌', event });
        } else if (event.includes('Substitute')) {
          events.push({ minute, type: '换人', event });
        }
      }
    });
  }
});

if (events.length > 0) {
  console.log(`找到 ${events.length} 个事件:`);
  events.forEach(e => {
    console.log(`  ${e.minute} - [${e.type}] ${e.event.substring(0, 60)}`);
  });
} else {
  console.log('未找到比赛事件');
}

console.log('');

// ============ 4. 统计数据 ============
console.log('【4. 统计数据】');

const stats = [];
$('div').each((i, elem) => {
  const text = $(elem).text();

  if (text.includes('Possession') && text.includes('%')) {
    const possMatch = text.match(/(\d+)%.*?(\d+)%/);
    if (possMatch) {
      stats.push({ name: '控球率', home: possMatch[1] + '%', away: possMatch[2] + '%' });
      console.log(`控球率: ${possMatch[1]}% vs ${possMatch[2]}%`);
    }
  }

  if (text.includes('Shots on Target')) {
    const shotsMatch = text.match(/(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)/);
    if (shotsMatch) {
      stats.push({ name: '射正', home: shotsMatch[1], away: shotsMatch[3] });
      stats.push({ name: '射门', home: shotsMatch[2], away: shotsMatch[4] });
      console.log(`射正: ${shotsMatch[1]} vs ${shotsMatch[3]}`);
      console.log(`射门: ${shotsMatch[2]} vs ${shotsMatch[4]}`);
    }
  }
});

console.log('');

// ============ 5. 保存到CSV ============
console.log('【5. 保存数据到CSV】');

const csvRows = [];

// 标题行
csvRows.push([
  '数据类型', '字段', '主队值', '客队值', '备注'
]);

// 比赛信息
csvRows.push(['比赛信息', '主队', teams[0].name, '', '']);
csvRows.push(['比赛信息', '客队', teams[1].name, '', '']);
csvRows.push(['比赛信息', '日期', matchInfo ? matchInfo[3] : '', '', '']);
csvRows.push(['比赛信息', '比分', scores[0] || 0, scores[1] || 0, '']);

// 球员数据
teams.forEach((team, idx) => {
  team.players.forEach(player => {
    csvRows.push([
      idx === 0 ? '主队球员' : '客队球员',
      player.name,
      `#${player.number}`,
      player.position,
      `${player.minutes}分钟 ${player.goals}球 ${player.assists}助`
    ]);
  });
});

// 统计数据
stats.forEach(stat => {
  csvRows.push(['统计数据', stat.name, stat.home, stat.away, '']);
});

// 比赛事件
events.forEach(event => {
  csvRows.push(['比赛事件', event.minute, event.type, event.event.substring(0, 50), '']);
});

// 保存CSV
const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/test_match_data.csv', '\ufeff' + csvContent, 'utf8');

console.log('✓ 已保存到CSV: data/test_match_data.csv');
console.log(`  共 ${csvRows.length} 行数据`);
console.log('');

// ============ 6. 生成JSON报告 ============
console.log('【6. 生成JSON报告】');

// 读取模板
const template = JSON.parse(fs.readFileSync('./templates/full_match_report.json', 'utf8'));

// 填充数据
template.match.id = 1;
template.match.round = '第1轮';
template.match.homeTeam = '上海海港';
template.match.awayTeam = '武汉三镇';
template.match.result = `${scores[0] || 0}-${scores[1] || 0}`;

// 转换日期格式
if (matchInfo) {
  const dateStr = matchInfo[3];
  const dateMatch = dateStr.match(/(\w+)\s+(\d+),?\s+(\d{4})/);
  if (dateMatch) {
    const months = {
      'January': '01', 'February': '02', 'March': '03',
      'April': '04', 'May': '05', 'June': '06',
      'July': '07', 'August': '08', 'September': '09',
      'October': '10', 'November': '11', 'December': '12'
    };
    const month = months[dateMatch[1]] || '03';
    const day = dateMatch[2].padStart(2, '0');
    template.match.date = `${dateMatch[3]}-${month}-${day}`;
  }
}

template.lineups.home.players = teams[0].players.slice(0, 11);
template.lineups.home.substitutes = teams[0].players.slice(11);
template.lineups.away.players = teams[1].players.slice(0, 11);
template.lineups.away.substitutes = teams[1].players.slice(11);

template.statistics = stats;

template.matchTimeline = events.map(e => ({
  minute: parseInt(e.minute.replace("'", '')),
  type: e.type,
  description: e.event
}));

// 保存JSON
fs.writeFileSync('./data/test_match_report.json', JSON.stringify(template, null, 2), 'utf8');

console.log('✓ 已生成JSON报告: data/test_match_report.json');
console.log('');

console.log('='.repeat(80));
console.log('✅ 测试完成！');
console.log('='.repeat(80));

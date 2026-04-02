#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

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
  'Chengdu Better City': '成都蓉城',
  'Changchun Yatai': '长春亚泰',
  'Qingdao Hainiu': '青岛海牛',
  'Shanghai Shenhua': '上海申花',
  'Beijing Guoan': '北京国安',
  'Dalian Pro': '大连人'
};

const positionMap = {
  'GK': '门将', 'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫',
  'DM': '后腰', 'CM': '中场', 'AM': '攻击型中场',
  'RM': '右中场', 'LM': '左中场', 'RW': '右边锋', 'LW': '左边锋',
  'FW': '前锋', 'MF': '中场', 'DF': '后卫'
};

// 使用cheerio解析HTML
const cheerio = require('cheerio');

function parseHTML(html, roundNum) {
  const $ = cheerio.load(html);
  const data = {
    basic: { round: roundNum },
    homePlayers: [],
    awayPlayers: [],
    timeline: [],
    stats: {}
  };

  // 提取比赛标题
  const title = $('h1').first().text();
  const matchInfo = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/i);
  if (matchInfo) {
    data.basic.homeTeam = matchInfo[1].trim();
    data.basic.awayTeam = matchInfo[2].trim();
  }

  // 提取比分
  $('div.score').each((i, elem) => {
    const score = $(elem).text().trim();
    if (score.match(/^\d+-\d+$/)) {
      const parts = score.split('-');
      data.basic.homeScore = parts[0].trim();
      data.basic.awayScore = parts[1].trim();
    }
  });

  // 提取基本信息
  $('strong:contains("Venue")').each((i, elem) => {
    data.basic.venue = $(elem).next().text().trim();
  });
  $('strong:contains("Attendance")').each((i, elem) => {
    data.basic.attendance = $(elem).next().text().trim();
  });
  $('div:contains("Referee")').each((i, elem) => {
    const text = $(elem).text();
    const refMatch = text.match(/Referee:\s*(.+)/);
    if (refMatch) {
      data.basic.referee = refMatch[1].trim();
    }
  });

  // 提取球员统计表
  $('table.stats_table').each((tableIndex, table) => {
    const $table = $(table);
    const tableId = $table.attr('id');

    let team = 'home';
    if (tableId && tableId.includes('away')) {
      team = 'away';
    }

    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      const player = {
        name: $row.find('th a').text().trim() || $row.find('td').eq(0).text().trim(),
        number: parseInt($row.find('td').eq(0).text()) || 0,
        position: positionMap[$row.find('td').eq(1).text().trim()] || $row.find('td').eq(1).text().trim(),
        nationality: $row.find('td').eq(2).text().trim(),
        age: $row.find('td').eq(3).text().trim(),
        minutes: parseInt($row.find('td').eq(4).text()) || 0,
        goals: parseInt($row.find('td').eq(5).text()) || 0,
        assists: parseInt($row.find('td').eq(6).text()) || 0,
        shots: parseInt($row.find('td').eq(9).text()) || 0,
        shotsOnTarget: parseInt($row.find('td').eq(10).text()) || 0,
        yellowCards: parseInt($row.find('td').eq(11).text()) || 0,
        redCards: parseInt($row.find('td').eq(12).text()) || 0
      };

      if (player.name && player.name.length > 0) {
        if (team === 'home') {
          data.homePlayers.push(player);
        } else {
          data.awayPlayers.push(player);
        }
      }
    });
  });

  // 提取时间线事件
  $('div.event').each((i, elem) => {
    const $elem = $(elem);
    const minute = $elem.find('.minute').text().replace("'", '').trim();
    const event = $elem.text().trim();
    if (minute && event) {
      data.timeline.push({
        minute: parseInt(minute),
        event: event
      });
    }
  });

  return data;
}

// 生成CSV
function generateCSV(allMatches) {
  const rows = [];

  rows.push([
    '比赛ID', '轮次', '日期', '主队', '客队', '比分',
    '场馆', '观众', '裁判',
    '球员', '号码', '位置', '国籍', '年龄', '时间',
    '进球', '助攻', '射门', '射正', '黄牌', '红牌',
    '所属球队', '首发替补'
  ]);

  allMatches.forEach(m => {
    const base = [
      m.basic.round,
      `第${m.basic.round}轮`,
      m.basic.date || '',
      teamNameMap[m.basic.homeTeam] || m.basic.homeTeam,
      teamNameMap[m.basic.awayTeam] || m.basic.awayTeam,
      `${m.basic.homeScore || 0}-${m.basic.awayScore || 0}`,
      m.basic.venue || '',
      m.basic.attendance || '',
      m.basic.referee || ''
    ];

    // 主队首发
    m.homePlayers.slice(0, 11).forEach(p => {
      rows.push([...base, p.name, p.number, p.position, p.nationality, p.age,
        p.minutes, p.goals, p.assists, p.shots, p.shotsOnTarget, p.yellowCards, p.redCards,
        teamNameMap[m.basic.homeTeam] || m.basic.homeTeam, '首发']);
    });

    // 主队替补
    m.homePlayers.slice(11).forEach(p => {
      rows.push([...base, p.name, p.number, p.position, p.nationality, p.age,
        p.minutes, p.goals, p.assists, p.shots, p.shotsOnTarget, p.yellowCards, p.redCards,
        teamNameMap[m.basic.homeTeam] || m.basic.homeTeam, '替补']);
    });

    // 客队首发
    m.awayPlayers.slice(0, 11).forEach(p => {
      rows.push([...base, p.name, p.number, p.position, p.nationality, p.age,
        p.minutes, p.goals, p.assists, p.shots, p.shotsOnTarget, p.yellowCards, p.redCards,
        teamNameMap[m.basic.awayTeam] || m.basic.awayTeam, '首发']);
    });

    // 客队替补
    m.awayPlayers.slice(11).forEach(p => {
      rows.push([...base, p.name, p.number, p.position, p.nationality, p.age,
        p.minutes, p.goals, p.assists, p.shots, p.shotsOnTarget, p.yellowCards, p.redCards,
        teamNameMap[m.basic.awayTeam] || m.basic.awayTeam, '替补']);
    });
  });

  return rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n');
}

// 主函数
function main() {
  const htmlDir = './data/scraped_html';
  const files = fs.readdirSync(htmlDir).filter(f => f.endsWith('.html'));

  console.log(`处理 ${files.length} 个HTML文件...\n`);

  const allMatches = [];

  files.forEach(file => {
    const match = file.match(/match_(\d+)\.html/);
    if (!match) return;

    const roundNum = parseInt(match[1]);
    const filePath = path.join(htmlDir, file);
    const html = fs.readFileSync(filePath, 'utf8');

    console.log(`处理: ${file}`);
    const data = parseHTML(html, roundNum);
    allMatches.push(data);

    console.log(`  ${data.basic.homeTeam} vs ${data.basic.awayTeam}`);
    console.log(`  比分: ${data.basic.homeScore}-${data.basic.awayScore}`);
    console.log(`  主队球员: ${data.homePlayers.length}人`);
    console.log(`  客队球员: ${data.awayPlayers.length}人\n`);
  });

  // 保存CSV
  const csvPath = './data/matches_from_html.csv';
  const csv = generateCSV(allMatches);
  fs.writeFileSync(csvPath, '\ufeff' + csv, 'utf8');

  console.log(`\n✓ 已保存CSV: ${csvPath}`);
  console.log(`  总计: ${allMatches.length} 场比赛`);
}

main();

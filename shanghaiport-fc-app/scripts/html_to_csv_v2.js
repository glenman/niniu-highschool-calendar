#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

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

const cheerio = require('cheerio');

function parseHTML(html, roundNum) {
  const $ = cheerio.load(html);
  const data = {
    basic: { round: roundNum },
    homePlayers: [],
    awayPlayers: [],
    timeline: []
  };

  // 提取标题和球队
  const title = $('title').text();
  console.log(`  标题: ${title}`);

  // 尝试多种方式提取球队
  let homeTeam = '', awayTeam = '';

  // 方法1: 从URL提取
  const urlMatch = html.match(/\/matches\/\d+\/(.+?)-(.+?)-/);
  if (urlMatch) {
    homeTeam = urlMatch[1].replace(/-/g, ' ');
    awayTeam = urlMatch[2].replace(/-/g, ' ');
  }

  // 方法2: 从标题提取
  if (!homeTeam) {
    const titleMatch = title.match(/(.+?)\s+vs\.?\s+(.+?)\s+Match/i);
    if (titleMatch) {
      homeTeam = titleMatch[1].trim();
      awayTeam = titleMatch[2].trim();
    }
  }

  data.basic.homeTeam = homeTeam;
  data.basic.awayTeam = awayTeam;

  // 提取比分 - 多种方式
  $('div').each((i, elem) => {
    const text = $(elem).text().trim();
    if (text.match(/^\d+\s*-\s*\d+$/)) {
      const parts = text.split('-').map(s => s.trim());
      if (!data.basic.homeScore) {
        data.basic.homeScore = parts[0];
        data.basic.awayScore = parts[1];
      }
    }
  });

  // 提取场馆信息
  $('*:contains("Venue")').each((i, elem) => {
    const text = $(elem).text();
    if (text.includes('Venue') && !data.basic.venue) {
      const venueMatch = text.match(/Venue:\s*(.+?)(?:Att|Ref|$)/s);
      if (venueMatch) {
        data.basic.venue = venueMatch[1].trim().split('\n')[0];
      }
    }
  });

  // 提取观众人数
  $('*:contains("Attendance")').each((i, elem) => {
    const text = $(elem).text();
    const attMatch = text.match(/Attendance:\s*([\d,]+)/);
    if (attMatch && !data.basic.attendance) {
      data.basic.attendance = attMatch[1];
    }
  });

  // 提取裁判
  $('*:contains("Referee")').each((i, elem) => {
    const text = $(elem).text();
    const refMatch = text.match(/Referee:\s*([^\n]+)/);
    if (refMatch && !data.basic.referee) {
      data.basic.referee = refMatch[1].trim();
    }
  });

  // 提取球员统计 - 查找表格
  $('table').each((tableIndex, table) => {
    const $table = $(table);
    const tableHtml = $table.html();

    // 判断是主队还是客队
    let isHome = true;
    if (tableHtml.includes('id="away"') || tableHtml.includes('id="player_away')) {
      isHome = false;
    }

    // 提取球员数据
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      const cells = [];

      $row.find('td, th').each((i, cell) => {
        cells.push($(cell).text().trim());
      });

      if (cells.length >= 10 && cells[0]) {
        const player = {
          name: cells[0].replace(/^\d+\s*/, ''), // 移除号码
          number: parseInt(cells[0].match(/^\d+/)?.[0]) || 0,
          position: positionMap[cells[2]] || cells[2],
          nationality: cells[1] || '',
          age: cells[3] || '',
          minutes: parseInt(cells[4]) || 0,
          goals: parseInt(cells[5]) || 0,
          assists: parseInt(cells[6]) || 0,
          shots: parseInt(cells[9]) || 0,
          shotsOnTarget: parseInt(cells[10]) || 0,
          yellowCards: parseInt(cells[11]) || 0,
          redCards: parseInt(cells[12]) || 0
        };

        if (player.name && player.name.length > 0 && !player.name.includes('Player')) {
          if (isHome) {
            data.homePlayers.push(player);
          } else {
            data.awayPlayers.push(player);
          }
        }
      }
    });
  });

  return data;
}

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

function main() {
  const htmlDir = './data/scraped_html';
  const files = fs.readdirSync(htmlDir).filter(f => f.endsWith('.html'));

  console.log(`处理 ${files.length} 个HTML文件...\n`);

  const allMatches = [];

  files.sort().forEach(file => {
    const match = file.match(/match_(\d+)\.html/);
    if (!match) return;

    const roundNum = parseInt(match[1]);
    const filePath = path.join(htmlDir, file);
    const html = fs.readFileSync(filePath, 'utf8');

    console.log(`处理: ${file}`);
    const data = parseHTML(html, roundNum);
    allMatches.push(data);

    console.log(`  ${data.basic.homeTeam} vs ${data.basic.awayTeam}`);
    console.log(`  比分: ${data.basic.homeScore || 0}-${data.basic.awayScore || 0}`);
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

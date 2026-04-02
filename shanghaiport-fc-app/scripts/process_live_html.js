#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

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

function parseHTML(html) {
  const $ = cheerio.load(html);
  const data = {
    basic: {},
    homePlayers: [],
    awayPlayers: [],
    timeline: []
  };

  // 提取标题
  const title = $('title').text();
  console.log(`标题: ${title}`);

  // 提取球队名称
  const matchInfo = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/i);
  if (matchInfo) {
    data.basic.homeTeam = matchInfo[1].trim();
    data.basic.awayTeam = matchInfo[2].trim().split(' – ')[0].trim();
  }

  // 提取比分
  $('div.score').each((i, elem) => {
    const score = $(elem).text().trim();
    if (score.match(/^\d+\s*-\s*\d+$/)) {
      const parts = score.split('-').map(s => s.trim());
      data.basic.homeScore = parts[0];
      data.basic.awayScore = parts[1];
    }
  });

  // 提取日期
  $('div').each((i, elem) => {
    const text = $(elem).text();
    if (text.includes('Friday') || text.includes('Saturday') || text.includes('Sunday')) {
      const dateMatch = text.match(/(Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+,?\s+\d{4}/);
      if (dateMatch && !data.basic.date) {
        data.basic.date = dateMatch[0];
      }
    }
  });

  // 提取场馆
  $('*:contains("Venue")').each((i, elem) => {
    const text = $(elem).text();
    if (text.includes('Venue') && !data.basic.venue) {
      const venueMatch = text.match(/Venue:\s*([^\n]+)/);
      if (venueMatch) {
        data.basic.venue = venueMatch[1].trim();
      }
    }
  });

  // 提取观众
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

  // 提取球员统计表
  let tableCount = 0;
  let firstTeamId = null;
  
  $('table.stats_table').each((tableIndex, table) => {
    const $table = $(table);
    const tableId = $table.attr('id') || '';
    
    // 跳过门将统计表
    if (tableId.includes('keeper_stats')) {
      return;
    }

    // 判断主客队：第一个出现的是主队
    let team = 'home';
    if (tableCount === 0) {
      firstTeamId = tableId;
    } else if (tableId !== firstTeamId && tableId.includes('stats_')) {
      team = 'away';
    }

    tableCount++;

    // 提取球员数据
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      const cells = [];

      $row.find('td, th').each((i, cell) => {
        cells.push($(cell).text().trim());
      });

      if (cells.length >= 10) {
        const player = {
          name: cells[0].replace(/^\d+\s*/, '').trim(),
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
          if (team === 'home') {
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

// 处理HTML文件
const htmlPath = process.argv[2] || './data/scraped_html/match_live.html';
const html = fs.readFileSync(htmlPath, 'utf8');

console.log(`\n处理HTML文件: ${htmlPath}`);
console.log(`文件大小: ${(html.length / 1024).toFixed(1)} KB\n`);

const data = parseHTML(html);

console.log('提取结果:');
console.log(`  主队: ${data.basic.homeTeam}`);
console.log(`  客队: ${data.basic.awayTeam}`);
console.log(`  比分: ${data.basic.homeScore || 0}-${data.basic.awayScore || 0}`);
console.log(`  日期: ${data.basic.date || '未知'}`);
console.log(`  场馆: ${data.basic.venue || '未知'}`);
console.log(`  观众: ${data.basic.attendance || '未知'}`);
console.log(`  裁判: ${data.basic.referee || '未知'}`);
console.log(`  主队球员: ${data.homePlayers.length}人`);
console.log(`  客队球员: ${data.awayPlayers.length}人`);

if (data.homePlayers.length > 0) {
  console.log('\n主队首发:');
  data.homePlayers.slice(0, 11).forEach((p, i) => {
    console.log(`  ${i+1}. ${p.name} (#${p.number}) - ${p.position} - ${p.goals}球 ${p.assists}助`);
  });
}

if (data.awayPlayers.length > 0) {
  console.log('\n客队首发:');
  data.awayPlayers.slice(0, 11).forEach((p, i) => {
    console.log(`  ${i+1}. ${p.name} (#${p.number}) - ${p.position} - ${p.goals}球 ${p.assists}助`);
  });
}

// 保存为JSON
const output = {
  ...data,
  basic: {
    ...data.basic,
    homeTeam: teamNameMap[data.basic.homeTeam] || data.basic.homeTeam,
    awayTeam: teamNameMap[data.basic.awayTeam] || data.basic.awayTeam
  },
  homePlayers: data.homePlayers,
  awayPlayers: data.awayPlayers
};

const outputPath = htmlPath.replace('.html', '_extracted.json');
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2), 'utf8');
console.log(`\n✓ 数据已保存: ${outputPath}`);

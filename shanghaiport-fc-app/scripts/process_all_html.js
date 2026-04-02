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

function parseMatchHTML(html, roundNum) {
  const $ = cheerio.load(html);
  const data = {
    basic: { round: roundNum },
    homePlayers: [],
    awayPlayers: []
  };

  // 提取标题和球队
  const title = $('title').text();
  const matchInfo = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/i);
  if (matchInfo) {
    data.basic.homeTeam = matchInfo[1].trim();
    data.basic.awayTeam = matchInfo[2].trim().split(' – ')[0].trim();
  }

  // 提取比分
  let foundScore = false;
  $('div').each((i, elem) => {
    if (foundScore) return;
    const text = $(elem).text().trim();
    if (text.match(/^\d+\s*-\s*\d+$/)) {
      const parts = text.split('-').map(s => s.trim());
      data.basic.homeScore = parts[0];
      data.basic.awayScore = parts[1];
      foundScore = true;
    }
  });

  // 提取日期
  $('div').each((i, elem) => {
    const text = $(elem).text();
    const dateMatch = text.match(/(Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+,?\s+\d{4}/);
    if (dateMatch && !data.basic.date) {
      data.basic.date = dateMatch[0];
    }
  });

  // 提取场馆
  $('*').each((i, elem) => {
    const text = $(elem).text();
    if (text.includes('Venue:') && !data.basic.venue) {
      const venueMatch = text.match(/Venue:\s*([^\n]+)/);
      if (venueMatch) {
        data.basic.venue = venueMatch[1].trim().substring(0, 100);
      }
    }
  });

  // 提取观众
  $('*').each((i, elem) => {
    const text = $(elem).text();
    const attMatch = text.match(/Attendance:\s*([\d,]+)/);
    if (attMatch && !data.basic.attendance) {
      data.basic.attendance = attMatch[1];
    }
  });

  // 提取裁判
  $('*').each((i, elem) => {
    const text = $(elem).text();
    const refMatch = text.match(/Referee:\s*([^\n]+)/);
    if (refMatch && !data.basic.referee) {
      data.basic.referee = refMatch[1].trim();
    }
  });

  // 提取球员统计表
  let tableIndex = 0;
  let firstTeamId = null;

  $('table.stats_table').each((i, table) => {
    const $table = $(table);
    const tableId = $table.attr('id') || '';

    // 跳过门将统计
    if (tableId.includes('keeper_stats')) {
      return;
    }

    // 判断主客队
    let team = 'home';
    if (tableIndex === 0) {
      firstTeamId = tableId;
    } else if (tableId !== firstTeamId) {
      team = 'away';
    }

    tableIndex++;

    // 提取球员数据
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      const cells = [];

      $row.find('td, th').each((j, cell) => {
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

        if (player.name && player.name.length > 0) {
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

function generateFullReport(matchData) {
  return {
    match: {
      id: matchData.basic.round,
      round: `第${matchData.basic.round}轮`,
      date: matchData.basic.date || '未知',
      time: "19:35",
      homeTeam: teamNameMap[matchData.basic.homeTeam] || matchData.basic.homeTeam,
      awayTeam: teamNameMap[matchData.basic.awayTeam] || matchData.basic.awayTeam,
      venue: matchData.basic.venue || '未知',
      result: `${matchData.basic.homeScore || 0}-${matchData.basic.awayScore || 0}`,
      status: "已结束",
      attendance: matchData.basic.attendance || '未知',
      referee: matchData.basic.referee || '未知',
      competition: "中国足球协会超级联赛",
      season: "2024"
    },
    lineups: {
      home: {
        name: teamNameMap[matchData.basic.homeTeam] || matchData.basic.homeTeam,
        formation: "4-2-3-1",
        players: matchData.homePlayers.slice(0, 11),
        substitutes: matchData.homePlayers.slice(11)
      },
      away: {
        name: teamNameMap[matchData.basic.awayTeam] || matchData.basic.awayTeam,
        formation: "4-2-3-1",
        players: matchData.awayPlayers.slice(0, 11),
        substitutes: matchData.awayPlayers.slice(11)
      }
    },
    detailedPlayerStats: {
      home: matchData.homePlayers.slice(0, 5).map(p => ({
        player: p.name, number: p.number, position: p.position, age: p.age, minutes: p.minutes,
        shots: p.shots, shotsOnTarget: p.shotsOnTarget, goals: p.goals, assists: p.assists,
        keyPasses: 0, crosses: 0, tacklesWon: 0, interceptions: 0, foulsCommitted: 0,
        foulsWon: 0, offsides: 0, yellowCards: p.yellowCards, redCards: p.redCards
      })),
      away: matchData.awayPlayers.slice(0, 5).map(p => ({
        player: p.name, number: p.number, position: p.position, age: p.age, minutes: p.minutes,
        shots: p.shots, shotsOnTarget: p.shotsOnTarget, goals: p.goals, assists: p.assists,
        keyPasses: 0, crosses: 0, tacklesWon: 0, interceptions: 0, foulsCommitted: 0,
        foulsWon: 0, offsides: 0, yellowCards: p.yellowCards, redCards: p.redCards
      }))
    },
    matchTimeline: [],
    statistics: [],
    tacticalAnalysis: { homeFormation: "4-2-3-1", awayFormation: "4-2-3-1", possession: { home: 50, away: 50 } },
    keyMetrics: { expectedGoals: { home: 0, away: 0 }, bigChances: { home: 0, away: 0 } },
    summary: "比赛报告",
    highlights: []
  };
}

function main() {
  const htmlDir = './data/scraped_html_live';
  const outputDir = './data/match_reports_final_v2';

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const files = fs.readdirSync(htmlDir).filter(f => f.endsWith('.html'));
  console.log(`处理 ${files.length} 个HTML文件...\n`);

  files.sort().forEach(file => {
    const match = file.match(/match_(\d+)\.html/);
    if (!match) return;

    const roundNum = parseInt(match[1]);
    const htmlPath = path.join(htmlDir, file);
    const html = fs.readFileSync(htmlPath, 'utf8');

    console.log(`处理: ${file}`);
    const matchData = parseMatchHTML(html, roundNum);
    const fullReport = generateFullReport(matchData);

    // 生成文件名
    const fileName = `${fullReport.match.date.replace(/[^0-9-]/g, '-')}-中超-第${roundNum}轮.json`;
    const outputPath = path.join(outputDir, fileName);

    fs.writeFileSync(outputPath, JSON.stringify(fullReport, null, 2), 'utf8');

    console.log(`  ✓ ${fileName}`);
    console.log(`    ${fullReport.match.homeTeam} vs ${fullReport.match.awayTeam}`);
    console.log(`    比分: ${fullReport.match.result}`);
    console.log(`    主队球员: ${matchData.homePlayers.length}人`);
    console.log(`    客队球员: ${matchData.awayPlayers.length}人\n`);
  });

  console.log(`\n✅ 完成！共生成 ${files.length} 个报告`);
  console.log(`📁 保存位置: ${outputDir}`);
}

main();

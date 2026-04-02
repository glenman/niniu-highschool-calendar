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
  'Changchun Yatai': '长春亚泰',
  'Qingdao Hainiu': '青岛海牛',
  'Shanghai Shenhua': '上海申花',
  'Beijing Guoan': '北京国安'
};

const positionMap = {
  'GK': '门将', 'FW': '前锋', 'MF': '中场', 'DF': '后卫',
  'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫',
  'DM': '后腰', 'CM': '中场', 'AM': '攻击型中场'
};

function parseMatchHTML(html, roundNum) {
  const $ = cheerio.load(html);
  const data = {
    basic: { round: roundNum },
    homePlayers: [],
    awayPlayers: []
  };

  // 1. 提取标题和球队名称
  const title = $('title').text();
  const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/);
  if (titleMatch) {
    data.basic.homeTeam = titleMatch[1].trim();
    data.basic.awayTeam = titleMatch[2].trim();
  }

  // 2. 提取比分 - 查找独立的比分元素
  let foundScore = false;
  $('div, span, strong').each((i, elem) => {
    if (foundScore) return;
    const text = $(elem).text().trim();
    // 只匹配纯数字-数字格式
    if (text.match(/^\d+\s*-\s*\d+$/)) {
      const parts = text.split(/\s*-\s*/).map(s => parseInt(s.trim()));
      if (parts.length === 2 && parts[0] >= 0 && parts[0] <= 10 && parts[1] >= 0 && parts[1] <= 10) {
        data.basic.homeScore = parts[0];
        data.basic.awayScore = parts[1];
        foundScore = true;
      }
    }
  });

  // 3. 提取日期 - 从标题
  const dateMatch = title.match(/–\s*(.+?)$/);
  if (dateMatch) {
    data.basic.date = dateMatch[1].trim();
  }

  // 4. 提取球员统计表
  let teamCount = 0;
  $('table').each((i, table) => {
    const $table = $(table);
    const id = $table.attr('id') || '';
    const className = $table.attr('class') || '';

    // 跳过门将统计表
    if (id.includes('keeper')) {
      return;
    }

    // 只处理stats_table
    if (!className.includes('stats_table')) {
      return;
    }

    const team = teamCount === 0 ? 'home' : 'away';
    teamCount++;

    // 提取球员数据
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);

      // 球员姓名在th中
      const name = $row.find('th').text().trim();

      // 其他数据在td中
      const cells = [];
      $row.find('td').each((j, cell) => {
        cells.push($(cell).text().trim());
      });

      if (name && cells.length >= 13) {
        const player = {
          name: name,
          number: parseInt(cells[0]) || 0,
          nationality: cells[1] || '',
          position: positionMap[cells[2]] || cells[2] || '',
          age: cells[3] || '',
          minutes: parseInt(cells[4]) || 0,
          goals: parseInt(cells[5]) || 0,
          assists: parseInt(cells[6]) || 0,
          shots: parseInt(cells[10]) || 0,
          shotsOnTarget: parseInt(cells[11]) || 0,
          yellowCards: parseInt(cells[12]) || 0,
          redCards: parseInt(cells[13]) || 0
        };

        if (player.name && player.minutes > 0) {
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
  const date = matchData.basic.date || '2024-03-01';
  // 转换日期格式 "Friday March 1, 2024" -> "2024-03-01"
  const dateParts = date.match(/(\w+)\s+(\d+),?\s+(\d{4})/);
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

  return {
    match: {
      id: matchData.basic.round,
      round: `第${matchData.basic.round}轮`,
      date: formattedDate,
      time: "19:35",
      homeTeam: teamNameMap[matchData.basic.homeTeam] || matchData.basic.homeTeam,
      awayTeam: teamNameMap[matchData.basic.awayTeam] || matchData.basic.awayTeam,
      result: `${matchData.basic.homeScore || 0}-${matchData.basic.awayScore || 0}`,
      status: "已结束",
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
        player: p.name, number: p.number, position: p.position,
        minutes: p.minutes, goals: p.goals, assists: p.assists,
        shots: p.shots, shotsOnTarget: p.shotsOnTarget,
        yellowCards: p.yellowCards, redCards: p.redCards
      })),
      away: matchData.awayPlayers.slice(0, 5).map(p => ({
        player: p.name, number: p.number, position: p.position,
        minutes: p.minutes, goals: p.goals, assists: p.assists,
        shots: p.shots, shotsOnTarget: p.shotsOnTarget,
        yellowCards: p.yellowCards, redCards: p.redCards
      }))
    },
    matchTimeline: [],
    statistics: [],
    tacticalAnalysis: {
      homeFormation: "4-2-3-1",
      awayFormation: "4-2-3-1",
      possession: { home: 50, away: 50 }
    },
    summary: "比赛报告",
    highlights: []
  };
}

function main() {
  const htmlDir = './data/scraped_html_live';
  const outputDir = './data/match_reports_from_html';

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const files = fs.readdirSync(htmlDir).filter(f => f.endsWith('.html'));
  console.log(`处理 ${files.length} 个HTML文件...\n`);

  let successCount = 0;
  let failCount = 0;

  files.sort((a, b) => {
    const numA = parseInt(a.match(/match_(\d+)/)?.[1] || 0);
    const numB = parseInt(b.match(/match_(\d+)/)?.[1] || 0);
    return numA - numB;
  }).forEach(file => {
    const match = file.match(/match_(\d+)\.html/);
    if (!match) return;

    const roundNum = parseInt(match[1]);
    const htmlPath = path.join(htmlDir, file);
    const html = fs.readFileSync(htmlPath, 'utf8');

    try {
      console.log(`[${roundNum}/30] 处理: ${file}`);
      const matchData = parseMatchHTML(html, roundNum);
      const fullReport = generateFullReport(matchData);

      // 生成文件名
      const fileName = `${fullReport.match.date}-中超-第${roundNum}轮.json`;
      const outputPath = path.join(outputDir, fileName);

      fs.writeFileSync(outputPath, JSON.stringify(fullReport, null, 2), 'utf8');

      console.log(`  ✓ ${fileName}`);
      console.log(`    ${fullReport.match.homeTeam} vs ${fullReport.match.awayTeam} (${fullReport.match.result})`);
      console.log(`    主队: ${matchData.homePlayers.length}人, 客队: ${matchData.awayPlayers.length}人\n`);

      successCount++;
    } catch (error) {
      console.log(`  ✗ 处理失败: ${error.message}\n`);
      failCount++;
    }
  });

  console.log(`\n✅ 完成！`);
  console.log(`  成功: ${successCount}个`);
  console.log(`  失败: ${failCount}个`);
  console.log(`📁 保存位置: ${outputDir}`);
}

main();

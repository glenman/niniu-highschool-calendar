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
  'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫'
};

function parseHTML(html, roundNum) {
  const $ = cheerio.load(html);
  const data = {
    basic: { round: roundNum },
    homePlayers: [],
    awayPlayers: []
  };

  // 提取球队名称 - 从URL
  const urlMatch = html.match(/\/matches\/[^/]+\/(.+?)-(.+?)-\w+-\d+-\d+/);
  if (urlMatch) {
    data.basic.homeTeam = urlMatch[1].replace(/-/g, ' ');
    data.basic.awayTeam = urlMatch[2].replace(/-/g, ' ');
  }

  // 提取比分 - 查找所有可能的比分格式
  $('*').each((i, elem) => {
    const text = $(elem).text().trim();
    if (text.match(/^\d+\s*-\s*\d+$/) && !data.basic.homeScore) {
      const parts = text.split('-').map(s => parseInt(s.trim()));
      if (parts[0] >= 0 && parts[0] <= 10 && parts[1] >= 0 && parts[1] <= 10) {
        data.basic.homeScore = parts[0];
        data.basic.awayScore = parts[1];
      }
    }
  });

  // 提取日期 - 从标题
  const title = $('title').text();
  const dateMatch = title.match(/(\w+)\s+(\w+)\s+(\d+),?\s+(\d{4})/);
  if (dateMatch) {
    data.basic.date = dateMatch[0];
  }

  // 提取球员统计表
  let teamCount = 0;
  $('table[id^="stats_"][id$="_summary"]').each((i, table) => {
    const $table = $(table);
    const team = teamCount === 0 ? 'home' : 'away';
    teamCount++;

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
      date: matchData.basic.date || '2024-03-01',
      time: "19:35",
      homeTeam: teamNameMap[matchData.basic.homeTeam] || matchData.basic.homeTeam,
      awayTeam: teamNameMap[matchData.basic.awayTeam] || matchData.basic.awayTeam,
      result: `${matchData.basic.homeScore || 0}-${matchData.basic.awayScore || 0}`,
      status: "已结束"
    },
    lineups: {
      home: {
        name: teamNameMap[matchData.basic.homeTeam] || matchData.basic.homeTeam,
        players: matchData.homePlayers.slice(0, 11),
        substitutes: matchData.homePlayers.slice(11)
      },
      away: {
        name: teamNameMap[matchData.basic.awayTeam] || matchData.basic.awayTeam,
        players: matchData.awayPlayers.slice(0, 11),
        substitutes: matchData.awayPlayers.slice(11)
      }
    }
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

    console.log(`[${roundNum}/30] 处理: ${file}`);
    const matchData = parseHTML(html, roundNum);
    const fullReport = generateFullReport(matchData);

    // 生成文件名
    const fileName = `${fullReport.match.date.replace(/[^0-9]/g, '-')}-中超-第${roundNum}轮.json`;
    const outputPath = path.join(outputDir, fileName);

    fs.writeFileSync(outputPath, JSON.stringify(fullReport, null, 2), 'utf8');

    console.log(`  ✓ ${fileName}`);
    console.log(`    ${fullReport.match.homeTeam} vs ${fullReport.match.awayTeam} (${fullReport.match.result})`);
    console.log(`    主队: ${matchData.homePlayers.length}人, 客队: ${matchData.awayPlayers.length}人\n`);
  });

  console.log(`\n✅ 完成！共生成 ${files.length} 个报告`);
  console.log(`📁 保存位置: ${outputDir}`);
}

main();

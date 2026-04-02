#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

console.log('========================================');
console.log('批量处理 - 改进版v2');
console.log('========================================\n');

// 读取模板
const template = JSON.parse(fs.readFileSync('./templates/full_match_report.json', 'utf8'));

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

function processMatchSimple(htmlFile, roundNum) {
  try {
    const html = fs.readFileSync(htmlFile, 'utf8');
    const $ = cheerio.load(html);

    console.log(`\n【第${roundNum}轮】`);

    // 提取标题
    const title = $('title').text();
    console.log(`  标题: ${title.substring(0, 60)}...`);

    // 提取球队名
    const match = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/);
    if (!match) {
      console.log(`  ❌ 无法提取球队信息`);
      return null;
    }

    const homeTeam = match[1].trim();
    const awayTeam = match[2].trim().split(' – ')[0].trim();

    console.log(`  主队: ${homeTeam}`);
    console.log(`  客队: ${awayTeam}`);

    // 提取比分
    const scores = [];
    $('div.score').each((i, elem) => {
      const score = $(elem).text().trim();
      if (score.match(/^\d+$/)) {
        scores.push(parseInt(score));
      }
    });

    const homeScore = scores[0] || 0;
    const awayScore = scores[1] || 0;
    console.log(`  比分: ${homeScore} - ${awayScore}`);

    // 提取日期
    const dateMatch = title.match(/–\s+(.+?)\s+\|/);
    const dateStr = dateMatch ? dateMatch[1].trim() : '2024-03-01';

    // 转换日期格式
    let formattedDate = '2024-03-01';
    const dateParts = dateStr.match(/(\w+)\s+(\d+),?\s+(\d{4})/);
    if (dateParts) {
      const months = {
        'January': '01', 'February': '02', 'March': '03',
        'April': '04', 'May': '05', 'June': '06',
        'July': '07', 'August': '08', 'September': '09',
        'October': '10', 'November': '11', 'December': '12'
      };
      const month = months[dateParts[1]] || '01';
      const day = dateParts[2].padStart(2, '0');
      const year = dateParts[3];
      formattedDate = `${year}-${month}-${day}`;
    }

    console.log(`  日期: ${formattedDate}`);

    // 提取球员数据（简化版）
    const homePlayers = [];
    const awayPlayers = [];
    let tableIndex = 0;

    $('table.stats_table').each((i, table) => {
      const $table = $(table);
      const tableId = $table.attr('id') || '';
      
      if (tableId.includes('keeper')) return;

      const team = tableIndex < 1 ? 'home' : 'away';
      tableIndex++;

      const players = team === 'home' ? homePlayers : awayPlayers;

      $table.find('tr').each((rowIndex, row) => {
        const $row = $(row);
        const name = $row.find('th').text().trim();

        if (!name || name.includes('Player')) return;

        const cells = [];
        $row.find('td').each((j, cell) => {
          cells.push($(cell).text().trim());
        });

        if (cells.length >= 13) {
          players.push({
            name: name,
            number: parseInt(cells[0]) || 0,
            position: cells[3] || '中场',
            minutes: parseInt(cells[5]) || 0,
            goals: parseInt(cells[6]) || 0,
            assists: parseInt(cells[7]) || 0
          });
        }
      });
    });

    console.log(`  主队球员: ${homePlayers.length}人`);
    console.log(`  客队球员: ${awayPlayers.length}人`);

    // 生成JSON
    const matchData = JSON.parse(JSON.stringify(template));

    matchData.match = {
      id: roundNum,
      round: `第${roundNum}轮`,
      date: formattedDate,
      time: '19:35',
      homeTeam: teamNameMap[homeTeam] || homeTeam,
      awayTeam: teamNameMap[awayTeam] || awayTeam,
      result: `${homeScore}-${awayScore}`,
      status: '已结束',
      competition: '中国足球协会超级联赛',
      matchweek: roundNum,
      season: '2024'
    };

    matchData.lineups.home = {
      name: teamNameMap[homeTeam] || homeTeam,
      formation: '4-2-3-1',
      players: homePlayers.slice(0, 11),
      substitutes: homePlayers.slice(11)
    };

    matchData.lineups.away = {
      name: teamNameMap[awayTeam] || awayTeam,
      formation: '4-2-3-1',
      players: awayPlayers.slice(0, 11),
      substitutes: awayPlayers.slice(11)
    };

    return {
      success: true,
      data: matchData,
      fileName: `${formattedDate}-中超-第${roundNum}轮.json`,
      stats: {
        homePlayers: homePlayers.length,
        awayPlayers: awayPlayers.length
      }
    };

  } catch (error) {
    console.log(`  ❌ 错误: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// 主函数
function main() {
  const htmlDir = './data/scraped_html_live';
  const outputDir = './data/match_reports_final_v2';

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const files = fs.readdirSync(htmlDir)
    .filter(f => f.endsWith('.html'))
    .sort((a, b) => {
      const numA = parseInt(a.match(/match_(\d+)/)?.[1] || 0);
      const numB = parseInt(b.match(/match_(\d+)/)?.[1] || 0);
      return numA - numB;
    });

  console.log(`找到 ${files.length} 个HTML文件\n`);

  const results = { success: [], failed: [] };

  files.forEach((file, index) => {
    const roundNum = parseInt(file.match(/match_(\d+)/)?.[1] || 0);
    const htmlPath = path.join(htmlDir, file);

    const result = processMatchSimple(htmlPath, roundNum);

    if (result && result.success) {
      const outputPath = path.join(outputDir, result.fileName);
      fs.writeFileSync(outputPath, JSON.stringify(result.data, null, 2), 'utf8');
      console.log(`  ✅ 已保存: ${result.fileName}`);
      results.success.push({ round: roundNum, file: result.fileName });
    } else {
      results.failed.push({ round: roundNum, file: file });
    }

    // 每10场汇报
    if ((index + 1) % 10 === 0) {
      console.log(`\n📊 进度: ${index + 1}/${files.length} (成功: ${results.success.length})\n`);
    }
  });

  // 最终汇总
  console.log('\n========================================');
  console.log('处理完成！');
  console.log('========================================');
  console.log(`总计: ${files.length}场`);
  console.log(`  ✅ 成功: ${results.success.length}场`);
  console.log(`  ❌ 失败: ${results.failed.length}场`);

  if (results.success.length > 0) {
    console.log(`\n✓ 文件位置: ${outputDir}`);
    console.log(`✓ 成功率: ${((results.success.length / files.length) * 100).toFixed(1)}%`);
  }
}

main();

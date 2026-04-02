#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

console.log('========================================');
console.log('批量处理 - 最终完成版');
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
  'Chengdu Better City': '成都蓉城',
  'Changchun Yatai': '长春亚泰',
  'Qingdao Hainiu': '青岛海牛',
  'Shanghai Shenhua': '上海申花',
  'Beijing Guoan': '北京国安'
};

const positionMap = {
  'GK': '门将', 'FW': '前锋', 'MF': '中场', 'DF': '后卫',
  'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫',
  'DM': '后腰', 'CM': '中场', 'AM': '攻击型中场',
  'RW': '右边锋', 'LW': '左边锋'
};

function processMatch(htmlFile, roundNum) {
  try {
    const html = fs.readFileSync(htmlFile, 'utf8');
    const $ = cheerio.load(html);

    // 1. 提取比赛基本信息
    const title = $('title').text();
    let homeTeam = '', awayTeam = '', dateStr = '';

    // 尝试多种方式提取
    const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)\s*\|/);
    if (titleMatch) {
      homeTeam = titleMatch[1].trim();
      awayTeam = titleMatch[2].trim();
      dateStr = titleMatch[3].trim();
    } else {
      // 从URL提取
      const urlMatch = html.match(/matches\/[^/]+\/(.+?)-(.+?)-\w+-\d+-\d+/);
      if (urlMatch) {
        homeTeam = urlMatch[1].replace(/-/g, ' ');
        awayTeam = urlMatch[2].replace(/-/g, ' ');
      }
    }

    if (!homeTeam || !awayTeam) {
      return { success: false, error: '无法提取球队信息' };
    }

    console.log(`\n【第${roundNum}轮】${homeTeam} vs ${awayTeam}`);

    // 2. 提取比分
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

    // 3. 提取球员数据
    const allPlayers = { home: [], away: [] };
    let tableIndex = 0;

    $('table.stats_table').each((i, table) => {
      const $table = $(table);
      const tableId = $table.attr('id') || '';
      
      if (tableId.includes('keeper')) return;

      const team = tableIndex < 1 ? 'home' : 'away';
      tableIndex++;

      let playerCount = 0;
      $table.find('tr').each((rowIndex, row) => {
        const $row = $(row);
        const name = $row.find('th').text().trim();

        if (!name || name.includes('Player') || name.includes('#')) return;

        const cells = [];
        $row.find('td').each((j, cell) => {
          cells.push($(cell).text().trim());
        });

        if (cells.length >= 13) {
          const player = {
            name: name,
            number: parseInt(cells[0]) || 0,
            nationality: cells[1] || '',
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

          allPlayers[team].push(player);
          playerCount++;
        }
      });

      console.log(`  ${team === 'home' ? '主队' : '客队'}: ${playerCount}人`);
    });

    // 4. 提取进球事件
    const goals = [];
    const bodyText = $('body').text();
    
    // 查找进球模式
    const goalPattern = /(\d+(?:\+\d+)?')\s+([A-Z][a-z]+ [A-Z][a-z'·]+)[^\n]{0,100}Goal/g;
    let match;
    while ((match = goalPattern.exec(bodyText)) !== null) {
      const playerName = match[2].split('·')[0].trim();
      const isHome = bodyText.substring(match.index - 200, match.index).includes('Shanghai Port') ||
                     playerName === 'Wu Lei' || 
                     playerName === 'Wang Shenchao' ||
                     playerName === 'Lü Wenjun';
      
      goals.push({
        minute: match[1].replace("'", ''),
        player: playerName,
        team: isHome ? '主队' : '客队'
      });
    }

    console.log(`  进球: ${goals.length}个`);

    // 5. 转换日期格式
    let formattedDate = '2024-03-01';
    const dateMatch = dateStr.match(/(\w+)\s+(\d+),?\s+(\d{4})/);
    if (dateMatch) {
      const months = {
        'January': '01', 'February': '02', 'March': '03',
        'April': '04', 'May': '05', 'June': '06',
        'July': '07', 'August': '08', 'September': '09',
        'October': '10', 'November': '11', 'December': '12'
      };
      const month = months[dateMatch[1]] || '01';
      const day = dateMatch[2].padStart(2, '0');
      const year = dateMatch[3];
      formattedDate = `${year}-${month}-${day}`;
    }

    // 6. 生成JSON
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
      players: allPlayers.home.slice(0, 11),
      substitutes: allPlayers.home.slice(11)
    };

    matchData.lineups.away = {
      name: teamNameMap[awayTeam] || awayTeam,
      formation: '4-2-3-1',
      players: allPlayers.away.slice(0, 11),
      substitutes: allPlayers.away.slice(11)
    };

    matchData.matchTimeline = goals.map(g => ({
      minute: parseInt(g.minute.replace('+', '')),
      type: '进球',
      player: g.player,
      team: g.team
    }));

    return {
      success: true,
      data: matchData,
      fileName: `${formattedDate}-中超-第${roundNum}轮.json`,
      stats: {
        homePlayers: allPlayers.home.length,
        awayPlayers: allPlayers.away.length,
        goals: goals.length
      }
    };

  } catch (error) {
    return { success: false, error: error.message };
  }
}

function main() {
  const htmlDir = './data/scraped_html_live';
  const outputDir = './data/match_reports_complete';

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

    const result = processMatch(htmlPath, roundNum);

    if (result && result.success) {
      const outputPath = path.join(outputDir, result.fileName);
      fs.writeFileSync(outputPath, JSON.stringify(result.data, null, 2), 'utf8');
      console.log(`  ✅ 已保存: ${result.fileName}`);
      results.success.push({ round: roundNum, file: result.fileName });
    } else {
      console.log(`  ❌ 失败: ${result?.error || '未知错误'}`);
      results.failed.push({ round: roundNum, file: file, error: result?.error });
    }

    // 每10场汇报
    if ((index + 1) % 10 === 0) {
      console.log(`\n📊 进度: ${index + 1}/${files.length} (成功: ${results.success.length})\n`);
    }
  });

  // 最终汇总
  console.log('\n' + '='.repeat(80));
  console.log('处理完成！');
  console.log('='.repeat(80));
  console.log(`总计: ${files.length}场`);
  console.log(`  ✅ 成功: ${results.success.length}场`);
  console.log(`  ❌ 失败: ${results.failed.length}场`);

  if (results.failed.length > 0) {
    console.log('\n失败的场次:');
    results.failed.forEach(f => {
      console.log(`  第${f.round}轮: ${f.error}`);
    });
  }

  console.log(`\n✓ 文件位置: ${outputDir}`);
  console.log(`✓ 成功率: ${((results.success.length / files.length) * 100).toFixed(1)}%`);
}

main();

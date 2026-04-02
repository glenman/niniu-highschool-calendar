#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
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
  'Chengdu Better City': '成都蓉城',
  'Changchun Yatai': '长春亚泰',
  'Qingdao Hainiu': '青岛海牛',
  'Shanghai Shenhua': '上海申花',
  'Beijing Guoan': '北京国安'
};

// 位置映射
const positionMap = {
  'GK': '门将', 'FW': '前锋', 'MF': '中场', 'DF': '后卫',
  'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫',
  'DM': '后腰', 'CM': '中场', 'AM': '攻击型中场',
  'RW': '右边锋', 'LW': '左边锋'
};

// 读取模板
const template = JSON.parse(fs.readFileSync('./templates/full_match_report.json', 'utf8'));

function processMatch(htmlFile, roundNum) {
  try {
    const html = fs.readFileSync(htmlFile, 'utf8');
    const $ = cheerio.load(html);

    console.log(`\n${'='.repeat(60)}`);
    console.log(`处理第${roundNum}轮: ${path.basename(htmlFile)}`);
    console.log('='.repeat(60));

    // 1. 提取比赛基本信息
    const title = $('title').text();
    const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)\s*\|/);

    if (!titleMatch) {
      console.log(`  ⚠️  无法提取比赛信息`);
      return null;
    }

    const homeTeam = titleMatch[1].trim();
    const awayTeam = titleMatch[2].trim();
    const dateStr = titleMatch[3].trim();

    console.log(`  主队: ${homeTeam} -> ${teamNameMap[homeTeam] || homeTeam}`);
    console.log(`  客队: ${awayTeam} -> ${teamNameMap[awayTeam] || awayTeam}`);
    console.log(`  日期: ${dateStr}`);

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
    let currentTeam = 'home';

    $('table.stats_table').each((tableIndex, table) => {
      const $table = $(table);
      const tableId = $table.attr('id') || '';

      if (tableId.includes('keeper')) return;

      if (tableIndex > 0 && currentTeam === 'home') {
        currentTeam = 'away';
      }

      let playerCount = 0;
      $table.find('tr').each((rowIndex, row) => {
        const $row = $(row);
        const name = $row.find('th').text().trim();

        if (name.includes('Player') || name.includes('#')) return;

        const cells = [];
        $row.find('td').each((j, cell) => {
          cells.push($(cell).text().trim());
        });

        if (name && cells.length >= 13) {
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

          allPlayers[currentTeam].push(player);
          playerCount++;
        }
      });

      console.log(`  ${currentTeam === 'home' ? '主队' : '客队'}: ${playerCount}人`);
    });

    // 4. 提取进球事件
    const goals = [];
    const bodyText = $('body').text();

    // 查找进球模式
    const goalPatterns = [
      /(\d+(?:\+\d+)?')\s+([^\n]*?Goal[^\n]*?)/g
    ];

    goalPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(bodyText)) !== null) {
        const time = match[1];
        const detail = match[2].trim();
        
        const playerMatch = detail.match(/([A-Z][a-z]+ [A-Z][a-z'·]+)/);
        const player = playerMatch ? playerMatch[1] : '';

        if (player) {
          goals.push({
            time,
            player,
            team: detail.includes('Shanghai Port') ? '主队' : '客队'
          });
        }
      }
    });

    console.log(`  进球: ${goals.length}个`);

    // 5. 生成JSON
    const matchData = JSON.parse(JSON.stringify(template));

    // 转换日期格式
    const dateMatch = dateStr.match(/(\w+)\s+(\d+),?\s+(\d{4})/);
    let formattedDate = '2024-03-01';
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
      minute: parseInt(g.time.replace("'", '')),
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
    console.log(`  ❌ 错误: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// 主函数
function main() {
  const htmlDir = './data/scraped_html_live';
  const outputDir = './data/match_reports_final';

  // 创建输出目录
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 获取所有HTML文件
  const files = fs.readdirSync(htmlDir)
    .filter(f => f.endsWith('.html'))
    .sort((a, b) => {
      const numA = parseInt(a.match(/match_(\d+)/)?.[1] || 0);
      const numB = parseInt(b.match(/match_(\d+)/)?.[1] || 0);
      return numA - numB;
    });

  console.log('\n' + '='.repeat(80));
  console.log('开始批量处理比赛报告');
  console.log('='.repeat(80));
  console.log(`共找到 ${files.length} 个HTML文件\n`);

  const results = {
    success: [],
    failed: []
  };

  files.forEach((file, index) => {
    const roundNum = parseInt(file.match(/match_(\d+)/)?.[1] || 0);
    const htmlPath = path.join(htmlDir, file);

    const result = processMatch(htmlPath, roundNum);

    if (result && result.success) {
      // 保存JSON
      const outputPath = path.join(outputDir, result.fileName);
      fs.writeFileSync(outputPath, JSON.stringify(result.data, null, 2), 'utf8');
      
      console.log(`  ✅ 成功: ${result.fileName}`);
      console.log(`     主队${result.stats.homePlayers}人, 客队${result.stats.awayPlayers}人, 进球${result.stats.goals}个`);
      
      results.success.push({
        round: roundNum,
        file: result.fileName
      });
    } else {
      results.failed.push({
        round: roundNum,
        file: file,
        error: result?.error || '未知错误'
      });
    }

    // 每10场汇报一次
    if ((index + 1) % 10 === 0) {
      console.log(`\n📊 进度汇报: 已处理 ${index + 1}/${files.length} 场`);
      console.log(`   成功: ${results.success.length}场`);
      console.log(`   失败: ${results.failed.length}场\n`);
    }
  });

  // 最终汇总
  console.log('\n' + '='.repeat(80));
  console.log('批量处理完成！');
  console.log('='.repeat(80));
  console.log(`\n总计: ${files.length}场比赛`);
  console.log(`  ✅ 成功: ${results.success.length}场`);
  console.log(`  ❌ 失败: ${results.failed.length}场`);

  if (results.failed.length > 0) {
    console.log('\n失败的场次:');
    results.failed.forEach(f => {
      console.log(`  第${f.round}轮: ${f.file}`);
      console.log(`    原因: ${f.error}`);
    });
  }

  console.log(`\n✓ 所有文件已保存到: ${outputDir}`);
}

main();

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
  'Chengdu Better City': '成都蓉城',
  'Changchun Yatai': '长春亚泰',
  'Qingdao Hainiu': '青岛海牛',
  'Shanghai Shenhua': '上海申花',
  'Beijing Guoan': '北京国安',
  'Chengdu Rongcheng': '成都蓉城',
  'Dalian Pro': '大连人'
};

const positionMap = {
  'GK': '门将', 'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫',
  'DM': '后腰', 'CM': '中场', 'AM': '攻击型中场',
  'RM': '右中场', 'LM': '左中场', 'RW': '右边锋', 'LW': '左边锋',
  'FW': '前锋', 'MF': '中场', 'DF': '后卫'
};

// 从snapshot中提取比分
function extractScore(snapshot, homeTeam, awayTeam) {
  const lines = snapshot.split('\n');

  // 方法1: 查找比分模式
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const nextLine = lines[i + 1]?.trim() || '';

    // 查找数字：数字的模式
    if (line.includes('StaticText') && nextLine.includes('StaticText')) {
      const scoreMatch = line.match(/(\d+)\s*:\s*(\d+)/);
      if (scoreMatch) {
        return { home: scoreMatch[1], away: scoreMatch[2] };
      }
    }

    // 查找相邻的数字
    if (line.match(/^-\s+generic\s*$/)) {
      const num1 = lines[i + 1]?.match(/StaticText "(\d+)"/);
      const colon = lines[i + 2]?.match(/StaticText ":"/);
      const num2 = lines[i + 3]?.match(/StaticText "(\d+)"/);

      if (num1 && colon && num2) {
        return { home: num1[1], away: num2[1] };
      }
    }
  }

  return { home: '0', away: '0' };
}

// 改进的球员数据提取
function extractPlayersImproved(snapshot, teamName) {
  const lines = snapshot.split('\n');
  const players = [];
  let currentPlayer = null;
  let cells = [];
  let inTeamSection = false;
  let teamFound = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // 检测球队统计部分
    if (line.includes('Player Stats') && !line.includes('Goalkeeper')) {
      if (line.includes(teamName) || line.includes(teamNameMap[teamName])) {
        inTeamSection = true;
        teamFound = true;
      } else if (teamFound) {
        // 已经处理完该球队，退出
        break;
      }
    }

    // 提取球员
    if (inTeamSection && line.includes('rowheader "')) {
      // 保存上一个球员
      if (currentPlayer && cells.length >= 13) {
        players.push({
          name: currentPlayer.replace(/^\s+/, ''),
          number: parseInt(cells[0]) || 0,
          position: positionMap[cells[2]] || cells[2],
          nationality: cells[1]?.split(' ')[1] || cells[1],
          age: cells[3],
          minutes: parseInt(cells[4]) || 0,
          goals: parseInt(cells[5]) || 0,
          assists: parseInt(cells[6]) || 0,
          shots: parseInt(cells[9]) || 0,
          shotsOnTarget: parseInt(cells[10]) || 0,
          yellowCards: parseInt(cells[11]) || 0,
          redCards: parseInt(cells[12]) || 0
        });
      }

      currentPlayer = line.match(/rowheader "([^"]+)"/)?.[1];
      cells = [];
    }

    if (inTeamSection && currentPlayer && line.includes('cell "')) {
      const cellMatch = line.match(/cell "([^"]*)"/);
      if (cellMatch) cells.push(cellMatch[1]);
    }

    // 检测结束
    if (inTeamSection && (line.includes('Goalkeeper Stats') || line.includes('Team Stats'))) {
      // 保存最后一个球员
      if (currentPlayer && cells.length >= 13) {
        players.push({
          name: currentPlayer.replace(/^\s+/, ''),
          number: parseInt(cells[0]) || 0,
          position: positionMap[cells[2]] || cells[2],
          nationality: cells[1]?.split(' ')[1] || cells[1],
          age: cells[3],
          minutes: parseInt(cells[4]) || 0,
          goals: parseInt(cells[5]) || 0,
          assists: parseInt(cells[6]) || 0,
          shots: parseInt(cells[9]) || 0,
          shotsOnTarget: parseInt(cells[10]) || 0,
          yellowCards: parseInt(cells[11]) || 0,
          redCards: parseInt(cells[12]) || 0
        });
      }
      inTeamSection = false;
      currentPlayer = null;
      cells = [];
    }
  }

  return players;
}

// 处理单场比赛
function fixMatch(originalFile, outputDir) {
  const data = JSON.parse(fs.readFileSync(originalFile, 'utf8'));
  const snapshot = data.snapshot;
  const matchInfo = data.match;

  console.log(`\n处理: ${matchInfo.date} - 第${matchInfo.id}轮`);

  // 提取比分
  const score = extractScore(snapshot, matchInfo.homeTeam, matchInfo.awayTeam);
  console.log(`  比分: ${score.home}-${score.away}`);

  // 提取主队球员
  const homePlayers = extractPlayersImproved(snapshot, matchInfo.homeTeam);
  console.log(`  主队球员: ${homePlayers.length}人`);

  // 提取客队球员
  const awayPlayers = extractPlayersImproved(snapshot, matchInfo.awayTeam);
  console.log(`  客队球员: ${awayPlayers.length}人`);

  return {
    score,
    homePlayers,
    awayPlayers
  };
}

// 主函数
function main() {
  const originalDir = './data/match_reports_original';
  const outputDir = './data/match_reports_final';

  // 确保输出目录存在
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 需要重新处理的所有比赛（17场）
  const allMatches = [];
  const files = fs.readdirSync(originalDir).filter(f => f.endsWith('.json'));

  console.log('='.repeat(80));
  console.log('重新处理所有比赛数据');
  console.log('='.repeat(80));

  files.forEach(file => {
    const filePath = path.join(originalDir, file);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

    const fixed = fixMatch(filePath, outputDir);

    // 更新现有的JSON文件
    const matchId = data.match.id;
    const outputFiles = fs.readdirSync(outputDir).filter(f => f.includes(`第${matchId}轮`));

    if (outputFiles.length > 0) {
      const outputFile = path.join(outputDir, outputFiles[0]);
      const existing = JSON.parse(fs.readFileSync(outputFile, 'utf8'));

      // 更新比分
      if (fixed.score.home !== '0' || fixed.score.away !== '0') {
        existing.match.result = `${fixed.score.home}-${fixed.score.away}`;
        existing.matchDetails.fulltimeScore = `${fixed.score.home}-${fixed.score.away}`;
        console.log(`    ✓ 更新比分: ${fixed.score.home}-${fixed.score.away}`);
      }

      // 更新球员数据（如果有数据）
      if (fixed.homePlayers.length > 0 && existing.lineups.home.players.length === 0) {
        existing.lineups.home.players = fixed.homePlayers.slice(0, 11);
        existing.lineups.home.substitutes = fixed.homePlayers.slice(11);
        existing.detailedPlayerStats.home = fixed.homePlayers.slice(0, 5).map(p => ({
          player: p.name,
          number: p.number,
          position: p.position,
          age: p.age,
          minutes: p.minutes,
          shots: p.shots,
          shotsOnTarget: p.shotsOnTarget,
          goals: p.goals,
          assists: p.assists,
          keyPasses: 0,
          crosses: 0,
          tacklesWon: 0,
          interceptions: 0,
          foulsCommitted: 0,
          foulsWon: 0,
          offsides: 0,
          yellowCards: p.yellowCards,
          redCards: p.redCards
        }));
        console.log(`    ✓ 更新主队球员: ${fixed.homePlayers.length}人`);
      }

      if (fixed.awayPlayers.length > 0 && existing.lineups.away.players.length === 0) {
        existing.lineups.away.players = fixed.awayPlayers.slice(0, 11);
        existing.lineups.away.substitutes = fixed.awayPlayers.slice(11);
        existing.detailedPlayerStats.away = fixed.awayPlayers.slice(0, 5).map(p => ({
          player: p.name,
          number: p.number,
          position: p.position,
          age: p.age,
          minutes: p.minutes,
          shots: p.shots,
          shotsOnTarget: p.shotsOnTarget,
          goals: p.goals,
          assists: p.assists,
          keyPasses: 0,
          crosses: 0,
          tacklesWon: 0,
          interceptions: 0,
          foulsCommitted: 0,
          foulsWon: 0,
          offsides: 0,
          yellowCards: p.yellowCards,
          redCards: p.redCards
        }));
        console.log(`    ✓ 更新客队球员: ${fixed.awayPlayers.length}人`);
      }

      // 保存更新后的文件
      fs.writeFileSync(outputFile, JSON.stringify(existing, null, 2), 'utf8');
      console.log(`    ✓ 已保存: ${outputFiles[0]}`);
    }
  });

  console.log('\n' + '='.repeat(80));
  console.log('重新处理完成！');
  console.log('='.repeat(80));
}

main();

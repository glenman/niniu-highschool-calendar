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
  'Dalian Pro': '大连人'
};

const positionMap = {
  'GK': '门将', 'CB': '中后卫', 'RB': '右后卫', 'LB': '左后卫',
  'DM': '后腰', 'CM': '中场', 'AM': '攻击型中场',
  'RM': '右中场', 'LM': '左中场', 'RW': '右边锋', 'LW': '左边锋',
  'FW': '前锋', 'MF': '中场', 'DF': '后卫'
};

// 完整解析accessibility tree
function parseFullData(snapshot, originalData) {
  const lines = snapshot.split('\n');
  const data = {
    basic: {
      id: originalData.match.id,
      date: originalData.match.date // 使用原始JSON中的日期
    },
    homePlayers: [],
    awayPlayers: [],
    timeline: [],
    stats: {}
  };

  let currentTeam = null;
  let currentPlayer = null;
  let cells = [];
  let section = '';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // 比赛标题
    if (line.includes('heading') && line.includes('Match Report')) {
      const match = line.match(/heading "([^"]+) vs\.\s*([^"]+) Match Report/);
      if (match) {
        data.basic.homeTeam = match[1].trim();
        data.basic.awayTeam = match[2].trim();
      }
    }

    // 场馆
    if (line.includes('StaticText "Venue')) {
      for (let j = i + 1; j < i + 10; j++) {
        const v = lines[j]?.trim();
        if (v?.includes('StaticText') && v.includes(',') && !v.includes('Venue')) {
          data.basic.venue = v.match(/StaticText "([^"]+)"/)?.[1];
          break;
        }
      }
    }

    // 观众
    if (line.includes('StaticText "Attendance')) {
      for (let j = i + 1; j < i + 5; j++) {
        const a = lines[j]?.trim();
        if (a?.includes('StaticText') && /\d/.test(a)) {
          data.basic.attendance = a.match(/StaticText "([^"]+)"/)?.[1];
          break;
        }
      }
    }

    // 裁判
    if (line.includes('Referee')) {
      const refMatch = line.match(/Referee\)\s*([^\[]+)/);
      if (refMatch) data.basic.referee = refMatch[1].trim();
    }

    // 比分 - 从标题中提取
    if (line.includes('generic') && line.match(/\d+/)) {
      const scoreMatch = lines.slice(i, i + 10).join(' ').match(/(\d+)\s*:\s*(\d+)/);
      if (scoreMatch && !data.basic.homeScore) {
        data.basic.homeScore = scoreMatch[1];
        data.basic.awayScore = scoreMatch[2];
      }
    }

    // 球员数据
    if (line.includes('Player Stats') && !line.includes('Goalkeeper')) {
      section = 'players';
      currentTeam = line.includes(data.basic.homeTeam) ? 'home' : 'away';
    }

    if (section === 'players' && line.includes('rowheader "')) {
      // 保存上一个球员
      if (currentPlayer && cells.length >= 13) {
        const player = {
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
        };
        
        if (currentTeam === 'home') {
          data.homePlayers.push(player);
        } else {
          data.awayPlayers.push(player);
        }
      }

      currentPlayer = line.match(/rowheader "([^"]+)"/)?.[1];
      cells = [];
    }

    if (section === 'players' && currentPlayer && line.includes('cell "')) {
      const cellMatch = line.match(/cell "([^"]*)"/);
      if (cellMatch) cells.push(cellMatch[1]);
    }

    if (section === 'players' && (line.includes('Goalkeeper') || line.includes('Team Stats'))) {
      section = '';
      currentTeam = null;
      currentPlayer = null;
      cells = [];
    }

    // 时间线事件
    if (line.includes('·') && line.includes("'")) {
      const minuteMatch = line.match(/(\d+)'/);
      if (minuteMatch) {
        data.timeline.push({
          minute: parseInt(minuteMatch[1]),
          event: line.replace(/"/g, '').trim()
        });
      }
    }

    // 统计数据
    if (line.includes('Possession')) {
      let percents = [];
      for (let j = i; j < i + 30; j++) {
        const p = lines[j]?.match(/(\d+)%/);
        if (p) percents.push(parseInt(p[1]));
        if (percents.length === 2) {
          data.stats.possession = { home: percents[0], away: percents[1] };
          break;
        }
      }
    }
  }

  return data;
}

// 生成CSV
function generateCSV(allMatches) {
  const rows = [];
  
  rows.push([
    '比赛ID', '轮次', '日期', '主队', '客队', '比分', '场馆', '观众', '裁判',
    '球员', '号码', '位置', '国籍', '年龄', '时间', '进球', '助攻', '射门', '射正', '黄牌', '红牌',
    '所属球队', '首发替补'
  ]);

  allMatches.forEach(m => {
    const base = [
      m.basic.id || 0,
      `第${m.basic.id || 0}轮`,
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
  const inputDir = './data/match_reports_original';
  const files = fs.readdirSync(inputDir).filter(f => f.endsWith('.json'));

  console.log(`正在处理 ${files.length} 个文件...\n`);

  const allMatches = [];

  files.forEach(file => {
    const filePath = path.join(inputDir, file);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    
    const parsed = parseFullData(data.snapshot, data);
    allMatches.push(parsed);

    console.log(`✓ ${file}: 主队${parsed.homePlayers.length}人, 客队${parsed.awayPlayers.length}人`);
  });

  // 保存CSV
  const csvPath = './data/matches_complete_data.csv';
  const csv = generateCSV(allMatches);
  fs.writeFileSync(csvPath, '\ufeff' + csv, 'utf8');

  console.log(`\n✓ 已保存到: ${csvPath}`);
  console.log(`  总计: ${allMatches.length} 场比赛`);
  console.log(`  球员数据: ${allMatches.reduce((sum, m) => sum + m.homePlayers.length + m.awayPlayers.length, 0)} 条`);
}

main();

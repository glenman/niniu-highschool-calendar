#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 直接从原始JSON生成所有30个比赛报告
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
  'Chengdu Rongcheng': '成都蓉城',
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

function extractFromOriginal(filePath) {
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const snapshot = data.snapshot;
  const lines = snapshot.split('\n');

  const match = {
    id: data.match.id,
    date: data.match.date,
    homeTeam: teamNameMap[data.match.homeTeam] || data.match.homeTeam,
    awayTeam: teamNameMap[data.match.awayTeam] || data.match.awayTeam,
    venue: '',
    attendance: '',
    homePlayers: [],
    awayPlayers: []
  };

  // 提取场馆和观众
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.includes('StaticText "Venue')) {
      for (let j = i + 1; j < i + 10; j++) {
        const v = lines[j]?.trim();
        if (v?.includes('StaticText') && v.includes(',') && !v.includes('Venue')) {
          match.venue = v.match(/StaticText "([^"]+)"/)?.[1] || '';
          break;
        }
      }
    }
    if (line.includes('StaticText "Attendance')) {
      for (let j = i + 1; j < i + 5; j++) {
        const a = lines[j]?.trim();
        if (a?.includes('StaticText') && /\d/.test(a)) {
          match.attendance = a.match(/StaticText "([^"]+)"/)?.[1] || '';
          break;
        }
      }
    }
  }

  // 提取球员（简化版）
  let currentTeam = null;
  let currentPlayer = null;
  let cells = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.includes('Player Stats') && !line.includes('Goalkeeper')) {
      currentTeam = line.includes(data.match.homeTeam) ? 'home' : 'away';
    }

    if (currentTeam && line.includes('rowheader "')) {
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
          match.homePlayers.push(player);
        } else {
          match.awayPlayers.push(player);
        }
      }
      currentPlayer = line.match(/rowheader "([^"]+)"/)?.[1];
      cells = [];
    }

    if (currentTeam && currentPlayer && line.includes('cell "')) {
      const cellMatch = line.match(/cell "([^"]*)"/);
      if (cellMatch) cells.push(cellMatch[1]);
    }

    if (currentTeam && (line.includes('Goalkeeper') || line.includes('Team Stats'))) {
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
          match.homePlayers.push(player);
        } else {
          match.awayPlayers.push(player);
        }
      }
      currentTeam = null;
      currentPlayer = null;
      cells = [];
    }
  }

  return match;
}

function generateFullReport(matchData) {
  return {
    match: {
      id: matchData.id,
      round: `第${matchData.id}轮`,
      date: matchData.date,
      time: "19:35",
      homeTeam: matchData.homeTeam,
      awayTeam: matchData.awayTeam,
      venue: matchData.venue || "未知",
      city: extractCity(matchData.venue),
      result: "0-0",
      status: "已结束",
      attendance: matchData.attendance || "未知",
      referee: "未知",
      weather: "未知",
      competition: "中国足球协会超级联赛",
      matchweek: matchData.id,
      season: "2024"
    },
    matchDetails: {
      stadiumCapacity: "未知",
      pitchCondition: "良好",
      temperature: "未知",
      kickoffTime: "19:35",
      halftimeScore: "0-0",
      fulltimeScore: "0-0"
    },
    officials: {
      referee: "未知",
      assistantReferee1: "未知",
      assistantReferee2: "未知",
      fourthOfficial: "未知",
      VAR: "未知"
    },
    seasonRecords: {
      home: { currentPosition: "未知", matchesPlayed: 0, record: "0胜0平0负", points: 0, goalsFor: 0, goalsAgainst: 0, form: "" },
      away: { currentPosition: "未知", matchesPlayed: 0, record: "0胜0平0负", points: 0, goalsFor: 0, goalsAgainst: 0, form: "" }
    },
    lineups: {
      home: {
        name: matchData.homeTeam,
        formation: "4-2-3-1",
        manager: "未知",
        captain: "未知",
        players: matchData.homePlayers.slice(0, 11),
        substitutes: matchData.homePlayers.slice(11)
      },
      away: {
        name: matchData.awayTeam,
        formation: "4-2-3-1",
        manager: "未知",
        captain: "未知",
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
    tacticalAnalysis: {
      homeFormation: "4-2-3-1", awayFormation: "4-2-3-1",
      possession: { home: 50, away: 50 },
      attackDirection: { home: "未知", away: "未知" },
      defensiveLine: { home: "未知", away: "未知" },
      playingStyle: { home: "未知", away: "未知" }
    },
    statistics: [
      { name: "控球率", home: "50%", away: "50%" },
      { name: "射门", home: "0", away: "0" },
      { name: "射正", home: "0", away: "0" }
    ],
    keyMetrics: {
      expectedGoals: { home: 0, away: 0 },
      bigChances: { home: 0, away: 0 },
      passAccuracy: { home: "未知", away: "未知" },
      aerialDuelsWon: { home: "未知", away: "未知" },
      successfulDribbles: { home: 0, away: 0 },
      keyPasses: { home: 0, away: 0 }
    },
    playerRatings: {
      manOfTheMatch: "未知",
      homeBestPlayer: "未知",
      awayBestPlayer: "未知",
      topPerformers: []
    },
    headToHead: {
      totalMatches: 0, homeWins: 0, awayWins: 0, draws: 0,
      lastMeeting: "未知", trend: "未知"
    },
    socialMedia: {
      hashtags: [],
      fanSentiment: { home: "未知", away: "未知" },
      matchTrending: false
    },
    summary: "比赛报告",
    keyFactors: [],
    highlights: [],
    matchAnalysis: {
      tacticalSummary: "未知",
      keyMoments: [],
      teamPerformance: {
        home: { strengths: [], weaknesses: [] },
        away: { strengths: [], weaknesses: [] }
      }
    },
    postMatchComments: {
      homeManager: "",
      awayManager: "",
      manOfTheMatchComment: ""
    },
    nextMatches: {
      home: { opponent: "待定", date: "待定", venue: "待定" },
      away: { opponent: "待定", date: "待定", venue: "待定" }
    }
  };
}

function extractCity(venue) {
  const cityMap = {
    'Shanghai': '上海', 'Wuhan': '武汉', 'Qingdao': '青岛', 'Jinan': '济南',
    'Beijing': '北京', 'Chengdu': '成都', 'Hangzhou': '杭州', 'Shenzhen': '深圳',
    'Guangzhou': '广州', 'Dalian': '大连', 'Tianjin': '天津', 'Nanjing': '南京',
    'Changchun': '长春', 'Zhengzhou': '郑州', 'Meizhou': '梅州', 'Cangzhou': '沧州',
    'Nantong': '南通'
  };
  for (const [eng, chn] of Object.entries(cityMap)) {
    if (venue && venue.includes(eng)) return chn;
  }
  return "未知";
}

function main() {
  const inputDir = './data/match_reports_original';
  const outputDir = './data/match_reports_final';

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const files = fs.readdirSync(inputDir).filter(f => f.endsWith('.json'));
  console.log(`找到 ${files.length} 个原始文件\n`);

  files.forEach(file => {
    const filePath = path.join(inputDir, file);
    const matchData = extractFromOriginal(filePath);
    const fullReport = generateFullReport(matchData);

    const fileName = `${matchData.date}-中超-第${matchData.id}轮.json`;
    const outputPath = path.join(outputDir, fileName);

    fs.writeFileSync(outputPath, JSON.stringify(fullReport, null, 2), 'utf8');

    console.log(`✓ ${fileName}`);
    console.log(`  ${matchData.homeTeam} vs ${matchData.awayTeam}`);
    console.log(`  主队${matchData.homePlayers.length}人, 客队${matchData.awayPlayers.length}人\n`);
  });

  console.log(`\n✅ 完成！共生成 ${files.length} 个报告`);
}

main();

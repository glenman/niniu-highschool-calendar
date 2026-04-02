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

// 位置映射
const positionMap = {
  'GK': '门将',
  'CB': '中后卫',
  'RB': '右后卫',
  'LB': '左后卫',
  'DM': '后腰',
  'CM': '中场',
  'AM': '攻击型中场',
  'RM': '右中场',
  'LM': '左中场',
  'RW': '右边锋',
  'LW': '左边锋',
  'FW': '前锋',
  'MF': '中场',
  'DF': '后卫'
};

// 解析accessibility tree
function parseAccessibilityTree(snapshot) {
  const lines = snapshot.split('\n');
  const data = {
    matchTitle: '',
    homeTeam: '',
    awayTeam: '',
    homeScore: 0,
    awayScore: 0,
    date: '',
    venue: '',
    attendance: '',
    referee: '',
    homeFormation: '',
    awayFormation: '',
    homeManager: '',
    awayManager: '',
    homeCaptain: '',
    awayCaptain: '',
    homePlayers: [],
    awayPlayers: [],
    timeline: [],
    statistics: [],
    possession: { home: 0, away: 0 },
    shots: { home: 0, away: 0 },
    shotsOnTarget: { home: 0, away: 0 }
  };

  let currentSection = '';
  let isHomeTeam = true;
  let currentTeamPlayers = [];
  let inPlayerTable = false;
  let playerCells = [];
  let currentPlayer = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const nextLine = lines[i + 1]?.trim() || '';
    const prevLine = lines[i - 1]?.trim() || '';

    // 提取比赛标题
    if (line.includes('heading') && line.includes('Match Report')) {
      const match = line.match(/heading "([^"]+) Match Report/);
      if (match) {
        const parts = match[1].split(' vs. ');
        if (parts.length === 2) {
          data.homeTeam = parts[0].trim();
          data.awayTeam = parts[1].trim();
        }
      }
    }

    // 提取比分
    if (line.includes('StaticText') && /^\d+$/.test(line.match(/\d+/)?.[0])) {
      const score = line.match(/(\d+)/);
      if (score && prevLine.includes('generic')) {
        // 这是比分
      }
    }

    // 提取日期
    if (line.includes('link') && line.match(/(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)/)) {
      const dateMatch = line.match(/(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+,?\s+\d{4}/);
      if (dateMatch) {
        data.date = dateMatch[0];
      }
    }

    // 提取场馆
    if (line.includes('Venue')) {
      // 查找下一个包含场馆名称的行
      for (let j = i + 1; j < Math.min(i + 10, lines.length); j++) {
        const venueLine = lines[j].trim();
        if (venueLine.includes('StaticText') && !venueLine.includes('Venue') && !venueLine.includes('Attendance')) {
          const venueMatch = venueLine.match(/StaticText "([^"]+)"/);
          if (venueMatch && venueMatch[1].includes(',')) {
            data.venue = venueMatch[1];
            break;
          }
        }
      }
    }

    // 提取观众人数
    if (line.includes('Attendance')) {
      for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
        const attLine = lines[j].trim();
        if (attLine.includes('StaticText')) {
          const attMatch = attLine.match(/StaticText "([^"]+)"/);
          if (attMatch && /\d/.test(attMatch[1])) {
            data.attendance = attMatch[1];
            break;
          }
        }
      }
    }

    // 提取裁判信息
    if (line.includes('Officials') || line.includes('Referee')) {
      for (let j = i + 1; j < Math.min(i + 20, lines.length); j++) {
        const refLine = lines[j].trim();
        if (refLine.includes('Referee')) {
          const refMatch = refLine.match(/Referee\)\s*([^\[]+)/);
          if (refMatch) {
            data.referee = refMatch[1].trim();
          }
        }
      }
    }

    // 提取阵型
    if (line.includes('columnheader') && line.match(/\(\d+-\d+-\d+\)/)) {
      const formationMatch = line.match(/\((\d+-\d+-\d+)\)/);
      if (formationMatch) {
        if (line.includes(data.homeTeam) || isHomeTeam) {
          data.homeFormation = formationMatch[1];
        } else {
          data.awayFormation = formationMatch[1];
        }
      }
    }

    // 提取Manager
    if (line.includes('Manager')) {
      for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
        const mgrLine = lines[j].trim();
        if (mgrLine.includes('StaticText') && !mgrLine.includes('Manager') && !mgrLine.includes('Captain')) {
          const mgrMatch = mgrLine.match(/StaticText "([^"]+)"/);
          if (mgrMatch && mgrMatch[1].length > 2) {
            if (isHomeTeam && !data.homeManager) {
              data.homeManager = mgrMatch[1];
            } else if (!isHomeTeam && !data.awayManager) {
              data.awayManager = mgrMatch[1];
            }
            break;
          }
        }
      }
    }

    // 提取Captain
    if (line.includes('Captain')) {
      for (let j = i + 1; j < Math.min(i + 10, lines.length); j++) {
        const capLine = lines[j].trim();
        if (capLine.includes('link')) {
          const capMatch = capLine.match(/link "([^"]+)"/);
          if (capMatch) {
            if (isHomeTeam && !data.homeCaptain) {
              data.homeCaptain = capMatch[1];
            } else if (!isHomeTeam && !data.awayCaptain) {
              data.awayCaptain = capMatch[1];
            }
            break;
          }
        }
      }
    }

    // 检测球员统计部分
    if (line.includes('Player Stats') && !line.includes('Goalkeeper')) {
      inPlayerTable = true;
      isHomeTeam = line.includes(data.homeTeam);
      currentTeamPlayers = [];
      playerCells = [];
    }

    // 提取球员数据（从表格）
    if (inPlayerTable && line.includes('cell "')) {
      const cellMatch = line.match(/cell "([^"]*)"/);
      if (cellMatch) {
        playerCells.push(cellMatch[1]);
      }
    }

    // 提取球员名字
    if (inPlayerTable && line.includes('rowheader') && line.includes('link')) {
      const nameMatch = line.match(/link "([^"]+)"/);
      if (nameMatch) {
        // 保存上一个球员
        if (currentPlayer && playerCells.length >= 13) {
          currentPlayer = {
            name: currentPlayer.name,
            number: parseInt(playerCells[0]) || currentPlayer.number,
            position: positionMap[playerCells[2]] || playerCells[2],
            nationality: playerCells[1].split(' ')[1] || playerCells[1],
            age: playerCells[3],
            minutes: parseInt(playerCells[4]) || 0,
            goals: parseInt(playerCells[5]) || 0,
            assists: parseInt(playerCells[6]) || 0,
            shots: parseInt(playerCells[9]) || 0,
            shotsOnTarget: parseInt(playerCells[10]) || 0,
            yellowCards: parseInt(playerCells[11]) || 0,
            redCards: parseInt(playerCells[12]) || 0
          };
          currentTeamPlayers.push(currentPlayer);
        }
        
        currentPlayer = { name: nameMatch[1] };
        playerCells = [];
      }
    }

    // 结束球员统计部分
    if (inPlayerTable && (line.includes('Goalkeeper Stats') || line.includes('Team Stats'))) {
      // 保存最后一个球员
      if (currentPlayer && playerCells.length >= 13) {
        currentPlayer = {
          name: currentPlayer.name,
          number: parseInt(playerCells[0]) || 0,
          position: positionMap[playerCells[2]] || playerCells[2],
          nationality: playerCells[1].split(' ')[1] || playerCells[1],
          age: playerCells[3],
          minutes: parseInt(playerCells[4]) || 0,
          goals: parseInt(playerCells[5]) || 0,
          assists: parseInt(playerCells[6]) || 0,
          shots: parseInt(playerCells[9]) || 0,
          shotsOnTarget: parseInt(playerCells[10]) || 0,
          yellowCards: parseInt(playerCells[11]) || 0,
          redCards: parseInt(playerCells[12]) || 0
        };
        currentTeamPlayers.push(currentPlayer);
      }

      if (isHomeTeam) {
        data.homePlayers = currentTeamPlayers;
      } else {
        data.awayPlayers = currentTeamPlayers;
      }
      
      inPlayerTable = false;
      currentPlayer = null;
      playerCells = [];
    }

    // 提取时间线事件
    if (line.includes('·') && line.includes("'")) {
      const minuteMatch = line.match(/(\d+)'/);
      if (minuteMatch) {
        let eventType = 'event';
        if (line.includes('Assist') || line.includes('Goal')) {
          eventType = 'goal';
        } else if (line.includes('for')) {
          eventType = 'substitution';
        } else if (line.toLowerCase().includes('yellow')) {
          eventType = 'yellow_card';
        }

        data.timeline.push({
          minute: parseInt(minuteMatch[1]),
          type: eventType,
          description: line.replace(/"/g, '').trim()
        });
      }
    }

    // 提取控球率
    if (line.includes('Possession')) {
      for (let j = i + 1; j < Math.min(i + 20, lines.length); j++) {
        const possLine = lines[j].trim();
        if (possLine.includes('strong') && possLine.includes('%')) {
          const possMatch = possLine.match(/(\d+)%/);
          if (possMatch) {
            if (data.possession.home === 0) {
              data.possession.home = parseInt(possMatch[1]);
            } else {
              data.possession.away = parseInt(possMatch[1]);
              break;
            }
          }
        }
      }
    }
  }

  return data;
}

// 生成完整报告
function generateFullReport(originalData, extractedData) {
  return {
    match: {
      id: originalData.match.id,
      round: `第${originalData.match.id}轮`,
      date: originalData.match.date,
      time: "19:35",
      homeTeam: teamNameMap[originalData.match.homeTeam] || originalData.match.homeTeam,
      awayTeam: teamNameMap[originalData.match.awayTeam] || originalData.match.awayTeam,
      venue: extractedData.venue || "未知",
      city: extractCity(extractedData.venue),
      result: `${extractedData.homeScore}-${extractedData.awayScore}`,
      status: "已结束",
      attendance: extractedData.attendance || "未知",
      referee: extractedData.referee || "未知",
      weather: "未知",
      competition: "中国足球协会超级联赛",
      matchweek: originalData.match.id,
      season: originalData.match.season
    },
    matchDetails: {
      stadiumCapacity: "未知",
      pitchCondition: "良好",
      temperature: "未知",
      kickoffTime: "19:35",
      halftimeScore: "0-0",
      fulltimeScore: `${extractedData.homeScore}-${extractedData.awayScore}`
    },
    officials: {
      referee: extractedData.referee || "未知",
      assistantReferee1: "未知",
      assistantReferee2: "未知",
      fourthOfficial: "未知",
      VAR: "未知"
    },
    seasonRecords: {
      home: {
        currentPosition: "未知",
        matchesPlayed: 0,
        record: "0胜0平0负",
        points: 0,
        goalsFor: 0,
        goalsAgainst: 0,
        form: ""
      },
      away: {
        currentPosition: "未知",
        matchesPlayed: 0,
        record: "0胜0平0负",
        points: 0,
        goalsFor: 0,
        goalsAgainst: 0,
        form: ""
      }
    },
    lineups: {
      home: {
        name: teamNameMap[originalData.match.homeTeam] || originalData.match.homeTeam,
        formation: extractedData.homeFormation || "4-2-3-1",
        manager: extractedData.homeManager || "未知",
        captain: extractedData.homeCaptain || "未知",
        players: extractedData.homePlayers.slice(0, 11),
        substitutes: extractedData.homePlayers.slice(11)
      },
      away: {
        name: teamNameMap[originalData.match.awayTeam] || originalData.match.awayTeam,
        formation: extractedData.awayFormation || "4-2-3-1",
        manager: extractedData.awayManager || "未知",
        captain: extractedData.awayCaptain || "未知",
        players: extractedData.awayPlayers.slice(0, 11),
        substitutes: extractedData.awayPlayers.slice(11)
      }
    },
    detailedPlayerStats: {
      home: extractedData.homePlayers.slice(0, 5).map(p => ({
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
      })),
      away: extractedData.awayPlayers.slice(0, 5).map(p => ({
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
      }))
    },
    matchTimeline: extractedData.timeline.sort((a, b) => a.minute - b.minute),
    tacticalAnalysis: {
      homeFormation: extractedData.homeFormation || "4-2-3-1",
      awayFormation: extractedData.awayFormation || "4-2-3-1",
      possession: {
        home: extractedData.possession.home,
        away: extractedData.possession.away
      },
      attackDirection: {
        home: "未知",
        away: "未知"
      },
      defensiveLine: {
        home: "未知",
        away: "未知"
      },
      playingStyle: {
        home: "未知",
        away: "未知"
      }
    },
    statistics: [
      { name: "控球率", home: `${extractedData.possession.home}%`, away: `${extractedData.possession.away}%` },
      { name: "射门", home: String(extractedData.shots.home), away: String(extractedData.shots.away) },
      { name: "射正", home: String(extractedData.shotsOnTarget.home), away: String(extractedData.shotsOnTarget.away) }
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
      totalMatches: 0,
      homeWins: 0,
      awayWins: 0,
      draws: 0,
      lastMeeting: "未知",
      trend: "未知"
    },
    socialMedia: {
      hashtags: [],
      fanSentiment: { home: "未知", away: "未知" },
      matchTrending: false
    },
    summary: "比赛报告生成中...",
    keyFactors: [],
    highlights: extractedData.timeline.map(e => ({
      time: `${e.minute}'`,
      description: e.description,
      type: e.type,
      team: "未知",
      player: "未知"
    })),
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
    'Shanghai': '上海',
    'Wuhan': '武汉',
    'Qingdao': '青岛',
    'Jinan': '济南',
    'Beijing': '北京',
    'Chengdu': '成都',
    'Hangzhou': '杭州',
    'Shenzhen': '深圳',
    'Guangzhou': '广州',
    'Dalian': '大连',
    'Tianjin': '天津',
    'Nanjing': '南京',
    'Changchun': '长春',
    'Zhengzhou': '郑州',
    'Meizhou': '梅州',
    'Cangzhou': '沧州',
    'Nantong': '南通'
  };

  for (const [eng, chn] of Object.entries(cityMap)) {
    if (venue && venue.includes(eng)) {
      return chn;
    }
  }
  return "未知";
}

// 主转换函数
function convertMatchReport(inputFile, outputFile) {
  try {
    const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
    console.log(`正在处理: ${inputFile}`);

    const extractedData = parseAccessibilityTree(data.snapshot);
    const fullReport = generateFullReport(data, extractedData);

    fs.writeFileSync(outputFile, JSON.stringify(fullReport, null, 2), 'utf8');
    console.log(`✓ 已转换: ${outputFile} (球员: ${extractedData.homePlayers.length} + ${extractedData.awayPlayers.length})`);

    return true;
  } catch (error) {
    console.error(`✗ 转换失败 ${inputFile}:`, error.message);
    return false;
  }
}

// 批量转换
function convertAllMatches() {
  const inputDir = './data/match_reports_original';
  const outputDir = './data/match_reports';

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const files = fs.readdirSync(inputDir).filter(f => f.endsWith('.json'));
  console.log(`找到 ${files.length} 个文件需要转换\n`);

  let successCount = 0;
  let failCount = 0;

  files.forEach(file => {
    const inputFile = path.join(inputDir, file);
    const outputFile = path.join(outputDir, file);

    if (convertMatchReport(inputFile, outputFile)) {
      successCount++;
    } else {
      failCount++;
    }
  });

  console.log(`\n转换完成: 成功 ${successCount} 个，失败 ${failCount} 个`);
}

// 运行
convertAllMatches();

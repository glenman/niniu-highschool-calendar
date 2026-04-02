#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 球队名称映射（英文 -> 中文）
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

// 从accessibility tree中提取信息
function extractMatchInfo(snapshot) {
  const lines = snapshot.split('\n');
  const info = {
    homeTeam: '',
    awayTeam: '',
    homeScore: 0,
    awayScore: 0,
    date: '',
    venue: '',
    city: '',
    attendance: '',
    referee: '',
    competition: '中国足球协会超级联赛',
    homeFormation: '',
    awayFormation: '',
    homeManager: '',
    awayManager: '',
    homeCaptain: '',
    awayCaptain: '',
    homePlayers: [],
    awayPlayers: [],
    homeSubstitutes: [],
    awaySubstitutes: [],
    timeline: [],
    statistics: {}
  };

  let currentSection = '';
  let currentPlayer = null;
  let players = [];
  let isHomeTeam = true;
  let inPlayerTable = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 提取比分信息
    if (line.includes('Matchday') || line.includes('Match Report')) {
      const match = line.match(/(.+?)\s+vs\.?\s+(.+?)\s+Match Report/);
      if (match) {
        info.homeTeam = match[1].trim();
        info.awayTeam = match[2].split('–')[0].trim();
      }
    }

    // 提取比分
    if (line.includes('StaticText') && /^\d+$/.test(line.match(/\d+/)?.[0])) {
      const scoreMatch = lines.slice(i-2, i+3).join(' ');
      // 比分提取逻辑
    }

    // 提取日期
    if (line.includes('Saturday') || line.includes('Sunday') || line.includes('Monday') || 
        line.includes('Tuesday') || line.includes('Wednesday') || line.includes('Thursday') || line.includes('Friday')) {
      const dateMatch = line.match(/(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)\s+(\w+\s+\d+,?\s+\d{4})/);
      if (dateMatch) {
        info.date = dateMatch[2];
      }
    }

    // 提取场馆和观众人数
    if (line.includes('Venue')) {
      const venueLine = lines[i+2] || '';
      info.venue = venueLine.replace(/"/g, '').trim();
    }
    if (line.includes('Attendance')) {
      const attLine = lines[i+2] || '';
      info.attendance = attLine.replace(/"/g, '').trim();
    }

    // 提取裁判
    if (line.includes('Referee')) {
      const refMatch = line.match(/Referee\)\s*([^(]+)/);
      if (refMatch) {
        info.referee = refMatch[1].trim();
      }
    }

    // 提取阵型
    if (line.includes('(4-') || line.includes('(3-') || line.includes('(5-')) {
      const formationMatch = line.match(/\((\d+-\d+-\d+)\)/);
      if (formationMatch) {
        if (isHomeTeam) {
          info.homeFormation = formationMatch[1];
        } else {
          info.awayFormation = formationMatch[1];
        }
      }
    }

    // 提取主教练
    if (line.includes('Manager')) {
      const managerLine = lines[i+2] || '';
      const manager = managerLine.replace(/"/g, '').trim();
      if (manager && !manager.includes('columnheader')) {
        if (isHomeTeam && !info.homeManager) {
          info.homeManager = manager;
        } else if (!isHomeTeam && !info.awayManager) {
          info.awayManager = manager;
        }
      }
    }

    // 提取队长
    if (line.includes('Captain')) {
      const captainLine = lines[i+2] || lines[i+5] || '';
      const captain = captainLine.replace(/"/g, '').trim();
      if (captain && !captain.includes('columnheader')) {
        if (isHomeTeam && !info.homeCaptain) {
          info.homeCaptain = captain;
        } else if (!isHomeTeam && !info.awayCaptain) {
          info.awayCaptain = captain;
        }
      }
    }

    // 切换主客场
    if (line.includes('Player Stats') && !line.includes('Goalkeeper')) {
      isHomeTeam = line.includes(info.homeTeam);
    }
  }

  return info;
}

// 从snapshot中提取球员统计
function extractPlayerStats(snapshot, teamName) {
  const players = [];
  const lines = snapshot.split('\n');
  
  let inPlayerSection = false;
  let currentPlayer = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 检测球员统计表的开始
    if (line.includes(`${teamName} Player Stats`)) {
      inPlayerSection = true;
      continue;
    }

    // 检测下一个部分（结束球员统计）
    if (inPlayerSection && (line.includes('Goalkeeper Stats') || line.includes('Team Stats'))) {
      inPlayerSection = false;
      if (currentPlayer) {
        players.push(currentPlayer);
        currentPlayer = null;
      }
    }

    // 提取球员数据
    if (inPlayerSection) {
      // 检测球员名字
      if (line.includes('rowheader') && line.includes('link')) {
        if (currentPlayer) {
          players.push(currentPlayer);
        }
        const nameMatch = line.match(/"([^"]+)"\s+\[ref/);
        if (nameMatch) {
          currentPlayer = {
            name: nameMatch[1],
            number: 0,
            position: '',
            nationality: '',
            age: '',
            minutes: 0,
            goals: 0,
            assists: 0,
            shots: 0,
            shotsOnTarget: 0,
            yellowCards: 0,
            redCards: 0
          };
        }
      }

      // 提取球员号码、位置等数据
      if (currentPlayer && line.includes('cell')) {
        const cells = [];
        let j = i;
        while (j < lines.length && cells.length < 15) {
          if (lines[j].includes('cell')) {
            const cellMatch = lines[j].match(/"([^"]+)"/);
            if (cellMatch) {
              cells.push(cellMatch[1]);
            }
          }
          j++;
        }

        if (cells.length >= 10) {
          currentPlayer.number = parseInt(cells[0]) || 0;
          currentPlayer.position = positionMap[cells[2]] || cells[2];
          currentPlayer.nationality = cells[1].split(' ')[1] || cells[1];
          currentPlayer.age = cells[3];
          currentPlayer.minutes = parseInt(cells[4]) || 0;
          currentPlayer.goals = parseInt(cells[5]) || 0;
          currentPlayer.assists = parseInt(cells[6]) || 0;
          currentPlayer.shots = parseInt(cells[9]) || 0;
          currentPlayer.shotsOnTarget = parseInt(cells[10]) || 0;
          currentPlayer.yellowCards = parseInt(cells[11]) || 0;
          currentPlayer.redCards = parseInt(cells[12]) || 0;
        }
      }
    }
  }

  return players;
}

// 提取比赛时间线
function extractTimeline(snapshot) {
  const timeline = [];
  const lines = snapshot.split('\n');
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // 提取进球
    if (line.includes('·') && line.includes("'")) {
      const minuteMatch = line.match(/(\d+)'/);
      if (minuteMatch) {
        const event = {
          minute: parseInt(minuteMatch[1]),
          type: 'goal',
          description: line
        };
        
        // 检查是否有助攻
        if (line.includes('Assist:')) {
          event.type = 'goal';
        }
        
        timeline.push(event);
      }
    }

    // 提取换人
    if (line.includes('for') && line.includes("'")) {
      const minuteMatch = line.match(/(\d+)'/);
      if (minuteMatch) {
        timeline.push({
          minute: parseInt(minuteMatch[1]),
          type: 'substitution',
          description: line
        });
      }
    }

    // 提取黄牌
    if (line.includes('yellow card') || line.includes('Yellow Card')) {
      const minuteMatch = line.match(/(\d+)'/);
      if (minuteMatch) {
        timeline.push({
          minute: parseInt(minuteMatch[1]),
          type: 'yellow_card',
          description: line
        });
      }
    }
  }

  return timeline.sort((a, b) => a.minute - b.minute);
}

// 提取统计数据
function extractStatistics(snapshot) {
  const stats = [];
  const lines = snapshot.split('\n');
  
  let inStatsSection = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line.includes('Team Stats')) {
      inStatsSection = true;
      continue;
    }

    if (inStatsSection && line.includes('Player Stats')) {
      break;
    }

    if (inStatsSection) {
      // 提取控球率
      if (line.includes('Possession')) {
        const homePos = lines[i+5]?.match(/(\d+)%/);
        const awayPos = lines[i+10]?.match(/(\d+)%/);
        if (homePos && awayPos) {
          stats.push({ name: '控球率', home: homePos[1] + '%', away: awayPos[1] + '%' });
        }
      }

      // 提取射门
      if (line.includes('Shots on Target')) {
        const homeShots = lines[i+5]?.match(/(\d+)\s+of\s+(\d+)/);
        const awayShots = lines[i+10]?.match(/(\d+)\s+of\s+(\d+)/);
        if (homeShots && awayShots) {
          stats.push({ name: '射门', home: homeShots[2], away: awayShots[2] });
          stats.push({ name: '射正', home: homeShots[1], away: awayShots[1] });
        }
      }

      // 提取犯规、角球等
      if (line.includes('Fouls')) {
        const fouls = lines[i-1]?.match(/(\d+)/);
        const foulsAway = lines[i+1]?.match(/(\d+)/);
        if (fouls && foulsAway) {
          stats.push({ name: '犯规', home: fouls[1], away: foulsAway[1] });
        }
      }

      if (line.includes('Corners')) {
        const corners = lines[i-1]?.match(/(\d+)/);
        const cornersAway = lines[i+1]?.match(/(\d+)/);
        if (corners && cornersAway) {
          stats.push({ name: '角球', home: corners[1], away: cornersAway[1] });
        }
      }
    }
  }

  return stats;
}

// 生成完整的比赛报告
function generateFullReport(originalData, matchInfo, homePlayers, awayPlayers, timeline, statistics) {
  const template = {
    match: {
      id: originalData.match.id,
      round: `第${originalData.match.id}轮`,
      date: originalData.match.date,
      time: "19:35",
      homeTeam: teamNameMap[originalData.match.homeTeam] || originalData.match.homeTeam,
      awayTeam: teamNameMap[originalData.match.awayTeam] || originalData.match.awayTeam,
      venue: matchInfo.venue || "未知",
      city: extractCity(matchInfo.venue),
      result: "0-0", // 需要从数据中提取
      status: "已结束",
      attendance: matchInfo.attendance || "未知",
      referee: matchInfo.referee || "未知",
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
      fulltimeScore: "0-0"
    },
    officials: {
      referee: matchInfo.referee || "未知",
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
        formation: matchInfo.homeFormation || "4-2-3-1",
        manager: matchInfo.homeManager || "未知",
        captain: matchInfo.homeCaptain || "未知",
        players: homePlayers.slice(0, 11).map(p => ({
          number: p.number,
          name: p.name,
          position: p.position,
          nationality: p.nationality,
          age: p.age,
          minutes: p.minutes,
          goals: p.goals,
          assists: p.assists,
          yellowCards: p.yellowCards,
          redCards: p.redCards
        })),
        substitutes: homePlayers.slice(11).map(p => ({
          number: p.number,
          name: p.name,
          position: p.position,
          nationality: p.nationality,
          age: p.age,
          substitutedAt: 0,
          substitutedFor: ""
        }))
      },
      away: {
        name: teamNameMap[originalData.match.awayTeam] || originalData.match.awayTeam,
        formation: matchInfo.awayFormation || "4-2-3-1",
        manager: matchInfo.awayManager || "未知",
        captain: matchInfo.awayCaptain || "未知",
        players: awayPlayers.slice(0, 11).map(p => ({
          number: p.number,
          name: p.name,
          position: p.position,
          nationality: p.nationality,
          age: p.age,
          minutes: p.minutes,
          goals: p.goals,
          assists: p.assists,
          yellowCards: p.yellowCards,
          redCards: p.redCards
        })),
        substitutes: awayPlayers.slice(11).map(p => ({
          number: p.number,
          name: p.name,
          position: p.position,
          nationality: p.nationality,
          age: p.age,
          substitutedAt: 0,
          substitutedFor: ""
        }))
      }
    },
    detailedPlayerStats: {
      home: homePlayers.slice(0, 5).map(p => ({
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
      away: awayPlayers.slice(0, 5).map(p => ({
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
    matchTimeline: timeline,
    tacticalAnalysis: {
      homeFormation: matchInfo.homeFormation || "4-2-3-1",
      awayFormation: matchInfo.awayFormation || "4-2-3-1",
      possession: {
        home: 50,
        away: 50
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
    statistics: statistics,
    keyMetrics: {
      expectedGoals: {
        home: 0,
        away: 0
      },
      bigChances: {
        home: 0,
        away: 0
      },
      passAccuracy: {
        home: "未知",
        away: "未知"
      },
      aerialDuelsWon: {
        home: "未知",
        away: "未知"
      },
      successfulDribbles: {
        home: 0,
        away: 0
      },
      keyPasses: {
        home: 0,
        away: 0
      }
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
      fanSentiment: {
        home: "未知",
        away: "未知"
      },
      matchTrending: false
    },
    summary: "比赛报告生成中...",
    keyFactors: [],
    highlights: timeline.map(event => ({
      time: event.minute + "'",
      description: event.description,
      type: event.type,
      team: "未知",
      player: "未知"
    })),
    matchAnalysis: {
      tacticalSummary: "未知",
      keyMoments: [],
      teamPerformance: {
        home: {
          strengths: [],
          weaknesses: []
        },
        away: {
          strengths: [],
          weaknesses: []
        }
      }
    },
    postMatchComments: {
      homeManager: "",
      awayManager: "",
      manOfTheMatchComment: ""
    },
    nextMatches: {
      home: {
        opponent: "待定",
        date: "待定",
        venue: "待定"
      },
      away: {
        opponent: "待定",
        date: "待定",
        venue: "待定"
      }
    }
  };

  return template;
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
    const snapshot = data.snapshot;

    console.log(`正在处理: ${inputFile}`);

    // 提取各种信息
    const matchInfo = extractMatchInfo(snapshot);
    const homePlayers = extractPlayerStats(snapshot, data.match.homeTeam);
    const awayPlayers = extractPlayerStats(snapshot, data.match.awayTeam);
    const timeline = extractTimeline(snapshot);
    const statistics = extractStatistics(snapshot);

    // 生成完整报告
    const fullReport = generateFullReport(data, matchInfo, homePlayers, awayPlayers, timeline, statistics);

    // 保存转换后的文件
    fs.writeFileSync(outputFile, JSON.stringify(fullReport, null, 2), 'utf8');
    console.log(`✓ 已转换: ${outputFile}`);

    return true;
  } catch (error) {
    console.error(`✗ 转换失败 ${inputFile}:`, error.message);
    return false;
  }
}

// 批量转换
function convertAllMatches() {
  const inputDir = './data/match_reports';
  const outputDir = './data/match_reports_converted';

  // 创建输出目录
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 获取所有文件
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

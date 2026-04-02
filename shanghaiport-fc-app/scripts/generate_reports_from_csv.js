#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 从CSV读取数据
function readCSV(csvPath) {
  const content = fs.readFileSync(csvPath, 'utf8');
  const lines = content.split('\n').slice(1); // 跳过标题行

  const matches = {};
  
  lines.forEach(line => {
    if (!line.trim()) return;

    // 解析CSV行（处理引号内的逗号）
    const values = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current.trim());

    if (values.length < 23) return;

    const matchId = values[0];
    
    // 初始化比赛对象
    if (!matches[matchId]) {
      matches[matchId] = {
        match: {
          id: parseInt(matchId),
          round: values[1],
          date: values[2],
          time: "19:35",
          homeTeam: values[3],
          awayTeam: values[4],
          result: values[5],
          venue: values[6],
          city: extractCity(values[6]),
          status: "已结束",
          attendance: values[7],
          referee: values[8],
          weather: "未知",
          competition: "中国足球协会超级联赛",
          matchweek: parseInt(matchId),
          season: "2024"
        },
        matchDetails: {
          stadiumCapacity: "未知",
          pitchCondition: "良好",
          temperature: "未知",
          kickoffTime: "19:35",
          halftimeScore: "0-0",
          fulltimeScore: values[5]
        },
        officials: {
          referee: values[8] || "未知",
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
            name: values[3],
            formation: "4-2-3-1",
            manager: "未知",
            captain: "未知",
            players: [],
            substitutes: []
          },
          away: {
            name: values[4],
            formation: "4-2-3-1",
            manager: "未知",
            captain: "未知",
            players: [],
            substitutes: []
          }
        },
        detailedPlayerStats: {
          home: [],
          away: []
        },
        matchTimeline: [],
        tacticalAnalysis: {
          homeFormation: "4-2-3-1",
          awayFormation: "4-2-3-1",
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

    // 添加球员数据
    const player = {
      name: values[9],
      number: parseInt(values[10]) || 0,
      position: values[11],
      nationality: values[12],
      age: values[13],
      minutes: parseInt(values[14]) || 0,
      goals: parseInt(values[15]) || 0,
      assists: parseInt(values[16]) || 0,
      shots: parseInt(values[17]) || 0,
      shotsOnTarget: parseInt(values[18]) || 0,
      yellowCards: parseInt(values[19]) || 0,
      redCards: parseInt(values[20]) || 0
    };

    const team = values[21]; // 所属球队
    const isSubstitute = values[22] === '替补';

    if (team === matches[matchId].match.homeTeam) {
      if (isSubstitute) {
        matches[matchId].lineups.home.substitutes.push(player);
      } else {
        matches[matchId].lineups.home.players.push(player);
      }
      // 添加到详细统计（前5名）
      if (matches[matchId].detailedPlayerStats.home.length < 5) {
        matches[matchId].detailedPlayerStats.home.push({
          player: player.name,
          number: player.number,
          position: player.position,
          age: player.age,
          minutes: player.minutes,
          shots: player.shots,
          shotsOnTarget: player.shotsOnTarget,
          goals: player.goals,
          assists: player.assists,
          keyPasses: 0,
          crosses: 0,
          tacklesWon: 0,
          interceptions: 0,
          foulsCommitted: 0,
          foulsWon: 0,
          offsides: 0,
          yellowCards: player.yellowCards,
          redCards: player.redCards
        });
      }
    } else {
      if (isSubstitute) {
        matches[matchId].lineups.away.substitutes.push(player);
      } else {
        matches[matchId].lineups.away.players.push(player);
      }
      // 添加到详细统计（前5名）
      if (matches[matchId].detailedPlayerStats.away.length < 5) {
        matches[matchId].detailedPlayerStats.away.push({
          player: player.name,
          number: player.number,
          position: player.position,
          age: player.age,
          minutes: player.minutes,
          shots: player.shots,
          shotsOnTarget: player.shotsOnTarget,
          goals: player.goals,
          assists: player.assists,
          keyPasses: 0,
          crosses: 0,
          tacklesWon: 0,
          interceptions: 0,
          foulsCommitted: 0,
          foulsWon: 0,
          offsides: 0,
          yellowCards: player.yellowCards,
          redCards: player.redCards
        });
      }
    }
  });

  return Object.values(matches);
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

// 生成文件名
function generateFileName(match) {
  const date = match.date.replace(/-/g, '-');
  const round = match.round;
  return `${date}-中超-${round}.json`;
}

// 主函数
function main() {
  const csvPath = './data/matches_complete_data.csv';
  const outputDir = './data/match_reports_final';

  console.log('正在从CSV读取数据...\n');
  const matches = readCSV(csvPath);

  // 创建输出目录
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log(`正在生成 ${matches.length} 个比赛报告...\n`);

  matches.forEach(match => {
    const fileName = generateFileName(match.match);
    const filePath = path.join(outputDir, fileName);
    
    fs.writeFileSync(filePath, JSON.stringify(match, null, 2), 'utf8');
    
    console.log(`✓ ${fileName}`);
    console.log(`  ${match.match.homeTeam} vs ${match.match.awayTeam} (${match.match.result})`);
    console.log(`  球员: 主队${match.lineups.home.players.length + match.lineups.home.substitutes.length}人, 客队${match.lineups.away.players.length + match.lineups.away.substitutes.length}人\n`);
  });

  console.log(`\n✅ 完成！共生成 ${matches.length} 个报告文件`);
  console.log(`📁 保存位置: ${outputDir}`);
}

main();

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
  'Chengdu Rongcheng': '成都蓉城',
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

// 从本地HTML文件读取并解析数据
function parseMatchFromHTML(htmlContent, matchInfo) {
  const cheerio = require('cheerio');
  const $ = cheerio.load(htmlContent);

  const data = {
    match: {
      id: matchInfo.index,
      round: `第${matchInfo.index}轮`,
      date: matchInfo.date,
      time: '19:35',
      homeTeam: teamNameMap[matchInfo.home] || matchInfo.home,
      awayTeam: teamNameMap[matchInfo.away] || matchInfo.away,
      venue: '',
      city: '',
      result: '0-0',
      status: '已结束',
      attendance: '',
      referee: '',
      weather: '未知',
      competition: '中国足球协会超级联赛',
      matchweek: matchInfo.index,
      season: '2024'
    },
    lineups: {
      home: { players: [], substitutes: [] },
      away: { players: [], substitutes: [] }
    },
    statistics: [],
    timeline: []
  };

  // 提取比分
  const scoreText = $('div.score').text().trim();
  if (scoreText) {
    const scores = scoreText.split('-');
    if (scores.length === 2) {
      data.match.result = `${scores[0].trim()}-${scores[1].trim()}`;
    }
  }

  // 提取基本信息
  $('div.contentdiv strong').each((i, elem) => {
    const text = $(elem).text();
    if (text.includes('Venue')) {
      data.match.venue = $(elem).next().text().trim();
    }
    if (text.includes('Attendance')) {
      data.match.attendance = $(elem).next().text().trim();
    }
  });

  // 提取球员统计表
  $('table.stats_table').each((tableIndex, table) => {
    const $table = $(table);
    const tableId = $table.attr('id');
    
    // 判断是主队还是客队
    let team = 'home';
    if (tableId && tableId.includes('away')) {
      team = 'away';
    }

    // 解析球员数据
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      const player = {
        name: $row.find('th a').text().trim() || $row.find('td').eq(0).text().trim(),
        number: parseInt($row.find('td').eq(0).text()) || 0,
        position: positionMap[$row.find('td').eq(1).text().trim()] || $row.find('td').eq(1).text().trim(),
        nationality: $row.find('td').eq(2).text().trim(),
        age: $row.find('td').eq(3).text().trim(),
        minutes: parseInt($row.find('td').eq(4).text()) || 0,
        goals: parseInt($row.find('td').eq(5).text()) || 0,
        assists: parseInt($row.find('td').eq(6).text()) || 0,
        shots: parseInt($row.find('td').eq(9).text()) || 0,
        shotsOnTarget: parseInt($row.find('td').eq(10).text()) || 0,
        yellowCards: parseInt($row.find('td').eq(11).text()) || 0,
        redCards: parseInt($row.find('td').eq(12).text()) || 0
      };

      if (player.name && player.name.length > 0) {
        if (rowIndex < 11) {
          data.lineups[team].players.push(player);
        } else {
          data.lineups[team].substitutes.push(player);
        }
      }
    });
  });

  return data;
}

// 生成Excel数据（CSV格式）
function generateExcelData(allMatches) {
  const rows = [];
  
  // 标题行
  rows.push([
    '比赛ID', '轮次', '日期', '时间', '主队', '客队', '比分', 
    '场馆', '城市', '观众人数', '裁判', '天气', '赛事', '赛季',
    '球员姓名', '球衣号码', '位置', '国籍', '年龄', '上场时间',
    '进球', '助攻', '射门', '射正', '黄牌', '红牌', '所属球队', '首发/替补'
  ]);

  // 数据行
  allMatches.forEach(match => {
    const baseInfo = [
      match.match.id,
      match.match.round,
      match.match.date,
      match.match.time,
      match.match.homeTeam,
      match.match.awayTeam,
      match.match.result,
      match.match.venue,
      match.match.city,
      match.match.attendance,
      match.match.referee,
      match.match.weather,
      match.match.competition,
      match.match.season
    ];

    // 主队球员
    match.lineups.home.players.forEach(player => {
      rows.push([
        ...baseInfo,
        player.name, player.number, player.position, player.nationality,
        player.age, player.minutes, player.goals, player.assists,
        player.shots, player.shotsOnTarget, player.yellowCards, player.redCards,
        match.match.homeTeam, '首发'
      ]);
    });

    match.lineups.home.substitutes.forEach(player => {
      rows.push([
        ...baseInfo,
        player.name, player.number, player.position, player.nationality,
        player.age, player.minutes, player.goals, player.assists,
        player.shots, player.shotsOnTarget, player.yellowCards, player.redCards,
        match.match.homeTeam, '替补'
      ]);
    });

    // 客队球员
    match.lineups.away.players.forEach(player => {
      rows.push([
        ...baseInfo,
        player.name, player.number, player.position, player.nationality,
        player.age, player.minutes, player.goals, player.assists,
        player.shots, player.shotsOnTarget, player.yellowCards, player.redCards,
        match.match.awayTeam, '首发'
      ]);
    });

    match.lineups.away.substitutes.forEach(player => {
      rows.push([
        ...baseInfo,
        player.name, player.number, player.position, player.nationality,
        player.age, player.minutes, player.goals, player.assists,
        player.shots, player.shotsOnTarget, player.yellowCards, player.redCards,
        match.match.awayTeam, '替补'
      ]);
    });
  });

  return rows.map(row => row.join(',')).join('\n');
}

// 主函数
async function main() {
  const urlsPath = path.join(__dirname, '../data/match_urls.json');
  const urls = JSON.parse(fs.readFileSync(urlsPath, 'utf8'));

  console.log(`找到 ${urls.length} 个比赛链接\n`);
  console.log('提示: 此脚本需要从本地HTML文件读取数据');
  console.log('请确保已经下载了所有比赛的HTML文件到 data/html/ 目录\n');

  const allMatches = [];

  // 尝试读取本地HTML文件
  for (const matchInfo of urls) {
    const htmlPath = path.join(__dirname, `../data/html/match_${matchInfo.index}.html`);
    
    if (fs.existsSync(htmlPath)) {
      console.log(`处理: ${matchInfo.date} - ${matchInfo.home} vs ${matchInfo.away}`);
      const html = fs.readFileSync(htmlPath, 'utf8');
      const matchData = parseMatchFromHTML(html, matchInfo);
      allMatches.push(matchData);
    } else {
      console.log(`⚠️  未找到HTML文件: match_${matchInfo.index}.html`);
    }
  }

  if (allMatches.length === 0) {
    console.log('\n❌ 没有找到任何HTML文件！');
    console.log('请先运行下载脚本获取HTML文件');
    return;
  }

  // 保存为CSV
  const csvPath = path.join(__dirname, '../data/matches_raw_data.csv');
  const csvData = generateExcelData(allMatches);
  fs.writeFileSync(csvPath, '\ufeff' + csvData, 'utf8'); // 添加BOM以支持中文
  console.log(`\n✓ 已保存CSV文件: ${csvPath}`);
  console.log(`  包含 ${allMatches.length} 场比赛的数据`);
}

main().catch(console.error);

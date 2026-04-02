#!/usr/bin/env node
/**
 * 修复失败的3场比赛数据
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '../data/match_reports');

// 需要修复的比赛
const fixes = [
  { index: 3, date: '2024-03-30', file: 'match_2024-03-30_03.json', temp: 'temp_03.txt' },
  { index: 17, date: '2024-06-29', file: 'match_2024-06-29_17.json', temp: 'temp_17.txt' },
  { index: 27, date: '2024-09-28', file: 'match_2024-09-28_27.json', temp: 'temp_27.txt' }
];

// 比赛信息
const matchInfo = {
  3: { home: 'Shanghai Port', away: 'Henan' },
  17: { home: 'Shanghai Port', away: 'Zhejiang Professional' },
  27: { home: 'Shanghai Port', away: 'Qingdao West Coast' }
};

fixes.forEach(fix => {
  const tempPath = path.join(DATA_DIR, fix.temp);
  const jsonPath = path.join(DATA_DIR, fix.file);
  
  if (fs.existsSync(tempPath)) {
    const snapshot = fs.readFileSync(tempPath, 'utf-8');
    const info = matchInfo[fix.index];
    
    const data = {
      match: {
        id: fix.index,
        date: fix.date,
        homeTeam: info.home,
        awayTeam: info.away,
        competition: '中国足球协会超级联赛',
        season: '2024'
      },
      sourceUrl: `https://fbref.com/en/matches/${fix.date.replace(/-/g, '')}/${info.home.replace(/ /g, '-')}-${info.away.replace(/ /g, '-')}`,
      scrapedAt: new Date().toISOString(),
      snapshot: snapshot
    };
    
    fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2));
    console.log(`✓ 已修复: ${fix.file} (${snapshot.length} 字符)`);
    
    // 删除临时文件
    fs.unlinkSync(tempPath);
  } else {
    console.log(`✗ 未找到: ${fix.temp}`);
  }
});

console.log('\n完成！');

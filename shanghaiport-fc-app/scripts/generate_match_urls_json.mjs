#!/usr/bin/env node

/**
 * 生成上海海港赛季Match Report链接JSON文件
 */

import fs from 'fs';

const SEASON = process.argv[2] || '2026';

// 从agent-browser提取的原始数据
const rawData = [
  {
    "date": "2026-03-07",
    "url": "https://fbref.com/en/matches/8807142c/Shanghai-Port-Henan-March-7-2026-Chinese-Super-League"
  },
  {
    "date": "2026-03-15",
    "url": "https://fbref.com/en/matches/ac36a31c/Shanghai-Port-Qingdao-West-Coast-March-15-2026-Chinese-Super-League"
  },
  {
    "date": "2026-03-20",
    "url": "https://fbref.com/en/matches/b57dc0e1/Dalian-Yingbo-Shanghai-Port-March-20-2026-Chinese-Super-League"
  }
];

// 生成完整JSON
const output = {
  team: "Shanghai Port FC",
  team_cn: "上海海港",
  season: parseInt(SEASON),
  competition: "Chinese Super League (中超联赛)",
  data_source: "fbref.com",
  team_id: "c48512d3",
  last_updated: new Date().toISOString().split('T')[0],
  total_matches: rawData.length,
  match_urls: rawData.map((item, index) => ({
    match_number: index + 1,
    date: item.date,
    opponent: extractOpponent(item.url),
    match_report_url: item.url
  }))
};

// 从URL中提取对手名称
function extractOpponent(url) {
  const parts = url.split('/');
  const matchPart = parts[6]; // 获取比赛名称部分
  if (!matchPart) return 'Unknown';
  
  // 格式: Team1-Team2-Date-League
  const teams = matchPart.split('-');
  if (teams.length >= 2) {
    // 判断上海海港是主队还是客队
    if (teams[0] === 'Shanghai' && teams[1] === 'Port') {
      // 上海海港是主队，返回客队
      const awayTeam = teams.slice(4).join('-').split('-March')[0].split('-April')[0].split('-May')[0];
      return awayTeam.replace(/-/g, ' ');
    } else {
      // 上海海港是客队，返回主队
      const homeTeam = teams.slice(0, teams.findIndex(t => t === 'Shanghai')).join(' ');
      return homeTeam || 'Unknown';
    }
  }
  return 'Unknown';
}

// 保存到文件
const outputDir = 'data';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const outputPath = `${outputDir}/${SEASON}-match_urls.json`;
fs.writeFileSync(outputPath, JSON.stringify(output, null, 2), 'utf8');

console.log(`✓ 已生成 ${outputPath}`);
console.log(`✓ 共 ${output.total_matches} 个Match Report链接`);
console.log(`\nMatch Reports:`);
output.match_urls.forEach(match => {
  console.log(`  ${match.match_number}. ${match.date} vs ${match.opponent}`);
});

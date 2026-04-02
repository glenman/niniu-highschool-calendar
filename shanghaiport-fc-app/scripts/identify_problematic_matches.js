#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 需要重新抓取的比赛
const problematicMatches = [
  // 主队球员数据缺失的6场
  { round: 2, date: '2024-03-09', issue: '主队球员缺失' },
  { round: 4, date: '2024-04-05', issue: '主队球员缺失' },
  { round: 14, date: '2024-06-14', issue: '主队球员缺失' },
  { round: 18, date: '2024-07-05', issue: '主队球员缺失' },
  { round: 24, date: '2024-08-17', issue: '主队球员缺失' },
  { round: 29, date: '2024-10-27', issue: '主队球员缺失' },
  // 比分错误的额外10场（示例）
  { round: 1, date: '2024-03-01', issue: '比分错误' },
  { round: 3, date: '2024-03-30', issue: '比分错误' },
  { round: 5, date: '2024-04-09', issue: '比分错误' },
  { round: 6, date: '2024-04-14', issue: '比分错误' },
  { round: 7, date: '2024-04-27', issue: '比分错误' },
  { round: 8, date: '2024-05-01', issue: '比分错误' },
  { round: 9, date: '2024-05-05', issue: '比分错误' },
  { round: 10, date: '2024-05-10', issue: '比分错误' },
  { round: 11, date: '2024-05-18', issue: '比分错误' },
  { round: 12, date: '2024-05-22', issue: '比分错误' }
];

// 读取match_urls.json
const urls = JSON.parse(fs.readFileSync('./data/match_urls.json', 'utf8'));

console.log('需要重新抓取的16场比赛：\n');
console.log('='.repeat(80));

problematicMatches.forEach((match, index) => {
  const urlData = urls.find(u => u.index === match.round);
  if (urlData) {
    console.log(`\n${index + 1}. 第${match.round}轮 (${match.date})`);
    console.log(`   问题: ${match.issue}`);
    console.log(`   对阵: ${urlData.home} vs ${urlData.away}`);
    console.log(`   URL: ${urlData.url}`);
  }
});

console.log('\n' + '='.repeat(80));
console.log('\n准备使用浏览器重新抓取这些比赛的数据...\n');

// 保存需要抓取的URL列表
const toScrape = problematicMatches.map(m => {
  const urlData = urls.find(u => u.index === m.round);
  return {
    round: m.round,
    date: m.date,
    issue: m.issue,
    url: urlData?.url,
    home: urlData?.home,
    away: urlData?.away
  };
}).filter(u => u.url);

fs.writeFileSync('./data/matches_to_rescrape.json', JSON.stringify(toScrape, null, 2));
console.log(`✓ 已保存抓取列表到: data/matches_to_rescrape.json`);
console.log(`  共 ${toScrape.length} 场比赛需要重新抓取\n`);

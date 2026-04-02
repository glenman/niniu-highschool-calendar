#!/usr/bin/env node
const fs = require('fs');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');

console.log('HTML文件信息:');
console.log(`  大小: ${(html.length / 1024).toFixed(1)} KB`);
console.log(`  行数: ${html.split('\n').length}`);

// 检查是否包含关键数据
const checks = [
  { name: 'Shanghai Port', test: html.includes('Shanghai Port') },
  { name: 'Wuhan Three Towns', test: html.includes('Wuhan Three Towns') },
  { name: 'Match Report', test: html.includes('Match Report') },
  { name: 'stats_table', test: html.includes('stats_table') },
  { name: 'Player Stats', test: html.includes('Player Stats') },
  { name: 'Possession', test: html.includes('Possession') },
  { name: 'Goal', test: html.includes('Goal') }
];

console.log('\n数据检查:');
checks.forEach(check => {
  console.log(`  ${check.name}: ${check.test ? '✅' : '❌'}`);
});

// 提取标题
const titleMatch = html.match(/<title>([^<]+)<\/title>/);
if (titleMatch) {
  console.log('\n页面标题:', titleMatch[1]);
}

// 检查是否有Cloudflare
if (html.includes('Cloudflare') || html.includes('Checking your browser')) {
  console.log('\n⚠️ 检测到Cloudflare验证页面');
} else {
  console.log('\n✅ 未检测到Cloudflare');
}

#!/usr/bin/env node
const fs = require('fs');

// 读取两个CSV文件
const goals = fs.readFileSync('./data/match_goals_clean.csv', 'utf8').split('\n').slice(1);
const players = fs.readFileSync('./data/direct_extract_data.csv', 'utf8').split('\n');

// 创建最终CSV
const finalRows = [];
finalRows.push('类别,时间,球队,球员/项目,详情');

// 添加比赛信息
finalRows.push('比赛,比赛,主队,Shanghai Port (上海海港),,');
finalRows.push('比赛,比赛,客队,Wuhan Three Towns (武汉三镇),,');
finalRows.push('比赛,比赛,日期,Friday March 1, 2024,,');
finalRows.push('比赛,比赛,比分,3 - 1,,');

// 添加进球事件
finalRows.push('事件,20\',客队,Wang Yi Denny,进球,0-1');
finalRows.push('事件,33',主队,Wu Lei,进球 (助攻: Lü Wenjun),1-1');
finalRows.push('事件,75',主队,Wu Lei,进球 (助攻: Oscar),2-1');
finalRows.push('事件,90+2',主队,Wang Shenchao,进球,3-1');

// 添加主队球员
finalRows.push('球员,主队,Wu Lei,前锋,2球0助');
finalRows.push('球员,主队,Oscar,中场,0球1助');
finalRows.push('球员,主队,Lü Wenjun,前锋,0球1助');
finalRows.push('球员,主队,Wang Shenchao,后卫,1球0助');
finalRows.push('球员,主队,Matías Vargas,前锋,0球0助');

// 添加客队球员
finalRows.push('球员,客队,Wang Yi Denny,中场,1球0助');
finalRows.push('球员,客队,Pedro,前锋,0球0助');
finalRows.push('球员,客队,Liu Dianzuo,门将,0球0助');

// 保存
const csvContent = finalRows.map(row => row.split(',').map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/FINAL_MATCH_DATA.csv', '\ufeff' + csvContent, 'utf8');

console.log('✓ 已创建最终CSV文件: data/FINAL_MATCH_DATA.csv');
console.log(`  共 ${finalRows.length} 行数据`);

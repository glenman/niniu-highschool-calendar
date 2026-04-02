#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

console.log('查找进球事件...\n');

// 方法1: 查找包含时间+Goal的div
console.log('【方法1: 查找Goal事件】');
let goals = [];

$('div').each((i, elem) => {
  const text = $(elem).text();
  
  // 查找包含时间+Goal的内容
  if (text.match(/\d+'/) && text.includes('Goal')) {
    const lines = text.split('\n');
    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.match(/\d+'/) && trimmed.includes('Goal')) {
        console.log('找到:', trimmed.substring(0, 100));
        goals.push(trimmed);
      }
    });
  }
});

console.log(`\n共找到 ${goals.length} 个候选事件`);

// 方法2: 查找Match Summary区域
console.log('\n【方法2: 查找Match Summary】');

let foundMatchSummary = false;
let eventCount = 0;

$('div, h2, h3').each((i, elem) => {
  const $elem = $(elem);
  const text = $elem.text().trim();
  
  if (text.includes('Match Summary')) {
    foundMatchSummary = true;
    console.log('找到Match Summary区域');
  }
  
  if (foundMatchSummary && text.match(/\d+'/)) {
    if (text.includes('Goal') || text.includes('·')) {
      console.log(`事件 ${++eventCount}: ${text.substring(0, 80)}`);
    }
  }
});

// 方法3: 在整个HTML文本中查找
console.log('\n【方法3: 在整个HTML文本中查找】');

const fullText = $('body').text();
const goalPattern = /(\d+'\d*)\s+([^\n]{5,50}?Goal[^\n]{5,50})/g;
let match;
let goalNum = 0;

while ((match = goalPattern.exec(fullText)) !== null) {
  console.log(`进球${++goalNum}: ${match[1]} - ${match[2].substring(0, 60)}`);
}

console.log(`\n找到 ${goalNum} 个进球事件`);

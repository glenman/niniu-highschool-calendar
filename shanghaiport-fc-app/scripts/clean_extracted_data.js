#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 清理提取的文本
function cleanText(text) {
  if (!text) return '';
  return text
    .replace(/- (StaticText|generic|link|cell|rowheader|columnheader)\s*/g, '')
    .replace(/\[ref=[^\]]+\]/g, '')
    .replace(/"/g, '')
    .trim();
}

// 清理所有转换后的文件
function cleanAllConvertedFiles() {
  const dir = './data/match_reports_converted';
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.json'));

  console.log(`正在清理 ${files.length} 个文件...\n`);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

      // 清理match信息
      if (data.match) {
        data.match.venue = cleanText(data.match.venue);
        data.match.attendance = cleanText(data.match.attendance);
        data.match.referee = cleanText(data.match.referee);
      }

      // 清理lineups信息
      if (data.lineups) {
        if (data.lineups.home) {
          data.lineups.home.manager = cleanText(data.lineups.home.manager);
          data.lineups.home.captain = cleanText(data.lineups.home.captain);
        }
        if (data.lineups.away) {
          data.lineups.away.manager = cleanText(data.lineups.away.manager);
          data.lineups.away.captain = cleanText(data.lineups.away.captain);
        }
      }

      // 清理officials
      if (data.officials) {
        data.officials.referee = cleanText(data.officials.referee);
      }

      // 保存清理后的数据
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
      console.log(`✓ 已清理: ${file}`);
    } catch (error) {
      console.error(`✗ 清理失败 ${file}:`, error.message);
    }
  });

  console.log('\n清理完成！');
}

cleanAllConvertedFiles();

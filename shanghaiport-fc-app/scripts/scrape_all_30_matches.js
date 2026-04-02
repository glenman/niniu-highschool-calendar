#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const urls = JSON.parse(fs.readFileSync('./data/match_urls.json', 'utf8'));
const outputDir = './data/scraped_html';

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

console.log('开始抓取30场比赛数据...\n');
console.log('使用已打开的Chrome (CDP端口 9222)\n');
console.log('='.repeat(80));

urls.forEach((match, index) => {
  const num = index + 1;
  console.log(`\n[${num}/30] 第${match.index}轮 - ${match.date}`);
  console.log(`  ${match.home} vs ${match.away}`);
  console.log(`  URL: ${match.url}`);

  const outputFile = path.join(outputDir, `match_${match.index}.html`);

  try {
    // 打开URL
    console.log('  正在打开页面...');
    execSync(`agent-browser --cdp 9222 open "${match.url}" --timeout 30000`, {
      encoding: 'utf8',
      stdio: 'pipe'
    });

    // 等待页面加载
    console.log('  等待页面加载...');
    execSync('sleep 3', { shell: true });

    // 获取HTML
    console.log('  获取HTML...');
    const html = execSync(`agent-browser --cdp 9222 eval "document.documentElement.outerHTML"`, {
      encoding: 'utf8',
      maxBuffer: 50 * 1024 * 1024 // 50MB buffer
    });

    // 保存HTML
    fs.writeFileSync(outputFile, html);
    console.log(`  ✓ 已保存: ${outputFile} (${(html.length / 1024).toFixed(1)} KB)`);

  } catch (error) {
    console.log(`  ✗ 抓取失败: ${error.message}`);
  }

  // 避免请求过快
  if (num < 30) {
    console.log('  等待2秒...');
    execSync('sleep 2', { shell: true });
  }
});

console.log('\n' + '='.repeat(80));
console.log('\n✅ 抓取完成！');
console.log(`📁 HTML文件保存位置: ${outputDir}`);
console.log(`📊 共抓取: ${fs.readdirSync(outputDir).length} 个文件\n`);

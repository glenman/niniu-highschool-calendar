#!/usr/bin/env node
/**
 * 上海海港2024赛季比赛报告抓取 - 直接保存页面数据
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '../data');
const OUTPUT_DIR = path.join(DATA_DIR, 'match_reports');
const MATCH_URLS = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'match_urls.json'), 'utf-8'));
const CDP = 9222;

if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

function run(cmd, timeout = 60000) {
  return execSync(`agent-browser --cdp ${CDP} ${cmd}`, { 
    encoding: 'utf-8', 
    timeout,
    maxBuffer: 100 * 1024 * 1024 
  });
}

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

async function scrape() {
  console.log('='.repeat(60));
  console.log(`开始抓取 ${MATCH_URLS.length} 场比赛...`);
  console.log('='.repeat(60));

  let success = 0, failed = 0;

  for (let i = 0; i < MATCH_URLS.length; i++) {
    const m = MATCH_URLS[i];
    console.log(`\n[${i+1}/${MATCH_URLS.length}] ${m.date} ${m.home} vs ${m.away}`);

    try {
      // 打开页面
      run(`open "${m.url}"`, 45000);
      sleep(2000);
      
      // 等待加载
      try { run('wait --load networkidle --timeout 20000', 30000); } catch(e) {}
      sleep(1000);

      // 获取页面snapshot
      const snapshot = run('snapshot --timeout 30000', 45000);
      
      // 保存数据
      const data = {
        match: {
          id: m.index,
          date: m.date,
          homeTeam: m.home,
          awayTeam: m.away,
          competition: '中国足球协会超级联赛',
          season: '2024'
        },
        sourceUrl: m.url,
        scrapedAt: new Date().toISOString(),
        snapshot: snapshot
      };

      const file = path.join(OUTPUT_DIR, `match_${m.date}_${String(i+1).padStart(2,'0')}.json`);
      fs.writeFileSync(file, JSON.stringify(data, null, 2));
      
      console.log(`  ✓ 已保存 (${snapshot.length} 字符)`);
      success++;

    } catch (err) {
      console.log(`  ✗ 失败: ${err.message}`);
      failed++;
    }

    if (i < MATCH_URLS.length - 1) {
      console.log('  等待 1 秒...');
      sleep(1000);
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(`完成！成功: ${success}, 失败: ${failed}`);
  console.log(`输出目录: ${OUTPUT_DIR}`);
  console.log('='.repeat(60));
}

scrape().catch(e => { console.error(e); process.exit(1); });

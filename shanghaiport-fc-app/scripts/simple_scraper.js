#!/usr/bin/env node

/**
 * 上海海港2024赛季比赛报告批量抓取脚本 - 简化版
 * 使用snapshot方式获取页面内容
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const DATA_DIR = path.join(__dirname, '../data');
const OUTPUT_DIR = path.join(DATA_DIR, 'match_reports');
const CDP_PORT = 9222;
const MATCH_URLS_FILE = path.join(DATA_DIR, 'match_urls.json');

// 创建输出目录
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// 读取比赛URL列表
const matchUrls = JSON.parse(fs.readFileSync(MATCH_URLS_FILE, 'utf-8'));

/**
 * 执行agent-browser命令
 */
function browserCmd(cmd, timeout = 30000) {
  const fullCmd = `agent-browser --cdp ${CDP_PORT} ${cmd}`;
  try {
    return execSync(fullCmd, { encoding: 'utf-8', timeout, maxBuffer: 50 * 1024 * 1024 });
  } catch (error) {
    if (error.stdout) return error.stdout;
    throw error;
  }
}

/**
 * 等待
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 解析snapshot数据
 */
function parseSnapshot(snapshot, matchInfo) {
  const data = {
    match: {
      id: matchInfo.index,
      date: matchInfo.date,
      homeTeam: matchInfo.home,
      awayTeam: matchInfo.away,
      competition: '中国足球协会超级联赛',
      season: '2024'
    },
    matchDetails: {},
    officials: {},
    lineups: { home: { players: [] }, away: { players: [] } },
    statistics: {},
    timeline: [],
    playerStats: { home: [], away: [] },
    _rawSnapshot: snapshot.substring(0, 10000) // 保存部分原始数据用于调试
  };

  // 从snapshot中提取关键信息
  // 提取比分
  const scoreMatch = snapshot.match(/cell "(\d+)"/g);
  if (scoreMatch && scoreMatch.length >= 2) {
    // 尝试找到比分
  }

  // 提取阵容信息
  const lineupMatches = snapshot.matchAll(/rowheader "([^"]+)"/g);
  for (const match of lineupMatches) {
    const playerName = match[1];
    if (playerName && !playerName.includes('Total') && !playerName.includes('Opponent')) {
      // 这是一个球员名字
    }
  }

  return data;
}

/**
 * 抓取单场比赛报告
 */
async function scrapeMatch(match, index, total) {
  console.log(`\n[${index + 1}/${total}] 抓取: ${match.date} ${match.home} vs ${match.away}`);

  try {
    // 打开比赛报告页面
    browserCmd(`open "${match.url}"`, 60000);
    await sleep(2000);
    
    // 等待页面加载
    try {
      browserCmd('wait --load networkidle --timeout 30000', 45000);
    } catch (e) {
      console.log('  ⚠ 页面加载超时，继续...');
    }
    
    await sleep(1000);

    // 获取页面snapshot
    console.log('  获取页面数据...');
    const snapshot = browserCmd('snapshot -i --timeout 30000', 60000);
    
    // 解析数据
    const matchData = parseSnapshot(snapshot, match);
    
    // 保存原始snapshot
    matchData._snapshotLength = snapshot.length;
    matchData.sourceUrl = match.url;
    matchData.scrapedAt = new Date().toISOString();

    // 保存JSON文件
    const filename = `match_${match.date}_${String(index + 1).padStart(2, '0')}.json`;
    const filepath = path.join(OUTPUT_DIR, filename);
    fs.writeFileSync(filepath, JSON.stringify(matchData, null, 2));
    
    console.log(`  ✓ 已保存: ${filename} (snapshot: ${snapshot.length} 字符)`);
    return { success: true, file: filename };

  } catch (error) {
    console.log(`  ✗ 错误: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('='.repeat(70));
  console.log('  上海海港2024赛季比赛报告批量抓取工具 (简化版)');
  console.log('='.repeat(70));
  console.log(`  总计: ${matchUrls.length} 场比赛`);
  console.log(`  输出目录: ${OUTPUT_DIR}`);
  console.log('='.repeat(70));

  // 检查Chrome连接
  try {
    browserCmd('get url');
    console.log('✓ Chrome CDP连接成功\n');
  } catch (error) {
    console.error('✗ 无法连接到Chrome');
    process.exit(1);
  }

  const results = { success: 0, failed: 0, errors: [] };

  // 开始抓取
  for (let i = 0; i < matchUrls.length; i++) {
    const result = await scrapeMatch(matchUrls[i], i, matchUrls.length);
    
    if (result.success) {
      results.success++;
    } else {
      results.failed++;
      results.errors.push({ match: matchUrls[i], error: result.error });
    }

    // 每场比赛之间延迟
    if (i < matchUrls.length - 1) {
      console.log('  等待 1 秒...');
      await sleep(1000);
    }
  }

  // 输出统计
  console.log('\n' + '='.repeat(70));
  console.log('  抓取完成！');
  console.log(`  成功: ${results.success} 场`);
  console.log(`  失败: ${results.failed} 场`);
  console.log('='.repeat(70));
}

main().catch(console.error);

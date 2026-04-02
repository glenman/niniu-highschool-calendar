#!/usr/bin/env node

/**
 * 上海海港2024赛季比赛报告抓取脚本
 * 使用agent-browser从fbref.com抓取比赛数据
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const OUTPUT_DIR = path.join(__dirname, '../data/match_reports');
const CDP_PORT = 9222;
const DELAY_BETWEEN_MATCHES = 2000; // 每场比赛之间延迟2秒

// 2024赛季比赛列表
const MATCHES = [
  { date: '2024-03-01', home: 'Shanghai Port', away: 'Wuhan Three Towns', gf: 3, ga: 1 },
  { date: '2024-03-09', home: 'Zhejiang', away: 'Shanghai Port', gf: 0, ga: 0 },
  { date: '2024-03-30', home: 'Shanghai Port', away: 'Henan', gf: 3, ga: 1 },
  { date: '2024-04-05', home: 'Beijing Guoan', away: 'Shanghai Port', gf: 2, ga: 2 },
  { date: '2024-04-09', home: 'Nantong Zhiyun', away: 'Shanghai Port', gf: 3, ga: 0 },
  { date: '2024-04-14', home: 'Shanghai Port', away: 'Shandong Taishan', gf: 4, ga: 3 },
  { date: '2024-04-27', home: 'Shanghai Port', away: 'Shanghai Shenhua', gf: 1, ga: 1 },
  { date: '2024-05-01', home: 'Qingdao Hainiu', away: 'Shanghai Port', gf: 5, ga: 0 },
  { date: '2024-05-05', home: 'Shenzhen Peng City', away: 'Shanghai Port', gf: 6, ga: 0 },
  { date: '2024-05-10', home: 'Shanghai Port', away: 'Changchun Yatai', gf: 5, ga: 2 },
  { date: '2024-05-18', home: 'Qingdao West Coast', away: 'Shanghai Port', gf: 5, ga: 3 },
  { date: '2024-05-22', home: 'Shanghai Port', away: 'Chengdu Rongcheng', gf: 2, ga: 0 },
  { date: '2024-05-26', home: 'Shanghai Port', away: 'Cangzhou Lions', gf: 4, ga: 1 },
  { date: '2024-06-14', home: 'Jinmen Tiger', away: 'Shanghai Port', gf: 3, ga: 0 },
  { date: '2024-06-18', home: 'Meizhou Hakka', away: 'Shanghai Port', gf: 2, ga: 1 },
  { date: '2024-06-25', home: 'Wuhan Three Towns', away: 'Shanghai Port', gf: 2, ga: 0 },
  { date: '2024-06-29', home: 'Shanghai Port', away: 'Zhejiang', gf: 3, ga: 1 },
  { date: '2024-07-05', home: 'Henan', away: 'Shanghai Port', gf: 1, ga: 0 },
  { date: '2024-07-12', home: 'Shanghai Port', away: 'Beijing Guoan', gf: 5, ga: 1 },
  { date: '2024-07-21', home: 'Shanghai Port', away: 'Qingdao Hainiu', gf: 5, ga: 0 },
  { date: '2024-07-26', home: 'Shanghai Port', away: 'Nantong Zhiyun', gf: 8, ga: 1 },
  { date: '2024-08-03', home: 'Shandong Taishan', away: 'Shanghai Port', gf: 1, ga: 0 },
  { date: '2024-08-09', home: 'Shanghai Port', away: 'Meizhou Hakka', gf: 7, ga: 2 },
  { date: '2024-08-17', home: 'Shanghai Shenhua', away: 'Shanghai Port', gf: 1, ga: 3 },
  { date: '2024-09-13', home: 'Shanghai Port', away: 'Shenzhen Peng City', gf: 2, ga: 0 },
  { date: '2024-09-21', home: 'Changchun Yatai', away: 'Shanghai Port', gf: 4, ga: 3 },
  { date: '2024-09-28', home: 'Shanghai Port', away: 'Qingdao West Coast', gf: 2, ga: 1 },
  { date: '2024-10-18', home: 'Chengdu Rongcheng', away: 'Shanghai Port', gf: 1, ga: 3 },
  { date: '2024-10-27', home: 'Cangzhou Lions', away: 'Shanghai Port', gf: 1, ga: 0 },
  { date: '2024-11-02', home: 'Shanghai Port', away: 'Jinmen Tiger', gf: 5, ga: 0 }
];

// 创建输出目录
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * 执行agent-browser命令
 */
function browserCmd(cmd) {
  const fullCmd = `agent-browser --cdp ${CDP_PORT} ${cmd}`;
  try {
    return execSync(fullCmd, { encoding: 'utf-8', timeout: 30000 });
  } catch (error) {
    console.error(`Command failed: ${fullCmd}`);
    throw error;
  }
}

/**
 * 等待指定毫秒
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 从fbref页面抓取比赛报告数据
 */
async function scrapeMatchReport(matchIndex, match) {
  console.log(`\n[${matchIndex + 1}/${MATCHES.length}] 抓取 ${match.date} ${match.home} vs ${match.away}`);
  
  // 构建搜索URL
  const searchUrl = `https://fbref.com/en/search/search.fcgi?search=${encodeURIComponent(match.home + ' ' + match.away + ' ' + match.date)}`;
  
  try {
    // 打开比赛报告页面
    browserCmd(`open "${searchUrl}"`);
    await sleep(3000);
    
    // 等待页面加载
    browserCmd('wait --load networkidle --timeout 30000');
    
    // 获取页面快照
    const snapshot = browserCmd('snapshot -i --timeout 30000');
    
    // 从快照中提取Match Report链接
    const matchReportMatch = snapshot.match(/link "Match Report" \[ref=e(\d+)\]/);
    if (!matchReportMatch) {
      console.log('  未找到Match Report链接，跳过...');
      return null;
    }
    
    // 点击Match Report链接
    browserCmd(`click @e${matchReportMatch[1]}`);
    await sleep(3000);
    browserCmd('wait --load networkidle --timeout 30000');
    
    // 获取比赛报告页面内容
    const reportSnapshot = browserCmd('snapshot -i --timeout 30000');
    
    // 解析比赛数据
    const matchData = parseMatchReport(reportSnapshot, match);
    
    // 保存JSON文件
    const filename = `match_${match.date}_${matchIndex + 1}.json`;
    const filepath = path.join(OUTPUT_DIR, filename);
    fs.writeFileSync(filepath, JSON.stringify(matchData, null, 2));
    
    console.log(`  ✓ 已保存: ${filename}`);
    
    return matchData;
    
  } catch (error) {
    console.error(`  ✗ 抓取失败: ${error.message}`);
    return null;
  }
}

/**
 * 解析比赛报告页面数据
 */
function parseMatchReport(snapshot, matchInfo) {
  // 这里需要根据实际的fbref页面结构来解析数据
  // 由于fbref页面结构复杂，这里提供一个基础模板
  
  const isHome = matchInfo.home === 'Shanghai Port';
  
  return {
    match: {
      id: null,
      round: null,
      date: matchInfo.date,
      time: null,
      homeTeam: matchInfo.home,
      awayTeam: matchInfo.away,
      venue: null,
      city: null,
      result: `${matchInfo.gf}-${matchInfo.ga}`,
      status: '已结束',
      attendance: null,
      referee: null,
      weather: null,
      competition: '中国足球协会超级联赛',
      matchweek: null,
      season: '2024'
    },
    matchDetails: {
      stadiumCapacity: null,
      pitchCondition: null,
      temperature: null,
      kickoffTime: null,
      halftimeScore: null,
      fulltimeScore: `${matchInfo.gf}-${matchInfo.ga}`
    },
    officials: {
      referee: null,
      assistantReferee1: null,
      assistantReferee2: null,
      fourthOfficial: null,
      VAR: null
    },
    lineups: {
      home: {
        name: matchInfo.home,
        formation: null,
        manager: null,
        captain: null,
        players: []
      },
      away: {
        name: matchInfo.away,
        formation: null,
        manager: null,
        captain: null,
        players: []
      }
    },
    statistics: {
      possession: { home: null, away: null },
      shots: { home: null, away: null },
      shotsOnTarget: { home: null, away: null },
      corners: { home: null, away: null },
      fouls: { home: null, away: null },
      yellowCards: { home: null, away: null },
      redCards: { home: null, away: null }
    },
    timeline: [],
    rawSnapshot: snapshot.substring(0, 5000) // 保存部分原始数据用于调试
  };
}

/**
 * 主函数
 */
async function main() {
  console.log('='.repeat(60));
  console.log('上海海港2024赛季比赛报告抓取工具');
  console.log('='.repeat(60));
  console.log(`总计: ${MATCHES.length} 场比赛`);
  console.log(`输出目录: ${OUTPUT_DIR}`);
  console.log('='.repeat(60));
  
  // 检查Chrome连接
  try {
    browserCmd('snapshot');
    console.log('✓ Chrome CDP连接成功');
  } catch (error) {
    console.error('✗ 无法连接到Chrome，请确保Chrome已启动并开启远程调试端口9222');
    process.exit(1);
  }
  
  // 开始抓取
  const results = {
    success: 0,
    failed: 0,
    skipped: 0
  };
  
  for (let i = 0; i < MATCHES.length; i++) {
    const result = await scrapeMatchReport(i, MATCHES[i]);
    
    if (result) {
      results.success++;
    } else {
      results.failed++;
    }
    
    // 比场比赛之间延迟
    if (i < MATCHES.length - 1) {
      console.log(`  等待 ${DELAY_BETWEEN_MATCHES / 1000} 秒...`);
      await sleep(DELAY_BETWEEN_MATCHES);
    }
  }
  
  // 输出统计
  console.log('\n' + '='.repeat(60));
  console.log('抓取完成！');
  console.log(`成功: ${results.success}`);
  console.log(`失败: ${results.failed}`);
  console.log(`跳过: ${results.skipped}`);
  console.log('='.repeat(60));
}

// 运行主函数
main().catch(console.error);

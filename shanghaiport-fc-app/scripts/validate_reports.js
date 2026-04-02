#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 定义必需的字段结构
const requiredStructure = {
  match: ['id', 'round', 'date', 'homeTeam', 'awayTeam', 'result', 'venue', 'competition'],
  matchDetails: ['kickoffTime', 'halftimeScore', 'fulltimeScore'],
  officials: ['referee'],
  lineups: {
    home: ['name', 'formation', 'players', 'substitutes'],
    away: ['name', 'formation', 'players', 'substitutes']
  },
  detailedPlayerStats: ['home', 'away'],
  matchTimeline: [],
  tacticalAnalysis: ['homeFormation', 'awayFormation', 'possession'],
  statistics: [],
  keyMetrics: ['expectedGoals', 'bigChances'],
  playerRatings: ['manOfTheMatch', 'homeBestPlayer', 'awayBestPlayer'],
  headToHead: ['totalMatches'],
  socialMedia: ['hashtags', 'fanSentiment'],
  summary: [],
  keyFactors: [],
  highlights: [],
  matchAnalysis: ['tacticalSummary', 'teamPerformance'],
  postMatchComments: ['homeManager', 'awayManager'],
  nextMatches: ['home', 'away']
};

// 检查字段是否有实际内容
function hasContent(value, fieldName) {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') {
    // 排除"未知"、"待定"等占位符
    if (value.trim() === '' || value === '未知' || value === '待定') {
      return false;
    }
    return true;
  }
  if (typeof value === 'number') return true;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return true;
}

// 检查球员数据完整性
function checkPlayerData(players, team) {
  const issues = [];
  
  if (!players || players.length === 0) {
    issues.push(`${team}球员数据为空`);
    return issues;
  }

  players.forEach((player, index) => {
    const missingFields = [];
    
    if (!player.name || player.name.trim() === '') missingFields.push('姓名');
    if (!player.number && player.number !== 0) missingFields.push('号码');
    if (!player.position || player.position === '未知') missingFields.push('位置');
    if (player.minutes === undefined || player.minutes === null) missingFields.push('上场时间');
    
    if (missingFields.length > 0) {
      issues.push(`${team}球员${index + 1}(${player.name || '未命名'}): 缺少${missingFields.join(', ')}`);
    }
  });

  return issues;
}

// 检查单个比赛报告
function validateReport(filePath) {
  const report = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const issues = {
    critical: [],    // 严重问题
    warning: [],     // 警告
    info: []         // 信息
  };

  // 检查match基本信息
  const match = report.match;
  if (!match.homeTeam || match.homeTeam === '未知') {
    issues.critical.push('主队名称缺失');
  }
  if (!match.awayTeam || match.awayTeam === '未知') {
    issues.critical.push('客队名称缺失');
  }
  if (!match.date || match.date === '未知') {
    issues.critical.push('比赛日期缺失');
  }
  if (!match.result || match.result === '0-0') {
    issues.warning.push('比分为0-0或缺失');
  }
  if (!match.venue || match.venue === '未知') {
    issues.warning.push('场馆信息缺失');
  }
  if (!match.attendance || match.attendance === '未知') {
    issues.info.push('观众人数缺失');
  }
  if (!match.referee || match.referee === '未知' || match.referee === '') {
    issues.info.push('裁判信息缺失');
  }

  // 检查阵容数据
  if (!report.lineups || !report.lineups.home || !report.lineups.away) {
    issues.critical.push('阵容数据结构不完整');
  } else {
    // 检查主队球员
    const homePlayerIssues = checkPlayerData(report.lineups.home.players, '主队首发');
    issues.warning.push(...homePlayerIssues);
    
    // 检查客队球员
    const awayPlayerIssues = checkPlayerData(report.lineups.away.players, '客队首发');
    issues.warning.push(...awayPlayerIssues);
    
    // 检查首发人数
    if (report.lineups.home.players.length !== 11) {
      issues.warning.push(`主队首发人数不正确: ${report.lineups.home.players.length}人`);
    }
    if (report.lineups.away.players.length !== 11) {
      issues.warning.push(`客队首发人数不正确: ${report.lineups.away.players.length}人`);
    }
    
    // 检查替补
    if (report.lineups.home.substitutes.length === 0) {
      issues.info.push('主队无替补球员');
    }
    if (report.lineups.away.substitutes.length === 0) {
      issues.info.push('客队无替补球员');
    }
  }

  // 检查详细统计
  if (!report.detailedPlayerStats || 
      !report.detailedPlayerStats.home || 
      report.detailedPlayerStats.home.length === 0) {
    issues.warning.push('主队详细统计数据缺失');
  }
  if (!report.detailedPlayerStats || 
      !report.detailedPlayerStats.away || 
      report.detailedPlayerStats.away.length === 0) {
    issues.warning.push('客队详细统计数据缺失');
  }

  // 检查时间线
  if (!report.matchTimeline || report.matchTimeline.length === 0) {
    issues.info.push('比赛时间线数据缺失（进球、换人等事件）');
  }

  // 检查统计
  if (!report.statistics || report.statistics.length === 0) {
    issues.warning.push('比赛统计数据缺失');
  } else {
    const hasPossession = report.statistics.some(s => s.name === '控球率');
    if (!hasPossession) {
      issues.info.push('控球率数据缺失');
    }
  }

  // 检查战术分析
  if (!report.tacticalAnalysis || !report.tacticalAnalysis.possession) {
    issues.info.push('战术分析数据不完整');
  }

  return issues;
}

// 主函数
function main() {
  const reportsDir = './data/match_reports_final';
  const files = fs.readdirSync(reportsDir).filter(f => f.endsWith('.json'));

  console.log('='.repeat(80));
  console.log('比赛报告数据完整性检查');
  console.log('='.repeat(80));
  console.log(`检查时间: ${new Date().toLocaleString('zh-CN')}`);
  console.log(`检查文件数: ${files.length}个\n`);

  const allIssues = [];
  let totalCritical = 0;
  let totalWarning = 0;
  let totalInfo = 0;

  files.forEach(file => {
    const filePath = path.join(reportsDir, file);
    const issues = validateReport(filePath);
    
    const criticalCount = issues.critical.length;
    const warningCount = issues.warning.length;
    const infoCount = issues.info.length;
    
    totalCritical += criticalCount;
    totalWarning += warningCount;
    totalInfo += infoCount;

    if (criticalCount > 0 || warningCount > 0) {
      console.log(`\n📄 ${file}`);
      
      if (criticalCount > 0) {
        console.log(`  ❌ 严重问题 (${criticalCount}):`);
        issues.critical.forEach(issue => console.log(`     - ${issue}`));
      }
      
      if (warningCount > 0) {
        console.log(`  ⚠️  警告 (${warningCount}):`);
        issues.warning.slice(0, 5).forEach(issue => console.log(`     - ${issue}`));
        if (warningCount > 5) {
          console.log(`     ... 还有${warningCount - 5}个警告`);
        }
      }
      
      if (infoCount > 0) {
        console.log(`  ℹ️  信息 (${infoCount}):`);
        issues.info.forEach(issue => console.log(`     - ${issue}`));
      }
    }

    allIssues.push({
      file,
      critical: criticalCount,
      warning: warningCount,
      info: infoCount,
      issues
    });
  });

  // 汇总统计
  console.log('\n' + '='.repeat(80));
  console.log('数据完整性汇总');
  console.log('='.repeat(80));
  
  console.log(`\n总计:`);
  console.log(`  ❌ 严重问题: ${totalCritical}个`);
  console.log(`  ⚠️  警告: ${totalWarning}个`);
  console.log(`  ℹ️  信息: ${totalInfo}个`);

  // 完整性评分
  const maxScore = files.length * 100;
  const deductions = (totalCritical * 20) + (totalWarning * 5) + (totalInfo * 1);
  const score = Math.max(0, Math.min(100, 100 - (deductions / files.length)));
  
  console.log(`\n📊 数据完整性评分: ${score.toFixed(1)}/100`);
  
  if (score >= 90) {
    console.log('  评级: ⭐⭐⭐⭐⭐ 优秀');
  } else if (score >= 80) {
    console.log('  评级: ⭐⭐⭐⭐ 良好');
  } else if (score >= 70) {
    console.log('  评级: ⭐⭐⭐ 一般');
  } else if (score >= 60) {
    console.log('  评级: ⭐⭐ 较差');
  } else {
    console.log('  评级: ⭐ 差');
  }

  // 分类统计
  console.log('\n📁 按问题类型统计:');
  
  const problemTypes = {
    '球员数据': 0,
    '比分信息': 0,
    '场馆信息': 0,
    '统计数据': 0,
    '时间线': 0,
    '其他': 0
  };

  allIssues.forEach(item => {
    item.issues.warning.forEach(issue => {
      if (issue.includes('球员')) problemTypes['球员数据']++;
      else if (issue.includes('比分')) problemTypes['比分信息']++;
      else if (issue.includes('场馆')) problemTypes['场馆信息']++;
      else if (issue.includes('统计')) problemTypes['统计数据']++;
      else if (issue.includes('时间线')) problemTypes['时间线']++;
      else problemTypes['其他']++;
    });
  });

  Object.entries(problemTypes)
    .filter(([_, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .forEach(([type, count]) => {
      console.log(`  ${type}: ${count}个问题`);
    });

  // 完整文件列表
  const completeFiles = allIssues.filter(f => f.critical === 0 && f.warning === 0);
  if (completeFiles.length > 0) {
    console.log(`\n✅ 完全无问题的文件 (${completeFiles.length}个):`);
    completeFiles.forEach(f => console.log(`  - ${f.file}`));
  }

  console.log('\n' + '='.repeat(80));
  
  // 保存详细报告
  const reportPath = './data/data_quality_report.json';
  fs.writeFileSync(reportPath, JSON.stringify({
    checkTime: new Date().toISOString(),
    totalFiles: files.length,
    summary: {
      critical: totalCritical,
      warning: totalWarning,
      info: totalInfo,
      score
    },
    details: allIssues
  }, null, 2), 'utf8');
  
  console.log(`\n💾 详细报告已保存到: ${reportPath}`);
}

main();

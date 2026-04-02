#!/usr/bin/env node

/**
 * 从fbref.com提取上海海港某赛季的所有Match Report链接
 * 使用方法: node extract_match_urls.mjs <season>
 * 示例: node extract_match_urls.mjs 2026
 */

import http from 'http';
import fs from 'fs';

// Node.js >= 22 内置WebSocket
const WebSocket = globalThis.WebSocket;

const SEASON = process.argv[2] || '2026';
const TEAM_ID = 'c48512d3'; // 上海海港在fbref.com的team ID

console.log(`正在提取上海海港 ${SEASON} 赛季的Match Report链接...`);

// 步骤1: 获取CDP WebSocket URL
async function getWebSocketUrl() {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 9222,
            path: '/json',
            method: 'GET'
        };
        
        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    const pages = JSON.parse(data);
                    if (pages.length === 0) {
                        reject(new Error('没有找到活动的Chrome页面'));
                        return;
                    }
                    // 找到最后一个页面（最新打开的）
                    console.log(`   找到 ${pages.length} 个页面`);
                    resolve(pages[pages.length - 1].webSocketDebuggerUrl);
                } catch (err) {
                    reject(err);
                }
            });
        });
        
        req.on('error', reject);
        req.end();
    });
}

// 步骤2: 通过CDP提取Match Report链接
async function extractMatchUrls(wsUrl) {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(wsUrl);
        let messageId = 1;
        
        ws.addEventListener('open', () => {
            console.log('   WebSocket已连接');
            
            // JavaScript代码：提取所有Match Report链接
            const jsCode = `
                (function() {
                    const links = [];
                    const rows = document.querySelectorAll('table.stats_table tbody tr');
                    
                    rows.forEach(row => {
                        const dateCell = row.querySelector('th[data-stat="date"] a') || 
                                        row.querySelector('td[data-stat="date"] a');
                        const matchReportLink = Array.from(row.querySelectorAll('a')).find(
                            link => link.textContent.trim() === 'Match Report' &&
                                   link.href.includes('/matches/')
                        );
                        
                        if (dateCell && matchReportLink) {
                            links.push({
                                date: dateCell.textContent.trim(),
                                url: matchReportLink.href
                            });
                        }
                    });
                    
                    return links;
                })();
            `;
            
            // 执行JavaScript
            ws.send(JSON.stringify({
                id: messageId++,
                method: 'Runtime.evaluate',
                params: { 
                    expression: jsCode, 
                    returnByValue: true 
                }
            }));
        });
        
        ws.addEventListener('message', (event) => {
            try {
                const data = event.data;
                
                // 跳过空消息
                if (!data || data.trim() === '') {
                    return;
                }
                
                const response = JSON.parse(data);
                
                // 只处理我们请求的响应
                if (response.id === 1 && response.result && response.result.result) {
                    const value = response.result.result.value;
                    if (value) {
                        const matchData = JSON.parse(value);
                        ws.close();
                        resolve(matchData);
                    } else {
                        ws.close();
                        reject(new Error('未找到Match Report链接'));
                    }
                }
            } catch (err) {
                console.error('解析响应失败:', err.message);
            }
        });
        
        ws.addEventListener('error', (event) => {
            console.error('WebSocket错误:', event);
            reject(new Error('WebSocket连接失败'));
        });
        
        // 超时处理
        setTimeout(() => {
            ws.close();
            reject(new Error('提取超时'));
        }, 30000);
    });
}

// 步骤3: 生成JSON文件
function generateJson(matchData) {
    const output = {
        team: "Shanghai Port FC",
        team_cn: "上海海港",
        season: parseInt(SEASON),
        competition: "Chinese Super League (中超联赛)",
        data_source: "fbref.com",
        team_id: TEAM_ID,
        last_updated: new Date().toISOString().split('T')[0],
        total_matches: matchData.length,
        match_urls: matchData.map((item, index) => ({
            match_number: index + 1,
            date: item.date || `待确定`,
            match_report_url: item.url
        }))
    };
    
    return JSON.stringify(output, null, 2);
}

// 主函数
async function main() {
    try {
        console.log('1. 连接到Chrome DevTools...');
        const wsUrl = await getWebSocketUrl();
        console.log('   ✓ 已连接');
        
        console.log('2. 提取Match Report链接...');
        const matchData = await extractMatchUrls(wsUrl);
        console.log(`   ✓ 找到 ${matchData.length} 个Match Report链接`);
        
        if (matchData.length === 0) {
            console.log('   ⚠️  未找到任何Match Report链接');
            console.log('   提示: 可能是因为赛季刚开始，还没有完成的比赛');
        }
        
        console.log('3. 生成JSON文件...');
        const jsonOutput = generateJson(matchData);
        
        // 保存到文件
        const outputDir = 'data';
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const outputPath = `${outputDir}/${SEASON}-match_urls.json`;
        fs.writeFileSync(outputPath, jsonOutput, 'utf8');
        
        console.log(`   ✓ 已保存到: ${outputPath}`);
        console.log('\n完成！');
        
    } catch (err) {
        console.error('错误:', err.message);
        console.error('\n请确保:');
        console.error('1. Chrome已启动并开启了远程调试（端口9222）');
        console.error('2. 已使用agent-browser打开了fbref.com的赛季页面');
        console.error('3. 页面已完全加载');
        process.exit(1);
    }
}

main();

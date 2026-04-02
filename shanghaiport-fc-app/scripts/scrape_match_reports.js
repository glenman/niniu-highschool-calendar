const fs = require('fs');
const path = require('path');

// 2024赛季上海海港比赛列表（从fbref抓取）
const matches = [
  { date: '2024-03-01', opponent: 'Wuhan Three Towns', venue: 'Home', result: 'W 3-1', matchweek: 1 },
  { date: '2024-03-09', opponent: 'Zhejiang', venue: 'Away', result: 'D 0-0', matchweek: 2 },
  { date: '2024-03-30', opponent: 'Henan', venue: 'Home', result: 'W 3-1', matchweek: 3 },
  { date: '2024-04-05', opponent: 'Beijing Guoan', venue: 'Away', result: 'D 2-2', matchweek: 4 },
  { date: '2024-04-09', opponent: 'Nantong Zhiyun', venue: 'Away', result: 'W 3-0', matchweek: 5 },
  { date: '2024-04-14', opponent: 'Shandong Taishan', venue: 'Home', result: 'W 4-3', matchweek: 6 },
  { date: '2024-04-27', opponent: 'Shanghai Shenhua', venue: 'Home', result: 'D 1-1', matchweek: 8 },
  { date: '2024-05-01', opponent: 'Qingdao Hainiu', venue: 'Away', result: 'W 5-0', matchweek: 9 },
  { date: '2024-05-05', opponent: 'Shenzhen Peng City', venue: 'Away', result: 'W 6-0', matchweek: 10 },
  { date: '2024-05-10', opponent: 'Changchun Yatai', venue: 'Home', result: 'W 5-2', matchweek: 11 },
  { date: '2024-05-18', opponent: 'Qingdao West Coast', venue: 'Away', result: 'W 5-3', matchweek: 12 },
  { date: '2024-05-22', opponent: 'Chengdu Rongcheng', venue: 'Home', result: 'W 2-0', matchweek: 13 },
  { date: '2024-05-26', opponent: 'Cangzhou Lions', venue: 'Home', result: 'W 4-1', matchweek: 14 },
  { date: '2024-06-14', opponent: 'Jinmen Tiger', venue: 'Away', result: 'W 3-0', matchweek: 15 },
  { date: '2024-06-18', opponent: 'Meizhou Hakka', venue: 'Away', result: 'W 2-1', matchweek: 7 },
  { date: '2024-06-25', opponent: 'Wuhan Three Towns', venue: 'Away', result: 'W 2-0', matchweek: 16 },
  { date: '2024-06-29', opponent: 'Zhejiang', venue: 'Home', result: 'W 3-1', matchweek: 17 },
  { date: '2024-07-05', opponent: 'Henan', venue: 'Away', result: 'W 1-0', matchweek: 18 },
  { date: '2024-07-12', opponent: 'Beijing Guoan', venue: 'Home', result: 'W 5-1', matchweek: 19 },
  { date: '2024-07-21', opponent: 'Qingdao Hainiu', venue: 'Home', result: 'W 5-0', matchweek: 24 },
  { date: '2024-07-26', opponent: 'Nantong Zhiyun', venue: 'Home', result: 'W 8-1', matchweek: 20 },
  { date: '2024-08-03', opponent: 'Shandong Taishan', venue: 'Away', result: 'W 1-0', matchweek: 21 },
  { date: '2024-08-09', opponent: 'Meizhou Hakka', venue: 'Home', result: 'W 7-2', matchweek: 22 },
  { date: '2024-08-17', opponent: 'Shanghai Shenhua', venue: 'Away', result: 'L 1-3', matchweek: 23 },
  { date: '2024-09-13', opponent: 'Shenzhen Peng City', venue: 'Home', result: 'W 2-0', matchweek: 25 },
  { date: '2024-09-21', opponent: 'Changchun Yatai', venue: 'Away', result: 'W 4-3', matchweek: 26 },
  { date: '2024-09-28', opponent: 'Qingdao West Coast', venue: 'Home', result: 'W 2-1', matchweek: 27 },
  { date: '2024-10-18', opponent: 'Chengdu Rongcheng', venue: 'Away', result: 'L 1-3', matchweek: 28 },
  { date: '2024-10-27', opponent: 'Cangzhou Lions', venue: 'Away', result: 'W 1-0', matchweek: 29 },
  { date: '2024-11-02', opponent: 'Jinmen Tiger', venue: 'Home', result: 'W 5-0', matchweek: 30 }
];

// 生成比赛报告URL列表
const baseUrl = 'https://fbref.com/en/matches';
const matchUrls = matches.map(m => {
  const dateSlug = m.date;
  const teamsSlug = `${m.venue === 'Home' ? 'Shanghai-Port' : m.opponent.replace(/ /g, '-')}-${m.venue === 'Home' ? m.opponent.replace(/ /g, '-') : 'Shanghai-Port'}`;
  return {
    ...m,
    url: `${baseUrl}/${dateSlug}/${teamsSlug}`
  };
});

console.log('Match URLs to scrape:');
console.log(JSON.stringify(matchUrls, null, 2));

// 保存URL列表
fs.writeFileSync(
  path.join(__dirname, '../data/match_urls.json'),
  JSON.stringify(matchUrls, null, 2)
);

console.log(`\nSaved ${matchUrls.length} match URLs to data/match_urls.json`);

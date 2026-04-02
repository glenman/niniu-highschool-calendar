#!/usr/bin/env python3
"""
足球比赛数据处理工具
用于将网页数据转换为标准化的JSON格式，并导出到Excel
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import os


class MatchDataProcessor:
    """处理足球比赛数据"""
    
    def __init__(self, template_path: str = None):
        """初始化处理器"""
        if template_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(script_dir, "match-report.json")
        self.template_path = template_path
        self.template = self._load_template()
        
    def _load_template(self) -> Dict:
        """加载JSON模板"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  模板文件未找到: {self.template_path}")
            return {}
    
    def validate_match_data(self, data: Dict) -> tuple[bool, List[str]]:
        """验证比赛数据是否符合模板要求"""
        errors = []
        
        # 检查必需字段
        required_sections = ['match_info', 'teams', 'events', 'statistics']
        for section in required_sections:
            if section not in data:
                errors.append(f"缺少必需部分: {section}")
        
        # 检查比赛信息
        if 'match_info' in data:
            info = data['match_info']
            if 'date' not in info:
                errors.append("缺少比赛日期")
            if 'competition' not in info:
                errors.append("缺少赛事信息")
        
        # 检查球队信息
        if 'teams' in data:
            teams = data['teams']
            if 'home' not in teams or 'away' not in teams:
                errors.append("缺少主队或客队信息")
            else:
                for team_type in ['home', 'away']:
                    team = teams[team_type]
                    if 'name' not in team:
                        errors.append(f"缺少{team_type}队名称")
                    if 'score' not in team:
                        errors.append(f"缺少{team_type}队比分")
        
        # 检查事件格式
        if 'events' in data:
            for i, event in enumerate(data['events']):
                if 'minute' not in event:
                    errors.append(f"事件{i+1}缺少时间")
                if 'type' not in event:
                    errors.append(f"事件{i+1}缺少类型")
                if 'team' not in event:
                    errors.append(f"事件{i+1}缺少球队信息")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def create_excel_report(self, data: Dict, output_path: str = None) -> str:
        """将比赛数据导出到Excel"""
        if output_path is None:
            output_path = f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 工作表1: 比赛基本信息
            if 'match_info' in data:
                info_data = self._flatten_match_info(data['match_info'])
                df_info = pd.DataFrame([info_data])
                df_info.to_excel(writer, sheet_name='比赛信息', index=False)
            
            # 工作表2: 球队阵容
            if 'teams' in data:
                lineup_data = []
                for team_type in ['home', 'away']:
                    if team_type in data['teams']:
                        team = data['teams'][team_type]
                        if 'lineup' in team:
                            for player in team['lineup']:
                                player_copy = player.copy()
                                player_copy['球队'] = team['name']
                                player_copy['主客'] = '主场' if team_type == 'home' else '客场'
                                lineup_data.append(player_copy)
                
                if lineup_data:
                    df_lineup = pd.DataFrame(lineup_data)
                    df_lineup.to_excel(writer, sheet_name='球员阵容', index=False)
            
            # 工作表3: 比赛事件
            if 'events' in data and data['events']:
                df_events = pd.DataFrame(data['events'])
                df_events.to_excel(writer, sheet_name='比赛事件', index=False)
            
            # 工作表4: 统计数据
            if 'statistics' in data:
                stats_data = self._flatten_statistics(data['statistics'])
                df_stats = pd.DataFrame(stats_data)
                df_stats.to_excel(writer, sheet_name='统计数据', index=False)
            
            # 工作表5: 球员详细统计
            if 'player_stats' in data:
                all_player_stats = []
                for team_type in ['home', 'away']:
                    if team_type in data['player_stats']:
                        team_name = data['teams'][team_type]['name']
                        for player in data['player_stats'][team_type]:
                            player_copy = player.copy()
                            player_copy['球队'] = team_name
                            all_player_stats.append(player_copy)
                
                if all_player_stats:
                    df_player_stats = pd.DataFrame(all_player_stats)
                    df_player_stats.to_excel(writer, sheet_name='球员统计', index=False)
        
        print(f"✅ Excel报告已生成: {output_path}")
        return output_path
    
    def _flatten_match_info(self, match_info: Dict) -> Dict:
        """扁平化比赛信息"""
        flat = {}
        flat['日期'] = match_info.get('date', '')
        flat['时间'] = match_info.get('time', '')
        
        if 'competition' in match_info:
            flat['赛事'] = match_info['competition'].get('name', '')
            flat['赛季'] = match_info['competition'].get('season', '')
            flat['轮次'] = match_info['competition'].get('round', '')
        
        if 'venue' in match_info:
            flat['球场'] = match_info['venue'].get('name', '')
            flat['城市'] = match_info['venue'].get('city', '')
            flat['观众'] = match_info['venue'].get('attendance', '')
        
        if 'referee' in match_info:
            flat['裁判'] = match_info['referee'].get('name', '')
        
        return flat
    
    def _flatten_statistics(self, statistics: Dict) -> List[Dict]:
        """扁平化统计数据为对比格式"""
        stats_list = []
        
        for stat_name, stat_data in statistics.items():
            if isinstance(stat_data, dict) and 'home' in stat_data:
                stats_list.append({
                    '统计项目': self._translate_stat_name(stat_name),
                    '主队': stat_data['home'],
                    '客队': stat_data['away']
                })
        
        return stats_list
    
    def _translate_stat_name(self, name: str) -> str:
        """翻译统计项名称"""
        translations = {
            'possession': '控球率 (%)',
            'shots': '射门',
            'shots_on_target': '射正',
            'corners': '角球',
            'fouls': '犯规',
            'yellow_cards': '黄牌',
            'red_cards': '红牌',
            'offsides': '越位',
            'passes': '传球',
            'pass_accuracy': '传球成功率 (%)'
        }
        return translations.get(name, name)
    
    def create_empty_template(self) -> Dict:
        """创建空的数据模板，方便手动填写"""
        return {
            "match_info": {
                "match_id": "",
                "date": "YYYY-MM-DD",
                "time": "HH:MM",
                "competition": {
                    "name": "",
                    "season": "",
                    "round": ""
                },
                "venue": {
                    "name": "",
                    "city": "",
                    "capacity": 0,
                    "attendance": 0
                },
                "referee": {
                    "name": "",
                    "country": ""
                }
            },
            "teams": {
                "home": {
                    "name": "",
                    "full_name": "",
                    "score": 0,
                    "score_ht": 0,
                    "formation": "",
                    "coach": "",
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                },
                "away": {
                    "name": "",
                    "full_name": "",
                    "score": 0,
                    "score_ht": 0,
                    "formation": "",
                    "coach": "",
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                }
            },
            "events": [],
            "statistics": {
                "possession": {"home": 0, "away": 0},
                "shots": {"home": 0, "away": 0},
                "shots_on_target": {"home": 0, "away": 0},
                "corners": {"home": 0, "away": 0},
                "fouls": {"home": 0, "away": 0},
                "yellow_cards": {"home": 0, "away": 0},
                "red_cards": {"home": 0, "away": 0},
                "offsides": {"home": 0, "away": 0},
                "passes": {"home": 0, "away": 0},
                "pass_accuracy": {"home": 0, "away": 0}
            },
            "player_stats": {
                "home": [],
                "away": []
            },
            "metadata": {
                "source": "FBref",
                "url": "",
                "scraped_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }


def main():
    """示例使用"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_file = os.path.join(script_dir, "match-report.json")
    
    processor = MatchDataProcessor(template_file)
    
    # 创建空模板
    template = processor.create_empty_template()
    template_path = os.path.join(script_dir, "match_data_template.json")
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    print(f"✅ 已创建数据模板: {template_path}")
    
    # 示例：加载并验证数据
    # data_path = "your_match_data.json"
    # with open(data_path, 'r', encoding='utf-8') as f:
    #     match_data = json.load(f)
    # 
    # is_valid, errors = processor.validate_match_data(match_data)
    # if is_valid:
    #     print("✅ 数据验证通过")
    #     excel_path = processor.create_excel_report(match_data)
    # else:
    #     print("❌ 数据验证失败:")
    #     for error in errors:
    #         print(f"  - {error}")


if __name__ == "__main__":
    main()

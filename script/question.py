import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from collections import defaultdict
from bqyx_parser.config.persistent_state import load_last_version
from bqyx_parser.parser.xml_to_json import parse_xml_by_files, parser_xml_root

import json


def get_hero_skill_yes_and_no_question(hero_skill_files):
    '''
    仅仅用于答题
    获取 技能有哪些效果
    所有技能的效果汇总
    有两种问答方式，一种是有  一种是没有
    思路： 先遍历所有技能，记录所有技能和每个技能的效果
           再通过所有技能, 取完相反
    { 
        yes_dict: {
        '效果名': 有效的技能列表
        },
        no_dict:{
        '效果名': 无效的技能列表
        },
        effect_arr:[效果列表]
    }
    '''
    roots = parse_xml_by_files(
        hero_skill_files
    )
    yes_effect_dict = defaultdict(set)
    no_effect_dict = defaultdict(set)
    skills_set = set()

    for root in roots:
        # 先获取所有的yes_effect 获取了key 
        #获取了yes_effect_dict
        for skill in root.findall('skill'):
            effect = skill.find('effectInfoArr')
            if effect != None and effect.text:
                effects = effect.text.split(',')

                for effect in effects:
                    yes_effect_dict[effect].add(skill.find('cnName').text)
                    skills_set.add(skill.find('cnName').text)
    #遍历yes_effect 排出No_effect_dict
    for key,value in yes_effect_dict.items():
        no_effect_dict[key] = skills_set - value
   
    result = {
        'yes_dict':{key: list(value) for key, value  in yes_effect_dict.items()},
        'no_dict':{key: list(value) for key, value  in no_effect_dict.items()},
        'effect_arr':list(yes_effect_dict.keys())
    }
    return result
    

def in_skill_effect(effect: str, yes_b: bool) -> str:
    title = "以下哪个英雄技能"
    
    if "瞬间释放" in effect:
        title += ("有概率" if yes_b else "不会") + effect
    elif "伤害输出" in effect or "弹药消耗" in effect:
        title += ("可" if yes_b else "不可") + effect
    else:
        title += ("具有" if yes_b else "不具有") + effect
        title += "群体效果" if effect == "群体" else "的效果"
    
    return title

def question_daily(hero_skill_files,life_game_files):

    roots = parse_xml_by_files(
        life_game_files
    )
    q_ans_dict = {}
    #分类
    t1 = 'game_and_life'
    t2 = 'heroSkill_positive'
    t3 = 'heroSkill_negative'
    q_ans_dict[t1] = {}
    q_ans_dict[t2] = {}
    q_ans_dict[t3] = {}
    #game and life 问题
    for root in roots:
        for ask in root.findall('ask'):
            question = ask.find('title').text
            answers = [correct.text for correct in ask.findall('correct')]
            #添加
            q_ans_dict[t1][question] = answers
    # 英雄技能部分 表肯定 和 表否定
    yes_no_dict = get_hero_skill_yes_and_no_question(hero_skill_files)
    effect_arr = yes_no_dict['effect_arr']
    for effect in effect_arr:
        #表肯定的
        yes_question = in_skill_effect(effect,True)
        yes_ans = yes_no_dict['yes_dict'][effect]
        #否定的
        no_question = in_skill_effect(effect,False)
        no_ans = yes_no_dict['no_dict'][effect]
        #添加
        q_ans_dict[t2][yes_question] = yes_ans
        q_ans_dict[t3][no_question] = no_ans
    return q_ans_dict


if __name__ == "__main__":
    hero_skill_files = [
        Path(r'output\v3541\xml\father\skill\name\heroSkillLink.xml'),
        Path(r'output\v3541\xml\father\skill\name\heroSkill.xml')
    ]
    life_game_files = [
        Path(r'output\v3541\xml\father\ask\name\life.xml'),
        Path(r'output\v3541\xml\father\ask\name\other.xml')
    ]       
    version = load_last_version()
    xml_dir = Path('output', version,'xml','father','bullet')
    output_dir = Path('output') / version /'json' /'question'
    output_dir.mkdir(parents=True,exist_ok=True)
    result = question_daily(hero_skill_files,life_game_files)
    with open(output_dir / 'question.json' ,'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        

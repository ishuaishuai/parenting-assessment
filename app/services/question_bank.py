import os
import re
from typing import Dict, List
from app.config import get_settings

settings = get_settings()

AGE_BANDS = {
    "3-4": "幼儿园前",
    "5-6": "幼儿园",
    "7-8": "小学低年级",
    "9-10": "小学中年级",
    "11-12": "小学高年级",
}

DIMENSION_NAMES = {
    "DEV": "儿童发展状态",
    "REL": "亲子关系质量",
    "ENV": "家庭教养环境",
    "PAR": "父母状态与能力",
    "RISK": "问题风险筛查",
}

DIM_OPTIONS = {
    "DEV": [
        "1 - 明显落后 / 还做不到",
        "2 - 稍落后 / 偶尔能做到",
        "3 - 基本正常 / 和同龄孩子差不多",
        "4 - 发展良好 / 大部分能做到",
        "5 - 做得很好 / 明显超前",
    ],
    "REL": [
        "1 - 很少 / 从不",
        "2 - 偶尔 / 不多",
        "3 - 有时 / 一般",
        "4 - 经常 / 比较自然",
        "5 - 总是 / 非常自然",
    ],
    "ENV": [
        "1 - 完全没做到 / 很不理想",
        "2 - 偶尔做到 / 不太稳定",
        "3 - 基本做到 / 还行",
        "4 - 做得不错 / 比较稳定",
        "5 - 做得很好 / 家庭氛围理想",
    ],
    "PAR": [
        "1 - 完全不符合 / 很难做到",
        "2 - 不太符合 / 偶尔能做到",
        "3 - 一般 / 有时能做到",
        "4 - 比较符合 / 大部分能做到",
        "5 - 非常符合 / 已经成为习惯",
    ],
    "RISK": [
        "1 - 严重 / 非常频繁",
        "2 - 较明显 / 经常",
        "3 - 偶尔有 / 轻微",
        "4 - 很少 / 基本正常",
        "5 - 完全没有 / 从不",
    ],
}

SUBDIM_PREFIXES = [
    '认知发展','语言发展','情绪发展','社交发展','生活习惯','运动发展','感官发展',
    '情感连接','沟通质量','冲突处理','共同活动','教养信心','配合与独立','求助行为',
    '家庭结构','教养一致性','物理环境','家庭氛围','屏幕管理',
    '情绪管理','支持网络','身心状态','教育观念','自我关怀',
    '发展迟缓','行为问题','情绪障碍','社交障碍','感官问题',
]


def parse_question_bank(age_band: str) -> List[Dict]:
    filepath = os.path.join(settings.DATA_DIR, f"题库-{age_band}岁.md")
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    questions = []
    dim_sections = re.split(r'## 维度[一二三四五]：', content)
    for section in dim_sections[1:]:
        dim_match = re.search(r'^(.*?)[（\(]', section)
        if not dim_match:
            continue
        dim_name = dim_match.group(1).strip()
        dim_code = _dim_name_to_code(dim_name)
        q_blocks = re.split(r'#### 【', section)
        for block in q_blocks[1:]:
            lines = block.strip().split('\n')
            if not lines:
                continue
            header = lines[0].replace('】', '').strip()
            text_match = re.search(r'[·\s]([^·\s].*)', header)
            text = text_match.group(1).strip() if text_match else header.strip()
            text = text.strip('# ').strip()
            for prefix in SUBDIM_PREFIXES:
                if text.startswith(prefix):
                    text = text[len(prefix):].strip()
                    break
            options = []
            labels = []
            for line in lines:
                # Try to match option with semantic label
                opt_match = re.search(r'[□✓]\s*(.+?)\s*\|\s*`(.+?)`', line)
                if opt_match and '选项' not in line and '---' not in line:
                    opt_text = opt_match.group(1).strip()
                    label = opt_match.group(2).strip()
                    if opt_text and opt_text not in ['选项', '语义标签'] and not opt_text.startswith('---'):
                        options.append(opt_text)
                        labels.append(label)
                    continue
                # Fallback: match option without label
                opt_match = re.search(r'[□✓]\s*(.+?)(?:\||$)', line)
                if opt_match and '选项' not in line and '---' not in line:
                    opt_text = opt_match.group(1).strip()
                    if opt_text and opt_text not in ['选项', '语义标签'] and not opt_text.startswith('---'):
                        options.append(opt_text)
            if not options:
                for line in lines:
                    if line.strip().startswith('- ') or line.strip().startswith('* '):
                        opt_text = line.strip()[2:].strip()
                        if opt_text and len(opt_text) < 100:
                            options.append(opt_text)
            is_red_flag = '红旗' in block or 'rf' in block or 'critical' in block.lower()
            is_critical = 'critical' in block.lower() or '紧急' in block or '自杀' in text
            q = {
                "id": f"{dim_code}_{len([q for q in questions if q['dim'] == dim_code]) + 1:02d}",
                "dim": dim_code,
                "text": text,
                "options": options if options else ["是", "否", "不确定"],
                "band": age_band,
                "red_flag": is_red_flag,
                "critical": is_critical,
                "reversed": _is_reversed(labels),
            }
            questions.append(q)
    return questions


def _is_reversed(labels: List[str]) -> bool:
    """检测反向计分题：通过语义标签判断选项1是否为'好'、选项5是否为'差'"""
    if len(labels) < 5:
        return False
    label1 = labels[0].lower()
    label5 = labels[-1].lower()
    good_indicators = [
        '.high', '.normal', '.good', '.excellent', '.positive', '.strong',
        '.secure', '.adaptive', '.compliant', '.ahead', '.well_adapted',
        '.maintained', '.evolved', '.perceived', '.accepting', '.collaborative',
    ]
    bad_indicators = [
        '.low', '.poor', '.avoidant', '.resistant', '.severe', '.dysregulated',
        '.negative', '.weak', '.isolated', '.rejected', '.entitled', '.careless',
        '.uncontrolled', '.unaware', '.numb', '.burnout', '.defeated',
        '.self_harm', '.suicidal', '.very_low', '.declining', '.struggling',
        '.fragmented', '.disorganized', '.withdrawal', '.forgetful',
        '.irregular', '.external', '.poor_retention', '.error_prone',
        '.unclear', '.suppressed', '.insecure', '.mismatched', '.unresolved',
        '.selective', '.inconsistent', '.permissive', '.neglectful',
        '.given_up', '.anxious', '.defensive', '.self_blame', '.dismissive',
        '.overreactive', '.ruminating', '.none', '.ineffective', '.minimal',
        '.unstable', '.child_led', '.family_norm', '.guilt', '.stressed',
        '.volatile', '.separate', '.uncertain', '.play_based', '.academic',
        '.delay', '.oppositional', '.aggression', '.conduct', '.bullying',
        '.mutism', '.sensory', '.auditory', '.vision', '.speech', '.learning',
        '.reading', '.writing', '.math', '.attention', '.behavior', '.mood',
        '.outburst', '.school_refusal', '.difficult', '.delayed', '.sneaky',
        '.unknown', '.dissatisfied', '.disordered', '.intense', '.provocative',
        '.emotional', '.literal', '.sensitive', '.polarized', '.uninterested',
        '.vague', '.absent', '.pessimistic', '.dependent', '.procrastinating',
        '.apathetic', '.unstructured', '.distracted', '.hesitant', '.solitary',
        '.follower', '.dominant', '.casual', '.situational', '.adult_oriented',
        '.victimized', '.impulsive', '.explosive_recovery', '.rumination',
        '.distraction', '.behavioral_only', '.externalizing', '.partial',
        '.basic', '.variable', '.parent_led', '.conflictual', '.testing',
        '.disregard', '.lax', '.overprotective', '.poor_grip',
        '.scissor_difficulty', '.school_preferred', '.inhibited',
        '.multitasking', '.interrupting', '.pretending', '.impatient',
        '.prescriptive', '.avoidance', '.clear_attribution', '.independent',
        '.not_applicable', '.dedicated', '.shared', '.flexible', '.aspiring',
        '.scarce', '.digital', '.conditional', '.stressful', '.rejected',
        '.receptive', '.anxious_open', '.separated', '.ruminating',
        '.balanced', '.conformist', '.vague', '.frequent', '.absence',
        '.hesitant', '.ineffective', '.isolated', '.professional', '.limited',
        '.numb', '.child_renewing', '.independent', '.compliant', '.happy',
        '.achieving', '.present_focused', '.general', '.teacher_flag',
        '.self_esteem_impact', '.significant', '.persistent', '.recent',
        '.not_yet', '.shy', '.consistent', '.nonverbal', '.inverted',
        '.hypersensitive', '.hyposensitive', '.overreactive',
        '.function_impaired', '.filtering', '.processing', '.output',
        '.unchecked', '.noncompliant', '.chronic_lying', '.stealing',
        '.destructive', '.new_onset', '.voluntary', '.suicidal_ideation',
        '.ahead', '.specific', '.sudden', '.victim', '.aggressive',
        '.somatic', '.joking', '.once', '.repeated',
    ]
    is_good1 = any(g in label1 for g in good_indicators)
    is_bad5 = any(b in label5 for b in bad_indicators)
    is_bad1 = any(b in label1 for b in bad_indicators)
    is_good5 = any(g in label5 for g in good_indicators)
    if is_good1 and is_bad5:
        return True
    if is_bad1 and is_good5:
        return False
    return False
    label1 = labels[0].lower()
    label5 = labels[-1].lower()
    good_indicators = [
        '.high', '.normal', '.good', '.excellent', '.positive', '.strong',
        '.secure', '.adaptive', '.compliant', '.ahead', '.well_adapted',
    ]
    bad_indicators = [
        '.low', '.poor', '.avoidant', '.resistant', '.severe', '.dysregulated',
        '.negative', '.weak', '.isolated', '.rejected', '.entitled', '.careless',
        '.uncontrolled', '.unaware', '.numb', '.burnout', '.defeated',
        '.self_harm', '.suicidal', '.very_low', '.declining', '.struggling',
        '.fragmented', '.minimal', '.disorganized', '.resistant', '.explosive',
        '.withdrawal', '.forgetful', '.irregular', '.external', '.dysregulated',
        '.poor_retention', '.error_prone', '.unclear', '.avoidant', '.suppressed',
        '.insecure', '.mismatched', '.minimal', '.unresolved', '.parent_pride',
        '.selective', '.inconsistent', '.permissive', '.authoritarian',
        '.neglectful', '.given_up', '.anxious', '.defensive', '.self_blame',
        '.dismissive', '.overreactive', '.withdrawal', '.dysregulated',
        '.ruminating', '.unresolved', '.conformist', '.ruminating', '.none',
        '.unaware', '.ineffective', '.isolated', '.minimal', '.parent_led',
        '.open_conflict', '.suppressed', '.boundary_blur', '.exploiting',
        '.confused', '.sophisticated', '.unstable', '.minimal_parents',
        '.unresolved', '.suppressed', '.deliberate', '.independent',
        '.child_led', '.family_norm', '.guilt', '.stressed', '.negative',
        '.volatile', '.separate', '.rare', '.uncertain', '.ineffective',
        '.given_up', '.play_based', '.academic', '.conformist', '.permissive',
        '.authoritarian', '.neglectful', '.present_focused', '.delay',
        '.oppositional', '.aggression', '.conduct', '.anxiety', '.depression',
        '.social', '.bullying', '.mutism', '.sensory', '.auditory', '.motor',
        '.vision', '.speech', '.learning', '.reading', '.writing', '.math',
        '.attention', '.behavior', '.mood', '.outburst', '.integration',
        '.digital', '.opposite_sex', '.peer', '.struggling', '.specific',
        '.sudden', '.victim', '.aggressive', '.school_refusal', '.difficult',
        '.delayed', '.irregular', '.sneaky', '.uncontrolled', '.unknown',
        '.dissatisfied', '.disordered', '.intense', '.provocative',
        '.emotional', '.poor', '.literal', '.sensitive', '.polarized',
        '.uninterested', '.vague', '.absent', '.pessimistic', '.careless',
        '.dependent', '.disorganized', '.procrastinating', '.apathetic',
        '.unstructured', '.very_low', '.low', '.moderate', '.distracted',
        '.hesitant', '.solitary', '.follower', '.dominant', '.casual',
        '.situational', '.adult_oriented', '.isolated', '.victimized',
        '.avoidant', '.impulsive', '.explosive_recovery', '.rumination',
        '.distraction', '.behavioral_only', '.suppressed', '.dysregulated',
        '.externalizing', '.partial', '.basic', '.variable', '.avoidant',
        '.fragmented', '.poor_retention', '.unclear', '.disorganized',
        '.minimal', '.testing', '.oppositional', '.disregard', '.lax',
        '.inconsistent', '.overprotective', '.struggling', '.parent_led',
        '.conflictual', '.none', '.declining', '.resistant', '.forgetful',
        '.external', '.dysregulated', '.poor_grip', '.scissor_difficulty',
        '.school_preferred', '.inhibited', '.anxious', '.unstable',
        '.parent_dominant', '.child_inquiry', '.reciprocal', '.mismatched',
        '.minimal', '.multitasking', '.interrupting', '.pretending',
        '.impatient', '.open', '.avoidant', '.anxious', '.prescriptive',
        '.collaborative', '.authoritative', '.authoritarian', '.permissive',
        '.unresolved', '.parent_initiated', '.child_initiated',
        '.clear_attribution', '.avoidance', '.parent_pride', '.clear',
        '.overprotective', '.struggling', '.lax', '.inconsistent',
        '.aligned', '.moderate', '.conflictual', '.unaware', '.deliberate',
        '.independent', '.parent_led', '.open_conflict', '.suppressed',
        '.not_applicable', '.aware', '.exploiting', '.confused',
        '.sophisticated', '.dedicated', '.shared', '.flexible', '.unstable',
        '.aspiring', '.abundant', '.scarce', '.digital', '.unaware',
        '.structured', '.inconsistent', '.child_led', '.family_norm',
        '.guilt', '.positive', '.neutral', '.stressed', '.negative',
        '.volatile', '.structured', '.physical', '.rare', '.separate',
        '.aspiring', '.secure', '.conditional', '.stressful', '.uncertain',
        '.rejected', '.receptive', '.anxious_open', '.defensive',
        '.self_blame', '.dismissive', '.controlled', '.moderate',
        '.overreactive', '.withdrawal', '.dysregulated', '.aware_managed',
        '.aware_uncontrolled', '.unaware', '.separated', '.uncertain',
        '.fast', '.moderate', '.slow', '.ruminating', '.unresolved',
        '.play_based', '.balanced', '.academic', '.conformist', '.anxious',
        '.clear', '.uncertain', '.anxious', '.vague', '.frequent',
        '.occasional', '.rare', '.none', '.ruminating', '.permissive',
        '.authoritarian', '.absence', '.emotional', '.unaware', '.strong',
        '.hesitant', '.ineffective', '.isolated', '.professional',
        '.rich', '.moderate', '.family_only', '.limited', '.none',
        '.low', '.moderate', '.high', '.severe', '.child_renewing',
        '.low', '.moderate', '.high', '.severe', '.numb', '.positive',
        '.variable', '.negative', '.minimal', '.anxious', '.authoritative',
        '.authoritarian', '.permissive', '.neglectful', '.inconsistent',
        '.independent', '.compliant', '.happy', '.achieving',
        '.present_focused', '.partial', '.general', '.teacher_flag',
        '.self_esteem_impact', '.mild', '.significant', '.severe',
        '.persistent', '.recent', '.not_yet', '.shy', '.consistent',
        '.situational', '.nonverbal', '.mild', '.significant', '.inverted',
        '.uncertain', '.hypersensitive', '.hyposensitive', '.overreactive',
        '.function_impaired', '.filtering', '.processing', '.output',
        '.unchecked', '.noncompliant', '.mild', '.significant', '.severe',
        '.chronic_lying', '.stealing', '.destructive', '.mild', '.moderate',
        '.severe', '.new_onset', '.voluntary', '.mild', '.frequent',
        '.severe', '.suicidal_ideation', '.normal', '.ahead', '.struggling',
        '.significant', '.specific', '.sudden', '.mild', '.moderate',
        '.significant', '.severe', '.mild', '.frequent', '.severe',
        '.sudden', '.situational', '.somatic', '.joking', '.once',
        '.repeated', '.mild', '.moderate', '.severe', '.sudden',
        '.situational', '.mild', '.frequent', '.severe', '.sudden',
        '.moderate', '.severe', '.sudden', '.situational', '.somatic',
        '.joking', '.once', '.repeated', '.mild', '.moderate', '.severe',
        '.sudden', '.situational', '.somatic', '.joking', '.once',
        '.repeated', '.mild', '.moderate', '.severe', '.sudden',
        '.situational', '.somatic', '.joking', '.once', '.repeated',
        '.mild', '.moderate', '.severe', '.sudden', '.situational',
        '.somatic', '.joking', '.once', '.repeated', '.mild', '.moderate',
        '.severe', '.sudden', '.situational', '.somatic', '.joking',
        '.once', '.repeated', '.mild', '.moderate', '.severe', '.sudden',
        '.situational', '.somatic', '.joking', '.once', '.repeated',
    ]
    is_good1 = any(g in label1 for g in good_indicators)
    is_bad5 = any(b in label5 for b in bad_indicators)
    is_bad1 = any(b in label1 for b in bad_indicators)
    is_good5 = any(g in label5 for g in good_indicators)
    if is_good1 and is_bad5:
        return True
    if is_bad1 and is_good5:
        return False
    return False


def _dim_name_to_code(name: str) -> str:
    mapping = {
        "儿童发展状态": "DEV", "亲子关系质量": "REL", "家庭教养环境": "ENV",
        "父母状态与能力": "PAR", "问题风险筛查": "RISK",
    }
    for cn, code in mapping.items():
        if cn in name:
            return code
    return "DEV"


def get_questions(age_band: str, limit: int = 40) -> List[Dict]:
    questions = parse_question_bank(age_band)
    if not questions:
        return []
    dim_questions = {"DEV": [], "REL": [], "ENV": [], "PAR": [], "RISK": []}
    for q in questions:
        if q["dim"] in dim_questions:
            dim_questions[q["dim"]].append(q)
    dim_limits = {"DEV": 8, "REL": 10, "ENV": 6, "PAR": 8, "RISK": 8}
    selected = []
    for dim, limit_count in dim_limits.items():
        dim_qs = dim_questions.get(dim, [])
        red_qs = [q for q in dim_qs if q.get("red_flag")]
        normal_qs = [q for q in dim_qs if not q.get("red_flag")]
        picked = (red_qs + normal_qs)[:limit_count]
        selected.extend(picked)
    for i, q in enumerate(selected):
        q["id"] = f"{q['dim']}{i+1:02d}"
    return selected[:limit]

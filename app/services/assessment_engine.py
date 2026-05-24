#!/usr/bin/env python3
"""
Parenting Assessment Engine
Extracted from parenting-assessment-skill-v1.2 assessment_skill.py
"""

from datetime import datetime
from typing import Dict, List


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

DIM_DEEP_ANALYSIS = {
    "DEV": {
        "excellent": {
            "interpretation": "孩子的认知、语言、情绪、社交等各方面发展均衡且良好，在同龄人中处于中上水平。这表明您在日常陪伴中给予了足够的刺激和支持。",
            "strengths": ["发展均衡，无明显短板", "学习能力与好奇心旺盛", "情绪调节能力较好"],
            "concerns": [],
            "tips": ["继续保持高质量的亲子互动", "适当增加挑战性活动，维持学习动机", "关注孩子的兴趣方向，适度引导深耕"],
            "scripts": ["你刚才的想法真有趣，能再多告诉我一些吗？", "这个问题有点难，但我相信你可以试试看。"],
            "reflections": ["我是否给了孩子足够的自主探索空间？", "孩子的优势领域，我是否在无意识中忽视了？"],
        },
        "good": {
            "interpretation": "孩子整体发展正常，大部分能力符合该年龄段预期，个别领域有轻微波动。这是完全正常的，每个孩子的发展节奏不同。",
            "strengths": ["整体发展在正常轨道", "部分领域表现突出"],
            "concerns": ["个别发展领域可稍加关注"],
            "tips": ["针对稍弱领域，每天10分钟专项游戏", "多给孩子正面反馈，强化自信", "通过绘本、游戏等趣味方式补强"],
            "scripts": ["我们一起试试，做不好也没关系。", "你今天比昨天进步了，我注意到了！"],
            "reflections": ["我是否对孩子的某个弱项过度焦虑了？", "我有没有把'发展中的正常'当成了'问题'？"],
        },
        "attention": {
            "interpretation": "孩子在部分发展领域的表现低于同龄平均水平，可能需要更多有意识的引导和支持。好消息是，这个年龄段的孩子可塑性极强，及时的干预效果显著。",
            "strengths": ["仍有发展的基础和潜力"],
            "concerns": ["部分能力发展稍滞后", "可能需要调整教养方式或环境"],
            "tips": ["尽快与幼儿园老师沟通，了解孩子在集体中的表现", "每天固定15分钟专注陪伴，做针对性游戏", "如持续2个月无改善，建议咨询儿童发展专家"],
            "scripts": ["这道题有点难，我们一起想办法。", "我看到你在努力，这很重要。"],
            "reflections": ["我的教养方式是否无意中限制了孩子的发展？", "家庭环境是否提供了足够的发展刺激？"],
        },
        "urgent": {
            "interpretation": "孩子在多个发展领域明显落后于同龄预期，建议尽快寻求专业评估。请不要自责——越早发现问题，越早干预，效果越好。",
            "strengths": ["孩子仍有发展潜力"],
            "concerns": ["多项能力明显滞后", "可能影响入园/入学适应"],
            "tips": ["尽快预约儿童保健科或发育行为科评估", "记录孩子日常表现，为医生提供参考", "在此期间，保持耐心，多鼓励少批评"],
            "scripts": ["不管发生什么，爸爸妈妈都在你身边。", "我们一起慢慢来，一步一步来。"],
            "reflections": ["我是否因为忙碌而忽视了孩子的发展信号？", "家庭成员之间对孩子的期望是否一致？"],
        },
    },
    "REL": {
        "excellent": {
            "interpretation": "您和孩子的亲子关系质量很高，情感连接牢固，沟通顺畅。这是孩子心理健康的最重要基石。",
            "strengths": ["情感连接紧密", "沟通顺畅自然", "冲突修复能力强"],
            "concerns": [],
            "tips": ["继续保持这种高质量的互动", "随着孩子成长，逐步调整沟通方式", "把良好的关系模式延伸到家庭其他成员"],
            "scripts": ["我很喜欢听你讲这些。", "不管发生什么，你都可以告诉我。"],
            "reflections": ["这种良好的关系，是我有意识培养的还是自然形成的？", "我能否把这份耐心也给予伴侣和自己？"],
        },
        "good": {
            "interpretation": "亲子关系整体良好，大部分时候能够顺畅沟通和互动。偶尔的小摩擦是正常的，关键是有修复的能力。",
            "strengths": ["关系基础稳固", "有基本的安全感"],
            "concerns": ["偶尔沟通不畅或冲突后修复较慢"],
            "tips": ["每天增加10分钟'只听不说'的陪伴时间", "冲突后主动示好，示范修复过程", "减少说教比例，增加共情回应"],
            "scripts": ["我理解你现在很生气。", "我们一起想想怎么解决这个问题。"],
            "reflections": ["我是否在疲惫时对孩子失去了耐心？", "我的沟通方式是否受到了自己成长经历的影响？"],
        },
        "attention": {
            "interpretation": "亲子关系的某些方面值得留意。孩子可能感觉不到足够的情感支持，或者沟通中存在一些障碍。及时改善可以避免问题累积。",
            "strengths": ["仍有改善的空间和基础"],
            "concerns": ["情感连接有待加强", "沟通模式可能需要调整"],
            "tips": ["每天设定'专属亲子时间'，至少15分钟", "练习'先连接后纠正'：先回应情绪，再讨论行为", "减少批评和否定，增加描述性表扬"],
            "scripts": ["我知道你现在很难过，我在这里陪你。", "我看到你了，你很努力。"],
            "reflections": ["我是否把工作中的压力带给了孩子？", "我有没有在无意识中重复了父母对待我的方式？"],
        },
        "urgent": {
            "interpretation": "亲子关系质量较低，孩子可能缺乏安全感，情感需求未被充分满足。这会影响孩子的自信和社交能力，建议尽快调整。",
            "strengths": ["意识到问题就是改变的开始"],
            "concerns": ["情感连接薄弱", "孩子可能缺乏安全感", "长期可能影响心理健康"],
            "tips": ["立即减少批评和命令，增加拥抱和肯定", "寻求家庭咨询或亲子课程支持", "给自己减压，疲惫的父母很难给出高质量陪伴"],
            "scripts": ["对不起，我刚才太着急了。", "不管怎么样，爸爸妈妈都是爱你的。"],
            "reflections": ["我自己的原生家庭经历是否在影响我的养育方式？", "我是否需要先照顾好自己的情绪，才能更好地陪伴孩子？"],
        },
    },
    "ENV": {
        "excellent": {
            "interpretation": "家庭教养环境非常理想，规则清晰一致，氛围温暖安全。这样的环境是孩子健康成长的最佳土壤。",
            "strengths": ["规则清晰且一致", "家庭氛围温暖", "物理环境有利于成长"],
            "concerns": [],
            "tips": ["保持现有环境优势", "随着孩子成长，适时调整规则", "定期家庭会议，让孩子参与规则制定"],
            "scripts": ["我们家的规矩是为了保护你，因为我们爱你。", "你有什么想法，也可以告诉我们。"],
            "reflections": ["这种理想环境是所有家庭成员共同努力的结果吗？", "我是否注意到了每个家庭成员的需求？"],
        },
        "good": {
            "interpretation": "家庭环境整体不错，大部分方面能够满足孩子成长需要。小部分可以优化的地方，稍作调整即可。",
            "strengths": ["家庭基本功能完善", "孩子有安全感"],
            "concerns": ["个别方面可优化"],
            "tips": ["统一家庭成员间的教养规则", "减少环境中的干扰因素（如过多的屏幕时间）", "增加家庭共同活动的时间"],
            "scripts": ["我们家约好了，吃饭时不看手机。", "周末我们一起做点什么好呢？"],
            "reflections": ["家庭成员之间对孩子的规则是否一致？", "家庭氛围是否有时会被大人的情绪影响？"],
        },
        "attention": {
            "interpretation": "家庭教养环境有一些需要改善的地方。可能是规则不统一、氛围紧张、或物理环境不够理想。这些问题会影响孩子的安全感和行为表现。",
            "strengths": ["有改善的基础"],
            "concerns": ["规则可能不统一", "家庭氛围有待改善", "教养分工可能不清晰"],
            "tips": ["和主要照护人沟通，统一核心规则", "设立'家庭宁静时间'，减少冲突", "整理孩子的活动空间，减少干扰"],
            "scripts": ["爸爸妈妈商量好了，这件事我们这样处理。", "家里是安全的，你可以放心。"],
            "reflections": ["我是否把夫妻之间的矛盾带给了孩子？", "家里的规则是保护孩子，还是为了方便大人？"],
        },
        "urgent": {
            "interpretation": "家庭环境存在较明显的问题，可能包括频繁冲突、规则混乱、或缺乏稳定的照护。孩子需要一个安全、稳定的环境才能健康成长。",
            "strengths": ["意识到问题就是改善的第一步"],
            "concerns": ["家庭氛围可能紧张", "规则混乱或缺乏", "可能影响孩子的安全感"],
            "tips": ["优先稳定家庭情绪氛围，减少在孩子面前争吵", "明确核心规则，所有大人统一执行", "如有家庭暴力或严重冲突，请寻求专业帮助"],
            "scripts": ["大人之间的事，我们会处理好，不是你的错。", "这里永远是你的家，你是安全的。"],
            "reflections": ["我自己的婚姻/家庭问题是否在影响孩子？", "我是否有能力独自为孩子创造一个安全的环境？"],
        },
    },
    "PAR": {
        "excellent": {
            "interpretation": "您的父母状态非常好，情绪管理能力佳，有充足的育儿信心和支持网络。您为孩子提供了很好的榜样。",
            "strengths": ["情绪管理能力强", "育儿信心充足", "有良好支持网络"],
            "concerns": [],
            "tips": ["继续保持自我关怀", "分享您的经验，帮助其他家长", "在忙碌中也别忘了照顾自己"],
            "scripts": ["我需要先冷静一下，然后我们再来谈。", "我也在学习怎么做妈妈/爸爸。"],
            "reflections": ["我的好状态是持续的还是间歇的？", "我是否有意识地为自己充电？"],
        },
        "good": {
            "interpretation": "您的父母状态整体不错，大部分时候能够应对育儿挑战。偶尔的疲惫和焦虑是正常的，关键是有恢复的能力。",
            "strengths": ["基本能应对育儿挑战", "有一定的自我调节能力"],
            "concerns": ["偶有疲惫或焦虑", "支持网络可能需要加强"],
            "tips": ["每天给自己留10分钟独处时间", "找到一个可以倾诉的朋友或社群", "降低对自己的完美期待"],
            "scripts": ["我今天有点累，但我依然爱你。", "我也会有情绪，这很正常。"],
            "reflections": ["我是否对自己要求太高了？", "我有没有把育儿当成必须'满分'的任务？"],
        },
        "attention": {
            "interpretation": "您的父母状态需要关注。持续的疲惫、焦虑或孤立感会影响您对孩子的回应质量。照顾好自己，才能更好地照顾孩子。",
            "strengths": ["仍在坚持，没有放弃"],
            "concerns": ["可能长期疲惫或焦虑", "支持系统不足", "情绪可能影响到孩子"],
            "tips": ["立即寻求至少一个倾诉对象（朋友、伴侣、咨询师）", "每天强制休息30分钟，做让自己放松的事", "如有持续焦虑或抑郁，请寻求心理咨询"],
            "scripts": ["妈妈/爸爸现在需要休息一下，等会儿再来陪你。", "我正在学习怎么做得更好。"],
            "reflections": ["我是否把全部的自我价值都放在了'做父母'这件事上？", "我上一次真正放松是什么时候？"],
        },
        "urgent": {
            "interpretation": "您的父母状态令人担忧。长期的疲惫、焦虑或抑郁不仅伤害您自己，也会深刻影响孩子。请先照顾好自己。",
            "strengths": ["您仍然在努力，这已经很不容易"],
            "concerns": ["长期疲惫或情绪问题", "可能已影响日常功能", "亲子关系可能受到负面影响"],
            "tips": ["请务必寻求专业心理咨询或精神科帮助", "让其他家庭成员分担育儿责任", "这不是您的错，寻求帮助是勇敢的表现"],
            "scripts": ["对不起，妈妈/爸爸最近不太好，但我在努力。", "请你给我一点时间，我需要休息一下。"],
            "reflections": ["我自己的心理健康是否长期被忽视了？", "我是否因为害怕被评价而不敢寻求帮助？"],
        },
    },
    "RISK": {
        "excellent": {
            "interpretation": "风险筛查结果非常理想，未发现明显的行为或情绪风险信号。孩子目前处于健康的发展轨道上。",
            "strengths": ["无明显风险信号", "行为情绪发展正常"],
            "concerns": [],
            "tips": ["继续保持观察和陪伴", "了解该年龄段常见的发展特点，避免过度焦虑", "建立良好的沟通习惯，为青春期做准备"],
            "scripts": ["如果你有什么不开心的事，记得告诉我。", "我相信你能处理好。"],
            "reflections": ["我是否在'无问题'时也能保持高质量的陪伴？", "我是否了解孩子这个年龄段正常的发展波动？"],
        },
        "good": {
            "interpretation": "风险筛查基本正常，个别轻微信号可能是发展过程中的正常波动，持续观察即可。",
            "strengths": ["整体风险较低"],
            "concerns": ["个别轻微信号，可能是正常波动"],
            "tips": ["保持日常观察，记录变化", "多与孩子沟通，了解内心想法", "如有持续或加重，再做进一步评估"],
            "scripts": ["我注意到你最近好像有点不一样，想聊聊吗？", "不管发生什么，我都在。"],
            "reflections": ["这个'轻微信号'是新出现的还是一直存在的？", "我是否因为孩子的一点变化就过度紧张了？"],
        },
        "attention": {
            "interpretation": "风险筛查发现了一些值得关注的信号。虽然目前不构成紧急危机，但建议提高警惕，及时关注和引导。",
            "strengths": ["尚未构成紧急危机", "及时发现，有时间干预"],
            "concerns": ["存在行为或情绪风险信号", "可能需要调整教养方式或环境"],
            "tips": ["增加与孩子的深度沟通时间", "排查是否有学校/同伴/家庭方面的压力源", "如信号持续2周以上，建议咨询儿童心理专业人士"],
            "scripts": ["我注意到你最近好像不太开心，我想了解你。", "这不是你的错，我们一起想办法。"],
            "reflections": ["孩子的这些变化，是否与家庭环境的变化有关？", "我是否有足够的耐心去倾听孩子的心声？"],
        },
        "urgent": {
            "interpretation": "风险筛查发现多个明显信号，可能涉及行为问题、情绪障碍或发展迟缓。建议尽快寻求专业评估和干预。",
            "strengths": ["及时发现，可以尽早干预"],
            "concerns": ["多项风险信号明显", "可能影响孩子的身心健康和社会功能"],
            "tips": ["尽快预约儿童心理科或发育行为科", "不要自行诊断，专业评估是关键", "在此期间，保持耐心，避免责备，多陪伴"],
            "scripts": ["不管发生什么，我们都会陪着你。", "这不是你的错，我们会一起面对。"],
            "reflections": ["这些信号出现多久了？我是否忽视了早期的迹象？", "我是否需要调整自己的期望和教养方式？"],
        },
    },
}

DIM_CROSS_TIPS = {
    "DEV": "发展问题往往与亲子关系质量密切相关。建议同时加强情感连接，让孩子在有安全感的环境中更好地发展。",
    "REL": "亲子关系问题可能是家庭环境或父母状态的折射。建议检视家庭规则是否统一，以及您自身的情绪状态是否需要支持。",
    "ENV": "家庭环境问题常常源于父母间的教养分歧。建议家庭成员坐下来沟通，统一核心规则，减少孩子接收到的矛盾信息。",
    "PAR": "父母状态不佳时，很难维持高质量的亲子关系和理想的家庭环境。建议优先照顾好自己的身心健康，再谈育儿。",
    "RISK": "风险信号的出现往往是多重因素的结果。建议同时检视亲子关系、家庭环境和您自身的压力水平，综合改善。",
}

DIM_RESOURCES = {
    "DEV": [
        "《自驱型成长》—— 内在动机与自主能力培养",
        "《孩子的大脑》—— 脑科学与认知发展规律",
        "《如何培养孩子的社会能力》—— 社交与问题解决",
    ],
    "REL": [
        "《如何说孩子才会听》—— 亲子沟通核心技巧",
        "《P.E.T.父母效能训练》—— 非暴力冲突解决",
        "《正面管教》—— 和善而坚定的教养方式",
    ],
    "ENV": [
        "《打造让孩子自主学习的住宅》—— 家庭环境设计",
        "《家庭会伤人》—— 家庭系统与代际疗愈",
        "《有家可回》—— 营造安全温暖的家庭氛围",
    ],
    "PAR": [
        "《不成熟的父母》—— 理解父母自身成长课题",
        "《正念父母心》—— 父母情绪管理与自我关怀",
        "《被讨厌的勇气》—— 建立健康的亲子心理边界",
    ],
    "RISK": [
        "《孩子的挑战》—— 行为问题应对策略",
        "《守护孩子的心理健康》—— 心理危机识别与干预",
        "《校园欺凌防范指南》—— 安全保护与权益维护",
    ],
}


def _score_to_level(score: float) -> str:
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "attention"
    else:
        return "urgent"


def _level_to_cn(level: str) -> str:
    mapping = {"excellent": "优秀", "good": "良好", "attention": "需关注", "urgent": "需重点关注"}
    return mapping.get(level, "良好")


def _effective_score(q, raw_score: int) -> int:
    """处理反向计分题：将原始分数转换为有效分数"""
    if q.get("reversed"):
        return 6 - raw_score
    return raw_score


def calc_scores(questions, answers) -> Dict[str, float]:
    """计算各维度得分"""
    dim_scores = {"DEV": [], "REL": [], "ENV": [], "PAR": [], "RISK": []}

    for idx, score in answers.items():
        if idx < len(questions):
            dim = questions[idx]["dim"]
            if dim in dim_scores:
                effective = _effective_score(questions[idx], score)
                dim_scores[dim].append(effective)

    result = {}
    for dim, scores in dim_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            result[dim] = round((avg / 5.0) * 100, 1)
        else:
            result[dim] = 50.0

    return result


def detect_flags(questions, answers) -> List[Dict]:
    """检测红旗"""
    flags = []
    for idx, score in answers.items():
        if idx < len(questions):
            q = questions[idx]
            effective = _effective_score(q, score)
            if q.get("red_flag") and effective <= 2:
                flags.append({
                    "question": q["text"][:50],
                    "dim": DIMENSION_NAMES.get(q["dim"], q["dim"]),
                    "score": effective,
                    "critical": q.get("critical", False),
                })
    return flags


def _dynamic_book_list(scores: Dict[str, float]) -> List[str]:
    """动态书单：按弱项维度推荐"""
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    picked = []
    for dim, score in sorted_scores:
        if dim in DIM_RESOURCES and DIM_RESOURCES[dim]:
            count = 2 if score < 50 else 1
            for book in DIM_RESOURCES[dim][:count]:
                if book not in picked:
                    picked.append(book)
                    if len(picked) >= 5:
                        break
        if len(picked) >= 5:
            break

    return picked if picked else [
        "《如何说孩子才会听》—— 亲子沟通核心技巧",
        "《正面管教》—— 和善而坚定的教养方式",
    ]


def _generate_priority_actions(lowest_dim: str, scores: Dict[str, float]) -> Dict:
    """生成映射到弱项维度的优先行动建议"""

    # 按得分排序，获取所有需要关注的维度（<80分）
    weak_dims = [(d, s) for d, s in sorted(scores.items(), key=lambda x: x[1]) if s < 80]

    recs = {
        "immediate": [],
        "short_term": [],
        "long_term": [],
        "resources": [],
    }

    # 即刻行动：聚焦最低维度，给3条具体建议
    immediate_map = {
        "DEV": [
            "从今天开始，每天固定15分钟陪孩子做专注类游戏（拼图、串珠、涂色）",
            "减少环境中的干扰物，为孩子创造安静的活动空间",
            "用描述性语言代替评价：'你把红色积木放在了蓝色上面'而不是'你真棒'",
        ],
        "REL": [
            "从今天开始，每天至少10分钟'只听不说'，让孩子主导话题",
            "发生冲突时，先蹲下来看着孩子的眼睛说'我知道你现在很难过'",
            "睡前给孩子一个拥抱，并说'今天有你真好'",
        ],
        "ENV": [
            "今天就和主要照护人沟通，统一一项核心规则（如屏幕时间、 bedtime）",
            "整理孩子的活动空间，确保有安全、专属的游戏角落",
            "设立'家庭共餐时间'，每天至少一餐全家人一起吃",
        ],
        "PAR": [
            "今天开始记录自己的情绪触发点，发现什么情境最容易让你失控",
            "每天强制给自己30分钟独处时间，哪怕是散步或喝咖啡",
            "找一个信任的人倾诉，不要独自承受所有育儿压力",
        ],
        "RISK": [
            "从今天起密切观察孩子的行为变化，每天记录5分钟",
            "增加与孩子的深度沟通时间，了解TA的内心想法",
            "如信号持续存在，尽快预约儿童心理科或发育行为科",
        ],
    }
    recs["immediate"] = immediate_map.get(lowest_dim, immediate_map["DEV"])

    # 本周聚焦：关注第二、第三弱的维度
    week_actions = []
    if len(weak_dims) >= 2:
        second_dim = weak_dims[1][0]
        week_map = {
            "DEV": "本周每天做一项促进认知或语言发展的活动（读绘本、数数游戏、形状配对）",
            "REL": "本周尝试'特别时光'：每天15分钟完全属于孩子的时间，TA选活动",
            "ENV": "本周召开一次家庭会议，让孩子也参与讨论一条家规",
            "PAR": "本周找一位朋友或加入家长社群，建立你的支持网络",
            "RISK": "本周排查孩子是否有压力源（学校、同伴、家庭变化），并与老师沟通",
        }
        week_actions.append(week_map.get(second_dim, ""))
    if len(weak_dims) >= 3:
        week_actions.append("本周观察另外两项维度的变化，记录进步")
    week_actions.extend(["每天记录一个孩子的积极行为", "和家庭成员同步本周调整计划"])
    recs["short_term"] = [a for a in week_actions if a][:3]

    # 本月目标：长期规划
    recs["long_term"] = [
        f"本月重点巩固{DIMENSION_NAMES.get(lowest_dim, lowest_dim)}的改善成果",
        "根据孩子的发展阶段，调整期望和策略",
        "持续学习相关育儿知识，推荐书单见下文",
    ]

    # 动态书单
    recs["resources"] = _dynamic_book_list(scores)

    return recs


def _generate_environment_advice(scores: Dict[str, float]) -> str:
    """生成环境调整建议"""
    env_score = scores.get("ENV", 50)
    par_score = scores.get("PAR", 50)

    if env_score >= 80 and par_score >= 60:
        return "当前家庭环境和父母状态都很好。建议保持现有模式，同时随着孩子成长适时调整规则。"
    elif env_score < 60 and par_score < 60:
        return "家庭环境和父母状态都需要关注。建议优先改善家庭情绪氛围，减少冲突；同时父母要关注自身身心健康，必要时寻求支持。"
    elif env_score < 60:
        return "家庭环境有待改善。建议家庭成员统一教养规则，减少在孩子面前的争吵，为孩子创造稳定、安全的成长空间。"
    elif par_score < 60:
        return "您的状态需要关注。建议优先照顾自己，每天留出专属休息时间，找到倾诉对象。只有您状态好了，家庭环境才会真正改善。"
    else:
        return "整体环境尚可。建议继续保持，并关注细节优化，如减少屏幕时间、增加家庭共同活动等。"


def generate_report(age_band, questions, answers):
    """生成深度评估报告"""
    scores = calc_scores(questions, answers)
    flags = detect_flags(questions, answers)
    sorted_dims = sorted(scores.items(), key=lambda x: x[1])

    # === 1. 维度深度分析 ===
    dimension_analysis = {}
    for dim, score in scores.items():
        level = _score_to_level(score)
        dim_name = DIMENSION_NAMES.get(dim, dim)
        analysis = DIM_DEEP_ANALYSIS.get(dim, {}).get(level, {})

        dimension_analysis[dim] = {
            "dim_code": dim,
            "dim_name": dim_name,
            "score": score,
            "level": _level_to_cn(level),
            "level_code": level,
            "interpretation": analysis.get("interpretation", ""),
            "strengths": analysis.get("strengths", []),
            "concerns": analysis.get("concerns", []),
            "development_tips": analysis.get("tips", []),
            "scripts": analysis.get("scripts", []),
            "reflections": analysis.get("reflections", []),
        }

    # === 2. 整体摘要 ===
    avg_score = round(sum(scores.values()) / len(scores), 1) if scores else 50
    lowest_dim = sorted_dims[0][0]
    lowest_score = sorted_dims[0][1]
    lowest_name = DIMENSION_NAMES.get(lowest_dim, lowest_dim)

    if avg_score >= 80:
        summary = f"整体评估结果优秀（{avg_score}分）。孩子在五个维度上发展均衡，尤其在{dimension_analysis[sorted_dims[-1][0]]['dim_name']}方面表现突出。继续保持即可。"
    elif avg_score >= 60:
        summary = f"整体评估结果良好（{avg_score}分）。{lowest_name}得分{lowest_score}分，是需要重点留意的领域。通过针对性调整，仍有较大提升空间。"
    elif avg_score >= 40:
        summary = f"整体评估结果需关注（{avg_score}分）。{lowest_name}得分{lowest_score}分，建议优先关注。及早干预可以带来显著改善。"
    else:
        summary = f"整体评估结果需重点关注（{avg_score}分）。多个领域需要优先改善，建议尽快寻求专业支持。发现问题就是改善的第一步。"

    # === 3. 维度间关联分析 ===
    cross_analysis = DIM_CROSS_TIPS.get(lowest_dim, "")

    # === 4. 风险分析 ===
    risk_analysis = {
        "risk_count": len(flags),
        "critical_count": sum(1 for f in flags if f.get("critical")),
        "has_risk": len(flags) > 0,
        "analysis": "",
    }
    if risk_analysis["critical_count"] > 0:
        risk_analysis["analysis"] = f"发现{risk_analysis['critical_count']}个严重风险信号，建议立即寻求专业帮助。"
    elif risk_analysis["risk_count"] > 0:
        risk_analysis["analysis"] = f"发现{risk_analysis['risk_count']}个需要关注的信号，建议提高警惕并及时跟进。"
    else:
        risk_analysis["analysis"] = "未发现明显风险信号，孩子目前处于健康的发展轨道上。"

    # === 5. 优先行动建议（映射到弱项维度） ===
    recs = _generate_priority_actions(lowest_dim, scores)

    # === 6. 环境建议 ===
    environment = _generate_environment_advice(scores)

    # === 7. 诊断衔接 ===
    links = []
    for dim, score in scores.items():
        if score < 40:
            links.append({
                "trigger": f"{DIMENSION_NAMES.get(dim, dim)}得分低于40",
                "action": "建议进入诊断Skill做深度分析"
            })
    critical_flags = [f for f in flags if f.get("critical")]
    if critical_flags:
        links.append({
            "trigger": f"触发{len(critical_flags)}个严重红旗信号",
            "action": "建议立即寻求专业帮助",
            "priority": "urgent"
        })

    return {
        "meta": {
            "band": age_band,
            "name": AGE_BANDS.get(age_band, ""),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_questions": len(questions),
            "answered": len(answers),
            "overall_score": avg_score,
        },
        "summary": summary,
        "scores": scores,
        "dimension_analysis": dimension_analysis,
        "risk_analysis": risk_analysis,
        "cross_analysis": cross_analysis,
        "priority_actions": recs,
        "environment": environment,
        "flags": flags,
        "diagnosis_links": links,
    }

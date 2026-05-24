import os
import json
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape

DIM_CONFIG = {
    "DEV": {"name": "儿童发展", "icon": "🧒", "icon_bg": "#e3f2fd", "color": "#42a5f5", "layer": "个体层"},
    "REL": {"name": "亲子关系", "icon": "💞", "icon_bg": "#fce4ec", "color": "#ef5350", "layer": "关系层"},
    "ENV": {"name": "家庭环境", "icon": "🏠", "icon_bg": "#e8f5e9", "color": "#66bb6a", "layer": "环境层"},
    "PAR": {"name": "父母状态", "icon": "👤", "icon_bg": "#fff3e0", "color": "#ef5350", "layer": "个体层"},
    "RISK": {"name": "风险筛查", "icon": "🛡️", "icon_bg": "#f3e5f5", "color": "#ab47bc", "layer": "环境层"},
}
RADAR_ORDER = ["DEV", "REL", "ENV", "PAR", "RISK"]


def _build_affirmation(overall: float) -> Dict[str, str]:
    if overall >= 70:
        return {"highlight": "您的孩子整体发展良好", "body": "在同龄人中处于中等偏上水平。评估显示您已具备较好的养育基础。"}
    elif overall >= 50:
        return {"highlight": "您的孩子发展平稳", "body": "与同龄人相比处于平均水平。评估发现了几个值得关注的领域，好消息是：这些都是可以通过小步调整来改善的。"}
    else:
        return {"highlight": "您很重视孩子的成长", "body": "这次评估帮助您识别了一些需要优先关注的领域。请不要焦虑——发现问题就是改善的第一步。"}


def _build_score_summary(dim_analysis: Dict) -> str:
    counts = {"优秀": 0, "良好": 0, "需关注": 0, "需重点关注": 0}
    for item in dim_analysis.values():
        counts[item.get("level", "良好")] = counts.get(item.get("level", "良好"), 0) + 1
    lines = []
    good_count = counts.get("优秀", 0) + counts.get("良好", 0)
    if good_count > 0:
        good_dims = [item["dim_name"] for item in dim_analysis.values() if item.get("level") in ["优秀", "良好"]]
        lines.append(f'<div class="item"><span class="pill pill-green">{good_count}项良好</span><span>{"、".join(good_dims[:2])}{"等" if len(good_dims) > 2 else ""}</span></div>')
    if counts.get("需关注", 0) > 0:
        warn_dims = [item["dim_name"] for item in dim_analysis.values() if item.get("level") == "需关注"]
        lines.append(f'<div class="item"><span class="pill pill-orange">{counts["需关注"]}项需关注</span><span>{"、".join(warn_dims)}</span></div>')
    if counts.get("需重点关注", 0) > 0:
        danger_dims = [item["dim_name"] for item in dim_analysis.values() if item.get("level") == "需重点关注"]
        lines.append(f'<div class="item"><span class="pill pill-red">{counts["需重点关注"]}项重点关注</span><span>{"、".join(danger_dims)}</span></div>')
    return "\n".join(lines) if lines else '<div class="item"><span class="pill pill-green">各项平稳</span></div>'


def _build_radar_data(scores: Dict) -> str:
    data = {}
    for d in RADAR_ORDER:
        conf = DIM_CONFIG.get(d, {})
        data[conf.get("name", d)] = {
            "score": scores.get(d, 50),
            "percentile": round(scores.get(d, 50)),
            "level": "良好",
            "color": conf.get("color", "#667eea"),
            "layer": conf.get("layer", ""),
            "trend": "flat",
            "trendText": "首次评估"
        }
    return json.dumps(data, ensure_ascii=False)


def _build_dim_list(scores: Dict, dim_analysis: Dict) -> str:
    items = []
    for d in RADAR_ORDER:
        conf = DIM_CONFIG.get(d, {})
        score = scores.get(d, 50)
        analysis = dim_analysis.get(d, {})
        items.append({
            "code": d, "name": conf.get("name", d), "icon": conf.get("icon", "📊"),
            "icon_bg": conf.get("icon_bg", "#e3f2fd"), "color": conf.get("color", "#667eea"),
            "layer": conf.get("layer", ""), "score": score,
            "percentile": round(score), "level": analysis.get("level", "良好"),
        })
    items.sort(key=lambda x: x["score"])
    html = ""
    for item in items:
        html += f'<div class="dim-row">'
        html += f'<div class="dim-icon" style="background:{item["icon_bg"]};">{item["icon"]}</div>'
        html += f'<div class="dim-info">'
        html += f'<div class="dim-name"><span>{item["name"]}</span><span class="percentile">{item["percentile"]}% 同龄</span></div>'
        html += f'<div class="dim-bar-wrap"><div class="dim-bar" style="width:0%;background:{item["color"]};" data-target="{item["percentile"]}"></div></div>'
        html += f'<div class="dim-footer"><span>{item["level"]}</span><span>· {item["layer"]}</span></div>'
        html += f'</div></div>'
    return html


def _build_dim_detail(dim_analysis: Dict) -> str:
    html = ""
    for d in RADAR_ORDER:
        analysis = dim_analysis.get(d, {})
        if not analysis:
            continue
        conf = DIM_CONFIG.get(d, {})
        score = analysis.get("score", 50)
        level = analysis.get("level", "")
        html += f'<div class="detail-card" style="border-left:4px solid {conf.get("color", "#ccc")};">'
        html += f'<div class="detail-header">'
        html += f'<span class="detail-icon">{conf.get("icon", "")}</span>'
        html += f'<span class="detail-name">{analysis.get("dim_name", "")}</span>'
        html += f'<span class="detail-score" style="color:{conf.get("color", "#333")};">{score}分 · {level}</span>'
        html += f'</div>'
        html += f'<div class="detail-section"><div class="section-title">💡 深度解读</div><p>{analysis.get("interpretation", "")}</p></div>'
        for section_key, title in [("strengths", "✅ 优势"), ("concerns", "⚠️ 关注点"), ("development_tips", "🎯 发展建议"), ("reflections", "🤔 家长反思")]:
            items = analysis.get(section_key, [])
            if items:
                html += f'<div class="detail-section"><div class="section-title">{title}</div><ul>'
                for s in items:
                    html += f'<li>{s}</li>'
                html += f'</ul></div>'
        scripts = analysis.get("scripts", [])
        if scripts:
            html += f'<div class="detail-section"><div class="section-title">💬 推荐话术</div>'
            for s in scripts:
                html += f'<div class="script-box">"{s}"</div>'
            html += f'</div>'
        html += f'</div>'
    return html


def _build_flag_list(flags: List[Dict]) -> str:
    if not flags:
        return '<div style="text-align:center;color:#2e7d32;padding:16px;font-size:14px;">✅ 未发现明显风险信号，继续保持！</div>'
    html = ""
    for flag in flags:
        icon = "🔴" if flag.get("critical") else "🟡"
        html += f'<div class="flag-item">'
        html += f'<div class="flag-icon">{icon}</div>'
        html += f'<div class="flag-body">'
        html += f'<div class="flag-text">{flag.get("question", "")}</div>'
        html += f'<div class="flag-meta">所属维度：{flag.get("dim", "")}</div>'
        html += f'</div></div>'
    return html


def _build_flag_cta(flags: List[Dict]) -> str:
    if not flags:
        return ""
    return '<div class="flag-cta"><div class="cta-text">部分信号建议进一步深度诊断</div><a href="#" class="cta-btn">🔍 进入 AI 深度诊断</a></div>'


def _build_advice_list(actions: List[str]) -> str:
    if not actions:
        return '<div style="padding:10px;color:#888;font-size:13px;">暂无具体建议</div>'
    html = ""
    for action in actions:
        html += f'<div class="advice-item"><div class="advice-dot"></div><div class="advice-text">{action}</div></div>'
    return html


def _build_resource_list(resources: List[str]) -> str:
    html = ""
    for r in resources:
        parts = r.split("——") if "——" in r else [r, ""]
        title = parts[0].strip()
        subtitle = parts[1].strip() if len(parts) > 1 else ""
        html += f'<div class="res-item"><div class="res-icon">📖</div><div class="res-body"><div class="title">{title}</div><div class="subtitle">{subtitle}</div></div><div class="res-arrow">›</div></div>'
    return html


def generate_html_report(report_data: Dict[str, Any]) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")

    scores = report_data.get("scores", {})
    dim_analysis = report_data.get("dimension_analysis", {})
    meta = report_data.get("meta", {})
    flags = report_data.get("flags", [])
    actions = report_data.get("priority_actions", {})
    overall = meta.get("overall_score", 50)
    affirmation = _build_affirmation(overall)

    context = {
        "BAND": meta.get("band", ""),
        "BAND_LABEL": meta.get("name", ""),
        "DATE": meta.get("date", ""),
        "OVERALL_SCORE": overall,
        "AFFIRMATION_HIGHLIGHT": affirmation["highlight"],
        "AFFIRMATION_BODY": affirmation["body"],
        "SUMMARY": report_data.get("summary", ""),
        "SCORE_SUMMARY": _build_score_summary(dim_analysis),
        "RADAR_DATA": _build_radar_data(scores),
        "RADAR_VALUES": ",".join([str(scores.get(d, 50)) for d in RADAR_ORDER]),
        "DIM_LIST": _build_dim_list(scores, dim_analysis),
        "DIM_DETAIL": _build_dim_detail(dim_analysis),
        "FLAG_TITLE": "需要关注的信号" if flags else "风险筛查结果",
        "FLAG_COUNT": len(flags),
        "FLAG_LIST": _build_flag_list(flags),
        "FLAG_CTA": _build_flag_cta(flags),
        "RISK_ANALYSIS": report_data.get("risk_analysis", {}).get("analysis", ""),
        "CROSS_ANALYSIS": report_data.get("cross_analysis", ""),
        "ENVIRONMENT": report_data.get("environment", ""),
        "TODAY_ACTIONS": _build_advice_list(actions.get("immediate", [])),
        "WEEK_ACTIONS": _build_advice_list(actions.get("short_term", [])),
        "MONTH_ACTIONS": _build_advice_list(actions.get("long_term", [])),
        "RESOURCE_LIST": _build_resource_list(actions.get("resources", [])),
        "FLAGS_JS_ARRAY": json.dumps([{"text": f.get("question", ""), "dim": f.get("dim", ""), "critical": f.get("critical", False)} for f in flags], ensure_ascii=False),
        "TODAY_JS_ARRAY": json.dumps(actions.get("immediate", [])[:3], ensure_ascii=False),
        "WEEK_JS_ARRAY": json.dumps(actions.get("short_term", [])[:3], ensure_ascii=False),
        "MONTH_JS_ARRAY": json.dumps(actions.get("long_term", [])[:3], ensure_ascii=False),
        "RESOURCES_JS_ARRAY": json.dumps([{"icon": "📖", "title": r.split("——")[0].strip(), "subtitle": r.split("——")[1].strip() if "——" in r else ""} for r in actions.get("resources", [])], ensure_ascii=False),
    }
    return template.render(**context)

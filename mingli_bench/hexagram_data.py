"""Curated I Ching text data for local hexagram reports.

The first version intentionally covers a small, useful subset that appears in
the deterministic demo and common time-hexagram paths. Uncovered hexagrams
still return stable structural metadata from :mod:`mingli_bench.hexagram`.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional


TEXT_SOURCE = "zhouyi_classic.v1"


HEXAGRAM_TEXTS: Dict[int, Dict[str, Any]] = {
    1: {
        "theme": "创始、主动、自强与持续推进",
        "judgment": "元亨利贞。",
        "image": "天行健，君子以自强不息。",
        "lines": {
            1: {"text": "潜龙勿用。", "note": "力量尚在酝酿，宜蓄势、观察，不急于显露。"},
            2: {"text": "见龙在田，利见大人。", "note": "能力开始显现，适合寻求资源、导师或关键协作。"},
            3: {"text": "君子终日乾乾，夕惕若厉，无咎。", "note": "进入高强度推进期，需要持续自省和风险意识。"},
            4: {"text": "或跃在渊，无咎。", "note": "处在进退转换点，试探性行动比一次性押注更稳。"},
            5: {"text": "飞龙在天，利见大人。", "note": "势能到达高位，适合承担更大责任并借助平台。"},
            6: {"text": "亢龙有悔。", "note": "过度亢进容易反噬，需主动降温和留余地。"},
        },
    },
    2: {
        "theme": "承载、顺势、积累与稳定落地",
        "judgment": "元亨，利牝马之贞。君子有攸往，先迷后得主，利。西南得朋，东北丧朋。安贞吉。",
        "image": "地势坤，君子以厚德载物。",
        "lines": {
            1: {"text": "履霜，坚冰至。", "note": "细微信号会累积成趋势，需尽早识别苗头。"},
            2: {"text": "直方大，不习无不利。", "note": "以朴素、稳定、守正的方式推进，反而最有利。"},
            3: {"text": "含章可贞。或从王事，无成有终。", "note": "有能力但不宜抢功，适合在协作中完成结果。"},
            4: {"text": "括囊，无咎无誉。", "note": "收敛表达、控制风险，是此阶段的保全策略。"},
            5: {"text": "黄裳，元吉。", "note": "中正而有分寸，能把稳健转化为真正优势。"},
            6: {"text": "龙战于野，其血玄黄。", "note": "柔顺走到极端会引发冲突，需避免被动积压。"},
        },
    },
    19: {
        "theme": "临近、推进、照临与承担",
        "judgment": "元亨，利贞。至于八月有凶。",
        "image": "泽上有地，临。君子以教思无穷，容保民无疆。",
        "lines": {
            1: {"text": "咸临，贞吉。", "note": "初步接近目标，保持正向动机与边界最重要。"},
            2: {"text": "咸临，吉，无不利。", "note": "动能与响应较佳，适合主动推进并建立互信。"},
            3: {"text": "甘临，无攸利。既忧之，无咎。", "note": "若只追求轻松或讨好，成效有限；意识到风险即可修正。"},
            4: {"text": "至临，无咎。", "note": "接近核心位置，需要真正到场并承担责任。"},
            5: {"text": "知临，大君之宜，吉。", "note": "以判断力和格局来管理局面，利于成熟决策。"},
            6: {"text": "敦临，吉，无咎。", "note": "厚道、稳重、长期主义会带来更好的收束。"},
        },
    },
    24: {
        "theme": "回返、修复、循环再起",
        "judgment": "亨。出入无疾，朋来无咎。反复其道，七日来复，利有攸往。",
        "image": "雷在地中，复。先王以至日闭关，商旅不行，后不省方。",
        "lines": {
            1: {"text": "不远复，无祗悔，元吉。", "note": "偏离尚浅，及时回头最有利。"},
            2: {"text": "休复，吉。", "note": "以温和方式回到正轨，恢复成本较低。"},
            3: {"text": "频复，厉，无咎。", "note": "反复修正会有压力，但持续纠偏仍能避免大错。"},
            4: {"text": "中行独复。", "note": "在群体惯性中保留独立判断，回到自己认可的路径。"},
            5: {"text": "敦复，无悔。", "note": "厚实地修复基础，长期看可减少后悔。"},
            6: {"text": "迷复，凶，有灾眚。用行师，终有大败，以其国君凶，至于十年不克征。", "note": "迷失太久再强行推进，代价会显著放大。"},
        },
    },
    29: {
        "theme": "险阻、重复考验、守信与穿越",
        "judgment": "习坎，有孚，维心亨，行有尚。",
        "image": "水洊至，习坎。君子以常德行，习教事。",
        "lines": {
            1: {"text": "习坎，入于坎窞，凶。", "note": "陷入重复困境，需先止损，不宜继续下探。"},
            2: {"text": "坎有险，求小得。", "note": "大局仍有险，先争取小的确定性成果。"},
            3: {"text": "来之坎坎，险且枕，入于坎窞，勿用。", "note": "进退皆难时，应暂停关键动作。"},
            4: {"text": "樽酒簋贰，用缶，纳约自牖，终无咎。", "note": "用朴素直接的方式沟通和交换，可减轻风险。"},
            5: {"text": "坎不盈，祗既平，无咎。", "note": "风险尚未完全化解，但趋于平衡，可稳步处理。"},
            6: {"text": "系用徽纆，寘于丛棘，三岁不得，凶。", "note": "若被困在制度或关系束缚中，恢复周期会很长。"},
        },
    },
    30: {
        "theme": "明辨、依附、显现与持续照明",
        "judgment": "利贞，亨。畜牝牛，吉。",
        "image": "明两作，离。大人以继明照于四方。",
        "lines": {
            1: {"text": "履错然，敬之无咎。", "note": "开局信息杂乱，以谨慎和敬畏心处理可避错。"},
            2: {"text": "黄离，元吉。", "note": "中正而清明，是最有利的显现状态。"},
            3: {"text": "日昃之离，不鼓缶而歌，则大耋之嗟，凶。", "note": "光势转弱时，需接受阶段变化，避免沉溺失落。"},
            4: {"text": "突如其来如，焚如，死如，弃如。", "note": "突发的强烈变化容易破坏原有结构。"},
            5: {"text": "出涕沱若，戚嗟若，吉。", "note": "经历情绪释放后，反而能恢复清明和方向。"},
            6: {"text": "王用出征，有嘉折首，获匪其丑，无咎。", "note": "需要明确处理主要矛盾，不宜扩大打击面。"},
        },
    },
    46: {
        "theme": "渐进、上升、积小成高",
        "judgment": "元亨，用见大人，勿恤，南征吉。",
        "image": "地中生木，升。君子以顺德，积小以高大。",
        "lines": {
            1: {"text": "允升，大吉。", "note": "上升路径获得允许或响应，开端顺利。"},
            2: {"text": "孚乃利用禴，无咎。", "note": "真诚与可信比形式更重要，可用轻量方式达成信任。"},
            3: {"text": "升虚邑。", "note": "前方阻力较小，但也要确认目标是否有真实承载。"},
            4: {"text": "王用亨于岐山，吉，无咎。", "note": "借助合适平台与仪式性承诺，可稳步抬升。"},
            5: {"text": "贞吉，升阶。", "note": "按阶梯推进，守正则吉。"},
            6: {"text": "冥升，利于不息之贞。", "note": "上升到后段容易看不清边界，需长期自律。"},
        },
    },
    48: {
        "theme": "资源、基础、汲取与公共供养",
        "judgment": "改邑不改井，无丧无得，往来井井。汔至亦未繘井，羸其瓶，凶。",
        "image": "木上有水，井。君子以劳民劝相。",
        "lines": {
            1: {"text": "井泥不食，旧井无禽。", "note": "资源淤塞，旧方法暂时无法产生供给。"},
            2: {"text": "井谷射鲋，瓮敝漏。", "note": "方向和容器都有漏洞，产出难以有效承接。"},
            3: {"text": "井渫不食，为我心恻。可用汲，王明，并受其福。", "note": "资源已被清理却未被使用，需要被看见和调用。"},
            4: {"text": "井甃，无咎。", "note": "先修井壁、打基础，短期不显眼但能避错。"},
            5: {"text": "井洌，寒泉食。", "note": "资源清洁可用，适合把能力转化为稳定供给。"},
            6: {"text": "井收勿幕，有孚元吉。", "note": "开放而可信的资源系统，能形成长期良性循环。"},
        },
    },
}


def get_hexagram_text(number: int) -> Optional[Dict[str, Any]]:
    """Return text metadata for one King Wen hexagram number, if available."""

    data = HEXAGRAM_TEXTS.get(number)
    if data is None:
        return None
    result = deepcopy(data)
    result["source"] = TEXT_SOURCE
    result["coverage"] = "initial_subset"
    return result


def get_line_text(number: int, line_index: int) -> Optional[Dict[str, Any]]:
    """Return line text for a hexagram and 1-based line index, if available."""

    data = HEXAGRAM_TEXTS.get(number)
    if data is None:
        return None
    line = data.get("lines", {}).get(line_index)
    if line is None:
        return None
    result = deepcopy(line)
    result["source"] = TEXT_SOURCE
    return result


def has_hexagram_text(number: int) -> bool:
    """Return whether the curated text subset currently covers a hexagram."""

    return number in HEXAGRAM_TEXTS


__all__ = [
    "HEXAGRAM_TEXTS",
    "TEXT_SOURCE",
    "get_hexagram_text",
    "get_line_text",
    "has_hexagram_text",
]

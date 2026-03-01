# =============================================================
#  肾移植后他克莫司相关 AKI 风险预测计算器
#  模型：LASSO-Logistic 回归 + 逻辑校准
#  运行：streamlit run app.py
# =============================================================

import math
import streamlit as st

# ─────────────────────────────────────────────
#  1. 模型参数（来自 model_package_shrunk.json）
# ─────────────────────────────────────────────

INTERCEPT = -3.9167448076114226

# 校准参数（来自 recalibration 字段）
CAL_A = -0.07942559395364185
CAL_B =  0.8785993043794286

# 风险阈值（可在侧边栏调整）
DEFAULT_THRESHOLD = 0.30

# 连续变量：coef / mean / sd / impute(中位数)
# 系数来自 shrunk；mean/sd/impute 来自 shrunk（完整，无需补齐）
NUMERIC_PARAMS = {
    "肌酐": {
        "label": "肌酐", "unit": "μmol/L",
        "coef": -0.12171722561434864,
        "mean": 948.7558624577226, "sd": 275.6164167090626, "impute": 921.95,
        "min": 50.0, "max": 2500.0, "step": 1.0,
        "help": "移植后肌酐，训练集中位数 921.95 μmol/L；范围 50–2500",
        "group": "lab"
    },
    "尿素": {
        "label": "尿素", "unit": "mmol/L",
        "coef": -0.3023789899558171,
        "mean": 23.64792559188275, "sd": 7.791569721067218, "impute": 23.0,
        "min": 1.0, "max": 80.0, "step": 0.1,
        "help": "血尿素，训练集中位数 23.0 mmol/L；范围 1–80",
        "group": "lab"
    },
    "尿酸": {
        "label": "尿酸", "unit": "μmol/L",
        "coef": -0.1029981119949067,
        "mean": 363.7528748590756, "sd": 108.63740508559044, "impute": 363.0,
        "min": 50.0, "max": 1200.0, "step": 1.0,
        "help": "血尿酸，训练集中位数 363.0 μmol/L；范围 50–1200",
        "group": "lab"
    },
    "血小板计数": {
        "label": "血小板计数", "unit": "×10⁹/L",
        "coef": -0.25578579561362463,
        "mean": 203.5445321307779, "sd": 63.742400046407504, "impute": 198.0,
        "min": 10.0, "max": 800.0, "step": 1.0,
        "help": "血小板计数，训练集中位数 198.0 ×10⁹/L；范围 10–800",
        "group": "lab"
    },
    "中性粒细胞计数": {
        "label": "中性粒细胞计数", "unit": "×10⁹/L",
        "coef": 0.34915353968100615,
        "mean": 4.722626832018038, "sd": 1.7641006381219, "impute": 4.45,
        "min": 0.1, "max": 30.0, "step": 0.01,
        "help": "中性粒细胞绝对计数，训练集中位数 4.45 ×10⁹/L；范围 0.1–30",
        "group": "lab"
    },
    "白蛋白": {
        "label": "白蛋白（溴甲酚绿法）", "unit": "g/L",
        "coef": 0.09257794730085031,
        "mean": 44.950394588500565, "sd": 5.161788028424633, "impute": 45.3,
        "min": 10.0, "max": 60.0, "step": 0.1,
        "help": "血清白蛋白（溴甲酚绿法），训练集中位数 45.3 g/L；范围 10–60",
        "group": "lab",
        "json_key": "白蛋白_溴甲酚绿法_"
    },
    "总蛋白": {
        "label": "总蛋白", "unit": "g/L",
        "coef": 0.07790231620949731,
        "mean": 74.3042841037204, "sd": 8.42541678122355, "impute": 74.2,
        "min": 20.0, "max": 120.0, "step": 0.1,
        "help": "血清总蛋白，训练集中位数 74.2 g/L；范围 20–120",
        "group": "lab"
    },
    "碱性磷酸酶": {
        "label": "碱性磷酸酶", "unit": "U/L",
        "coef": 0.07048430674575476,
        "mean": 98.13438556933484, "sd": 74.93148182642358, "impute": 81.0,
        "min": 10.0, "max": 2000.0, "step": 1.0,
        "help": "ALP，训练集中位数 81.0 U/L；范围 10–2000",
        "group": "lab"
    },
    "血糖": {
        "label": "血糖", "unit": "mmol/L",
        "coef": 0.03958255360790811,
        "mean": 5.702570462232244, "sd": 2.0281537967790007, "impute": 5.24,
        "min": 1.0, "max": 40.0, "step": 0.01,
        "help": "随机或空腹血糖，训练集中位数 5.24 mmol/L；范围 1–40",
        "group": "lab"
    },
    "未结合胆红素": {
        "label": "未结合胆红素（干式）", "unit": "μmol/L",
        "coef": 0.03543514228538939,
        "mean": 2.685569334836528, "sd": 2.406346196041616, "impute": 2.0,
        "min": 0.1, "max": 50.0, "step": 0.1,
        "help": "间接胆红素（干式法），训练集中位数 2.0 μmol/L；范围 0.1–50",
        "group": "lab",
        "json_key": "未结合胆红素_干_"
    },
}

# 二分类变量：coef 为"用=1"对应系数
BINARY_PARAMS = {
    "贫血":       {"label": "贫血",       "coef": 0.4858706450249856,  "group": "basic", "opt0": "无",  "opt1": "有"},
    "抗酸药":     {"label": "抗酸药",     "coef": 0.7139132108386299,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "利尿药":     {"label": "利尿药",     "coef": 1.0295177465151235,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "抗凝药":     {"label": "抗凝药",     "coef": 0.5567115121767890,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "吸附剂":     {"label": "吸附剂",     "coef": 0.4579490928695176,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "促凝药":     {"label": "促凝药",     "coef":-0.0067058806661860,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "钙补充剂":   {"label": "钙补充剂",   "coef": 0.4001520677968892,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "麻醉药":     {"label": "麻醉药",     "coef": 0.4455813263195331,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "免疫球蛋白": {"label": "免疫球蛋白", "coef": 0.4689831390847565,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "正性肌力药": {"label": "正性肌力药", "coef": 0.1644556246176317,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "抗癫痫药":   {"label": "抗癫痫药",   "coef": 0.9531317955922250,  "group": "drug",  "opt0": "未用","opt1": "用"},
    "胃肠黏膜保护剂": {"label": "胃肠黏膜保护剂", "coef": 0.7226057588799102, "group": "drug", "opt0": "未用","opt1": "用"},
    "升白药":     {"label": "升白药（粒细胞集落刺激因子）", "coef": 1.1094327588070032, "group": "drug", "opt0": "未用","opt1": "用"},
    "抗痛风":     {"label": "抗痛风药",   "coef": 1.0133550727295633,  "group": "drug",  "opt0": "未用","opt1": "用"},
}

# FK506 三分类（JSON内部标签 → 用户显示标签 → 系数）
FK506_MAP = {
    "持续达标":   {"json_ref": "全程窗内",  "coef": 0.0},
    "间歇性达标": {"json_ref": "曾超窗",    "coef": 0.40498607000779124},
    "从未达标":   {"json_ref": "全程超窗",  "coef": 1.2916688217943653},
}

# ─────────────────────────────────────────────
#  2. 预测函数
# ─────────────────────────────────────────────

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def safe_logit(p: float) -> float:
    p = max(1e-9, min(1 - 1e-9, p))
    return math.log(p / (1.0 - p))

def predict(inputs: dict) -> dict:
    """
    inputs: {变量名: 数值或None}
    返回: {lp, p_raw, p_cal}
    """
    lp = INTERCEPT

    # 连续变量
    for key, params in NUMERIC_PARAMS.items():
        raw = inputs.get(key)
        if raw is None or (isinstance(raw, float) and math.isnan(raw)):
            raw = params["impute"]           # 缺失 → 中位数填补
        z = (raw - params["mean"]) / params["sd"]   # z 标准化
        lp += params["coef"] * z

    # 二分类变量（opt1 = 1，opt0 = 0）
    for key, params in BINARY_PARAMS.items():
        val = inputs.get(key, 0)
        lp += params["coef"] * int(val)

    # FK506 三分类
    fk506_label = inputs.get("FK506", "持续达标")
    lp += FK506_MAP.get(fk506_label, FK506_MAP["持续达标"])["coef"]

    p_raw = sigmoid(lp)
    p_cal = sigmoid(CAL_A + CAL_B * safe_logit(p_raw))

    return {"lp": lp, "p_raw": p_raw, "p_cal": p_cal}

# ─────────────────────────────────────────────
#  3. Streamlit 页面
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AKI 风险预测 | 肾移植",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局样式 ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans SC', sans-serif; }

.main-title {
    font-size: 1.55rem; font-weight: 700;
    color: #1a3a5c; margin-bottom: 2px;
}
.sub-title {
    font-size: 0.82rem; color: #7f8c8d; margin-bottom: 18px;
}
.section-header {
    font-size: 0.95rem; font-weight: 600;
    color: #1a3a5c; border-left: 4px solid #2980b9;
    padding-left: 10px; margin: 18px 0 12px 0;
}
.result-box {
    border-radius: 10px; padding: 22px 24px;
    margin-top: 6px;
}
.result-high {
    background: #fdecea; border: 1.5px solid #e57373;
}
.result-low {
    background: #e8f5e9; border: 1.5px solid #66bb6a;
}
.risk-label-high { color: #c0392b; font-size: 1.35rem; font-weight: 700; }
.risk-label-low  { color: #27ae60; font-size: 1.35rem; font-weight: 700; }
.prob-big { font-size: 3.2rem; font-weight: 800; line-height: 1; }
.prob-high { color: #c0392b; }
.prob-low  { color: #27ae60; }
.meta-line { font-size: 0.8rem; color: #555; margin-top: 6px; }
.disclaimer {
    background: #fffbf0; border: 1px solid #f0c040;
    border-radius: 6px; padding: 12px 14px;
    font-size: 0.78rem; color: #7d6608; margin-top: 20px;
    line-height: 1.7;
}
.drug-hint { font-size: 0.73rem; color: #95a5a6; margin-bottom: 14px; }
</style>
""", unsafe_allow_html=True)

# ── 标题 ──
st.markdown('<div class="main-title">🏥 肾移植后 AKI 风险预测计算器</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">基于 LASSO-Logistic 回归模型 ｜ 1268 例肾移植患者 ｜ '
    '测试集 AUC = 0.797 ｜ 校准后阈值 ≥ 30% 为高风险</div>',
    unsafe_allow_html=True
)

# ── 侧边栏：高级设置 ──
with st.sidebar:
    st.markdown("### ⚙️ 高级设置")
    threshold = st.slider(
        "风险分层阈值",
        min_value=0.10, max_value=0.70, value=DEFAULT_THRESHOLD, step=0.01,
        format="%.2f",
        help="p_cal ≥ 阈值 → 高风险；默认 0.30（Youden 指数最优阈值）"
    )
    show_detail = st.checkbox("显示详细计算信息（lp、原始概率）", value=False)
    st.markdown("---")
    st.markdown(
        "**模型参数确认**\n\n"
        f"- 截距：`{INTERCEPT:.4f}`\n"
        f"- 校准截距 a：`{CAL_A:.4f}`\n"
        f"- 校准斜率 b：`{CAL_B:.4f}`\n"
        f"- 当前阈值：`{threshold:.2f}`"
    )

# ── 主体：三列布局 ──
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    inputs = {}

    # ══ 第一组：基本信息 ══
    st.markdown('<div class="section-header">📋 基本信息</div>', unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    with bc1:
        v = BINARY_PARAMS["贫血"]
        sel = st.radio(
            v["label"], options=[v["opt0"], v["opt1"]],
            horizontal=True, index=0,
            help="住院期间是否存在贫血（Hb < 120 g/L（女）或 < 130 g/L（男））"
        )
        inputs["贫血"] = 1 if sel == v["opt1"] else 0

    # FK506 独立一行
    st.markdown('<div class="section-header">⚕️ FK506（他克莫司）谷浓度达标情况</div>', unsafe_allow_html=True)
    fk_labels = list(FK506_MAP.keys())
    fk_sel = st.radio(
        "住院期间 FK506 谷浓度达标状态",
        options=fk_labels, index=0, horizontal=True,
        help="持续达标：全程在目标窗内（8–12 ng/mL 或遵医嘱）；间歇性达标：曾超窗；从未达标：全程超窗"
    )
    inputs["FK506"] = fk_sel

    # ══ 第二组：用药信息 ══
    st.markdown('<div class="section-header">💊 用药信息（住院期间是否使用）</div>', unsafe_allow_html=True)
    st.markdown('<div class="drug-hint">以下均为"未用 / 用"两选一</div>', unsafe_allow_html=True)

    drug_keys = [k for k, v in BINARY_PARAMS.items() if v["group"] == "drug"]
    # 4列展示
    drug_cols = st.columns(4)
    for idx, key in enumerate(drug_keys):
        v = BINARY_PARAMS[key]
        with drug_cols[idx % 4]:
            sel = st.radio(
                v["label"],
                options=[v["opt0"], v["opt1"]],
                horizontal=False, index=0,
                key=f"drug_{key}"
            )
            inputs[key] = 1 if sel == v["opt1"] else 0

    # ══ 第三组：实验室检查 ══
    st.markdown('<div class="section-header">🔬 实验室检查</div>', unsafe_allow_html=True)
    lab_keys = list(NUMERIC_PARAMS.keys())
    lab_cols_1, lab_cols_2 = st.columns(2)
    lab_col_list = [lab_cols_1, lab_cols_2]

    for idx, key in enumerate(lab_keys):
        p = NUMERIC_PARAMS[key]
        with lab_col_list[idx % 2]:
            val = st.number_input(
                f"{p['label']}  （{p['unit']}）",
                min_value=p["min"],
                max_value=p["max"],
                value=None,
                step=p["step"],
                format="%.2f" if p["step"] < 1 else "%.1f",
                placeholder=f"留空 → 自动填补中位数 {p['impute']}",
                help=p["help"],
                key=f"num_{key}"
            )
            inputs[key] = val  # None 表示缺失，由 predict() 填补

# ── 右列：结果区 ──
with col_right:
    st.markdown('<div class="section-header">📊 预测结果</div>', unsafe_allow_html=True)

    run = st.button("▶ 计算 AKI 风险", type="primary", use_container_width=True)

    if run:
        result = predict(inputs)
        p_cal = result["p_cal"]
        p_raw = result["p_raw"]
        lp    = result["lp"]
        p_pct = round(p_cal * 100, 1)
        is_high = p_cal >= threshold

        risk_label = "🔴 高风险" if is_high else "🟢 低风险"
        box_cls    = "result-high" if is_high else "result-low"
        label_cls  = "risk-label-high" if is_high else "risk-label-low"
        prob_cls   = "prob-high" if is_high else "prob-low"

        st.markdown(
            f'<div class="result-box {box_cls}">'
            f'<div class="{label_cls}">{risk_label}</div>'
            f'<div class="prob-big {prob_cls}">{p_pct}%</div>'
            f'<div class="meta-line">校准后 AKI 预测概率</div>'
            f'<div class="meta-line">阈值：≥ {round(threshold*100)}% → 高风险</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if show_detail:
            st.markdown(f"""
**详细计算信息**
- 原始概率 p_raw：`{round(p_raw*100, 2)}%`
- 线性预测值 lp：`{round(lp, 4)}`
- 校准公式：`sigmoid({CAL_A:.4f} + {CAL_B:.4f} × logit(p_raw))`
""")

        # 结果文本
        fk_display = inputs.get("FK506", "持续达标")
        used_drugs = [BINARY_PARAMS[k]["label"] for k in BINARY_PARAMS if inputs.get(k, 0) == 1]
        result_text = (
            f"【肾移植后 AKI 风险预测结果】\n"
            f"校准后概率：{p_pct}%\n"
            f"风险分层：{'高风险' if is_high else '低风险'}（阈值 ≥ {round(threshold*100)}%）\n"
            f"FK506达标情况：{fk_display}\n"
            f"使用药物：{', '.join(used_drugs) if used_drugs else '无'}\n"
            f"--\n"
            f"原始概率：{round(p_raw*100, 2)}%  |  lp：{round(lp, 4)}\n"
            f"⚠️ 本结果仅供辅助决策参考，不替代临床判断"
        )

        st.code(result_text, language=None)
        if st.button("📋 复制结果文本", key="copy_btn"):
            st.session_state["copied_text"] = result_text
            st.success("✅ 已写入下方代码框，可手动全选复制")

        # 存储结果以便复制
        st.session_state["last_result"] = result_text

    else:
        st.markdown(
            '<div style="text-align:center;padding:50px 0;color:#bbb;font-size:0.9rem;">'
            '请填写左侧信息<br>后点击【计算 AKI 风险】'
            '</div>',
            unsafe_allow_html=True
        )

    # ── 免责声明 ──
    st.markdown("""
<div class="disclaimer">
<b>⚠️ 免责声明</b><br>
本工具基于单中心回顾性数据建立，<b>仅供临床辅助决策参考</b>，
不能替代临床医生的综合判断。预测结果须结合患者实际临床情境解读。<br><br>
<b>适用范围：</b>成人肾移植术后住院患者，具备本模型所需的实验室及用药数据。<br>
<b>不适用范围：</b>儿童肾移植、联合器官移植、数据来源与训练集差异较大的中心。<br><br>
本工具不构成医疗建议，使用者须自行承担临床决策责任。
</div>
""", unsafe_allow_html=True)

# =============================================================
#  Post-Kidney Transplant AKI Risk Calculator
#  Multi-Subgroup Edition  |  Run: streamlit run app.py
#  Access: http://localhost:8501
# =============================================================

import math
import streamlit as st

# ─────────────────────────────────────────────────────────────
#  MODEL REGISTRY
#  All parameters inlined — no external JSON files required.
#  Coefficients: from model_package_shrunk{1,2,3}.json
#  mean/sd/impute: same source (shrunk JSONs are self-contained)
#  Calibration: from recalibration block; null → global defaults
#  Global defaults: a = -0.07942559, b = 0.87859930
# ─────────────────────────────────────────────────────────────

_DEFAULT_CAL_A = -0.07942559395364185
_DEFAULT_CAL_B =  0.8785993043794286

MODELS = {

# ── Subgroup 1: Post-KT Full Model (Tacrolimus / FK506) ──────
1: {
    "name":        "Post-KT Full Model (Tacrolimus / FK506)",
    "description": "Post-kidney transplant patients; FK506 attainment + 25 variables.",
    "intercept":   -3.9167448076114226,
    "cal_a":       -0.07942559395364185,   # from shrunk1 recalibration block
    "cal_b":        0.8785993043794286,
    "numeric": {
        "肌酐":              {"en":"Serum Creatinine",           "unit":"μmol/L",   "coef":-0.12171722561434864, "mean":948.7558624577226,  "sd":275.6164167090626,  "impute":921.95, "min":50.0,  "max":2500.0,"step":1.0},
        "尿素":              {"en":"Blood Urea Nitrogen (BUN)",  "unit":"mmol/L",   "coef":-0.3023789899558171,  "mean":23.64792559188275,  "sd":7.791569721067218,  "impute":23.0,   "min":1.0,   "max":80.0,  "step":0.1},
        "尿酸":              {"en":"Serum Uric Acid",             "unit":"μmol/L",   "coef":-0.1029981119949067,  "mean":363.7528748590756,  "sd":108.63740508559044, "impute":363.0,  "min":50.0,  "max":1200.0,"step":1.0},
        "血小板计数":        {"en":"Platelet Count",              "unit":"×10⁹/L",   "coef":-0.25578579561362463, "mean":203.5445321307779,  "sd":63.742400046407504, "impute":198.0,  "min":5.0,   "max":1200.0,"step":1.0},
        "中性粒细胞计数":    {"en":"Neutrophil Count",            "unit":"×10⁹/L",   "coef":0.34915353968100615,  "mean":4.722626832018038,  "sd":1.7641006381219,    "impute":4.45,   "min":0.1,   "max":50.0,  "step":0.01},
        "白蛋白_溴甲酚绿法_":{"en":"Albumin (BCG)",               "unit":"g/L",      "coef":0.09257794730085031,  "mean":44.950394588500565, "sd":5.161788028424633,  "impute":45.3,   "min":10.0,  "max":60.0,  "step":0.1},
        "总蛋白":            {"en":"Total Protein",               "unit":"g/L",      "coef":0.07790231620949731,  "mean":74.3042841037204,   "sd":8.42541678122355,   "impute":74.2,   "min":20.0,  "max":120.0, "step":0.1},
        "碱性磷酸酶":        {"en":"ALP",                         "unit":"U/L",      "coef":0.07048430674575476,  "mean":98.13438556933484,  "sd":74.93148182642358,  "impute":81.0,   "min":10.0,  "max":2000.0,"step":1.0},
        "血糖":              {"en":"Blood Glucose",               "unit":"mmol/L",   "coef":0.03958255360790811,  "mean":5.702570462232244,  "sd":2.0281537967790007, "impute":5.24,   "min":1.0,   "max":40.0,  "step":0.01},
        "未结合胆红素_干_":  {"en":"Indirect Bilirubin (dry)",    "unit":"μmol/L",   "coef":0.03543514228538939,  "mean":2.685569334836528,  "sd":2.406346196041616,  "impute":2.0,    "min":0.1,   "max":50.0,  "step":0.1},
    },
    "categorical": {
        "贫血":              {"en":"Anemia",                    "coef":0.4858706450249856,   "impute":0, "type":"binary"},
        "抗酸药":            {"en":"Antacids",                  "coef":0.7139132108386299,   "impute":0, "type":"binary"},
        "利尿药":            {"en":"Diuretics",                 "coef":1.0295177465151235,   "impute":0, "type":"binary"},
        "抗凝药":            {"en":"Anticoagulants",            "coef":0.556711512176789,    "impute":0, "type":"binary"},
        "吸附剂":            {"en":"Intestinal Adsorbents",     "coef":0.45794909286951757,  "impute":0, "type":"binary"},
        "促凝药":            {"en":"Procoagulants",             "coef":-0.0067058806661859606,"impute":0,"type":"binary"},
        "钙补充剂":          {"en":"Calcium Supplements",       "coef":0.40015206779688917,  "impute":0, "type":"binary"},
        "麻醉药":            {"en":"Anesthetics",               "coef":0.44558132631953307,  "impute":0, "type":"binary"},
        "免疫球蛋白":        {"en":"Immunoglobulin (IVIG)",     "coef":0.4689831390847565,   "impute":0, "type":"binary"},
        "正性肌力药":        {"en":"Positive Inotropes",        "coef":0.16445562461763166,  "impute":0, "type":"binary"},
        "抗癫痫药":          {"en":"Antiepileptics",            "coef":0.953131795592225,    "impute":0, "type":"binary"},
        "胃肠黏膜保护剂":    {"en":"GI Mucosal Protectives",   "coef":0.7226057588799102,   "impute":0, "type":"binary"},
        "升白药":            {"en":"G-CSF",                     "coef":1.1094327588070032,   "impute":0, "type":"binary"},
        "抗痛风":            {"en":"Anti-Gout Medications",     "coef":1.0133550727295633,   "impute":0, "type":"binary"},
        "FK506":             {
            "en":"Tacrolimus (FK506) Attainment",
            "type":"multiclass",
            "ref":"全程窗内",
            "impute":"全程窗内",
            "levels": {
                "全程窗内": {"en":"Consistently on Target",    "coef":0.0},
                "曾超窗":   {"en":"Intermittently on Target",  "coef":0.40498607000779124},
                "全程超窗": {"en":"Never on Target",           "coef":1.2916688217943653},
            }
        },
    },
    "groups": {
        "Tacrolimus Status": ["FK506"],
        "Baseline": ["贫血"],
        "Medications": ["抗酸药","利尿药","抗凝药","吸附剂","促凝药","钙补充剂",
                        "麻醉药","免疫球蛋白","正性肌力药","抗癫痫药","胃肠黏膜保护剂","升白药","抗痛风"],
        "Laboratory Tests": ["肌酐","尿素","尿酸","血小板计数","中性粒细胞计数",
                             "白蛋白_溴甲酚绿法_","总蛋白","碱性磷酸酶","血糖","未结合胆红素_干_"],
    }
},

# ── Subgroup 2: Post-KT Hematology / ICU Model ───────────────
2: {
    "name":        "Post-KT Hematology / ICU Model",
    "description": "Post-kidney transplant patients; hematological and ICU-focused variables.",
    "intercept":   -3.6606838134695305,
    "cal_a":       -0.07942559395364185,   # global default (shrunk2 has same values)
    "cal_b":        0.8785993043794286,
    "numeric": {
        "胱抑素c":           {"en":"Cystatin C",              "unit":"mg/L",     "coef":0.14049844803376624,  "mean":2.251268656716418,  "sd":1.0884978157937424,  "impute":2.01,   "min":0.1,  "max":15.0,  "step":0.01},
        "单核细胞百分比":    {"en":"Monocyte % (proportion)", "unit":"e.g. 0.08","coef":-0.16394161639759547, "mean":0.08298694029850745,"sd":0.03735117004955886, "impute":0.081,  "min":0.0,  "max":0.5,   "step":0.001},
        "中性粒细胞计数":    {"en":"Neutrophil Count",        "unit":"×10⁹/L",   "coef":0.15124652387278295,  "mean":5.906927238805971,  "sd":4.0337514945402635,  "impute":4.92,   "min":0.1,  "max":50.0,  "step":0.01},
        "平均血红蛋白含量":  {"en":"MCH",                     "unit":"pg",       "coef":0.2813782662919976,   "mean":29.975373134328358, "sd":1.6676212644561401,  "impute":29.9,   "min":18.0, "max":45.0,  "step":0.1},
        "淋巴细胞计数":      {"en":"Lymphocyte Count",        "unit":"×10⁹/L",   "coef":-0.3083915711748147,  "mean":0.9738078358208956, "sd":0.6252379505351112,  "impute":0.895,  "min":0.01, "max":10.0,  "step":0.01},
        "红细胞计数":        {"en":"RBC Count",               "unit":"×10¹²/L",  "coef":-0.03486010199222113, "mean":3.750298507462687,  "sd":0.7929064617985853,  "impute":3.76,   "min":0.5,  "max":8.0,   "step":0.01},
        "红细胞宽度_sd值":   {"en":"RDW-SD",                  "unit":"fL",       "coef":-0.030260712410191307,"mean":48.43824626865672,  "sd":7.804061078213451,   "impute":46.25,  "min":20.0, "max":120.0, "step":0.1},
        "血小板计数":        {"en":"Platelet Count",          "unit":"×10⁹/L",   "coef":-0.05681115667179618, "mean":185.85261194029852, "sd":67.9867381210626,    "impute":181.0,  "min":5.0,  "max":1200.0,"step":1.0},
        "钙":                {"en":"Serum Calcium",           "unit":"mmol/L",   "coef":-0.18298658500570214, "mean":2.2747015111940296, "sd":0.1666266076882498,  "impute":2.28,   "min":0.5,  "max":4.0,   "step":0.01},
    },
    "categorical": {
        "ICU":           {"en":"ICU Admission",               "coef":1.3289105514872415,  "impute":0, "type":"binary"},
        "血管活性药":    {"en":"Vasopressors / Vasoactive Agents","coef":0.6230129734325999,"impute":1, "type":"binary",
                         "_note":"⚠️ Default impute = 1 (Used). Leaving blank assumes vasopressors WERE administered."},
        "精神治疗药":    {"en":"Psychotropic Medications",    "coef":0.7279208805888284,  "impute":0, "type":"binary"},
        "利尿药":        {"en":"Diuretics",                   "coef":0.5755679515794798,  "impute":0, "type":"binary"},
        "扩容药":        {"en":"Volume Expanders",            "coef":0.37311253758337565, "impute":0, "type":"binary"},
        "抗凝药":        {"en":"Anticoagulants",              "coef":0.19970962654843802, "impute":0, "type":"binary"},
    },
    "groups": {
        "Baseline": ["ICU"],
        "Medications": ["血管活性药","精神治疗药","利尿药","扩容药","抗凝药"],
        "Laboratory Tests": ["胱抑素c","单核细胞百分比","中性粒细胞计数","平均血红蛋白含量",
                             "淋巴细胞计数","红细胞计数","红细胞宽度_sd值","血小板计数","钙"],
    }
},

# ── Subgroup 3: Hepatic / Coagulation Model ──────────────────
3: {
    "name":        "Hepatic / Coagulation Model",
    "description": "Patients with hepatic involvement; coagulation and liver-function variables.",
    "intercept":   -6.577238277941135,
    "cal_a":        0.05012968694220859,   # from shrunk3 recalibration block
    "cal_b":        0.8305403277675305,
    "numeric": {
        "天门冬氨酸转氨酶":  {"en":"AST",                          "unit":"U/L",      "coef":-0.14752481304709783, "mean":248.556,            "sd":716.0954177385199,  "impute":36.0,   "min":5.0,   "max":10000.0,"step":1.0},
        "尿酸":              {"en":"Serum Uric Acid",              "unit":"μmol/L",   "coef":-0.03717360054442158, "mean":263.90736842105264, "sd":138.29580854637587, "impute":247.0,  "min":50.0,  "max":1200.0,"step":1.0},
        "单核细胞计数":      {"en":"Monocyte Count",               "unit":"×10⁹/L",   "coef":-0.18737845378501594, "mean":0.48213263157894737,"sd":0.3052043548154874, "impute":0.43,   "min":0.0,   "max":5.0,   "step":0.01},
        "中性粒细胞百分比":  {"en":"Neutrophil % (proportion)",    "unit":"e.g. 0.78","coef":-0.21167006875203523, "mean":0.7788094736842104, "sd":0.1502850380014305, "impute":0.8075, "min":0.0,   "max":1.0,   "step":0.001},
        "总胆红素":          {"en":"Total Bilirubin",              "unit":"μmol/L",   "coef":0.0639750223438938,   "mean":51.12374736842105,  "sd":90.64991607775816,  "impute":17.75,  "min":1.0,   "max":1000.0,"step":0.1},
        "钾离子":            {"en":"Serum Potassium",              "unit":"mmol/L",   "coef":0.21316561818233884,  "mean":3.911894736842105,  "sd":0.5458715768322727, "impute":3.9,    "min":1.5,   "max":9.0,   "step":0.01},
        "胆碱酯酶":          {"en":"Cholinesterase (ChE)",         "unit":"U/L",      "coef":-0.3073241702220932,  "mean":5065.368421052632,  "sd":2671.8257020548076, "impute":4460.0, "min":100.0, "max":20000.0,"step":10.0},
        "平均血小板体积":    {"en":"Mean Platelet Volume (MPV)",   "unit":"fL",       "coef":-0.3185478313247615,  "mean":11.265894736842103, "sd":1.1458735989231714, "impute":11.2,   "min":3.0,   "max":25.0,  "step":0.1},
        "凝血酶比率":        {"en":"Thrombin Ratio",               "unit":"ratio",    "coef":-0.10702741775538163, "mean":1.1097473684210524, "sd":0.4182307841477768, "impute":1.02,   "min":0.5,   "max":10.0,  "step":0.01},
        "纤维蛋白原含量":    {"en":"Fibrinogen",                   "unit":"g/L",      "coef":-0.29100163788847,    "mean":2.680768421052631,  "sd":1.4525332821814705, "impute":2.375,  "min":0.1,   "max":15.0,  "step":0.01},
        "补_间接胆红素":     {"en":"Indirect Bilirubin (suppl.)", "unit":"μmol/L",   "coef":0.09382049132083763,  "mean":13.472842105263158, "sd":24.547556408055126, "impute":6.7,    "min":0.1,   "max":500.0, "step":0.1},
        "补_前白蛋白":       {"en":"Prealbumin",                   "unit":"mg/L",     "coef":-0.1372712532572401,  "mean":163.73894736842107, "sd":81.3323817103707,   "impute":151.5,  "min":5.0,   "max":600.0, "step":1.0},
    },
    "categorical": {
        "促凝药":        {"en":"Procoagulants / Hemostatics",    "coef":1.9211935939524067,  "impute":0, "type":"binary"},
        "抗凝药":        {"en":"Anticoagulants",                 "coef":1.8941241830686304,  "impute":0, "type":"binary"},
        "免疫球蛋白":    {"en":"Immunoglobulin (IVIG)",          "coef":1.3354586838669351,  "impute":0, "type":"binary"},
        "祛痰药":        {"en":"Expectorants / Mucolytics",      "coef":1.2280590672511853,  "impute":0, "type":"binary"},
        "矿物质补充剂":  {"en":"Mineral Supplements",            "coef":0.9528031965954611,  "impute":0, "type":"binary"},
        "肝硬化":        {"en":"Liver Cirrhosis",                "coef":0.5279482157819856,  "impute":0, "type":"binary"},
        "精神治疗药":    {"en":"Psychotropic Medications",       "coef":0.5477635150152356,  "impute":0, "type":"binary"},
        "NSAID":         {"en":"NSAIDs",                         "coef":0.5162383329406315,  "impute":0, "type":"binary"},
    },
    "groups": {
        "Baseline / Diagnosis": ["肝硬化"],
        "Medications": ["促凝药","抗凝药","免疫球蛋白","祛痰药","矿物质补充剂","精神治疗药","NSAID"],
        "Laboratory Tests": ["天门冬氨酸转氨酶","尿酸","单核细胞计数","中性粒细胞百分比",
                             "总胆红素","钾离子","胆碱酯酶","平均血小板体积",
                             "凝血酶比率","纤维蛋白原含量","补_间接胆红素","补_前白蛋白"],
    }
},

}  # end MODELS

# ─────────────────────────────────────────────────────────────
#  PREDICTION FUNCTION
# ─────────────────────────────────────────────────────────────

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def safe_logit(p: float) -> float:
    p = max(1e-9, min(1.0 - 1e-9, p))
    return math.log(p / (1.0 - p))

def predict(sg_id: int, inputs: dict) -> dict:
    """
    sg_id: 1, 2, or 3
    inputs: {cn_key: value or None}
    Returns: {lp, p_raw, p_cal, risk_label}
    """
    m   = MODELS[sg_id]
    lp  = m["intercept"]

    for key, p in m["numeric"].items():
        v = inputs.get(key)
        if v is None:
            v = p["impute"]
        lp += p["coef"] * (v - p["mean"]) / p["sd"]

    for key, p in m["categorical"].items():
        if p["type"] == "multiclass":
            chosen = inputs.get(key, p["impute"])
            lp += p["levels"].get(chosen, p["levels"][p["ref"]])["coef"]
        else:
            v = inputs.get(key)
            if v is None:
                v = p["impute"]
            lp += p["coef"] * int(v)

    p_raw = sigmoid(lp)
    p_cal = sigmoid(m["cal_a"] + m["cal_b"] * safe_logit(p_raw))
    threshold = st.session_state.get("threshold", 0.30)
    return {
        "lp": lp, "p_raw": p_raw, "p_cal": p_cal,
        "risk_label": "HIGH" if p_cal >= threshold else "LOW",
    }

# ─────────────────────────────────────────────────────────────
#  STREAMLIT APP
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Post-KT AKI Risk Calculator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}

.app-title  {font-size:1.55rem;font-weight:700;color:#1a3a5c;margin-bottom:2px;}
.app-sub    {font-size:0.82rem;color:#6b7280;margin-bottom:18px;}
.sg-badge   {display:inline-block;background:#dbeafe;color:#1e40af;border-radius:4px;
             padding:3px 10px;font-size:0.78rem;font-weight:600;margin-bottom:14px;}
.sec-hdr    {font-size:0.9rem;font-weight:600;color:#1e3a5f;
             border-left:4px solid #3b82f6;padding-left:10px;margin:18px 0 12px 0;}
.result-high{background:#fef2f2;border:2px solid #f87171;border-radius:10px;padding:22px 24px;margin-top:8px;}
.result-low {background:#f0fdf4;border:2px solid #86efac;border-radius:10px;padding:22px 24px;margin-top:8px;}
.badge-high {display:inline-block;background:#dc2626;color:#fff;border-radius:5px;
             padding:4px 14px;font-size:0.85rem;font-weight:700;letter-spacing:1px;margin-bottom:10px;}
.badge-low  {display:inline-block;background:#16a34a;color:#fff;border-radius:5px;
             padding:4px 14px;font-size:0.85rem;font-weight:700;letter-spacing:1px;margin-bottom:10px;}
.prob-high  {font-size:3.2rem;font-weight:800;color:#dc2626;line-height:1;}
.prob-low   {font-size:3.2rem;font-weight:800;color:#16a34a;line-height:1;}
.prob-sub   {font-size:0.78rem;color:#6b7280;margin-top:4px;}
.disclaimer {background:#fffbeb;border:1px solid #fcd34d;border-radius:6px;
             padding:12px 14px;font-size:0.76rem;color:#92400e;line-height:1.7;margin-top:18px;}
.vasowarning{background:#fef3c7;border:1px solid #f59e0b;border-radius:5px;
             padding:8px 12px;font-size:0.77rem;color:#92400e;margin-bottom:8px;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 AKI Risk Calculator")

    sg_options = {sg: MODELS[sg]["name"] for sg in [1, 2, 3]}
    sg_choice  = st.selectbox(
        "Select Subgroup Model",
        options=list(sg_options.keys()),
        format_func=lambda x: f"SG{x}: {sg_options[x]}",
        index=0,
        help="Each subgroup uses a distinct set of predictors. Select the model matching your patient population.",
    )

    threshold = st.slider(
        "Risk Threshold",
        min_value=0.10, max_value=0.70,
        value=0.30, step=0.01, format="%.2f",
        help="p_cal ≥ threshold → HIGH RISK. Default = 0.30 (Youden-index optimal).",
    )
    st.session_state["threshold"] = threshold
    show_tech = st.checkbox("Show technical details", value=False)

    st.markdown("---")
    m_info = MODELS[sg_choice]
    st.markdown(f"**Active model:** SG{sg_choice}")
    st.markdown(
        f"- Intercept: `{m_info['intercept']:.4f}`\n"
        f"- Cal. a: `{m_info['cal_a']:.5f}`\n"
        f"- Cal. b: `{m_info['cal_b']:.5f}`\n"
        f"- Threshold: `{threshold:.2f}`"
    )

# ── Header ───────────────────────────────────────────────────
st.markdown('<div class="app-title">🏥 Post-Kidney Transplant AKI Risk Calculator</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="app-sub">Multi-Subgroup Edition | LASSO-Logistic Regression + Logistic Calibration | '
    'Outcome: AKI | Default threshold ≥ 30% → High Risk</div>',
    unsafe_allow_html=True,
)

model     = MODELS[sg_choice]
sg_inputs = {}

# ── Main: two-column layout ───────────────────────────────────
col_in, col_out = st.columns([3, 2], gap="large")

with col_in:
    st.markdown(
        f'<div class="sg-badge">Active: SG{sg_choice} — {model["name"]}</div>',
        unsafe_allow_html=True,
    )
    st.caption(model["description"])

    for group_name, var_keys in model["groups"].items():
        st.markdown(f'<div class="sec-hdr">{"🔬" if "Lab" in group_name else "💊" if "Med" in group_name else "📋"} {group_name}</div>',
                    unsafe_allow_html=True)

        cat_vars = {k: v for k, v in model["categorical"].items() if k in var_keys}
        num_vars = {k: v for k, v in model["numeric"].items()     if k in var_keys}

        # Categorical inputs
        if cat_vars:
            if group_name in ("Medications", "Baseline", "Baseline / Diagnosis"):
                # Check for vasopressor special warning
                for key, p in cat_vars.items():
                    if p.get("_note"):
                        st.markdown(
                            f'<div class="vasowarning">⚠️ <b>{p["en"]}</b>: '
                            f'{p["_note"]}</div>', unsafe_allow_html=True
                        )

                n_cols = min(4, max(2, len(cat_vars)))
                cols = st.columns(n_cols)
                for i, (key, p) in enumerate(cat_vars.items()):
                    if p["type"] == "binary":
                        default_idx = 1 if p["impute"] == 1 else 0
                        sel = cols[i % n_cols].radio(
                            p["en"], options=["No", "Yes"],
                            horizontal=False, index=default_idx,
                            key=f"sg{sg_choice}_{key}",
                        )
                        sg_inputs[key] = 1 if sel == "Yes" else 0
            else:
                for key, p in cat_vars.items():
                    if p["type"] == "multiclass":
                        level_opts = list(p["levels"].keys())
                        level_en   = {lk: lv["en"] for lk, lv in p["levels"].items()}
                        sel = st.selectbox(
                            p["en"],
                            options=level_opts,
                            format_func=lambda x: level_en.get(x, x),
                            index=0,
                            help="Select tacrolimus trough-level attainment status during hospitalization.",
                            key=f"sg{sg_choice}_{key}",
                        )
                        sg_inputs[key] = sel

        # Numeric inputs — two-column grid
        if num_vars:
            nc1, nc2 = st.columns(2)
            col_list = [nc1, nc2]
            for idx, (key, p) in enumerate(num_vars.items()):
                with col_list[idx % 2]:
                    fmt = "%.3f" if p["step"] < 0.01 else ("%.2f" if p["step"] < 1 else "%.1f")
                    val = st.number_input(
                        f"{p['en']}  ({p['unit']})",
                        min_value=float(p["min"]),
                        max_value=float(p["max"]),
                        value=None,
                        step=float(p["step"]),
                        format=fmt,
                        placeholder=f"Median: {p['impute']}",
                        help=f"Training median = {p['impute']} {p['unit']}; range {p['min']}–{p['max']}",
                        key=f"sg{sg_choice}_num_{key}",
                    )
                    sg_inputs[key] = val

# ── Result panel ─────────────────────────────────────────────
with col_out:
    st.markdown('<div class="sec-hdr">📊 Prediction Result</div>', unsafe_allow_html=True)

    calc = st.button("▶ Calculate AKI Risk", type="primary", use_container_width=True)

    if calc:
        res      = predict(sg_choice, sg_inputs)
        p_pct    = round(res["p_cal"] * 100, 1)
        is_high  = res["risk_label"] == "HIGH"
        res_cls  = "result-high"  if is_high else "result-low"
        badge_cl = "badge-high"   if is_high else "badge-low"
        prob_cl  = "prob-high"    if is_high else "prob-low"
        badge_tx = "HIGH RISK"    if is_high else "LOW RISK"

        st.markdown(
            f'<div class="{res_cls}">'
            f'<div class="{badge_cl}">{badge_tx}</div><br>'
            f'<div class="{prob_cl}">{p_pct}%</div>'
            f'<div class="prob-sub">Calibrated AKI Risk</div>'
            f'<div class="prob-sub" style="margin-top:8px;">Threshold: ≥ {round(threshold*100)}% → High Risk</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if show_tech:
            with st.expander("🔧 Technical Details", expanded=True):
                sg_a = model["cal_a"]; sg_b = model["cal_b"]
                st.markdown(
                    f"| Parameter | Value |\n|-----------|-------|\n"
                    f"| Linear predictor (lp) | `{res['lp']:.5f}` |\n"
                    f"| Raw probability (p_raw) | `{res['p_raw']*100:.2f}%` |\n"
                    f"| Calibrated probability (p_cal) | `{res['p_cal']*100:.2f}%` |\n"
                    f"| Calibration intercept (a) | `{sg_a:.5f}` |\n"
                    f"| Calibration slope (b) | `{sg_b:.5f}` |\n"
                    f"| Source | `sigmoid(a + b × logit(p_raw))` |"
                )

        # Build report
        meds_on = [
            model["categorical"][k]["en"]
            for k in model["categorical"]
            if model["categorical"][k]["type"] == "binary"
            and sg_inputs.get(k, model["categorical"][k]["impute"]) == 1
        ]
        fk506_line = ""
        if "FK506" in model["categorical"]:
            fk_val = sg_inputs.get("FK506", "全程窗内")
            fk_en  = model["categorical"]["FK506"]["levels"].get(fk_val, {}).get("en", fk_val)
            fk506_line = f"FK506 status: {fk_en}\n"

        labs_filled = [
            f"{model['numeric'][k]['en']}={sg_inputs[k]} {model['numeric'][k]['unit']}"
            for k in model["numeric"] if sg_inputs.get(k) is not None
        ]
        report = (
            f"[AKI Risk Prediction Result]\n"
            f"Subgroup model: SG{sg_choice} — {model['name']}\n"
            f"Calibrated risk: {p_pct}%\n"
            f"Risk group: {res['risk_label']} (threshold ≥ {round(threshold*100)}%)\n"
            f"{fk506_line}"
            f"Medications used: {', '.join(meds_on) if meds_on else 'None'}\n"
            f"Lab values entered: {'; '.join(labs_filled) if labs_filled else 'All imputed (medians)'}\n"
            f"---\n"
            f"Raw probability (p_raw): {round(res['p_raw']*100,2)}%\n"
            f"Linear predictor (lp): {round(res['lp'],4)}\n"
            f"Calibration: a={model['cal_a']:.4f}, b={model['cal_b']:.4f}\n"
            f"---\n"
            f"Disclaimer: This result is for decision support only and does not replace clinical judgment."
        )
        st.code(report, language=None)
        st.caption("Select all text above (Ctrl+A / Cmd+A) and copy.")
        if st.button("📋 Mark as copied", key="copy_btn"):
            st.success("✅ Result noted — please copy the text above.")

    else:
        st.markdown(
            '<div style="text-align:center;padding:52px 0;color:#9ca3af;font-size:0.9rem;">'
            f'Using model: <b>SG{sg_choice}</b><br><br>'
            'Fill in the inputs on the left,<br>then click <b>Calculate AKI Risk</b>.'
            '</div>',
            unsafe_allow_html=True,
        )

    # Disclaimer
    st.markdown("""
<div class="disclaimer">
<b>⚠️ Disclaimer</b><br>
This tool is based on retrospective single-center data and is intended
<b>for clinical decision support only</b>. It does not replace the judgment
of a qualified clinician.<br><br>
<b>Applicable:</b> Adult kidney transplant recipients during hospitalization
with the required laboratory and medication data available.<br>
<b>Not applicable:</b> Pediatric transplants, combined organ transplants,
or centers with substantially different patient populations from the training cohort.<br><br>
The authors assume no liability for clinical decisions made using this tool.
</div>
""", unsafe_allow_html=True)

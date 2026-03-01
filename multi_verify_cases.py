# =============================================================
#  verify_cases.py  —  12 synthetic cases × 3 subgroups
#  Run: python verify_cases.py
#  Compare p_cal with Streamlit UI (tolerance ±0.1%)
#  All three C01=C08 checks should print PASS.
# =============================================================

import math

# ─────────────────────────────────────────────────────────────
#  MODEL PARAMETERS  (must be identical to app.py)
# ─────────────────────────────────────────────────────────────

MODELS = {

1: {
    "intercept": -3.9167448076114226,
    "cal_a": -0.07942559395364185, "cal_b": 0.8785993043794286,
    "numeric": {
        "肌酐":              {"coef":-0.12171722561434864, "mean":948.7558624577226,  "sd":275.6164167090626,  "impute":921.95},
        "尿素":              {"coef":-0.3023789899558171,  "mean":23.64792559188275,  "sd":7.791569721067218,  "impute":23.0},
        "尿酸":              {"coef":-0.1029981119949067,  "mean":363.7528748590756,  "sd":108.63740508559044, "impute":363.0},
        "血小板计数":        {"coef":-0.25578579561362463, "mean":203.5445321307779,  "sd":63.742400046407504, "impute":198.0},
        "中性粒细胞计数":    {"coef":0.34915353968100615,  "mean":4.722626832018038,  "sd":1.7641006381219,    "impute":4.45},
        "白蛋白_溴甲酚绿法_":{"coef":0.09257794730085031,  "mean":44.950394588500565, "sd":5.161788028424633,  "impute":45.3},
        "总蛋白":            {"coef":0.07790231620949731,  "mean":74.3042841037204,   "sd":8.42541678122355,   "impute":74.2},
        "碱性磷酸酶":        {"coef":0.07048430674575476,  "mean":98.13438556933484,  "sd":74.93148182642358,  "impute":81.0},
        "血糖":              {"coef":0.03958255360790811,  "mean":5.702570462232244,  "sd":2.0281537967790007, "impute":5.24},
        "未结合胆红素_干_":  {"coef":0.03543514228538939,  "mean":2.685569334836528,  "sd":2.406346196041616,  "impute":2.0},
    },
    "categorical": {
        "贫血":    {"coef":0.4858706450249856,   "impute":0, "type":"binary"},
        "抗酸药":  {"coef":0.7139132108386299,   "impute":0, "type":"binary"},
        "利尿药":  {"coef":1.0295177465151235,   "impute":0, "type":"binary"},
        "抗凝药":  {"coef":0.556711512176789,    "impute":0, "type":"binary"},
        "吸附剂":  {"coef":0.45794909286951757,  "impute":0, "type":"binary"},
        "促凝药":  {"coef":-0.0067058806661859606,"impute":0,"type":"binary"},
        "钙补充剂":{"coef":0.40015206779688917,  "impute":0, "type":"binary"},
        "麻醉药":  {"coef":0.44558132631953307,  "impute":0, "type":"binary"},
        "免疫球蛋白":{"coef":0.4689831390847565, "impute":0, "type":"binary"},
        "正性肌力药":{"coef":0.16445562461763166,"impute":0, "type":"binary"},
        "抗癫痫药":{"coef":0.953131795592225,    "impute":0, "type":"binary"},
        "胃肠黏膜保护剂":{"coef":0.7226057588799102,"impute":0,"type":"binary"},
        "升白药":  {"coef":1.1094327588070032,   "impute":0, "type":"binary"},
        "抗痛风":  {"coef":1.0133550727295633,   "impute":0, "type":"binary"},
        "FK506":   {"type":"multiclass","impute":"全程窗内","ref":"全程窗内",
                   "levels":{"全程窗内":{"coef":0.0},"曾超窗":{"coef":0.40498607000779124},"全程超窗":{"coef":1.2916688217943653}}},
    },
},

2: {
    "intercept": -3.6606838134695305,
    "cal_a": -0.07942559395364185, "cal_b": 0.8785993043794286,
    "numeric": {
        "胱抑素c":          {"coef":0.14049844803376624,  "mean":2.251268656716418,  "sd":1.0884978157937424,  "impute":2.01},
        "单核细胞百分比":   {"coef":-0.16394161639759547, "mean":0.08298694029850745,"sd":0.03735117004955886, "impute":0.081},
        "中性粒细胞计数":   {"coef":0.15124652387278295,  "mean":5.906927238805971,  "sd":4.0337514945402635,  "impute":4.92},
        "平均血红蛋白含量": {"coef":0.2813782662919976,   "mean":29.975373134328358, "sd":1.6676212644561401,  "impute":29.9},
        "淋巴细胞计数":     {"coef":-0.3083915711748147,  "mean":0.9738078358208956, "sd":0.6252379505351112,  "impute":0.895},
        "红细胞计数":       {"coef":-0.03486010199222113, "mean":3.750298507462687,  "sd":0.7929064617985853,  "impute":3.76},
        "红细胞宽度_sd值":  {"coef":-0.030260712410191307,"mean":48.43824626865672,  "sd":7.804061078213451,   "impute":46.25},
        "血小板计数":       {"coef":-0.05681115667179618, "mean":185.85261194029852, "sd":67.9867381210626,    "impute":181.0},
        "钙":               {"coef":-0.18298658500570214, "mean":2.2747015111940296, "sd":0.1666266076882498,  "impute":2.28},
    },
    "categorical": {
        "ICU":       {"coef":1.3289105514872415, "impute":0, "type":"binary"},
        "血管活性药":{"coef":0.6230129734325999, "impute":1, "type":"binary"},
        "精神治疗药":{"coef":0.7279208805888284, "impute":0, "type":"binary"},
        "利尿药":    {"coef":0.5755679515794798, "impute":0, "type":"binary"},
        "扩容药":    {"coef":0.37311253758337565,"impute":0, "type":"binary"},
        "抗凝药":    {"coef":0.19970962654843802,"impute":0, "type":"binary"},
    },
},

3: {
    "intercept": -6.577238277941135,
    "cal_a": 0.05012968694220859, "cal_b": 0.8305403277675305,
    "numeric": {
        "天门冬氨酸转氨酶": {"coef":-0.14752481304709783, "mean":248.556,            "sd":716.0954177385199,  "impute":36.0},
        "尿酸":             {"coef":-0.03717360054442158, "mean":263.90736842105264, "sd":138.29580854637587, "impute":247.0},
        "单核细胞计数":     {"coef":-0.18737845378501594, "mean":0.48213263157894737,"sd":0.3052043548154874, "impute":0.43},
        "中性粒细胞百分比": {"coef":-0.21167006875203523, "mean":0.7788094736842104, "sd":0.1502850380014305, "impute":0.8075},
        "总胆红素":         {"coef":0.0639750223438938,   "mean":51.12374736842105,  "sd":90.64991607775816,  "impute":17.75},
        "钾离子":           {"coef":0.21316561818233884,  "mean":3.911894736842105,  "sd":0.5458715768322727, "impute":3.9},
        "胆碱酯酶":         {"coef":-0.3073241702220932,  "mean":5065.368421052632,  "sd":2671.8257020548076, "impute":4460.0},
        "平均血小板体积":   {"coef":-0.3185478313247615,  "mean":11.265894736842103, "sd":1.1458735989231714, "impute":11.2},
        "凝血酶比率":       {"coef":-0.10702741775538163, "mean":1.1097473684210524, "sd":0.4182307841477768, "impute":1.02},
        "纤维蛋白原含量":   {"coef":-0.29100163788847,    "mean":2.680768421052631,  "sd":1.4525332821814705, "impute":2.375},
        "补_间接胆红素":    {"coef":0.09382049132083763,  "mean":13.472842105263158, "sd":24.547556408055126, "impute":6.7},
        "补_前白蛋白":      {"coef":-0.1372712532572401,  "mean":163.73894736842107, "sd":81.3323817103707,   "impute":151.5},
    },
    "categorical": {
        "促凝药":    {"coef":1.9211935939524067, "impute":0, "type":"binary"},
        "抗凝药":    {"coef":1.8941241830686304, "impute":0, "type":"binary"},
        "免疫球蛋白":{"coef":1.3354586838669351, "impute":0, "type":"binary"},
        "祛痰药":    {"coef":1.2280590672511853, "impute":0, "type":"binary"},
        "矿物质补充剂":{"coef":0.9528031965954611,"impute":0,"type":"binary"},
        "肝硬化":    {"coef":0.5279482157819856, "impute":0, "type":"binary"},
        "精神治疗药":{"coef":0.5477635150152356, "impute":0, "type":"binary"},
        "NSAID":     {"coef":0.5162383329406315, "impute":0, "type":"binary"},
    },
},

}  # end MODELS

# ─────────────────────────────────────────────────────────────
def sigmoid(x): return 1.0/(1.0+math.exp(-x))
def logit(p):
    p=max(1e-9,min(1-1e-9,p)); return math.log(p/(1.0-p))

def predict(sg, inputs):
    m  = MODELS[sg]; lp = m["intercept"]
    for k,p in m["numeric"].items():
        v=inputs.get(k); v=p["impute"] if v is None else v
        lp += p["coef"]*(v-p["mean"])/p["sd"]
    for k,p in m["categorical"].items():
        if p["type"]=="multiclass":
            chosen=inputs.get(k,p["impute"])
            lp += p["levels"].get(chosen,p["levels"][p["ref"]])["coef"]
        else:
            v=inputs.get(k); v=p["impute"] if v is None else int(v)
            lp += p["coef"]*v
    p_raw=sigmoid(lp); p_cal=sigmoid(m["cal_a"]+m["cal_b"]*logit(p_raw))
    return {"lp":round(lp,5),"p_raw":round(p_raw,6),"p_cal":round(p_cal,6)}

def base(sg):
    m=MODELS[sg]; d={k:None for k in m["numeric"]}
    for k,p in m["categorical"].items():
        d[k]=p.get("impute","全程窗内") if p["type"]=="multiclass" else None
    return d
def mg(b,o): d=dict(b);d.update(o);return d


# ─────────────────────────────────────────────────────────────
#  TEST CASE DEFINITIONS
# ─────────────────────────────────────────────────────────────

CASES = {

1: [
    ("C01","All missing → medians + binary=0 + FK506=Consistently",
     base(1)),
    ("C02","All binary=1, FK506=Never on Target, high-risk labs",
     mg(base(1),{k:1 for k in MODELS[1]["categorical"] if MODELS[1]["categorical"][k]["type"]=="binary"}|
                {"FK506":"全程超窗","肌酐":200,"中性粒细胞计数":15,"血小板计数":50})),
    ("C03","FK506=Never on Target only",
     mg(base(1),{"FK506":"全程超窗"})),
    ("C04","FK506=Intermittently on Target only",
     mg(base(1),{"FK506":"曾超窗"})),
    ("C05","G-CSF=1 + Anti-Gout=1 + Diuretics=1 (three largest coef)",
     mg(base(1),{"升白药":1,"抗痛风":1,"利尿药":1})),
    ("C06","Creatinine=200 (very low, negative coef → higher z-contrib)",
     mg(base(1),{"肌酐":200})),
    ("C07","Neutrophil=15 (very high, positive coef)",
     mg(base(1),{"中性粒细胞计数":15})),
    ("C08","Explicit medians (must equal C01)",
     mg(base(1),{k:v["impute"] for k,v in MODELS[1]["numeric"].items()})),
    ("C09","Anemia=1 + Antiepileptics=1 + FK506=Intermittent",
     mg(base(1),{"贫血":1,"抗癫痫药":1,"FK506":"曾超窗"})),
    ("C10","Platelet=30, BUN=60 (both negative coef, extreme low)",
     mg(base(1),{"血小板计数":30,"尿素":60})),
    ("C11","All binary=1, FK506=Consistently on Target",
     mg(base(1),{k:1 for k in MODELS[1]["categorical"] if MODELS[1]["categorical"][k]["type"]=="binary"}|
                {"FK506":"全程窗内"})),
    ("C12","Procoagulant=1 only (coef ≈ −0.007, near zero)",
     mg(base(1),{"促凝药":1})),
],

2: [
    ("C01","All missing → medians + cat defaults (vasopressors impute=1)",
     base(2)),
    ("C02","All binary=1, high-risk labs",
     mg(base(2),{k:1 for k in MODELS[2]["categorical"]}|
                {"胱抑素c":5.0,"中性粒细胞计数":15.0,"平均血红蛋白含量":35.0})),
    ("C03","ICU=1 only",
     mg(base(2),{"ICU":1})),
    ("C04","Vasopressors=0 (overrides impute=1)",
     mg(base(2),{"血管活性药":0})),
    ("C05","Cystatin-C=5.0 (high)",
     mg(base(2),{"胱抑素c":5.0})),
    ("C06","Lymphocyte=0.1 (very low, negative coef)",
     mg(base(2),{"淋巴细胞计数":0.1})),
    ("C07","Calcium=1.6 (very low, negative coef)",
     mg(base(2),{"钙":1.6})),
    ("C08","Explicit medians (must equal C01)",
     mg(base(2),{k:v["impute"] for k,v in MODELS[2]["numeric"].items()})),
    ("C09","Psychotropics=1 + Diuretics=1 + CysC=4.0",
     mg(base(2),{"精神治疗药":1,"利尿药":1,"胱抑素c":4.0})),
    ("C10","MCH=35, Monocyte%=0.02",
     mg(base(2),{"平均血红蛋白含量":35.0,"单核细胞百分比":0.02})),
    ("C11","Platelet=30, Calcium=2.8",
     mg(base(2),{"血小板计数":30.0,"钙":2.8})),
    ("C12","All binary=1, labs at medians",
     mg(base(2),{k:1 for k in MODELS[2]["categorical"]})),
],

3: [
    ("C01","All missing → medians, all cat=0",
     base(3)),
    ("C02","All binary=1, extreme high-risk labs",
     mg(base(3),{k:1 for k in MODELS[3]["categorical"]}|
                {"总胆红素":300,"钾离子":6.5,"补_间接胆红素":100})),
    ("C03","Procoagulants=1 + Anticoagulants=1 (two largest coef)",
     mg(base(3),{"促凝药":1,"抗凝药":1})),
    ("C04","IVIG=1 + Expectorants=1",
     mg(base(3),{"免疫球蛋白":1,"祛痰药":1})),
    ("C05","ChE=500 (very low, negative coef → higher risk)",
     mg(base(3),{"胆碱酯酶":500})),
    ("C06","Potassium=6.5 (high, positive coef)",
     mg(base(3),{"钾离子":6.5})),
    ("C07","Total bilirubin=300 (high, positive coef)",
     mg(base(3),{"总胆红素":300})),
    ("C08","Explicit medians (must equal C01)",
     mg(base(3),{k:v["impute"] for k,v in MODELS[3]["numeric"].items()})),
    ("C09","Cirrhosis=1 + Mineral supplements=1",
     mg(base(3),{"肝硬化":1,"矿物质补充剂":1})),
    ("C10","MPV=7.0 (very low, negative coef → higher lp contribution)",
     mg(base(3),{"平均血小板体积":7.0})),
    ("C11","Fibrinogen=0.5 (very low, negative coef)",
     mg(base(3),{"纤维蛋白原含量":0.5})),
    ("C12","NSAIDs=1 + Psychotropics=1 + Potassium=5.5",
     mg(base(3),{"NSAID":1,"精神治疗药":1,"钾离子":5.5})),
],

}

# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    THRESHOLD = 0.30
    SG_NAMES  = {1:"Post-KT Full (FK506)", 2:"Post-KT Hematology/ICU", 3:"Hepatic/Coag"}

    all_pass = True
    for sg in [1,2,3]:
        print()
        print("="*72)
        m=MODELS[sg]
        print(f"  Subgroup {sg}: {SG_NAMES[sg]}")
        print(f"  intercept={m['intercept']:.4f}  cal_a={m['cal_a']:.4f}  cal_b={m['cal_b']:.4f}  threshold={THRESHOLD}")
        print("="*72)
        print(f"{'ID':<5} {'p_raw':>8} {'p_cal':>8} {'Risk':<5}  Description")
        print("-"*72)
        for cid,desc,inp in CASES[sg]:
            r=predict(sg,inp); risk="HIGH" if r["p_cal"]>=THRESHOLD else "LOW"
            print(f"{cid:<5} {r['p_raw']*100:>7.2f}% {r['p_cal']*100:>7.2f}% {risk:<5}  {desc}")

        # Sanity: C01 == C08
        pc1=predict(sg,dict(CASES[sg][0][2]))["p_cal"]
        pc8=predict(sg,dict(CASES[sg][7][2]))["p_cal"]
        ok = abs(pc1-pc8)<1e-8
        all_pass &= ok
        print(f"\n  C01=C08 impute check: {pc1*100:.4f}% == {pc8*100:.4f}% → {'✅ PASS' if ok else '❌ FAIL'}")

        # SG2 specific: C04 vasopressor=0 must be less than C01
        if sg==2:
            pc4=predict(2,dict(CASES[2][3][2]))["p_cal"]
            ok2=pc4<pc1
            all_pass&=ok2
            print(f"  C04 < C01 (vasopressor override): {ok2 and '✅ PASS' or '❌ FAIL'}")

    print()
    print("="*72)
    print(f"  Overall: {'✅ ALL CHECKS PASSED' if all_pass else '❌ SOME CHECKS FAILED'}")
    print(f"  Tolerance: ±0.1% acceptable when comparing with Streamlit UI.")
    print("="*72)

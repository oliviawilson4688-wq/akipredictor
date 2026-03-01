# Post-Kidney Transplant AKI Risk Calculator — Multi-Subgroup Edition

Three subgroup models in one app | LASSO-Logistic Regression + Logistic Calibration | Outcome: AKI

---

## 🚀 Access URL

After launching, the terminal shows:
```
Local URL:  http://localhost:8501
```
Open **`http://localhost:8501`** in any browser.

---

## Local Run

### Requirements
- Python ≥ 3.9
- pip

### Steps

```bash
# 1. Go to project folder
cd aki_multigroup/

# 2. (Recommended) Virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch
streamlit run app.py
```

---

## Verify Prediction Logic

```bash
python verify_cases.py
```

Runs 12 synthetic cases per subgroup (36 total) and prints a table of p_cal + risk labels.
All three C01=C08 checks must print ✅ PASS.

### Expected values summary

**Subgroup 1 (Post-KT Full / FK506)**
| ID | p_cal | Risk | Description |
|----|-------|------|-------------|
| C01 | 2.81% | LOW | All defaults |
| C02 | 99.96% | **HIGH** | All risk factors on |
| C03 | 8.27% | LOW | FK506 = Never on Target |
| C05 | 31.60% | **HIGH** | G-CSF + Anti-Gout + Diuretics |
| C11 | 98.09% | **HIGH** | All binary=1, FK506=Consistently |

**Subgroup 2 (Post-KT Hematology/ICU)**
| ID | p_cal | Risk | Description |
|----|-------|------|-------------|
| C01 | 5.89% | LOW | All defaults (vasopressors imputed as Used) |
| C02 | 81.33% | **HIGH** | All risk factors on |
| C04 | 3.49% | LOW | Vasopressors=0 (overrides default=Used) |
| C12 | 51.10% | **HIGH** | All binary=1, labs at medians |

**Subgroup 3 (Hepatic/Coag)**
| ID | p_cal | Risk | Description |
|----|-------|------|-------------|
| C01 | 0.51% | LOW | All defaults (very low base rate) |
| C02 | 96.93% | **HIGH** | All risk factors on |
| C03 | 10.95% | LOW | Procoagulants + Anticoagulants |

> Subgroup 3 has a very low baseline risk (intercept = −6.58), so most individual-variable perturbations remain LOW risk. Only combined adverse factors reach HIGH.

---

## Deploy to Streamlit Community Cloud (Free)

### 1. Push to GitHub

```bash
git init
git add app.py requirements.txt README.md verify_cases.py labels_en.json
git commit -m "AKI multi-subgroup calculator"
git remote add origin https://github.com/YOUR_USERNAME/aki-multigroup.git
git push -u origin main
```

### 2. Deploy

1. Go to **https://share.streamlit.io** (log in with GitHub)
2. Click **New app**
3. Select your repo, branch (`main`), main file (`app.py`)
4. Click **Deploy** — takes ~2 min
5. Access at: `https://YOUR_USERNAME-aki-multigroup-app-XXXX.streamlit.app`

### Other Free Platforms

| Platform | Notes |
|----------|-------|
| Streamlit Community Cloud | Easiest — https://share.streamlit.io |
| Hugging Face Spaces | Supports Streamlit — https://huggingface.co/spaces |
| Render | Free web service — https://render.com |

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'streamlit'` | Not installed | `pip install streamlit` |
| `streamlit: command not found` | PATH issue | `python -m streamlit run app.py` |
| `Address already in use (port 8501)` | Port busy | `streamlit run app.py --server.port 8502` |
| Chinese characters garbled | Encoding issue | Ensure `app.py` is saved as **UTF-8** |
| Blank page after cloud deploy | Missing dependency | Check `requirements.txt` has `streamlit>=1.32.0` |
| Google Fonts timeout | Network blocked | Delete the `@import url(...)` line in `app.py` |

---

## UI Description

```
┌──────────────────────────────────────────────────────────────────┐
│  🏥 Post-Kidney Transplant AKI Risk Calculator                   │
│  Multi-Subgroup Edition | LASSO-Logistic + Logistic Calibration  │
│  [SG1 — Tacrolimus] badge                                        │
├─────────────────────────────────────┬────────────────────────────┤
│  LEFT PANEL (Inputs)                │  RIGHT PANEL (Results)     │
│                                     │                            │
│  ── Tacrolimus Status (SG1 only) ─  │  [▶ Calculate AKI Risk]    │
│    Selectbox: Consistently /        │                            │
│    Intermittently / Never on Target │  ┌──────────────────────┐ │
│                                     │  │ HIGH RISK  (red)     │ │
│  ── Baseline / Diagnosis ─────────  │  │  or                  │ │
│    Anemia (SG1) / ICU (SG2) /       │  │ LOW RISK   (green)   │ │
│    Liver Cirrhosis (SG3)            │  │  XX.X%               │ │
│                                     │  │  Calibrated Risk     │ │
│  ── Medications ───────────────────  │  └──────────────────────┘ │
│    Radio buttons (No/Yes)           │                            │
│    4-column grid for SG1 (14 drugs) │  [Technical Details ▼]    │
│    Vasopressor ⚠️ warning (SG2)     │    p_raw, lp, cal a/b     │
│                                     │                            │
│  ── Laboratory Tests ─────────────  │  [📋 Mark as copied]      │
│    2-column numeric inputs          │                            │
│    Each shows: unit + median hint   │  ⚠️ Disclaimer             │
│    Leave blank → auto-impute median │                            │
└─────────────────────────────────────┴────────────────────────────┘

SIDEBAR:
  Subgroup selector (SG1 / SG2 / SG3)
  Risk threshold slider (0.10–0.70, default 0.30)
  Show technical details toggle
  Active model parameters display
```

---

## Model Parameters Summary

| | Subgroup 1 | Subgroup 2 | Subgroup 3 |
|-|-----------|-----------|-----------|
| **Name** | Post-KT Full (FK506) | Post-KT Hematology/ICU | Hepatic/Coag |
| **Intercept** | −3.9167 | −3.6607 | −6.5772 |
| **Cal. a** | −0.07943 | −0.07943 | +0.05013 |
| **Cal. b** | 0.87860 | 0.87860 | 0.83054 |
| **Numeric vars** | 10 | 9 | 12 |
| **Categorical vars** | 14 binary + 1 multi (FK506) | 6 binary | 8 binary |
| **Cal. source** | shrunk1 recalibration block | global default | shrunk3 recalibration block |

```
Prediction formula (all subgroups):
  z_i   = (x_i − mean_i) / sd_i          # z-standardization per variable
  lp    = intercept + Σ(coef_i × z_i)    # continuous contributions
          + Σ(coef_j × I(drug_j=1))      # binary medication contributions
          + coef_FK506[level]             # FK506 multi-class (SG1 only)
  p_raw = sigmoid(lp)
  p_cal = sigmoid(a + b × logit(p_raw))  # logistic calibration
  risk  = HIGH if p_cal ≥ threshold else LOW
```

---

## TODOs (from labels_en.json low-confidence items)

1. **Monocyte Percentage (SG2)** — input as decimal proportion (0.08 = 8%). Confirm unit with your lab.
2. **Neutrophil Percentage (SG3)** — input as decimal proportion (0.78 = 78%). Confirm unit with your lab.
3. **Thrombin Ratio (SG3)** — confirm exact assay name (Thrombin Ratio, PT Ratio, or TT Ratio).
4. **Indirect Bilirubin supplemental (SG3 `补_间接胆红素`)** — confirm whether repeat or different assay.
5. **Prealbumin supplemental (SG3 `补_前白蛋白`)** — confirm prealbumin (PAB), not albumin.
6. **Vasopressors (SG2)** — imputation default = 1 (Used). Confirm this is appropriate for your population.
7. **Subgroup 3 calibration** — uses unique `a=+0.0501, b=0.8305` from shrunk3. Verify these are the intended values.

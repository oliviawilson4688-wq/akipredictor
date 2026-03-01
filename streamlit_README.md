# 肾移植后 AKI 风险预测计算器

基于 LASSO-Logistic 回归 + 逻辑校准 | 1268 例肾移植患者 | 测试集 AUC = 0.797

---

## 快速开始：访问地址

启动后在终端看到：
```
Local URL:  http://localhost:8501
```
**直接在浏览器打开 `http://localhost:8501`**

---

## 本地运行

### 环境要求
- Python >= 3.9
- pip

### 安装与启动

```bash
# 1. 进入项目目录
cd aki_predictor/

# 2. （推荐）创建虚拟环境
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动
streamlit run app.py
```

浏览器会自动打开，或手动访问 `http://localhost:8501`

---

## 核验预测逻辑

```bash
python verify_cases.py
```

输出 10 条样例的 p_cal，与页面逐条对照（允许 ±0.1% 误差）：

| 编号 | 案例 | p_cal | 风险 |
|------|------|-------|------|
| C01 | 全部默认/缺失 | **2.8%** | 低 |
| C02 | 全部风险因素 | **99.4%** | 高 |
| C03 | 肌酐/尿素极高 | **0.5%** | 低 |
| C04 | 中性粒细胞/血糖极高 | **35.8%** | 高 |
| C05 | FK506间歇性达标 | **4.0%** | 低 |
| C06 | 利尿药+升白药+抗痛风 | **31.6%** | 高 |
| C07 | 全部填中位数（应=C01） | **2.8%** | 低 |
| C08 | 血小板/白蛋白极低+贫血 | **5.1%** | 低 |
| C09 | FK506从未达标+三药 | **42.4%** | 高 |
| C10 | 肌酐极低(200) | **3.7%** | 低 |

---

## 部署到 Streamlit Community Cloud（免费）

### 前提
- GitHub 账号
- Streamlit 账号（用 GitHub 登录：https://streamlit.io）

### 步骤

```bash
# 1. 将项目推送到 GitHub
git init
git add app.py requirements.txt README.md verify_cases.py
git commit -m "initial commit"
git remote add origin https://github.com/你的用户名/aki-predictor.git
git push -u origin main
```

2. 登录 https://share.streamlit.io
3. 点击 **New app**
4. 选择你的 GitHub 仓库、分支（main）、主文件（app.py）
5. 点击 **Deploy** → 等待约 2 分钟
6. 获得公开 URL，例如：`https://你的用户名-aki-predictor-app-xxxx.streamlit.app`

### 其他免费部署方案

| 平台 | 说明 | 链接 |
|------|------|------|
| Streamlit Community Cloud | 最简单，GitHub 直连 | https://share.streamlit.io |
| Hugging Face Spaces | 支持 Streamlit，免费 GPU 可选 | https://huggingface.co/spaces |
| Railway | 每月 $5 免费额度，Docker 部署 | https://railway.app |
| Render | 免费静态+Web Service | https://render.com |

---

## 常见报错处理

| 报错信息 | 原因 | 解决方法 |
|---------|------|---------|
| `ModuleNotFoundError: No module named 'streamlit'` | 未安装 | `pip install streamlit` |
| `streamlit: command not found` | PATH 问题 | 用 `python -m streamlit run app.py` |
| `OSError: [Errno 98] Address already in use` | 端口 8501 被占 | `streamlit run app.py --server.port 8502` |
| 页面中文乱码 | 文件编码问题 | 确保 app.py 以 **UTF-8** 保存 |
| 云端部署后页面空白 | requirements.txt 缺包 | 检查是否包含 `streamlit>=1.32.0` |
| Google Fonts 加载慢 | 网络访问受限 | 删除 app.py 中 `@import url(...)` 行，使用系统默认字体 |

---

## 模型参数说明

```
截距（Intercept）：  -3.9167448076114226
校准截距（a）：      -0.07942559395364185
校准斜率（b）：       0.8785993043794286
默认风险阈值：        0.30（Youden 指数最优，页面可调）

预测公式：
  z_i = (x_i - mean_i) / sd_i          # 连续变量标准化
  lp  = 截距 + Σ coef_i * z_i          # 连续变量贡献
        + Σ coef_j * I(药物j=1)        # 二分类变量贡献
        + coef_FK506[分类]              # FK506三分类
  p_raw = sigmoid(lp)
  p_cal = sigmoid(a + b * logit(p_raw)) # 逻辑校准

FK506 系数映射：
  持续达标（全程窗内）  → 0.0
  间歇性达标（曾超窗）  → 0.405
  从未达标（全程超窗）  → 1.292
```

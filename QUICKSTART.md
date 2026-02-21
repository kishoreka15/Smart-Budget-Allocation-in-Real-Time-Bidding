# 🚀 Quick Start Guide

## Run in 30 Seconds

```bash
cd "/Users/kishorem/Documents/final year project document/final year project"
source rtb_env/bin/activate
streamlit run final_app.py
```

**Then open**: http://localhost:8501

---

## What to Do Next

### In the Web App:

1. **Set Daily Budget** (sidebar)
   - Example: $5,000 - $50,000

2. **Configure Parameters**
   - Time Slots: 24 hours
   - CTR: 2-3%
   - Traffic: 500-1000

3. **Select Models**
   - ✅ Phase 1 (Heuristic)
   - ✅ Phase 2 (PPO)
   - Or both for comparison

4. **Click "Run Simulation"**

5. **View Results**
   - Performance metrics
   - Interactive charts
   - Comparison table
   - Key insights

---

## Key Results to Expect

**Phase 2 is ~15-20% Better than Phase 1**

- More clicks generated
- Higher revenue
- Better efficiency
- Same or less budget spent

---

## Troubleshooting

### If streamlit not found:
```bash
pip install streamlit plotly
```

### If port 8501 in use:
```bash
streamlit run final_app.py --server.port 8502
```

### Stop the app:
Press `Ctrl + C` in terminal

---

## Files Explained

| File | Purpose |
|------|---------|
| **final_app.py** | Main app - RUN THIS ⭐ |
| **PROJECT_DOCUMENTATION.md** | Full technical docs |
| **README.md** | Project overview |
| **requirements.txt** | Dependencies |

---

**That's it! Enjoy exploring your RTB dashboard!** 💰📊

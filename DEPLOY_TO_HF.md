# 🚀 Deploying to HuggingFace with Cloud MLOps

## Quick Deploy (5 Steps)

### 1️⃣ Get Prefect Cloud API Key (Free)
```bash
# Visit: https://app.prefect.cloud/
# Sign up (free) → Profile → API Keys → Create API Key
# Copy the key (you'll need it in step 3)
```

### 2️⃣ Prepare Deployment
```bash
# Activate venv
.\.venv\Scripts\activate

# Run preparation script
python prepare_hf_deployment.py

# This will:
# - Add all necessary files to git
# - Commit changes
# - Show HuggingFace secrets configuration
```

### 3️⃣ Add Secrets to HuggingFace Space
```
Go to: https://huggingface.co/spaces/kshitijk20/nss/settings

Add Repository Secret:
┌────────────────────────────────┐
│ Name:  PREFECT_API_KEY         │
│ Value: <paste your API key>    │
└────────────────────────────────┘

Click "Add secret"
```

### 4️⃣ Push to HuggingFace
```bash
git push hf main
```

### 5️⃣ Monitor Build
```
Watch logs at: https://huggingface.co/spaces/kshitijk20/nss

Look for:
✅ Prefect Cloud configured successfully
✅ Initialization complete!
✅ Starting FastAPI application...
```

---

## What Happens During Docker Build

When you push to HuggingFace, Docker will:

### Build Phase (Dockerfile)
```dockerfile
1. Install Python 3.13 slim
2. Copy requirements.txt → Install packages
   - fastapi, uvicorn
   - prefect>=2.14.0
   - evidently>=0.4.0
   - scikit-learn, pandas, numpy
3. Copy application code
4. Create directories (monitoring/reports, final_model)
5. Initialize SQLite database
6. Run cloud_config.py (check for secrets)
```

### Startup Phase (startup.sh)
```bash
1. Check for PREFECT_API_KEY environment variable
   ├─ If found: Configure Prefect Cloud connection
   │  ├─ Set PREFECT_API_KEY
   │  ├─ Set PREFECT_API_URL
   │  └─ Verify connection: prefect cloud workspace ls
   └─ If not found: Skip Prefect features

2. Check for EVIDENTLY_CLOUD_TOKEN (optional)
   ├─ If found: Enable Evidently Cloud
   └─ If not found: Use open-source Evidently

3. Create monitoring directories
4. Start FastAPI application
```

### Runtime (app.py)
```python
1. Initialize cloud_config.py
   - Load environment variables
   - Configure Prefect/Evidently
   
2. Start FastAPI with endpoints:
   GET  / → System status (shows cloud MLOps status)
   GET  /train → Trigger training (can use Prefect)
   POST /predict → Make predictions
```

---

## Secrets Configuration

### Required (for Cloud MLOps)

**PREFECT_API_KEY**
- **What:** API key from Prefect Cloud
- **Get it:** https://app.prefect.cloud/ → Profile → API Keys
- **Purpose:** Connect HF Space to Prefect Cloud for orchestration
- **Free:** Yes (Hobby tier: 2 users, 5 workflows, unlimited runs)

### Optional (Advanced)

**PREFECT_WORKSPACE**
- **What:** Your Prefect workspace name
- **Example:** `my-org/phishing-detection`
- **Purpose:** Specify exact workspace (if you have multiple)

**AUTO_DEPLOY_FLOWS**
- **What:** `true` or `false`
- **Purpose:** Auto-deploy Prefect flows on container start
- **Default:** `false`

**USE_PREFECT_FOR_TRAINING**
- **What:** `true` or `false`
- **Purpose:** Use Prefect Cloud when /train endpoint is called
- **Default:** `false` (direct training)

**EVIDENTLY_CLOUD_TOKEN**
- **What:** Evidently Cloud API token (paid service)
- **Get it:** https://www.evidentlyai.com/get-demo
- **Purpose:** Centralized monitoring dashboard
- **Note:** Open-source Evidently works without this

**MONITORING_ENABLED**
- **What:** `true` or `false`
- **Purpose:** Enable/disable monitoring features
- **Default:** `true`

**DRIFT_CHECK_ENABLED**
- **What:** `true` or `false`
- **Purpose:** Automated drift detection on predictions
- **Default:** `false`

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          HuggingFace Space (Container)              │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │ Environment Variables (Secrets from HF UI)    │ │
│  │ • PREFECT_API_KEY=pnu_xxx                     │ │
│  │ • AUTO_DEPLOY_FLOWS=true                      │ │
│  └───────────────────────────────────────────────┘ │
│                       ↓                             │
│  ┌───────────────────────────────────────────────┐ │
│  │ startup.sh (Container Initialization)         │ │
│  │ • Configures Prefect Cloud                    │ │
│  │ • Sets up Evidently                           │ │
│  │ • Creates directories                         │ │
│  └───────────────────────────────────────────────┘ │
│                       ↓                             │
│  ┌───────────────────────────────────────────────┐ │
│  │ cloud_config.py (Python Configuration)        │ │
│  │ • Reads env vars                              │ │
│  │ • Initializes monitoring                      │ │
│  └───────────────────────────────────────────────┘ │
│                       ↓                             │
│  ┌───────────────────────────────────────────────┐ │
│  │ app.py (FastAPI Application)                  │ │
│  │ • Serves predictions                          │ │
│  │ • Training endpoint                           │ │
│  │ • Reports status                              │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  https://kshitijk20-nss.hf.space                   │
└─────────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────────┐
│         Prefect Cloud (External Service)            │
│  • Flow orchestration                               │
│  • Scheduling (weekly training)                     │
│  • Monitoring dashboard                             │
│  • Execution logs                                   │
│                                                     │
│  https://app.prefect.cloud/                         │
└─────────────────────────────────────────────────────┘
```

---

## Testing After Deployment

### 1. Check System Status
```bash
curl https://kshitijk20-nss.hf.space/

# Response should show:
{
  "status": "running",
  "cloud_mlops": {
    "prefect_cloud": "enabled",  # ✅ If API key configured
    "evidently": "open-source",
    "monitoring": "enabled"
  }
}
```

### 2. Test Training Endpoint
```bash
curl -X GET "https://kshitijk20-nss.hf.space/train"

# With Prefect: "Training triggered via Prefect Cloud!"
# Without: "Training successfull !!"
```

### 3. Check Prefect Cloud Dashboard
```
1. Go to: https://app.prefect.cloud/
2. Navigate to "Flow Runs"
3. You should see training executions from HF Space
4. Click on a run to see logs and details
```

### 4. Test Prediction
```bash
curl -X POST "https://kshitijk20-nss.hf.space/predict" \
  -F "file=@data/phisingData.csv"

# Should return HTML table with predictions
```

---

## Build Logs Examples

### ✅ Successful Build with Prefect Cloud
```
Building Docker image...
Step 1/15 : FROM python:3.13-slim
Step 2/15 : COPY requirements.txt
Step 3/15 : RUN pip install -r requirements.txt
...
🚀 Starting Network Security System...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Prefect Cloud API Key detected
🔧 Configuring Prefect Cloud connection...
✅ Successfully connected to Prefect Cloud
✅ Initialization complete!
🌐 Starting FastAPI application...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:7860
```

### ⚠️ Build without Secrets (Still Works)
```
🚀 Starting Network Security System...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️  No PREFECT_API_KEY found - Prefect Cloud features disabled
   Set PREFECT_API_KEY in HuggingFace Space secrets to enable
ℹ️  No EVIDENTLY_CLOUD_TOKEN - Using open-source Evidently
✅ Initialization complete!
🌐 Starting FastAPI application...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INFO: Started server process
```

---

## Troubleshooting

### Secret not recognized
**Symptom:** Logs show "No PREFECT_API_KEY found"
**Fix:**
1. Verify secret name is exactly `PREFECT_API_KEY` (case-sensitive)
2. Check secret value has no extra spaces
3. Rebuild Space: Settings → Factory reboot

### Prefect connection fails
**Symptom:** "Could not connect to Prefect Cloud"
**Fix:**
1. Test API key locally first:
   ```bash
   export PREFECT_API_KEY="your-key"
   prefect cloud workspace ls
   ```
2. Regenerate key if expired
3. Check HF Space has internet access (should be fine)

### Builds but features don't work
**Symptom:** App runs but cloud features inactive
**Fix:**
1. Check `/` endpoint response for cloud status
2. Review build logs for initialization messages
3. Ensure secrets were added BEFORE rebuild

---

## Cost Summary

| Service | Cost | What You Get |
|---------|------|-------------|
| **HuggingFace Spaces** | FREE | Docker hosting, public URL |
| **Prefect Cloud** | FREE | 2 users, 5 workflows, unlimited runs |
| **Evidently (Open Source)** | FREE | Local HTML reports, 100+ metrics |
| **Evidently Cloud** | Paid | Centralized dashboard (optional) |

**Total Cost: $0** for complete MLOps stack! 🎉

---

## Next Steps

After successful deployment:

1. **Monitor Prefect Dashboard:** https://app.prefect.cloud/
2. **Test API:** https://kshitijk20-nss.hf.space/docs
3. **Review Documentation:** 
   - [CLOUD_MLOPS_SETUP.md](CLOUD_MLOPS_SETUP.md) - Complete cloud setup
   - [HF_SECRETS_SETUP.md](HF_SECRETS_SETUP.md) - Secrets reference
4. **Set up Automations:** Configure failure alerts in Prefect
5. **Schedule Training:** Deploy weekly training flow

---

## Support Resources

- **Prefect Cloud:** https://docs.prefect.io/latest/cloud/
- **HuggingFace Spaces:** https://huggingface.co/docs/hub/spaces
- **Evidently:** https://docs.evidentlyai.com/
- **FastAPI:** https://fastapi.tiangolo.com/

---

## Files Created for Cloud MLOps

- ✅ **startup.sh** - Container initialization script
- ✅ **cloud_config.py** - Cloud services configuration
- ✅ **HF_SECRETS_SETUP.md** - Secrets documentation
- ✅ **CLOUD_MLOPS_SETUP.md** - Complete cloud guide
- ✅ **prepare_hf_deployment.py** - Deployment helper
- ✅ **Dockerfile** - Updated with cloud setup
- ✅ **app.py** - Integrated cloud features

All ready for `git push hf main`! 🚀

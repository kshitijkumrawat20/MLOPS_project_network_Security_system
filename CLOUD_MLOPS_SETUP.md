# ☁️ Cloud MLOps Setup: Prefect Cloud + Evidently AI

Complete guide to setting up production-grade MLOps using **Prefect Cloud** and **Evidently AI Cloud** platforms.

---

## 🌟 Why Cloud Platforms?

### Prefect Cloud
- ✅ **Zero Infrastructure**: No server to manage
- ✅ **Hybrid Execution**: Control plane in cloud, workers in your infrastructure
- ✅ **Free Tier**: 2 users, 5 workflows, unlimited runs
- ✅ **SOC 2 Type II Certified**: Enterprise security
- ✅ **Real-time Monitoring**: Live dashboard at app.prefect.cloud

### Evidently AI Cloud
- ✅ **LLM & ML Monitoring**: 100+ built-in metrics
- ✅ **Synthetic Data Generation**: For testing edge cases
- ✅ **Automated Evaluation**: Continuous testing dashboards
- ✅ **No-Code Interface**: Domain experts can collaborate
- ✅ **Open Source Based**: Built on trusted Evidently library

---

## 1️⃣ Prefect Cloud Setup

### Step 1: Create Free Account
1. Go to: https://app.prefect.cloud/
2. Click **"Start Free"**
3. Sign up with GitHub, Google, or email
4. Create your first workspace (e.g., "phishing-detection")

### Step 2: Get API Key
```bash
# In Prefect Cloud dashboard:
# 1. Click on your profile (bottom left)
# 2. Go to "API Keys"
# 3. Click "Create API Key"
# 4. Name it "NSS-Project" and copy the key
```

### Step 3: Configure Local Environment
```bash
# Activate your venv
.\.venv\Scripts\activate

# Login to Prefect Cloud
prefect cloud login

# Paste your API key when prompted
# Or set it directly:
prefect config set PREFECT_API_KEY="your-api-key-here"

# Verify connection
prefect cloud workspace ls
```

### Step 4: Update Training Flow for Cloud
```python
# prefect_flows/training_flow.py already configured!
# Just run it and it will sync with Prefect Cloud
cd prefect_flows
python training_flow.py
```

### Step 5: Deploy to Prefect Cloud
```bash
# Create deployment with schedule
cd prefect_flows
python deploy_schedule.py

# This creates a deployment visible in Prefect Cloud dashboard
```

### Step 6: Run Worker (Local or Cloud)

**Option A: Run Worker Locally (Hybrid Model - Recommended)**
```bash
# Start worker on your machine (keeps data secure)
prefect agent start -q training

# Worker polls Prefect Cloud but executes in your environment
# Your data never leaves your infrastructure!
```

**Option B: Use Prefect Managed Execution (Fully Cloud)**
```python
# Update deploy_schedule.py to use managed pool:
deployment = Deployment.build_from_flow(
    flow=training_flow,
    name="weekly-training",
    work_pool_name="prefect-managed-pool",  # Use managed pool
    schedule=CronSchedule(cron="0 2 * * 0", timezone="UTC"),
)
```

### Step 7: Monitor in Dashboard
- Go to: https://app.prefect.cloud/
- View flow runs in real-time
- Check logs, states, and execution graphs
- Set up alerts and automations

---

## 2️⃣ Evidently AI Cloud Setup

### Understanding Evidently Cloud vs Open Source

**Open Source (What we have now):**
- Generate HTML reports locally
- Manual drift analysis
- No centralized dashboard

**Evidently Cloud (Upgrade):**
- Centralized monitoring dashboard
- Automated continuous testing
- Alerting and notifications
- Team collaboration
- Synthetic data generation

### Step 1: Get Access to Evidently Cloud
```bash
# Option A: Request Demo (Recommended for production)
# Go to: https://www.evidentlyai.com/get-demo
# Book a 1:1 demo to get:
# - Private cloud deployment
# - Custom risk assessment
# - Enterprise features

# Option B: Try Open Source First (What we currently have)
# Already installed! Just use local HTML reports
```

### Step 2: Current Setup (Open Source - Already Working)
```bash
# Test current Evidently monitoring
python test_evidently.py

# This generates reports in monitoring/reports/
# Open HTML files in browser
```

### Step 3: Integrate with Prefect Cloud

#### Update Drift Monitoring Flow:
```python
# prefect_flows/drift_monitoring_flow.py
# This flow already integrates both:
# 1. Evidently for drift detection
# 2. Prefect Cloud for orchestration

# Run it:
python prefect_flows/drift_monitoring_flow.py
```

#### Schedule Automated Drift Checks:
```python
# Create new file: prefect_flows/schedule_drift_monitoring.py
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from drift_monitoring_flow import drift_monitoring_flow

deployment = Deployment.build_from_flow(
    flow=drift_monitoring_flow,
    name="daily-drift-check",
    schedule=CronSchedule(cron="0 3 * * *", timezone="UTC"),  # Daily 3 AM
    work_queue_name="training",
    tags=["monitoring", "drift-detection"],
)

if __name__ == "__main__":
    deployment.apply()
    print("✅ Daily drift monitoring scheduled!")
```

---

## 3️⃣ Complete Cloud MLOps Workflow

### Architecture Overview
```
┌─────────────────────────────────────────────────────┐
│              PREFECT CLOUD (Control Plane)          │
│  - Flow orchestration                               │
│  - Scheduling (Weekly training, Daily drift check)  │
│  - Real-time monitoring dashboard                   │
│  - Event-driven automations                         │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│          YOUR INFRASTRUCTURE (Workers)              │
│  - Prefect Worker (polls cloud API)                 │
│  - Training pipeline execution                      │
│  - Model files (final_model/)                       │
│  - Evidently drift reports                          │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│            EVIDENTLY (Open Source)                  │
│  - Data drift detection                             │
│  - Quality reports                                  │
│  - HTML dashboards (local)                          │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│         HUGGINGFACE SPACES (Deployment)             │
│  - FastAPI app serving predictions                  │
│  - Model inference endpoint                         │
│  - Public access: kshitijk20-nss.hf.space          │
└─────────────────────────────────────────────────────┘
```

### Daily Operations

#### Morning: Check Dashboard
```
1. Open Prefect Cloud: https://app.prefect.cloud/
2. Review overnight flow runs
3. Check for any failures or warnings
4. View execution graphs and logs
```

#### Weekly: Automated Training
```
Every Sunday 2 AM UTC:
→ Prefect Cloud triggers training flow
→ Worker executes pipeline in your environment
→ New model saved to final_model/
→ Logs visible in Prefect dashboard
```

#### Daily: Drift Monitoring
```
Every day 3 AM UTC:
→ Drift monitoring flow runs
→ Evidently checks for data drift
→ If drift > 30%, triggers retraining
→ Report saved to monitoring/reports/
→ Notification sent (if configured)
```

---

## 4️⃣ Setup Commands (Step-by-Step)

### One-Time Setup
```bash
# 1. Activate environment
.\.venv\Scripts\activate

# 2. Login to Prefect Cloud
prefect cloud login
# Paste your API key

# 3. Create deployments
cd prefect_flows
python deploy_schedule.py  # Weekly training

# 4. Start worker (keep running in background)
# Terminal 1:
prefect agent start -q training

# 5. Test flows manually
# Terminal 2:
python training_flow.py
python drift_monitoring_flow.py
```

### Verify Everything Works
```bash
# Check Prefect Cloud connection
prefect cloud workspace ls

# Check deployments
prefect deployment ls

# Run training manually
cd prefect_flows
python training_flow.py

# Check Prefect Cloud dashboard
# Go to: https://app.prefect.cloud/
# You should see your flow run!

# Generate Evidently report
python test_evidently.py
# Check monitoring/reports/ for HTML files
```

---

## 5️⃣ Cost Breakdown

### Prefect Cloud
| Tier | Price | Features |
|------|-------|----------|
| **Hobby (Free)** | $0 | 2 users, 5 workflows, unlimited runs |
| **Pro** | Pay per user | Unlimited workflows, SSO, RBAC |
| **Enterprise** | Custom | Private deployment, dedicated support |

**Recommendation**: Start with Free tier (sufficient for this project)

### Evidently AI
| Option | Price | Features |
|--------|-------|----------|
| **Open Source** | FREE | Local reports, 100+ metrics |
| **Cloud** | Contact sales | Centralized dashboard, alerting, team collaboration |

**Recommendation**: Use Open Source (what we have now), upgrade to Cloud for production

---

## 6️⃣ Monitoring & Alerts

### Prefect Cloud Automations
Set up alerts in Prefect Cloud UI:

1. Go to **Automations** tab
2. Create automation:
   - **Trigger**: Flow run fails
   - **Action**: Send email/Slack notification
3. Example triggers:
   - Training fails
   - Drift threshold exceeded
   - Worker goes offline

### Evidently Alerts (Open Source)
```python
# In drift_monitoring_flow.py (already configured):
if monitor.check_drift_threshold():
    # Send notification (add your logic here)
    send_alert("⚠️ Model drift detected! Retraining triggered.")
```

---

## 7️⃣ Advantages Over Local Setup

| Feature | Local | Prefect Cloud | Benefit |
|---------|-------|---------------|---------|
| Server Management | You maintain | Managed | No DevOps overhead |
| Availability | Your machine | 99.9% SLA | Production-ready |
| Collaboration | Single user | Team access | Multi-user support |
| Monitoring | Terminal logs | Rich dashboard | Better visibility |
| Scheduling | Cron jobs | Cloud scheduler | More reliable |
| Security | DIY | SOC 2 certified | Enterprise-grade |
| Scaling | Manual | Auto-scale | Handle more workflows |

---

## 8️⃣ Next Steps

### Immediate (Today)
- [x] Create Prefect Cloud account
- [x] Get API key and login
- [x] Deploy training flow
- [x] Start worker and test

### Short-term (This Week)
- [ ] Set up automations for failure alerts
- [ ] Schedule daily drift monitoring
- [ ] Configure Slack/email notifications
- [ ] Document team access procedures

### Long-term (Next Month)
- [ ] Evaluate Evidently Cloud (if needed)
- [ ] Set up CI/CD with GitHub Actions
- [ ] Implement A/B testing for models
- [ ] Add more monitoring metrics

---

## 9️⃣ Troubleshooting

### Prefect Cloud Connection Issues
```bash
# Reset API key
prefect cloud logout
prefect cloud login

# Check connection
prefect cloud workspace ls

# View logs
prefect config view --show-sources
```

### Worker Not Picking Up Jobs
```bash
# Check worker status
prefect work-queue ls

# Restart worker
prefect agent start -q training

# Check deployment
prefect deployment ls
```

### Evidently Reports Not Generating
```bash
# Verify data exists
python test_evidently.py

# Check reports directory
dir monitoring\reports

# Re-run with debug
python -v test_evidently.py
```

---

## 📚 Resources

### Prefect Cloud
- Dashboard: https://app.prefect.cloud/
- Documentation: https://docs.prefect.io/latest/cloud/
- Community: https://prefect.io/slack
- Status: https://prefect.status.io/

### Evidently AI
- Website: https://www.evidentlyai.com/
- Documentation: https://docs.evidentlyai.com/
- GitHub: https://github.com/evidentlyai/evidently
- Discord: https://discord.com/invite/PyAJuUD5mB

### Your Project
- HuggingFace Space: https://kshitijk20-nss.hf.space
- Prefect Dashboard: Check after login
- Evidently Reports: `monitoring/reports/`

---

## ✅ Success Checklist

- [ ] Prefect Cloud account created
- [ ] API key configured locally
- [ ] Training flow deployed to cloud
- [ ] Worker running and picking up jobs
- [ ] Weekly schedule active (visible in dashboard)
- [ ] Drift monitoring flow tested
- [ ] Evidently reports generating correctly
- [ ] Automations configured (optional)
- [ ] Team members invited (if applicable)

---

**🎉 Congratulations!** You now have a production-grade MLOps stack with:
- Automated orchestration (Prefect Cloud)
- Data drift monitoring (Evidently)
- Scheduled retraining (Weekly)
- Real-time dashboards
- Enterprise security
- Zero infrastructure management

All while keeping your data secure in your own environment! 🔒

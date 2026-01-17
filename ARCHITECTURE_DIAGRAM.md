# HuggingFace + Cloud MLOps - Complete Workflow

## Visual Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPER MACHINE                             │
│                                                                  │
│  1. Get Prefect API Key                                         │
│     https://app.prefect.cloud/ → Profile → API Keys             │
│                                                                  │
│  2. Run Deployment Script                                       │
│     python prepare_hf_deployment.py                             │
│     ├─ Adds files to git                                        │
│     ├─ Commits changes                                          │
│     └─ Shows secret configuration steps                         │
│                                                                  │
│  3. Configure HuggingFace Secrets                               │
│     https://huggingface.co/spaces/kshitijk20/nss/settings       │
│     Add: PREFECT_API_KEY = pnu_xxxxx                            │
│                                                                  │
│  4. Push to HuggingFace                                         │
│     git push hf main                                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  HUGGINGFACE SPACES (Build)                      │
│                                                                  │
│  Docker Build Process:                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. FROM python:3.13-slim                                   │ │
│  │ 2. COPY requirements.txt → pip install                     │ │
│  │    • prefect>=2.14.0                                       │ │
│  │    • evidently>=0.4.0                                      │ │
│  │    • fastapi, uvicorn, scikit-learn                        │ │
│  │ 3. COPY application code                                   │ │
│  │    • app.py, startup.sh, cloud_config.py                   │ │
│  │    • prefect_flows/, monitoring/                           │ │
│  │    • final_model/model.pkl, preprocessor.pkl               │ │
│  │ 4. RUN chmod +x startup.sh                                 │ │
│  │ 5. RUN python load_data_to_sqlite.py                       │ │
│  │ 6. RUN python cloud_config.py (check config)               │ │
│  │ 7. ENTRYPOINT ["./startup.sh"]                             │ │
│  │ 8. CMD ["uvicorn", "app:app", ...]                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│               CONTAINER STARTUP (startup.sh)                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 🔍 Check Environment Variables                             │ │
│  │                                                            │ │
│  │ if [ -n "$PREFECT_API_KEY" ]; then                         │ │
│  │   ✅ Prefect Cloud API Key detected                        │ │
│  │   🔧 Configuring Prefect Cloud...                          │ │
│  │   prefect config set PREFECT_API_KEY="$PREFECT_API_KEY"   │ │
│  │   prefect cloud workspace ls  # Verify connection          │ │
│  │   ✅ Successfully connected to Prefect Cloud               │ │
│  │                                                            │ │
│  │   if [ "$AUTO_DEPLOY_FLOWS" = "true" ]; then               │ │
│  │     📦 Auto-deploying Prefect flows...                     │ │
│  │     cd prefect_flows && python deploy_schedule.py          │ │
│  │   fi                                                       │ │
│  │ else                                                       │ │
│  │   ℹ️  No PREFECT_API_KEY - Cloud features disabled         │ │
│  │ fi                                                         │ │
│  │                                                            │ │
│  │ if [ -n "$EVIDENTLY_CLOUD_TOKEN" ]; then                   │ │
│  │   ✅ Evidently Cloud enabled                               │ │
│  │ else                                                       │ │
│  │   ℹ️  Using open-source Evidently                          │ │
│  │ fi                                                         │ │
│  │                                                            │ │
│  │ 📁 mkdir -p monitoring/reports final_model logs            │ │
│  │ ✅ Initialization complete!                                │ │
│  │ 🌐 Starting FastAPI application...                         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                FASTAPI APPLICATION (app.py)                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ from cloud_config import initialize_monitoring             │ │
│  │ cloud_status = initialize_monitoring()                     │ │
│  │                                                            │ │
│  │ app = FastAPI()                                            │ │
│  │                                                            │ │
│  │ @app.get("/")                                              │ │
│  │ def root():                                                │ │
│  │     return {                                               │ │
│  │         "status": "running",                               │ │
│  │         "cloud_mlops": {                                   │ │
│  │             "prefect_cloud": "enabled" ✅                  │ │
│  │             "evidently": "open-source"                     │ │
│  │         }                                                  │ │
│  │     }                                                      │ │
│  │                                                            │ │
│  │ @app.get("/train")                                         │ │
│  │ def training_route():                                      │ │
│  │     if ENABLE_PREFECT:                                     │ │
│  │         # Option 1: Trigger via Prefect Cloud              │ │
│  │         training_flow()  # Logged to Prefect dashboard     │ │
│  │     else:                                                  │ │
│  │         # Option 2: Direct training                        │ │
│  │         training_pipeline.run_pipeline()                   │ │
│  │                                                            │ │
│  │ @app.post("/predict")                                      │ │
│  │ def predict_route(file):                                   │ │
│  │     # Make predictions                                     │ │
│  │     # Optionally log to Evidently                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  🌐 Running at: https://kshitijk20-nss.hf.space                │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│               PREFECT CLOUD (External Service)                   │
│                                                                  │
│  Dashboard: https://app.prefect.cloud/                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 📊 Flow Runs                                               │ │
│  │ ├─ training-flow-2026-01-17-14:30:00 ✅ Success           │ │
│  │ ├─ training-flow-2026-01-10-14:30:00 ✅ Success           │ │
│  │ └─ drift-monitoring-2026-01-17-03:00:00 ✅ Success        │ │
│  │                                                            │ │
│  │ 📅 Deployments                                             │ │
│  │ ├─ weekly-training (Every Sunday 2 AM)                     │ │
│  │ └─ daily-drift-check (Every day 3 AM)                      │ │
│  │                                                            │ │
│  │ 🔔 Automations                                             │ │
│  │ └─ Notify on training failure → Slack/Email                │ │
│  │                                                            │ │
│  │ 📈 Metrics                                                 │ │
│  │ • Total runs: 45                                           │ │
│  │ • Success rate: 97.8%                                      │ │
│  │ • Avg duration: 2.3 min                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────────┐
│            EVIDENTLY (Open Source - Local Reports)               │
│                                                                  │
│  Reports stored in: /app/monitoring/reports/                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ drift_report_20260117_143000.html                          │ │
│  │ ├─ Data Drift: 12% of features drifted                     │ │
│  │ ├─ Data Quality: 98.5% complete                            │ │
│  │ └─ Recommendation: No retraining needed                    │ │
│  │                                                            │ │
│  │ performance_report_20260117_143000.html                    │ │
│  │ ├─ Accuracy: 94.2%                                         │ │
│  │ ├─ Precision: 93.8%                                        │ │
│  │ └─ Recall: 95.1%                                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐       ┌─────────────┐       ┌──────────────┐
│          │       │             │       │              │
│  User    │──────>│ HuggingFace │──────>│   FastAPI    │
│          │ POST  │   Space     │       │   app.py     │
│          │ /pred │             │       │              │
└──────────┘       └─────────────┘       └──────┬───────┘
                                                 │
                   ┌─────────────────────────────┼─────────────────┐
                   │                             │                 │
                   ↓                             ↓                 ↓
          ┌────────────────┐          ┌─────────────────┐  ┌──────────────┐
          │  Model Files   │          │ Prefect Cloud   │  │  Evidently   │
          │  • model.pkl   │          │ • Log training  │  │  • Reports   │
          │  • preproc.pkl │          │ • Schedule jobs │  │  • Drift det │
          └────────────────┘          └─────────────────┘  └──────────────┘
```

## Secrets Flow

```
Developer → Get API Key from Prefect Cloud
              ↓
           Add to HuggingFace Space Secrets
              ↓
           Push code: git push hf main
              ↓
           HuggingFace builds Docker container
              ↓
           Injects secrets as environment variables
              ↓
           startup.sh reads $PREFECT_API_KEY
              ↓
           Configures Prefect Cloud connection
              ↓
           app.py uses cloud features
              ↓
           All operations visible in Prefect dashboard
```

## File Interaction Map

```
prepare_hf_deployment.py
    ├─ Adds to git:
    │   ├─ startup.sh
    │   ├─ cloud_config.py
    │   ├─ app.py (updated)
    │   ├─ Dockerfile (updated)
    │   └─ prefect_flows/
    └─ Shows: Secret configuration instructions

Dockerfile
    ├─ Copies: startup.sh, cloud_config.py
    ├─ RUN: chmod +x startup.sh
    ├─ RUN: python cloud_config.py
    └─ ENTRYPOINT: ./startup.sh

startup.sh
    ├─ Reads: $PREFECT_API_KEY, $EVIDENTLY_CLOUD_TOKEN
    ├─ Configures: Prefect Cloud connection
    ├─ Creates: monitoring/reports, final_model
    └─ Starts: uvicorn app:app

cloud_config.py
    ├─ Reads: All environment variables
    ├─ Exports: Configuration status
    └─ Used by: app.py, startup.sh

app.py
    ├─ Imports: cloud_config
    ├─ GET /: Shows cloud status
    ├─ GET /train: Can use Prefect Cloud
    └─ POST /predict: Normal predictions
```

---

## Success Flow (Happy Path)

```
1. Developer runs: python prepare_hf_deployment.py
   ✅ Files added to git
   ✅ Commit created

2. Developer adds PREFECT_API_KEY to HF Space
   ✅ Secret configured

3. Developer pushes: git push hf main
   ✅ Code pushed to HuggingFace

4. HuggingFace builds container
   ✅ Docker image built
   ✅ Dependencies installed

5. Container starts (startup.sh runs)
   ✅ Prefect Cloud API Key detected
   ✅ Successfully connected to Prefect Cloud
   ✅ Initialization complete!

6. FastAPI starts
   ✅ Server running on port 7860
   ✅ Cloud features enabled

7. User calls GET /
   ✅ Returns: "prefect_cloud": "enabled"

8. User calls GET /train
   ✅ Training executes
   ✅ Logged to Prefect Cloud dashboard

9. Developer checks Prefect dashboard
   ✅ Sees flow run from HF Space
   ✅ Views logs and execution graph
```

---

## Cost-Free Production MLOps! 🎉

```
┌───────────────────────────────────────────┐
│ Component          │ Tier      │ Cost    │
├───────────────────────────────────────────┤
│ HuggingFace Spaces │ Community │ FREE ✅ │
│ Prefect Cloud      │ Hobby     │ FREE ✅ │
│ Evidently          │ Open Src  │ FREE ✅ │
├───────────────────────────────────────────┤
│ TOTAL MONTHLY COST                │ $0  │
└───────────────────────────────────────────┘
```

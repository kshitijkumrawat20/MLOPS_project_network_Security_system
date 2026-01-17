# 🔐 HuggingFace Space Secrets Configuration

To enable cloud MLOps features in your HuggingFace Space, add these secrets:

## Required Secrets

### 1. Prefect Cloud (Recommended)
Add these to HuggingFace Space Settings → Repository secrets:

```
Name: PREFECT_API_KEY
Value: <Your Prefect Cloud API Key>
```

**How to get:**
1. Go to https://app.prefect.cloud/
2. Click your profile (bottom left) → API Keys
3. Click "Create API Key"
4. Name it "HuggingFace-NSS"
5. Copy the key and paste as secret

### 2. Prefect Workspace (Optional)
```
Name: PREFECT_WORKSPACE
Value: <Your workspace ID or name>
```

**How to get:**
- In Prefect Cloud, go to workspace settings
- Copy the workspace name (e.g., "my-workspace/phishing-detection")

### 3. Auto-Deploy Flows (Optional)
```
Name: AUTO_DEPLOY_FLOWS
Value: true
```
Set to `true` if you want flows automatically deployed on container start.

---

## Optional Secrets

### Evidently Cloud (For Enterprise Users)
```
Name: EVIDENTLY_CLOUD_TOKEN
Value: <Your Evidently Cloud Token>
```

```
Name: EVIDENTLY_PROJECT_ID
Value: <Your Project ID>
```

**How to get:**
- Contact Evidently AI for cloud access: https://www.evidentlyai.com/get-demo
- They will provide token and project ID

### Additional Configuration
```
Name: MONITORING_ENABLED
Value: true (default)
```

```
Name: DRIFT_CHECK_ENABLED
Value: false (set to true for automated drift checks)
```

---

## How to Add Secrets to HuggingFace Space

### Method 1: Web UI (Recommended)
1. Go to your HuggingFace Space: https://huggingface.co/spaces/kshitijk20/nss
2. Click **"Settings"** tab
3. Scroll to **"Repository secrets"**
4. Click **"Add a secret"**
5. Enter **Name** and **Value**
6. Click **"Add secret"**
7. Rebuild your Space (Settings → Factory reboot)

### Method 2: CLI
```bash
# Install HuggingFace CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Add secret
huggingface-cli space add-secret kshitijk20/nss PREFECT_API_KEY "your-api-key-here"
```

---

## Testing Configuration

After adding secrets and rebuilding:

1. **Check Logs:**
   - Go to your Space → Logs tab
   - Look for: "✅ Prefect Cloud configured successfully"

2. **Verify Prefect Connection:**
   - In Prefect Cloud dashboard: https://app.prefect.cloud/
   - Check if deployments appear

3. **Test Endpoints:**
   ```bash
   # Training endpoint
   curl -X GET "https://kshitijk20-nss.hf.space/train"
   
   # Prediction endpoint  
   curl -X POST "https://kshitijk20-nss.hf.space/predict" \
     -F "file=@data/phisingData.csv"
   ```

---

## Environment Variables Summary

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `PREFECT_API_KEY` | ✅ Recommended | None | Connect to Prefect Cloud |
| `PREFECT_API_URL` | ❌ | https://api.prefect.cloud/api | Prefect API endpoint |
| `PREFECT_WORKSPACE` | ❌ | None | Specific workspace |
| `AUTO_DEPLOY_FLOWS` | ❌ | false | Auto-deploy on startup |
| `EVIDENTLY_CLOUD_TOKEN` | ❌ | None | Evidently Cloud (paid) |
| `EVIDENTLY_PROJECT_ID` | ❌ | None | Evidently project |
| `MONITORING_ENABLED` | ❌ | true | Enable monitoring |
| `DRIFT_CHECK_ENABLED` | ❌ | false | Auto drift checks |

---

## Architecture with Secrets

```
┌─────────────────────────────────────────────┐
│     HuggingFace Space (Docker Container)    │
│  ┌────────────────────────────────────────┐ │
│  │  Environment Variables (Secrets)       │ │
│  │  - PREFECT_API_KEY                     │ │
│  │  - EVIDENTLY_CLOUD_TOKEN (optional)    │ │
│  └────────────────────────────────────────┘ │
│                    ↓                         │
│  ┌────────────────────────────────────────┐ │
│  │  startup.sh (Initialization)           │ │
│  │  - Configures Prefect Cloud            │ │
│  │  - Sets up Evidently                   │ │
│  │  - Creates directories                 │ │
│  └────────────────────────────────────────┘ │
│                    ↓                         │
│  ┌────────────────────────────────────────┐ │
│  │  FastAPI App (app.py)                  │ │
│  │  - Serves predictions                  │ │
│  │  - Training endpoint                   │ │
│  │  - Reports to Prefect Cloud            │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Prefect Cloud (Monitoring)          │
│  - Flow execution logs                      │
│  - Training history                         │
│  - Automated scheduling                     │
└─────────────────────────────────────────────┘
```

---

## Troubleshooting

### Secret not recognized
**Problem:** Container doesn't see secret
**Solution:** 
- Verify secret name matches exactly (case-sensitive)
- Rebuild Space (Settings → Factory reboot)
- Check logs for initialization messages

### Prefect connection fails
**Problem:** "Could not connect to Prefect Cloud"
**Solution:**
- Verify API key is valid (test locally first)
- Check PREFECT_API_URL is correct
- Ensure network access from HF Spaces

### Auto-deploy fails
**Problem:** Flows not deploying automatically
**Solution:**
- Set `AUTO_DEPLOY_FLOWS=true`
- Check prefect_flows/ directory exists
- Review logs for deployment errors

---

## Security Best Practices

1. **Never commit secrets to git**
   - Use `.gitignore` for local `.env` files
   - Only use HF Space secrets feature

2. **Rotate keys regularly**
   - Update Prefect API key monthly
   - Delete old unused keys

3. **Use minimal permissions**
   - Create separate API keys for different environments
   - Limit key scope to required operations

4. **Monitor access**
   - Check Prefect Cloud audit logs
   - Review Space access logs

---

## Next Steps

After configuration:

1. **Test locally first:**
   ```bash
   export PREFECT_API_KEY="your-key"
   python cloud_config.py
   ```

2. **Add to HuggingFace Space**
3. **Rebuild and monitor logs**
4. **Verify Prefect Cloud shows deployments**
5. **Run training to test end-to-end**

---

## Support

- **Prefect Cloud:** https://docs.prefect.io/latest/cloud/
- **HuggingFace Spaces:** https://huggingface.co/docs/hub/spaces
- **Evidently:** https://docs.evidentlyai.com/
- **Project Issues:** Report bugs in your GitHub repository

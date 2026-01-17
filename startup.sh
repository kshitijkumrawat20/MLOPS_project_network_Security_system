#!/bin/bash
# Startup script for HuggingFace Space
# Initializes Prefect Cloud and Evidently monitoring

set -e

echo "🚀 Starting Network Security System..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Prefect Cloud API key is provided
if [ -n "$PREFECT_API_KEY" ]; then
    echo "✅ Prefect Cloud API Key detected"
    echo "🔧 Configuring Prefect Cloud connection..."
    
    # Set Prefect Cloud API URL (default to cloud)
    export PREFECT_API_URL="${PREFECT_API_URL:-https://api.prefect.cloud/api}"
    
    # Configure Prefect
    prefect config set PREFECT_API_KEY="$PREFECT_API_KEY"
    prefect config set PREFECT_API_URL="$PREFECT_API_URL"
    
    # Verify connection
    if prefect cloud workspace ls 2>/dev/null; then
        echo "✅ Successfully connected to Prefect Cloud"
        
        # Optional: Auto-deploy flows if enabled
        if [ "$AUTO_DEPLOY_FLOWS" = "true" ]; then
            echo "📦 Auto-deploying Prefect flows..."
            cd /app/prefect_flows
            python deploy_schedule.py || echo "⚠️  Flow deployment skipped"
            cd /app
        fi
    else
        echo "⚠️  Warning: Could not connect to Prefect Cloud"
        echo "   Prefect features will be limited"
    fi
else
    echo "ℹ️  No PREFECT_API_KEY found - Prefect Cloud features disabled"
    echo "   Set PREFECT_API_KEY in HuggingFace Space secrets to enable"
fi

# Check if Evidently Cloud token is provided (optional)
if [ -n "$EVIDENTLY_API_KEY" ]; then
    echo "✅ Evidently Cloud Token detected"
    export EVIDENTLY_API_KEY="$EVIDENTLY_API_KEY"
    echo "🔧 Evidently Cloud integration enabled"
else
    echo "ℹ️  No EVIDENTLY_API_KEY - Using open-source Evidently"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /app/monitoring/reports
mkdir -p /app/final_model
mkdir -p /app/logs

# Set permissions
chmod +x /app/app.py 2>/dev/null || true

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Initialization complete!"
echo "🌐 Starting FastAPI application..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start the application
exec "$@"

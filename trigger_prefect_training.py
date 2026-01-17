"""
Trigger Prefect training flow manually
Use this to run training through Prefect Cloud from command line
"""
import sys
sys.path.append('.')

from prefect_flows.training_flow import training_flow

if __name__ == "__main__":
    print("🚀 Starting training via Prefect Cloud...")
    result = training_flow()
    print(f"✅ Training completed: {result}")
    print("📊 Check Prefect Cloud dashboard: https://app.prefect.cloud/")

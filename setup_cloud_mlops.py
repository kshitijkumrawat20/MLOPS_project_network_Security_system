"""
Quick Setup Script for Prefect Cloud + Evidently
Run this after getting your Prefect Cloud API key
"""
import subprocess
import sys

def run_command(command, description):
    """Run a command and print result"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Prefect Cloud + Evidently Setup for NSS Project       ║
    ╚══════════════════════════════════════════════════════════╝
    
    Prerequisites:
    1. Created Prefect Cloud account at https://app.prefect.cloud/
    2. Generated API key from dashboard
    3. Virtual environment activated (.venv)
    
    """)
    
    input("Press Enter to continue...")
    
    # Step 1: Check Prefect installation
    if not run_command("prefect --version", "Checking Prefect installation"):
        print("\n❌ Prefect not installed. Run: pip install prefect>=2.14.0")
        return
    
    # Step 2: Check Evidently installation
    if not run_command("python -c \"import evidently; print(f'Evidently {evidently.__version__}')\"", 
                      "Checking Evidently installation"):
        print("\n❌ Evidently not installed. Run: pip install evidently>=0.4.0")
        return
    
    # Step 3: Login to Prefect Cloud
    print("\n" + "="*60)
    print("🔑 Prefect Cloud Login")
    print("="*60)
    print("Please paste your Prefect Cloud API key when prompted...")
    print("(Get it from: https://app.prefect.cloud/ → Profile → API Keys)")
    
    if not run_command("prefect cloud login", "Logging into Prefect Cloud"):
        print("\n❌ Login failed. Please check your API key.")
        return
    
    # Step 4: Verify connection
    if not run_command("prefect cloud workspace ls", "Verifying Prefect Cloud connection"):
        print("\n❌ Could not connect to Prefect Cloud.")
        return
    
    # Step 5: Create deployments
    print("\n" + "="*60)
    print("📦 Creating Prefect Deployments")
    print("="*60)
    
    deploy_result = subprocess.run(
        "cd prefect_flows && python deploy_schedule.py",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if deploy_result.returncode == 0:
        print("✅ Weekly training deployment created!")
        print(deploy_result.stdout)
    else:
        print(f"⚠️  Deployment creation skipped or failed: {deploy_result.stderr}")
    
    # Step 6: Test Evidently
    print("\n" + "="*60)
    print("📊 Testing Evidently Monitoring")
    print("="*60)
    
    test_result = subprocess.run(
        "python test_evidently.py",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if test_result.returncode == 0:
        print("✅ Evidently reports generated successfully!")
        print("Check monitoring/reports/ for HTML files")
    else:
        print(f"⚠️  Evidently test failed: {test_result.stderr}")
    
    # Final Instructions
    print("""
    
    ╔══════════════════════════════════════════════════════════╗
    ║                  Setup Complete! 🎉                      ║
    ╚══════════════════════════════════════════════════════════╝
    
    📋 NEXT STEPS:
    
    1. Start Prefect Worker (keep running):
       Command: prefect agent start -q training
    
    2. View Dashboard:
       URL: https://app.prefect.cloud/
    
    3. Run Training Flow (test):
       Command: cd prefect_flows && python training_flow.py
    
    4. Run Drift Monitoring (test):
       Command: cd prefect_flows && python drift_monitoring_flow.py
    
    5. Check Evidently Reports:
       Location: monitoring/reports/*.html
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📚 DOCUMENTATION:
    - Full guide: CLOUD_MLOPS_SETUP.md
    - Prefect Cloud: https://docs.prefect.io/latest/cloud/
    - Evidently: https://docs.evidentlyai.com/
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    ⚡ QUICK TEST:
    Open a new terminal and run:
    
    Terminal 1 (Worker):
    > prefect agent start -q training
    
    Terminal 2 (Test Flow):
    > cd prefect_flows
    > python training_flow.py
    
    Then check: https://app.prefect.cloud/ to see your flow run!
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

if __name__ == "__main__":
    main()

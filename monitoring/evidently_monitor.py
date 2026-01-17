"""
Evidently Monitoring Module
Tracks data drift, model performance, and data quality
"""
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset
from evidently.metrics import *
from datetime import datetime
import json
import os

class PhishingModelMonitor:
    """Monitor phishing detection model for drift and performance"""
    
    def __init__(self, reference_data_path="data/phisingData.csv"):
        """
        Initialize monitor with reference dataset
        
        Args:
            reference_data_path: Path to the original training data
        """
        self.reference_data = pd.read_csv(reference_data_path)
        self.reports_dir = "monitoring/reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_data_drift_report(self, current_data: pd.DataFrame):
        """
        Generate data drift report comparing current data with reference
        
        Args:
            current_data: Recent prediction data
            
        Returns:
            Report object and saves HTML report
        """
        # Create drift report
        report = Report(metrics=[
            DataDriftPreset(),
            DataQualityPreset(),
        ])
        
        report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.reports_dir}/drift_report_{timestamp}.html"
        report.save_html(report_path)
        
        # Extract metrics
        report_json = report.as_dict()
        
        return {
            "report_path": report_path,
            "metrics": self._extract_drift_metrics(report_json),
            "timestamp": timestamp
        }
    
    def generate_model_performance_report(self, current_data: pd.DataFrame, 
                                         predictions: pd.Series, 
                                         actuals: pd.Series = None):
        """
        Generate model performance report
        
        Args:
            current_data: Feature data
            predictions: Model predictions
            actuals: Actual labels (if available)
        """
        current_data = current_data.copy()
        current_data['prediction'] = predictions
        
        if actuals is not None:
            current_data['target'] = actuals
            reference_data = self.reference_data.copy()
            
            # Create performance report
            report = Report(metrics=[
                ClassificationQualityMetric(),
                ClassificationClassBalance(),
                ClassificationConfusionMatrix(),
                ClassificationQualityByClass()
            ])
            
            report.run(
                reference_data=reference_data,
                current_data=current_data,
                column_mapping={
                    'target': 'Result',
                    'prediction': 'prediction'
                }
            )
        else:
            # Only prediction drift if no actuals
            report = Report(metrics=[
                TargetDriftPreset(),
            ])
            
            report.run(
                reference_data=self.reference_data,
                current_data=current_data,
                column_mapping={'prediction': 'prediction'}
            )
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.reports_dir}/performance_report_{timestamp}.html"
        report.save_html(report_path)
        
        return {
            "report_path": report_path,
            "timestamp": timestamp
        }
    
    def _extract_drift_metrics(self, report_json):
        """Extract key metrics from drift report"""
        try:
            metrics = report_json.get('metrics', [])
            drift_summary = {
                'dataset_drift': False,
                'number_of_drifted_columns': 0,
                'share_of_drifted_columns': 0.0,
                'drifted_features': []
            }
            
            for metric in metrics:
                if metric.get('metric') == 'DatasetDriftMetric':
                    result = metric.get('result', {})
                    drift_summary['dataset_drift'] = result.get('dataset_drift', False)
                    drift_summary['number_of_drifted_columns'] = result.get('number_of_drifted_columns', 0)
                    drift_summary['share_of_drifted_columns'] = result.get('share_of_drifted_columns', 0.0)
                    
                    # Extract drifted features
                    drift_by_columns = result.get('drift_by_columns', {})
                    drift_summary['drifted_features'] = [
                        col for col, info in drift_by_columns.items() 
                        if info.get('drift_detected', False)
                    ]
                    break
            
            return drift_summary
        except Exception as e:
            return {"error": str(e)}
    
    def check_drift_threshold(self, drift_metrics, threshold=0.3):
        """
        Check if drift exceeds threshold
        
        Args:
            drift_metrics: Output from generate_data_drift_report
            threshold: Maximum acceptable share of drifted columns
            
        Returns:
            bool: True if retraining is recommended
        """
        share_drifted = drift_metrics['metrics'].get('share_of_drifted_columns', 0)
        return share_drifted > threshold
    
    def save_monitoring_state(self, metrics, filepath="monitoring/monitoring_state.json"):
        """Save monitoring metrics to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        state = {
            "last_check": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)


# Utility function to monitor predictions
def monitor_predictions(data_csv_path: str, reference_csv_path: str = "data/phisingData.csv"):
    """
    Quick function to monitor predictions from CSV
    
    Args:
        data_csv_path: Path to CSV with recent predictions
        reference_csv_path: Path to reference training data
    """
    monitor = PhishingModelMonitor(reference_csv_path)
    current_data = pd.read_csv(data_csv_path)
    
    # Generate drift report
    drift_result = monitor.generate_data_drift_report(current_data)
    
    print(f"📊 Drift Report Generated: {drift_result['report_path']}")
    print(f"📈 Metrics: {drift_result['metrics']}")
    
    # Check if retraining needed
    if monitor.check_drift_threshold(drift_result):
        print("⚠️  WARNING: Significant drift detected! Retraining recommended.")
    else:
        print("✅ Drift within acceptable limits.")
    
    return drift_result


if __name__ == "__main__":
    # Example: Monitor predictions
    monitor_predictions("final_model/predicted.csv")

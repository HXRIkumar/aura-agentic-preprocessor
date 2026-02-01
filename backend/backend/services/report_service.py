"""
Report Generator Module for AURA Preprocessor 2.0

Generates comprehensive reports of data preprocessing steps and results.
Saves reports in JSON format for easy analysis and visualization.
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates comprehensive reports of data preprocessing pipeline.
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save report files
        """
        self.output_dir = output_dir
        self.report_data = {
            "pipeline_info": {},
            "data_summary": {},
            "preprocessing_steps": [],
            "model_results": {},
            "recommendations": []
        }
        self.ensure_output_dir()
    
    def ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_pipeline_report(self, 
                               original_df: pd.DataFrame,
                               processed_df: pd.DataFrame,
                               target_col: str,
                               preprocessing_steps: List[Dict[str, Any]],
                               model_results: Optional[Dict[str, Any]] = None,
                               encoding_info: Optional[Dict[str, Any]] = None,
                               scaling_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive pipeline report.
        
        Args:
            original_df: Original dataset before preprocessing
            processed_df: Dataset after preprocessing
            target_col: Target column name
            preprocessing_steps: List of preprocessing steps performed
            model_results: Model training results (optional)
            encoding_info: Feature encoding information (optional)
            scaling_info: Feature scaling information (optional)
            
        Returns:
            Complete report dictionary
        """
        try:
            # Pipeline information
            self.report_data["pipeline_info"] = {
                "timestamp": datetime.now().isoformat(),
                "target_column": target_col,
                "pipeline_version": "2.0",
                "total_steps": len(preprocessing_steps)
            }
            
            # Data summary
            self.report_data["data_summary"] = self._generate_data_summary(
                original_df, processed_df, target_col
            )
            
            # Preprocessing steps
            self.report_data["preprocessing_steps"] = preprocessing_steps
            
            # Add encoding and scaling details
            if encoding_info:
                self.report_data["encoding_details"] = encoding_info
            
            if scaling_info:
                self.report_data["scaling_details"] = scaling_info
            
            # Model results
            if model_results:
                self.report_data["model_results"] = model_results
            
            # Generate recommendations
            self.report_data["recommendations"] = self._generate_recommendations(
                original_df, processed_df, model_results
            )
            
            logger.info("Pipeline report generated successfully")
            
        except Exception as e:
            error_msg = f"Error generating pipeline report: {str(e)}"
            logger.error(error_msg)
            self.report_data["error"] = error_msg
        
        return self.report_data
    
    def _generate_data_summary(self, 
                              original_df: pd.DataFrame, 
                              processed_df: pd.DataFrame, 
                              target_col: str) -> Dict[str, Any]:
        """
        Generate data summary comparing original and processed datasets.
        
        Args:
            original_df: Original dataset
            processed_df: Processed dataset
            target_col: Target column name
            
        Returns:
            Data summary dictionary
        """
        summary = {
            "original_dataset": {
                "shape": original_df.shape,
                "columns": original_df.columns.tolist(),
                "dtypes": original_df.dtypes.astype(str).to_dict(),
                "missing_values": original_df.isnull().sum().to_dict(),
                "missing_percentage": (original_df.isnull().sum() / len(original_df) * 100).to_dict()
            },
            "processed_dataset": {
                "shape": processed_df.shape,
                "columns": processed_df.columns.tolist(),
                "dtypes": processed_df.dtypes.astype(str).to_dict(),
                "missing_values": processed_df.isnull().sum().to_dict(),
                "missing_percentage": (processed_df.isnull().sum() / len(processed_df) * 100).to_dict()
            },
            "changes": {
                "rows_added": processed_df.shape[0] - original_df.shape[0],
                "columns_added": processed_df.shape[1] - original_df.shape[1],
                "columns_removed": len(set(original_df.columns) - set(processed_df.columns)),
                "columns_added_list": list(set(processed_df.columns) - set(original_df.columns)),
                "columns_removed_list": list(set(original_df.columns) - set(processed_df.columns))
            }
        }
        
        # Target column analysis
        if target_col in original_df.columns:
            summary["target_analysis"] = {
                "target_column": target_col,
                "target_type": str(original_df[target_col].dtype),
                "unique_values": int(original_df[target_col].nunique()),
                "value_counts": original_df[target_col].value_counts().to_dict(),
                "class_distribution": (original_df[target_col].value_counts(normalize=True) * 100).to_dict()
            }
        
        return summary
    
    def _generate_recommendations(self, 
                                 original_df: pd.DataFrame,
                                 processed_df: pd.DataFrame,
                                 model_results: Optional[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on data analysis.
        
        Args:
            original_df: Original dataset
            processed_df: Processed dataset
            model_results: Model training results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            # Missing values recommendations
            missing_cols = original_df.columns[original_df.isnull().any()].tolist()
            if missing_cols:
                recommendations.append(
                    f"Consider investigating missing values in columns: {missing_cols}. "
                    "High missing percentages (>50%) might indicate data quality issues."
                )
            
            # Categorical columns recommendations
            categorical_cols = original_df.select_dtypes(include=['object']).columns.tolist()
            if categorical_cols:
                high_cardinality = [col for col in categorical_cols 
                                 if original_df[col].nunique() > 20]
                if high_cardinality:
                    recommendations.append(
                        f"High cardinality categorical columns detected: {high_cardinality}. "
                        "Consider feature engineering or dimensionality reduction techniques."
                    )
            
            # Model performance recommendations
            if model_results and "accuracy" in model_results:
                accuracy = model_results["accuracy"]
                if accuracy < 0.7:
                    recommendations.append(
                        f"Model accuracy ({accuracy:.3f}) is below 70%. "
                        "Consider feature engineering, hyperparameter tuning, or trying different algorithms."
                    )
                elif accuracy > 0.9:
                    recommendations.append(
                        f"Excellent model performance ({accuracy:.3f})! "
                        "Consider validating on additional test data to ensure generalization."
                    )
            
            # Data size recommendations
            if processed_df.shape[0] < 1000:
                recommendations.append(
                    "Small dataset detected. Consider collecting more data or using "
                    "techniques like data augmentation to improve model robustness."
                )
            
            # Feature count recommendations
            if processed_df.shape[1] > 100:
                recommendations.append(
                    "High-dimensional dataset detected. Consider feature selection "
                    "or dimensionality reduction techniques to prevent overfitting."
                )
            
            # Default recommendation if no specific issues found
            if not recommendations:
                recommendations.append(
                    "Dataset appears well-prepared for machine learning. "
                    "Consider experimenting with different algorithms and hyperparameters."
                )
            
        except Exception as e:
            logger.warning(f"Error generating recommendations: {str(e)}")
            recommendations.append("Unable to generate specific recommendations due to data analysis error.")
        
        return recommendations
    
    def save_report(self, filename: str = "report.json") -> bool:
        """
        Save the report to a JSON file.
        
        Args:
            filename: Name of the report file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.report_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Report saved to {filepath}")
            print(f"📊 Report saved to {filepath}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error saving report: {str(e)}"
            logger.error(error_msg)
            print(f"⚠️ {error_msg}")
            return False
    
    def print_summary(self) -> None:
        """Print a summary of the report to console."""
        try:
            print("\n" + "="*60)
            print("📊 AURA PREPROCESSOR 2.0 - PIPELINE SUMMARY")
            print("="*60)
            
            # Pipeline info
            if "pipeline_info" in self.report_data:
                info = self.report_data["pipeline_info"]
                print(f"🕒 Timestamp: {info.get('timestamp', 'N/A')}")
                print(f"🎯 Target Column: {info.get('target_column', 'N/A')}")
                print(f"📋 Total Steps: {info.get('total_steps', 'N/A')}")
            
            # Data summary
            if "data_summary" in self.report_data:
                summary = self.report_data["data_summary"]
                print(f"\n📈 Dataset Summary:")
                print(f"   Original: {summary['original_dataset']['shape']}")
                print(f"   Processed: {summary['processed_dataset']['shape']}")
                print(f"   Changes: +{summary['changes']['columns_added']} columns, "
                      f"-{summary['changes']['columns_removed']} columns")
            
            # Model results
            if "model_results" in self.report_data and self.report_data["model_results"]:
                results = self.report_data["model_results"]
                if "results" in results and "accuracy" in results["results"]:
                    accuracy = results["results"]["accuracy"]
                    print(f"\n🤖 Model Performance:")
                    print(f"   Algorithm: {results.get('model_name', 'N/A')}")
                    print(f"   Accuracy: {accuracy:.4f}")
            
            # Recommendations
            if "recommendations" in self.report_data:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(self.report_data["recommendations"], 1):
                    print(f"   {i}. {rec}")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"Error printing summary: {str(e)}")
            print("⚠️ Error generating summary")


def generate_pipeline_report(original_df: pd.DataFrame,
                            processed_df: pd.DataFrame,
                            target_col: str,
                            preprocessing_steps: List[Dict[str, Any]],
                            output_dir: str = "outputs",
                            **kwargs) -> Dict[str, Any]:
    """
    Convenience function to generate a pipeline report.
    
    Args:
        original_df: Original dataset
        processed_df: Processed dataset
        target_col: Target column name
        preprocessing_steps: List of preprocessing steps
        output_dir: Output directory
        **kwargs: Additional arguments for report generation
        
    Returns:
        Report dictionary
    """
    generator = ReportGenerator(output_dir)
    return generator.generate_pipeline_report(
        original_df, processed_df, target_col, preprocessing_steps, **kwargs
    )


import mlflow
import shap
import matplotlib.pyplot as plt
import os

def log_experiment(model_name, model, params, metrics, X_train):
    """
    Logs parameters, metrics, models, and SHAP explainability artifacts to MLflow.
    """
    # Ensure tracking URI is set (handled by docker-compose environment vars)
    mlflow.set_experiment("OmniQuant_Forecasting")
    
    with mlflow.start_run(run_name=model_name):
        # 1. Log Parameters
        mlflow.log_params(params)
        
        # 2. Log Metrics
        mlflow.log_metrics(metrics)
        
        # 3. Log Explainability Artifacts (SHAP)
        if model_name in ["XGBoost", "LightGBM"]:
            try:
                # Use TreeExplainer for XGBoost/LightGBM
                explainer = shap.Explainer(model.model)
                shap_values = explainer(X_train)
                
                plt.figure(figsize=(10, 6))
                shap.summary_plot(shap_values, X_train, plot_type="bar", show=False)
                plt.title(f"SHAP Feature Importance ({model_name})")
                plt.tight_layout()
                
                # Save plot to file and log as artifact
                os.makedirs("artifacts", exist_ok=True)
                plot_path = f"artifacts/{model_name}_shap.png"
                plt.savefig(plot_path)
                mlflow.log_artifact(plot_path)
                plt.close()
            except Exception as e:
                print(f"Could not generate SHAP plot for {model_name}: {e}")

        # 4. Save Model to MLflow Model Registry
        try:
            if model_name == "XGBoost":
                mlflow.xgboost.log_model(model.model, "model")
            elif model_name == "LightGBM":
                mlflow.lightgbm.log_model(model.model, "model")
            elif model_name == "LSTM":
                # Only log if it's a real Keras model (not our dummy fallback)
                if hasattr(model.model, 'save'):
                    mlflow.tensorflow.log_model(model.model, "model")
        except Exception as e:
            print(f"Could not log model {model_name} to registry: {e}")

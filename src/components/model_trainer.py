import os, sys
from src.utils.ml_utils.model.estimator import NetworkSecurityModel
from src.exception.exception import NetworkSecurityException
from src.logging.logger import logging
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from src.entity.config_entity import Model_trainer_config
from src.utils.main_utils.utils import save_object, load_object
from src.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from src.utils.ml_utils.metric.classification_metric import classification_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier, 
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
import mlflow 
import dagshub
dagshub.init(repo_owner='kshitijk146', repo_name='MLOPS_project_network_Security_system', mlflow=True)
class ModelTrainer:
    def __init__(self, model_trainer_config: Model_trainer_config, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def track_mlflow(self,best_model, classificationmetric):
        with mlflow.start_run():
            f1_score = classificationmetric.f1_score
            precision_score = classificationmetric.precision_score
            recall_score = classificationmetric.recall_score
        
            mlflow.log_metric("f1_score", f1_score)
            mlflow.log_metric("precision_score", precision_score)
            mlflow.log_metric("recall_score", recall_score)
            mlflow.sklearn.log_model(best_model, "model")
        
    def train_model(self, x_train, y_train,x_test, y_test):
        models = {
            "KNN": KNeighborsClassifier(),
            "Decision Tree": DecisionTreeClassifier(),
            "Random Forest": RandomForestClassifier(verbose=True),
            "AdaBoost": AdaBoostClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=True),
            "logistic regression": LogisticRegression(verbose=True)
        }
        params = {
            "KNN": {
                'n_neighbors': [3, 5, 7],  
                'weights': ['uniform', 'distance'],
                'metric': ['euclidean']  
            },
            "Decision Tree": {
                'criterion': ['gini', 'entropy'], 
                'max_depth': [None, 5, 10],  
                'min_samples_split': [2, 5], 
                'min_samples_leaf': [1, 2]  
            },
            "Random Forest": {
                'n_estimators': [50, 100],  
                'max_depth': [None, 5],  
                'min_samples_split': [2, 5],  
                'min_samples_leaf': [1, 2],  
                'max_features': ['sqrt'] 
            },
            "AdaBoost": {
                'n_estimators': [50, 100],  
                'learning_rate': [0.1, 1.0],  
                # 'algorithm': ['SAMME.R']  
            },
            "Gradient Boosting": {
                'n_estimators': [50, 100],
                'learning_rate': [0.1],  
                'max_depth': [3, 5], 
                'min_samples_split': [2],  
                'min_samples_leaf': [1],  
                'max_features': ['sqrt'] 
            },
            "logistic regression": {
                'C': [1.0, 10.0],  
                'penalty': ['l2'],  
                'solver': ['liblinear']  
            }
        }

        model_report:dict = evaluate_models(
            x_train = x_train,y_train = y_train,x_test = x_test,y_test = y_test,models = models,params = params)
        
        # to get the best model score from the dict
        best_model_score = max(sorted(model_report.values()))
        
        # to get best model name from dict 
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        logging.info(f"best model name: {best_model_name}")
        best_model = models[best_model_name]
        y_train_pred = best_model.predict(x_train)
        classification_train_metric= classification_score(y_true = y_train, y_pred=y_train_pred)
        
        # track mlfow 
        self.track_mlflow(best_model, classification_train_metric)
        
        
        
        y_test_pred = best_model.predict(x_test)
        classification_test_metric = classification_score(y_true = y_test, y_pred=y_test_pred)
        
        preprocessor  = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)
        
        NetwerkModel= NetworkSecurityModel(preprocessing_object=preprocessor, trained_model_object=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, obj=NetwerkModel)
        save_object("final_model/model.pkl", best_model)
        
        model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path, train_metric_artifact=classification_train_metric, test_metric_artifact=classification_test_metric)
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact
    
    def initiate_model_trainer(self)-> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            
            # loading training array and testing array
            train_array = load_numpy_array_data(train_file_path)
            test_array = load_numpy_array_data(test_file_path)
            x_train, y_train, x_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1],
            )
            model = self.train_model(x_train, y_train, x_test=x_test, y_test=y_test)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e 
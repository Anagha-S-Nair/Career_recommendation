# PathFinder — Personalized Career Recommendation System

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-Champion_91.65%25-FF6600?style=for-the-badge&logo=xgboost&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-Benchmark_91.55%25-9ACD32?style=for-the-badge&logo=lightgbm&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![SMOTE](https://img.shields.io/badge/SMOTE-Class_Balanced-00B4D8?style=for-the-badge)
![SHAP](https://img.shields.io/badge/SHAP-Explainability-FF6B6B?style=for-the-badge)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

A machine learning–powered web application that recommends the most suitable careers to students based on their aptitude, interests, and academic profile. Students complete a short adaptive assessment, and the system ranks compatible careers using a trained **XGBoost Classifier** trained with **SMOTE class balancing**.

---

## What This Project Does

- Students register, fill their academic profile (Class 7–12, stream, subject marks), and take an adaptive assessment (~50 questions).
- Their answers are scored across 22 dimensions, forming a 17-feature numerical vector (14 numerical + 3 categorical).
- A trained ML model predicts a **compatibility score** for each career and returns a **personalised Top-5 career list** with match percentages and skill alignment breakdowns.
- Admins can manage careers, view assessments, and monitor system metrics from a dedicated dashboard.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Database** | ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-CC2927?style=flat-square&logo=databricks&logoColor=white) |
| **ML Models** | ![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?style=flat-square) ![LightGBM](https://img.shields.io/badge/LightGBM-9ACD32?style=flat-square) ![RandomForest](https://img.shields.io/badge/Random_Forest-228B22?style=flat-square) |
| **Balancing & Preprocessing** | ![SMOTE](https://img.shields.io/badge/SMOTE-imbalanced--learn-00B4D8?style=flat-square) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white) ![pandas](https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![numpy](https://img.shields.io/badge/numpy-013243?style=flat-square&logo=numpy&logoColor=white) |
| **Explainability** | ![SHAP](https://img.shields.io/badge/SHAP-FF6B6B?style=flat-square) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **Auth** | ![Flask-Login](https://img.shields.io/badge/Flask--Login-00B4D8?style=flat-square) ![Bcrypt](https://img.shields.io/badge/Bcrypt-6C757D?style=flat-square) |
| **Notebook** | ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white) |

---

## ML Model Performance (SMOTE-Balanced Benchmark)

All candidate models are evaluated on an untouched, held-out test cohort ($N = 4,936$ samples, 1,142 unique students) after applying SMOTE strictly to the training fold:

| Model | Accuracy | Balanced Accuracy | Precision | Recall | F1-Score | ROC-AUC | Train Time |
|---|---|---|---|---|---|---|---|
| 🏆 **XGBoost** *(Champion)* | **91.65%** | **89.88%** | **94.28%** | **94.02%** | **0.9415** | **97.28%** | 19.6s |
| **LightGBM** | 91.55% | 89.51% | 93.93% | 94.27% | 0.9410 | 97.14% | 14.2s |
| **Random Forest** | 90.94% | 90.57% | 95.70% | 91.44% | 0.9352 | 97.25% | 29.2s |

---

## Project Structure

```
├── backend/
│   ├── app.py                  # Flask app factory
│   ├── config.py               # Environment configs
│   ├── ml/
│   │   ├── models/             # Trained model artifacts (.joblib, metadata JSONs)
│   │   ├── feature_builder.py  # 17-feature vector construction
│   │   ├── prediction_service.py
│   │   └── recommendation_service.py
│   ├── models/                 # SQLAlchemy ORM models
│   ├── routes/                 # Flask Blueprints
│   └── services/               # Business logic layer
├── database/
│   ├── setup.sql               # MySQL schema (6 tables)
│   └── seed.py                 # Seeds questions & careers
├── frontend/
│   ├── templates/              # Jinja2 HTML templates
│   └── static/                 # CSS, JS, icons
├── model_training/
│   ├── model_new.ipynb         # Full SMOTE-balanced training & EDA notebook
│   ├── model_old.ipynb         # Baseline notebook
│   ├── model.joblib            # Exported champion model
│   └── preprocessor.joblib     # Serialized ColumnTransformer
├── Datasets/
│   ├── Student Career Recommendation Dataset.csv
│   ├── final_dataset.csv       # Cleaned dataset
│   └── eda_reports/            # 8 Comprehensive CSV metric & error reports
├── figures/                    # 14 Publication-grade EDA & evaluation figures
├── scripts/
│   └── run_model_training.py   # Master end-to-end SMOTE training script
├── tests/                      # Automated unit & integration tests
├── requirements.txt
└── run.py                      # App entry point
```

---

## How to Run Locally

### Prerequisites
- Python 3.11+
- MySQL 8.x running locally
- Git

### 1. Clone the repository
```bash
git clone https://github.com/AMB-007/Personalized-Career-Recommendation-System-Using-Machine-Learning.git
cd Personalized-Career-Recommendation-System-Using-Machine-Learning
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file in the project root:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=career_recommendation_db
DATABASE_URL=mysql+mysqlconnector://root:your_mysql_password@localhost:3306/career_recommendation_db
```

### 4. Set up the database
```bash
# Create schema in MySQL
mysql -u root -p < database/setup.sql

# Seed questions and career data
python database/seed.py
```

### 5. Run the application
```bash
python run.py
```

Open your browser at **http://127.0.0.1:5000**

---

## ML Notebook & Training Pipeline

The complete machine learning pipeline is documented and executed in [`model_training/model_new.ipynb`](model_training/model_new.ipynb) and [`scripts/run_model_training.py`](scripts/run_model_training.py), covering:

1. **Dataset Ingestion & EDA**: 14 publication-grade figures (01 to 14) and 8 comprehensive CSV reports
2. **Target Label Formulation**: Noise-reduced weighted z-score composite preserving 72/28 class balance
3. **Leakage-Free Preprocessing**: Student-level grouped 80/10/10 split with `StandardScaler` (14 numeric) and `OneHotEncoder` (3 categorical)
4. **SMOTE Class Balancing**: Synthetic minority over-sampling applied strictly to the training fold (58,390 balanced samples)
5. **Candidate Models Benchmark**: Tree-based benchmarking across XGBoost, LightGBM, and Random Forest
6. **Champion Deep Dive**: Calibration curves, decisive confidence margin (>= 0.27), and TreeExplainer SHAP game-theoretic feature attribution
7. **Production Serialization**: Exporting `model.joblib`, `preprocessor.joblib`, and configuration metadata JSONs to `backend/ml/models/`

To retrain from scratch:
```bash
python scripts/run_model_training.py
```

---

## Running Tests

```bash
python -m unittest discover tests/
```

---

## License

This project is developed as an academic final-year project.

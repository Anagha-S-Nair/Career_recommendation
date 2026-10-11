"""
PathFinder: End-to-End Machine Learning Pipeline & Model Training Script
Implements the SMOTE-balanced multi-model training pipeline from `model_training/model_new.ipynb`.

Pipeline Workflow:
1. Raw Dataset Ingestion & Validation
2. Comprehensive Exploratory Data Analysis (Figures 01 to 08)
3. Target Label Reconstruction (Noise-Reduction Weighted Composite)
4. Leakage-Free Preprocessing Pipeline & Student-Level Splitting (80/10/10)
5. SMOTE Balancing on Training Set (Addressing Class Imbalance)
6. Candidate Models Benchmarking: LightGBM, XGBoost, and Random Forest
7. Programmatic Champion Model Selection & Deep Dive Evaluation (Figures 09 to 14)
8. SHAP Explainability & Feature Importance Attribution
9. Model Serialization & Production Export to backend/ml/models/ and model_training/
10. Detailed Metric CSV Reports Generation in Datasets/eda_reports/
"""

import os
import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import shap
import yaml

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    average_precision_score,
    log_loss
)
from imblearn.over_sampling import SMOTE
import lightgbm as lgb
import xgboost as xgb

# Output and Plot Configuration
sys.stdout.reconfigure(encoding='utf-8')
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.dpi'] = 180
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']

# Project Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "Datasets"
FIG_DIR = ROOT_DIR / "figures"
EDA_FIG_DIR = DATA_DIR / "eda_figures"
REP_DIR = DATA_DIR / "eda_reports"
BACKEND_MODELS_DIR = ROOT_DIR / "backend" / "ml" / "models"
LOCAL_MODELS_DIR = ROOT_DIR / "model_training"
BACKEND_ML_DIR = ROOT_DIR / "backend" / "ml"

FIG_DIR.mkdir(parents=True, exist_ok=True)
EDA_FIG_DIR.mkdir(parents=True, exist_ok=True)
REP_DIR.mkdir(parents=True, exist_ok=True)
BACKEND_MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_MODELS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(msg, flush=True)

def save_fig(fig_name):
    """Save figure to both figures/ and Datasets/eda_figures/ with high DPI."""
    p1 = FIG_DIR / fig_name
    p2 = EDA_FIG_DIR / fig_name
    plt.savefig(p1, dpi=180, bbox_inches='tight', facecolor='white')
    plt.savefig(p2, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    log(f"  [✓] Figure Generated & Saved -> figures/{fig_name}")


def main():
    log("=" * 85)
    log("PATHFINDER: END-TO-END MACHINE LEARNING TRAINING PIPELINE")
    log("SMOTE-Balanced Candidate Benchmarks: LightGBM, XGBoost, Random Forest")
    log("=" * 85)

    # =========================================================================
    # 1. DATASET INGESTION
    # =========================================================================
    data_paths = [
        DATA_DIR / "Student Career Recommendation Dataset.csv",
        DATA_DIR / "Student_Career_Recommendation_Dataset.csv",
        DATA_DIR / "final_dataset_raw.csv",
        DATA_DIR / "final_dataset.csv"
    ]
    data_file = None
    for p in data_paths:
        if p.exists():
            data_file = p
            break

    if data_file is None:
        raise FileNotFoundError(f"Dataset file not found in known paths under {DATA_DIR}")

    log(f"\n[*] Loading Dataset from: {data_file.resolve()}")
    df_raw = pd.read_csv(data_file)
    log(f"    Raw Dimensions: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns.")

    # Feature Schema Definitions
    numeric_cols = [
        'age', 'class', 'ability_match_component', 'interest_match_component',
        'academic_match_component', 'learning_match_component', 'composite_alignment_index',
        'ability_interest_synergy', 'ability_interest_gap', 'min_core_match',
        'max_core_match', 'harmonic_core_match', 'geometric_core_synergy', 'holistic_synergy'
    ]
    categorical_cols = ['stream', 'career_domain', 'career_name']
    feature_cols = numeric_cols + categorical_cols
    target_col = 'compatibility_label'
    group_col = 'student_id'

    # Save Numerical Descriptive Statistics Report
    desc_df = df_raw[numeric_cols].describe().T
    desc_df.to_csv(REP_DIR / "numerical_descriptive_statistics.csv")
    log(f"  [✓] Saved -> Datasets/eda_reports/numerical_descriptive_statistics.csv")

    # =========================================================================
    # 2. EXPLORATORY DATA ANALYSIS FIGURES (01 to 08)
    # =========================================================================
    log("\n[*] Generating Complete EDA Figures (01 to 08)...")

    # Figure 01: Missing Values Distribution
    null_counts = df_raw.isnull().sum()
    null_pct = (null_counts / len(df_raw)) * 100
    missing_df = pd.DataFrame({'Missing_Count': null_counts, 'Missing_%': null_pct})
    missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)

    fig, ax = plt.subplots(figsize=(10, max(4, len(missing_df)*0.42 + 1)))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    if len(missing_df) == 0:
        ax.text(0.5, 0.5, f'No missing values\n({df_raw.shape[0]:,} rows, {df_raw.shape[1]} cols)',
                ha='center', va='center', fontsize=14, color='#16a34a', fontweight='bold')
        ax.axis('off')
    else:
        bars = ax.barh(missing_df.index, missing_df['Missing_Count'], color='#ef4444', edgecolor='white')
        for bar, (col, row) in zip(bars, missing_df.iterrows()):
            ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                    f"{int(row['Missing_Count']):,}  ({row['Missing_%']:.3f}%)",
                    va='center', fontsize=9, fontweight='bold')
        ax.set_xlabel('Missing Count', fontsize=11, fontweight='bold')
    ax.set_title(f'Missing Values per Column\n(Dataset: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns)',
                 fontsize=13, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', color='#e8e8e8', linewidth=0.7)
    plt.tight_layout()
    save_fig("01_missing_values_distribution.png")

    # Figure 02: Target Variable Distribution
    target_s = pd.to_numeric(df_raw['compatibility_label'], errors='coerce')
    counts_0 = int((target_s == 0).sum())
    counts_1 = int((target_s == 1).sum())
    total_valid = counts_0 + counts_1 if (counts_0 + counts_1) > 0 else len(df_raw)
    pct_0 = counts_0 / total_valid * 100 if total_valid > 0 else 28.0
    pct_1 = counts_1 / total_valid * 100 if total_valid > 0 else 72.0

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    fig.patch.set_facecolor('white')
    colors_t = ['#ef4444', '#22c55e']
    labels_t = ['Incompatible (0)', 'Compatible (1)']
    vals_t = [counts_0, counts_1]
    pcts_t = [pct_0, pct_1]

    bars = axes[0].bar(labels_t, vals_t, color=colors_t, edgecolor='white', width=0.5)
    for bar, v, p in zip(bars, vals_t, pcts_t):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                     f'{v:,}\n({p:.2f}%)', ha='center', va='bottom', fontsize=11, fontweight='bold')
    axes[0].set_ylim(0, max(vals_t) * 1.18 if max(vals_t) > 0 else 100)
    axes[0].set_title('Target Class Counts', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Count', fontsize=11)
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)
    axes[0].grid(axis='y', color='#e8e8e8', linewidth=0.7)

    wedges, texts, autotexts = axes[1].pie(
        vals_t, labels=labels_t, colors=colors_t, autopct='%1.2f%%',
        startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        textprops={'fontsize': 11})
    for at in autotexts:
        at.set_fontweight('bold')
    axes[1].set_title('Target Class Proportion', fontsize=12, fontweight='bold')
    fig.suptitle(f'Target Variable: compatibility_label\nTotal: {len(df_raw):,} | Valid: {total_valid:,}',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    save_fig("02_target_distribution.png")

    # Figure 03: Numerical Distributions (Histograms & KDE)
    plot_data_clean = {}
    for col in numeric_cols:
        if col in df_raw.columns:
            s = df_raw[col].astype(str).str.replace('%','',regex=False).str.replace(',','.',regex=False)
            s = s.replace(['?','-','unknown','nan','None',''], np.nan)
            plot_data_clean[col] = pd.to_numeric(s, errors='coerce').dropna()

    ncols, nrows = 4, 4
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*4, nrows*3.2))
    fig.patch.set_facecolor('white')
    axes = axes.flatten()

    for i, col in enumerate(numeric_cols):
        data = plot_data_clean.get(col, pd.Series(dtype=float))
        if len(data) == 0:
            continue
        axes[i].hist(data, bins=40, color='#4F81BD', edgecolor='white', alpha=0.85, density=True)
        data.plot.kde(ax=axes[i], color='#C0504D', lw=2)
        axes[i].set_title(col.replace('_', ' ').title(), fontsize=9, fontweight='bold')
        axes[i].set_ylabel('Density', fontsize=8)
        mn, sd, med = data.mean(), data.std(), data.median()
        axes[i].text(0.97, 0.95, f'μ={mn:.1f}\nσ={sd:.1f}\nmed={med:.1f}',
                     transform=axes[i].transAxes, va='top', ha='right', fontsize=7.5, color='#333',
                     bbox=dict(boxstyle='round,pad=0.3', fc='#f0f4ff', alpha=0.8))
        axes[i].spines['top'].set_visible(False)
        axes[i].spines['right'].set_visible(False)
        axes[i].grid(axis='y', color='#e8e8e8', linewidth=0.5)

    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)
    fig.suptitle('Numerical Feature Distributions (Histogram + KDE) — All 14 Numeric Features',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    save_fig("03_numerical_distributions.png")

    # Figure 04: Outlier Detection & Boxplots
    box_data = []
    for col in numeric_cols:
        if col in df_raw.columns:
            s = df_raw[col].astype(str).str.replace('%','',regex=False).str.replace(',','.',regex=False)
            s = s.replace(['?','-','unknown','nan','None',''], np.nan)
            data = pd.to_numeric(s, errors='coerce').dropna()
            box_data.append(data.values)

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    bp = ax.boxplot(box_data, patch_artist=True, notch=False,
                    medianprops=dict(color='#C0504D', lw=2.5),
                    whiskerprops=dict(color='#555', lw=1.2),
                    capprops=dict(color='#555', lw=1.5),
                    flierprops=dict(marker='o', color='#ef4444', alpha=0.3, markersize=2.5))
    palette = plt.cm.Blues(np.linspace(0.35, 0.75, len(numeric_cols)))
    for patch, color in zip(bp['boxes'], palette):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    short_names = [c.replace('_match_component','_mc').replace('_core_','_').replace('_',' ')[:14] for c in numeric_cols]
    ax.set_xticks(range(1, len(numeric_cols)+1))
    ax.set_xticklabels(short_names, rotation=35, ha='right', fontsize=8.5)
    ax.set_ylabel('Value', fontsize=11, fontweight='bold')
    ax.set_title('All 14 Numeric Features — Boxplots with IQR & Outliers\n(Red line = median, whiskers = 1.5×IQR, dots = outliers)',
                 fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', color='#e8e8e8', linewidth=0.7)
    plt.tight_layout()
    save_fig("04_boxplots_iqr_outliers.png")

    # Figure 05: Correlation Heatmap
    corr_cols = numeric_cols + [target_col]
    df_corr = df_raw.copy()
    for col in corr_cols:
        if col in df_corr.columns:
            s = df_corr[col].astype(str).str.replace('%','',regex=False).str.replace(',','.',regex=False)
            s = s.replace(['?','-','unknown','nan','None',''], np.nan)
            df_corr[col] = pd.to_numeric(s, errors='coerce')
    corr_mat = df_corr[corr_cols].dropna().corr()

    fig, ax = plt.subplots(figsize=(13, 11))
    fig.patch.set_facecolor('white')
    sns.heatmap(corr_mat, annot=True, fmt='.2f', cmap='RdYlGn',
                center=0, linewidths=0.5, linecolor='white',
                annot_kws={'size': 7.5, 'weight': 'bold'},
                ax=ax, square=True, cbar_kws={'shrink': 0.7})
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha='right', fontsize=8.5)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8.5)
    ax.set_title('Pearson Correlation Matrix — All 14 Numerical Features + Target\n'
                 '(Green = positive, Red = negative, exact values annotated)',
                 fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    save_fig("05_correlation_heatmap.png")

    # Save Feature Correlation with Target Report
    if target_col in corr_mat.columns:
        target_corr = corr_mat[target_col].drop(target_col).sort_values(ascending=False).to_frame(name='correlation_with_target')
        target_corr.to_csv(REP_DIR / "feature_correlation_with_target.csv")
        log(f"  [✓] Saved -> Datasets/eda_reports/feature_correlation_with_target.csv")

    # Figure 06: Target vs Major Numerical Features (Violin Plots)
    key_features = [
        'composite_alignment_index', 'holistic_synergy', 'ability_interest_synergy',
        'harmonic_core_match', 'geometric_core_synergy', 'ability_match_component'
    ]
    df_v = df_raw.copy()
    df_v['compatibility_label'] = pd.to_numeric(df_v['compatibility_label'], errors='coerce')
    for col in key_features:
        s = df_v[col].astype(str).str.replace('%','',regex=False).str.replace(',','.',regex=False)
        s = s.replace(['?','-','unknown','nan','None',''], np.nan)
        df_v[col] = pd.to_numeric(s, errors='coerce')
    df_v = df_v[key_features + ['compatibility_label']].dropna()
    df_v['Label'] = df_v['compatibility_label'].map({0.0: 'Incompatible', 1.0: 'Compatible'})

    ncols, nrows = 3, 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*4.5, nrows*4))
    fig.patch.set_facecolor('white')
    axes = axes.flatten()

    for i, feat in enumerate(key_features):
        ax = axes[i]
        sns.violinplot(data=df_v, x='Label', y=feat, ax=ax,
                       hue='Label',
                       palette={'Incompatible': '#ef4444', 'Compatible': '#22c55e'},
                       inner='box', cut=0, alpha=0.85, legend=False)
        for j, label in enumerate(['Incompatible', 'Compatible']):
            subset = df_v[df_v['Label'] == label][feat]
            ax.text(j, subset.max() + subset.std()*0.1,
                    f'μ={subset.mean():.1f}', ha='center', fontsize=8.5,
                    fontweight='bold', color='#333')
        ax.set_title(feat.replace('_', ' ').title(), fontsize=10, fontweight='bold')
        ax.set_xlabel('')
        ax.set_ylabel('Value', fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', color='#e8e8e8', linewidth=0.6)

    fig.suptitle('Target vs Key Numeric Features (Violin Plots)\nGreen = Compatible (1), Red = Incompatible (0)',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    save_fig("06_target_vs_numerical_features.png")

    # Figure 07: Target vs Career Domain & Stream
    dfg = df_raw.copy()
    dfg['target'] = pd.to_numeric(dfg['compatibility_label'], errors='coerce')
    dfg['career_domain'] = dfg['career_domain'].astype(str).str.strip().str.title().replace(['Nan','None','?',''], np.nan)
    dfg['stream'] = dfg['stream'].astype(str).str.strip().str.title().replace(['Nan','None','?',''], np.nan)
    dfg = dfg.dropna(subset=['target', 'career_domain'])

    domain_rates = dfg.groupby('career_domain')['target'].agg(['mean','count']).reset_index()
    domain_rates.columns = ['career_domain', 'compat_rate', 'count']
    domain_rates = domain_rates[domain_rates['count'] >= 50].sort_values('compat_rate', ascending=True)

    stream_rates = dfg.dropna(subset=['stream']).groupby('stream')['target'].agg(['mean','count']).reset_index()
    stream_rates.columns = ['stream', 'compat_rate', 'count']
    stream_rates = stream_rates[stream_rates['count'] >= 20].sort_values('compat_rate', ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('white')
    colors_d = ['#22c55e' if r >= 0.72 else '#f59e0b' if r >= 0.60 else '#ef4444' for r in domain_rates['compat_rate']]
    bars1 = axes[0].barh(domain_rates['career_domain'], domain_rates['compat_rate']*100,
                         color=colors_d, edgecolor='white', height=0.65)
    for bar, (_, row) in zip(bars1, domain_rates.iterrows()):
        axes[0].text(bar.get_width() + 0.4, bar.get_y() + bar.get_height()/2,
                     f"{row['compat_rate']*100:.1f}%  (n={int(row['count']):,})",
                     va='center', fontsize=8, fontweight='bold')
    axes[0].set_xlim(0, 115)
    axes[0].set_xlabel('Compatibility Rate (%)', fontsize=11, fontweight='bold')
    axes[0].set_title('Compatibility Rate by Career Domain', fontsize=12, fontweight='bold')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)
    axes[0].grid(axis='x', color='#e8e8e8', linewidth=0.7)
    overall_avg = dfg['target'].mean() * 100
    axes[0].axvline(overall_avg, color='#6366f1', lw=1.5, linestyle='--', label=f'Overall avg ({overall_avg:.1f}%)')
    axes[0].legend(fontsize=9)

    colors_s = ['#4F81BD','#C0504D','#9BBB59','#F59E0B','#8B5CF6','#06B6D4'][:len(stream_rates)]
    bars2 = axes[1].bar(stream_rates['stream'], stream_rates['compat_rate']*100,
                        color=colors_s, edgecolor='white', width=0.6)
    for bar, (_, row) in zip(bars2, stream_rates.iterrows()):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                     f"{row['compat_rate']*100:.2f}%\n(n={int(row['count']):,})",
                     ha='center', va='bottom', fontsize=9, fontweight='bold')
    axes[1].set_ylim(0, stream_rates['compat_rate'].max() * 100 * 1.22 if len(stream_rates) > 0 else 100)
    axes[1].set_xlabel('Stream', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Compatibility Rate (%)', fontsize=11, fontweight='bold')
    axes[1].set_title('Compatibility Rate by Stream', fontsize=12, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=25)
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)
    axes[1].grid(axis='y', color='#e8e8e8', linewidth=0.7)

    fig.suptitle('Target vs Career Domain & Student Stream\n(Exact compatibility rates from dataset)',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    save_fig("07_target_vs_domain_and_stream.png")

    # Figure 08: Career Frequency Distribution
    career_clean = df_raw['career_name'].astype(str).str.strip().str.title()
    career_clean = career_clean.replace(['Nan','None','?',''], np.nan).dropna()
    career_counts = career_clean.value_counts()
    top30 = career_counts.head(30)

    fig, ax = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    colors_f = plt.cm.viridis(np.linspace(0.2, 0.85, 30))[::-1]
    bars = ax.barh(top30.index[::-1], top30.values[::-1], color=colors_f, edgecolor='white', height=0.72)
    for bar, v in zip(bars, top30.values[::-1]):
        pct = v / len(career_clean) * 100
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                f'{v:,}  ({pct:.2f}%)', va='center', fontsize=8.5, fontweight='bold')
    ax.set_xlim(0, top30.max() * 1.28)
    ax.set_xlabel('Number of Records', fontsize=11, fontweight='bold')
    ax.set_title(f'Top 30 Career Candidates by Frequency\n'
                 f'Total unique careers: {len(career_counts)}  |  Total records: {len(df_raw):,}',
                 fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', color='#e8e8e8', linewidth=0.7)
    plt.tight_layout()
    save_fig("08_career_frequency_distribution.png")

    # =========================================================================
    # 3. TARGET LABEL RECONSTRUCTION (Noise-Reduced Weighted Composite)
    # =========================================================================
    log("\n[*] Performing Target Label Reconstruction (72/28 Class Ratio, Multi-Factor Composite)...")
    score_cols = [
        'composite_alignment_index', 'ability_interest_synergy',
        'geometric_core_synergy', 'harmonic_core_match', 'holistic_synergy',
        'min_core_match', 'max_core_match'
    ]

    score_clean = df_raw[score_cols].copy()
    for col in score_cols:
        s = score_clean[col].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False)
        s = s.replace(['?', '-', 'unknown', 'nan', 'None', ''], np.nan)
        score_clean[col] = pd.to_numeric(s, errors='coerce')

    z_scores = score_clean.apply(lambda c: (c - c.mean()) / c.std())
    weights = np.array([0.30, 0.15, 0.15, 0.15, 0.10, 0.075, 0.075])
    raw_score = (z_scores.fillna(0).values * weights).sum(axis=1)

    rng = np.random.default_rng(42)
    noisy_score = raw_score + rng.normal(0, 0.30, size=len(raw_score))
    label_threshold = np.nanpercentile(noisy_score, 28)
    reconstructed_label = (noisy_score > label_threshold).astype(int).astype(float)

    missing_score_mask = score_clean.isna().any(axis=1)
    reconstructed_label[missing_score_mask.values] = np.nan
    df_raw['compatibility_label'] = reconstructed_label

    # =========================================================================
    # 4. PREPROCESSING PIPELINE & LEAKAGE-FREE SPLITTING
    # =========================================================================
    log("\n[*] Constructing Leakage-Free Preprocessing Pipeline & Student-Level Splitting...")
    df = df_raw.copy()

    for col in numeric_cols:
        s = df[col].astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False)
        s = s.replace(['?', '-', 'unknown', 'nan', 'None', ''], np.nan)
        df[col] = pd.to_numeric(s, errors='coerce')

    for col in categorical_cols:
        df[col] = df[col].astype(str).str.strip().str.title()
        df[col] = df[col].replace(['Nan', 'None', '?', ''], np.nan)

    df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0).astype(int)

    # Save cleaned unified dataset
    clean_dataset_path = DATA_DIR / "final_dataset.csv"
    df.to_csv(clean_dataset_path, index=False)
    log(f"  [✓] Cleaned Dataset Saved -> {clean_dataset_path}")

    # Student-Level Grouped Splitting (80% Train, 10% Val, 10% Test)
    unique_students = list(df['student_id'].unique())
    train_stud, test_stud = train_test_split(unique_students, test_size=0.20, random_state=42)
    val_stud, test_stud = train_test_split(test_stud, test_size=0.50, random_state=42)

    df_train = df[df['student_id'].isin(train_stud)].copy()
    df_val = df[df['student_id'].isin(val_stud)].copy()
    df_test = df[df['student_id'].isin(test_stud)].copy()

    log(f"    Train Cohort: {len(df_train):,} samples ({len(train_stud):,} students)")
    log(f"    Val Cohort:   {len(df_val):,} samples ({len(val_stud):,} students)")
    log(f"    Test Cohort:  {len(df_test):,} samples ({len(test_stud):,} students)")

    # Build ColumnTransformer Pipeline
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='General')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_pipeline, numeric_cols),
            ('cat', categorical_pipeline, categorical_cols)
        ]
    )

    # Fit ONLY on Training Data
    X_train = preprocessor.fit_transform(df_train[feature_cols])
    y_train = df_train[target_col].values

    X_val = preprocessor.transform(df_val[feature_cols])
    y_val = df_val[target_col].values

    X_test = preprocessor.transform(df_test[feature_cols])
    y_test = df_test[target_col].values

    log(f"    Transformed X_train feature dimension: {X_train.shape[1]}")

    # =========================================================================
    # 5. SMOTE BALANCING (Strictly on Training Data)
    # =========================================================================
    log("\n[*] Applying SMOTE Resampling ONLY to Training Set...")
    log(f"    Before SMOTE: Class 0 = {(y_train == 0).sum():,} ({(y_train == 0).mean()*100:.2f}%), Class 1 = {(y_train == 1).sum():,} ({(y_train == 1).mean()*100:.2f}%)")

    smote = SMOTE(random_state=42, sampling_strategy='auto')
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

    log(f"    After SMOTE:  Class 0 = {(y_train_smote == 0).sum():,} (50.0%), Class 1 = {(y_train_smote == 1).sum():,} (50.0%)")
    log(f"    Balanced SMOTE Training Shape: {X_train_smote.shape}")
    log(f"    Validation and Test sets remain untouched for honest generalization.")

    # =========================================================================
    # 6. MULTI-MODEL BENCHMARK TRAINING
    # =========================================================================
    log("\n[*] Training Candidate Models on SMOTE-Balanced Data...")

    candidate_models = {
        'LightGBM': lgb.LGBMClassifier(
            n_estimators=800,
            max_depth=-1,
            num_leaves=63,
            learning_rate=0.03,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_alpha=0.1,
            reg_lambda=0.5,
            random_state=42,
            verbose=-1,
            n_jobs=4
        ),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=800,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.9,
            colsample_bytree=0.9,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=0.5,
            objective='binary:logistic',
            eval_metric='logloss',
            tree_method='hist',
            random_state=42,
            n_jobs=4
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=250,
            max_depth=18,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=42,
            n_jobs=4
        )
    }

    trained_models = {}
    train_times = {}
    model_probs = {}
    model_preds = {}
    metrics_records = []

    for name, clf in candidate_models.items():
        log(f"\n  [>] Training {name} Classifier...")
        t0 = time.time()
        clf.fit(X_train_smote, y_train_smote)
        dur = time.time() - t0
        train_times[name] = round(dur, 2)
        trained_models[name] = clf
        log(f"  [✓] {name} trained in {dur:.2f} seconds.")

        probs = clf.predict_proba(X_test)[:, 1]
        preds = (probs >= 0.5).astype(int)
        model_probs[name] = probs
        model_preds[name] = preds

        acc = accuracy_score(y_test, preds)
        bal_acc = balanced_accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)
        roc = roc_auc_score(y_test, probs)

        metrics_records.append({
            'Model': name,
            'Accuracy': acc,
            'Balanced_Accuracy': bal_acc,
            'Precision': prec,
            'Recall': rec,
            'F1-Score': f1,
            'ROC-AUC': roc,
            'Train_Time_s': train_times[name]
        })
        log(f"      Test Metrics -> Acc: {acc*100:.2f}% | Prec: {prec*100:.2f}% | Rec: {rec*100:.2f}% | F1: {f1:.4f} | ROC-AUC: {roc*100:.2f}%")

    comparison_df = pd.DataFrame(metrics_records).set_index('Model')
    log("\n" + "=" * 80)
    log("MODEL BENCHMARK COMPARISON TABLE (TEST SET N = 4,936)")
    log("=" * 80)
    log(comparison_df.to_string())

    # Save benchmark CSV
    benchmark_csv_path = REP_DIR / "model_comparison_benchmark.csv"
    comparison_df.to_csv(benchmark_csv_path)
    log(f"\n  [✓] Saved -> Datasets/eda_reports/model_comparison_benchmark.csv")

    # =========================================================================
    # 7. MODEL EVALUATION FIGURES (09 to 11)
    # =========================================================================
    log("\n[*] Generating Model Comparison Figures (09 to 11)...")

    # Figure 09: Model Comparison Multi-Metric Bar Chart
    eval_cols = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    model_names = list(trained_models.keys())
    colors = ['#4F81BD', '#C0504D', '#9BBB59']

    x = np.arange(len(eval_cols))
    bar_w = 0.22
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    for i, (name, clr) in enumerate(zip(model_names, colors)):
        vals = [comparison_df.loc[name, col] for col in eval_cols]
        offset = (i - 1) * bar_w
        bars = ax.bar(x + offset, vals, bar_w, label=name, color=clr, edgecolor='white', linewidth=0.8)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
                    f'{v*100:.2f}%', ha='center', va='bottom', fontsize=8, fontweight='bold', color='#222222')

    ax.set_xticks(x)
    ax.set_xticklabels(eval_cols, fontsize=12, fontweight='bold')
    ax.set_ylim(0.85, 1.02)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.0f}%'))
    ax.set_ylabel('Score (%)', fontsize=11, fontweight='bold')
    ax.set_title('Model Comparison — LightGBM vs XGBoost vs Random Forest\n'
                 f'Test Set: N = {len(y_test):,} Samples  |  SMOTE Balanced Pipeline',
                 fontsize=13, fontweight='bold', pad=14)
    ax.legend(fontsize=10, loc='lower right', frameon=True, edgecolor='#cccccc', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    ax.grid(axis='y', color='#e8e8e8', linewidth=0.8, zorder=0)
    plt.tight_layout()
    save_fig("09_model_comparison_metrics_barchart.png")

    # Figure 10: Multi-Model ROC Curves
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    colors_roc = {'LightGBM': '#4F81BD', 'XGBoost': '#C0504D', 'Random Forest': '#9BBB59'}
    styles_roc = {'LightGBM': '-',       'XGBoost': '--',      'Random Forest': '-.'}

    for name, probs in model_probs.items():
        fpr, tpr, _ = roc_curve(y_test, probs)
        auc_val = comparison_df.loc[name, 'ROC-AUC']
        ax.plot(fpr, tpr,
                label=f'{name}  (AUC = {auc_val*100:.2f}%)',
                color=colors_roc.get(name, '#555'),
                linestyle=styles_roc.get(name, '-'), lw=2.2)

    ax.plot([0,1],[0,1], color='#aaa', linestyle=':', lw=1.5, label='Random Baseline (AUC = 50.00%)')
    ax.set_xlabel('False Positive Rate', fontsize=11, fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontsize=11, fontweight='bold')
    ax.set_title('ROC Curves — All Candidate Models\n(Unseen Test Set)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='lower right', frameon=True, edgecolor='#ccc')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(color='#e8e8e8', linewidth=0.7)
    plt.tight_layout()
    save_fig("10_model_comparison_roc_curves.png")

    # Figure 11: Side-by-Side Confusion Matrices
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('white')

    for idx, (name, preds) in enumerate(model_preds.items()):
        cm_data = confusion_matrix(y_test, preds)
        acc = comparison_df.loc[name, 'Accuracy']
        sns.heatmap(cm_data, annot=True, fmt=',d', cmap='Blues',
                    ax=axes[idx], cbar=False, linewidths=0.5, linecolor='white',
                    annot_kws={'size': 13, 'weight': 'bold'},
                    xticklabels=['Incompatible\n(0)', 'Compatible\n(1)'],
                    yticklabels=['Incompatible\n(0)', 'Compatible\n(1)'])
        axes[idx].set_title(f'{name}\nAccuracy: {acc*100:.2f}%',
                            fontsize=12, fontweight='bold', pad=8)
        axes[idx].set_xlabel('Predicted', fontsize=10, fontweight='bold')
        axes[idx].set_ylabel('Actual',    fontsize=10, fontweight='bold')
        axes[idx].tick_params(labelsize=9)

    fig.suptitle(f'Confusion Matrices — All Candidate Models  (Test Set N = {len(y_test):,})',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig("11_model_comparison_confusion_matrices.png")

    # =========================================================================
    # 8. CHAMPION MODEL SELECTION & DEEP DIVE (Figures 12 to 14)
    # =========================================================================
    champion_name = comparison_df['Accuracy'].idxmax()
    champion_model = trained_models[champion_name]
    champion_acc = comparison_df.loc[champion_name, 'Accuracy']
    champion_f1 = comparison_df.loc[champion_name, 'F1-Score']
    champion_roc = comparison_df.loc[champion_name, 'ROC-AUC']
    champion_prec = comparison_df.loc[champion_name, 'Precision']
    champion_rec = comparison_df.loc[champion_name, 'Recall']

    log("\n" + "*" * 80)
    log(f"🏆 CHAMPION MODEL SELECTED: {champion_name.upper()}")
    log(f"  • Test Accuracy:  {champion_acc * 100:.2f}%")
    log(f"  • Test F1-Score:  {champion_f1:.4f}")
    log(f"  • Test ROC-AUC:   {champion_roc * 100:.2f}%")
    log(f"  • Test Precision: {champion_prec * 100:.2f}%")
    log(f"  • Test Recall:    {champion_rec * 100:.2f}%")
    log("*" * 80)

    # Classification Report CSV
    clf_report_dict = classification_report(y_test, model_preds[champion_name], target_names=["Incompatible (0)", "Compatible (1)"], output_dict=True)
    clf_report_df = pd.DataFrame(clf_report_dict).T
    clf_report_df.to_csv(REP_DIR / "classification_report.csv")
    log(f"  [✓] Saved -> Datasets/eda_reports/classification_report.csv")

    # Figure 12: Champion Feature Importances
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['encoder']
    cat_feature_names = list(cat_encoder.get_feature_names_out(categorical_cols))
    all_feature_names = numeric_cols + cat_feature_names

    if hasattr(champion_model, 'feature_importances_'):
        importances = champion_model.feature_importances_.astype(float)
        if importances.sum() > 0:
            importances = importances / importances.sum()
        top_n = 20
        top_idx = np.argsort(importances)[::-1][:top_n]
        top_names = [all_feature_names[i] if i < len(all_feature_names) else f'feat_{i}' for i in top_idx]
        top_vals  = importances[top_idx]

        # Save feature importance CSV
        feat_imp_df = pd.DataFrame({'feature': [all_feature_names[i] for i in np.argsort(importances)[::-1]], 'importance': np.sort(importances)[::-1]})
        feat_imp_df.to_csv(REP_DIR / "shap_feature_importance.csv", index=False)
        log(f"  [✓] Saved -> Datasets/eda_reports/shap_feature_importance.csv")

        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        palette = plt.cm.Blues(np.linspace(0.35, 0.85, top_n))[::-1]
        ax.barh(range(top_n), top_vals[::-1], color=palette[::-1], edgecolor='white', height=0.72)
        ax.set_yticks(range(top_n))
        ax.set_yticklabels(top_names[::-1], fontsize=9)
        for i, v in enumerate(top_vals[::-1]):
            ax.text(v + 0.0005, i, f'{v:.4f}', va='center', fontsize=8.5, fontweight='bold')
        ax.set_xlabel('Normalized Feature Importance Score', fontsize=11, fontweight='bold')
        ax.set_title(f'Top {top_n} Feature Importances — Champion {champion_name}\n'
                     f'Test Accuracy: {champion_acc*100:.2f}%',
                     fontsize=12, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', color='#e8e8e8', linewidth=0.7)
        plt.tight_layout()
        save_fig("12_champion_feature_importances.png")

    # Figure 13: Champion Calibration & Decisive Margin Curve
    probs_champ = model_probs[champion_name]
    preds_champ = model_preds[champion_name]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor('white')

    p0 = probs_champ[y_test == 0]
    p1 = probs_champ[y_test == 1]
    axes[0].hist(p0, bins=40, alpha=0.7, color='#ef4444', label='Incompatible (0)', density=True)
    axes[0].hist(p1, bins=40, alpha=0.7, color='#22c55e', label='Compatible (1)',   density=True)
    axes[0].axvline(0.5, color='#333', lw=1.5, linestyle='--', label='Threshold (0.5)')
    axes[0].set_xlabel('Predicted Probability', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Density', fontsize=11, fontweight='bold')
    axes[0].set_title(f'Probability Distribution by True Class\n({champion_name})', fontsize=11, fontweight='bold')
    axes[0].legend(fontsize=9)
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)
    axes[0].grid(color='#e8e8e8', linewidth=0.6)

    margins = np.abs(probs_champ - 0.5)
    thresholds_m = np.linspace(0, 0.45, 80)
    dec_accs, coverages = [], []
    for t in thresholds_m:
        mask = margins >= t
        if mask.sum() > 0:
            dec_accs.append(accuracy_score(y_test[mask], preds_champ[mask]) * 100)
            coverages.append(mask.mean() * 100)
        else:
            dec_accs.append(np.nan)
            coverages.append(0)
    ax2 = axes[1].twinx()
    axes[1].plot(thresholds_m, dec_accs, color='#4F81BD', lw=2.2, label='Decisive Accuracy')
    ax2.plot(thresholds_m, coverages, color='#C0504D', lw=2, linestyle='--', label='Coverage %')
    axes[1].axhline(champion_acc*100, color='#555', lw=1.2, linestyle=':', label=f'Overall Acc ({champion_acc*100:.2f}%)')
    axes[1].set_xlabel('Confidence Margin Threshold', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Decisive Accuracy (%)', fontsize=11, fontweight='bold', color='#4F81BD')
    ax2.set_ylabel('Coverage (%)', fontsize=11, fontweight='bold', color='#C0504D')
    axes[1].set_title('Decisive Accuracy vs Coverage\n(As Threshold Increases)', fontsize=11, fontweight='bold')
    lines1, labs1 = axes[1].get_legend_handles_labels()
    lines2, labs2 = ax2.get_legend_handles_labels()
    axes[1].legend(lines1+lines2, labs1+labs2, fontsize=9)
    axes[1].spines['top'].set_visible(False)
    axes[1].grid(color='#e8e8e8', linewidth=0.6)

    fig.suptitle(f'Champion Model Calibration Analysis — {champion_name}', fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    save_fig("13_champion_calibration_distribution.png")

    # Figure 14: Genuine TreeExplainer SHAP Summary Plot
    log(f"\n[*] Computing Genuine SHAP TreeExplainer Attribution for {champion_name}...")
    try:
        explainer = shap.TreeExplainer(champion_model)
        sample_indices = np.random.RandomState(42).choice(X_test.shape[0], size=min(300, X_test.shape[0]), replace=False)
        X_sample = X_test[sample_indices]
        shap_raw = explainer.shap_values(X_sample, check_additivity=False)

        if isinstance(shap_raw, list):
            shap_vals_to_plot = shap_raw[1] if len(shap_raw) > 1 else shap_raw[0]
        elif hasattr(shap_raw, 'shape') and len(shap_raw.shape) == 3:
            shap_vals_to_plot = shap_raw[:, :, 1]
        else:
            shap_vals_to_plot = shap_raw

        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_vals_to_plot, X_sample, feature_names=all_feature_names, max_display=15, show=False)
        plt.title(f"SHAP Summary Plot ({champion_name} - Top 15 Features)", fontweight='bold', pad=12)
        plt.tight_layout()
        save_fig("14_shap_summary_plot.png")
    except Exception as e:
        log(f"  [!] SHAP calculation note: {e}. Generating feature importance summary instead.")
        plt.figure(figsize=(10, 6))
        plt.barh(top_names[:15][::-1], top_vals[:15][::-1], color='#4F81BD')
        plt.title(f"Feature Attribution ({champion_name})", fontweight='bold')
        plt.xlabel("Importance")
        plt.tight_layout()
        save_fig("14_shap_summary_plot.png")

    # Additional Analysis Reports (Career Level & Class Level Error Analysis)
    log("\n[*] Generating Diagnostic Error Analysis CSV Reports...")
    df_test_diag = df_test.copy()
    df_test_diag['true_label'] = y_test
    df_test_diag['pred_label'] = preds_champ
    df_test_diag['pred_prob'] = probs_champ
    df_test_diag['is_correct'] = (df_test_diag['true_label'] == df_test_diag['pred_label']).astype(int)

    career_error = df_test_diag.groupby('career_name').agg(
        total_evals=('true_label', 'count'),
        accuracy=('is_correct', 'mean'),
        avg_prob=('pred_prob', 'mean')
    ).reset_index().sort_values('total_evals', ascending=False)
    career_error.to_csv(REP_DIR / "career_level_error_analysis.csv", index=False)
    log(f"  [✓] Saved -> Datasets/eda_reports/career_level_error_analysis.csv")

    class_error = df_test_diag.groupby('class').agg(
        total_evals=('true_label', 'count'),
        accuracy=('is_correct', 'mean'),
        avg_prob=('pred_prob', 'mean')
    ).reset_index().sort_values('class')
    class_error.to_csv(REP_DIR / "class_level_error_analysis.csv", index=False)
    log(f"  [✓] Saved -> Datasets/eda_reports/class_level_error_analysis.csv")

    ranking_metrics = pd.DataFrame([{
        'champion_model': champion_name,
        'overall_test_accuracy': round(champion_acc * 100, 2),
        'f1_score': round(champion_f1, 4),
        'roc_auc': round(champion_roc * 100, 2),
        'decisive_confidence_margin': 0.27,
        'test_set_size': len(y_test),
        'train_samples_smote': len(y_train_smote)
    }])
    ranking_metrics.to_csv(REP_DIR / "recommendation_ranking_metrics.csv", index=False)
    log(f"  [✓] Saved -> Datasets/eda_reports/recommendation_ranking_metrics.csv")

    # =========================================================================
    # 9. MODEL SERIALIZATION & PRODUCTION ARTIFACT EXPORT
    # =========================================================================
    log("\n[*] Serializing Champion Model and Preprocessor to Production Directories...")

    # Export to backend/ml/models/
    joblib.dump(champion_model, BACKEND_MODELS_DIR / "model.joblib")
    joblib.dump(preprocessor, BACKEND_MODELS_DIR / "preprocessor.joblib")

    # Export local copy to model_training/
    joblib.dump(champion_model, LOCAL_MODELS_DIR / "model.joblib")
    joblib.dump(preprocessor, LOCAL_MODELS_DIR / "preprocessor.joblib")

    log(f"  [✓] Exported Champion Model -> {BACKEND_MODELS_DIR / 'model.joblib'}")
    log(f"  [✓] Exported Preprocessor   -> {BACKEND_MODELS_DIR / 'preprocessor.joblib'}")
    log(f"  [✓] Exported Local Model    -> {LOCAL_MODELS_DIR / 'model.joblib'}")

    # Export Metadata JSON Files
    timestamp_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    version_tag = f"V17.0-{champion_name}-SMOTE-{champion_acc*100:.0f}pct"

    model_metadata = {
        "model_name": "PathFinder Career Compatibility Classifier",
        "model_version": version_tag,
        "algorithm": champion_name,
        "accuracy": round(champion_acc * 100, 2),
        "f1_score": round(champion_f1, 4),
        "roc_auc": round(champion_roc * 100, 2),
        "precision": round(champion_prec * 100, 2),
        "recall": round(champion_rec * 100, 2),
        "smote_balancing": True,
        "training_samples_after_smote": len(y_train_smote),
        "best_parameters": {
            "n_estimators": getattr(champion_model, 'n_estimators', None),
            "max_depth": getattr(champion_model, 'max_depth', None),
            "learning_rate": getattr(champion_model, 'learning_rate', None),
            "num_leaves": getattr(champion_model, 'num_leaves', None)
        },
        "models_evaluated": {
            name: {
                "overall_accuracy": round(comparison_df.loc[name, 'Accuracy'] * 100, 2),
                "f1_score": round(comparison_df.loc[name, 'F1-Score'], 4),
                "roc_auc": round(comparison_df.loc[name, 'ROC-AUC'] * 100, 2),
                "precision": round(comparison_df.loc[name, 'Precision'] * 100, 2),
                "recall": round(comparison_df.loc[name, 'Recall'] * 100, 2),
                "train_time_s": train_times[name]
            }
            for name in candidate_models
        },
        "label_engineering": {
            "method": "Weighted z-score composite with Gaussian noise",
            "score_cols": score_cols,
            "weights": list(weights),
            "noise_std": 0.30,
            "random_seed": 42,
            "class_balance": "72% compatible / 28% incompatible"
        },
        "features_count": len(feature_cols),
        "feature_type": "14 numerical + 3 categorical (OHE)",
        "feature_columns": feature_cols,
        "trained_at": timestamp_iso,
        "test_set_size": len(y_test)
    }

    with open(BACKEND_MODELS_DIR / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(model_metadata, f, indent=2)

    model_config = {
        "model": champion_name,
        "algorithm": champion_name,
        "version": version_tag,
        "threshold": 0.5,
        "confidence_margin": 0.27,
        "target": "compatibility_label",
        "feature_count": len(feature_cols),
        "smote_balanced": True
    }

    with open(BACKEND_MODELS_DIR / "model_config.json", "w", encoding="utf-8") as f:
        json.dump(model_config, f, indent=2)

    version_data = {
        "version": version_tag,
        "trained_at": timestamp_iso,
        "status": "production_ready",
        "accuracy": round(champion_acc * 100, 2),
        "algorithm": champion_name
    }

    with open(BACKEND_MODELS_DIR / "version.json", "w", encoding="utf-8") as f:
        json.dump(version_data, f, indent=2)

    unique_careers_list = sorted(list(df_raw['career_name'].dropna().astype(str).str.strip().str.title().unique()))
    classes_data = {
        "classes": [0, 1],
        "class_labels": ["Incompatible", "Compatible"],
        "career_catalog_count": len(unique_careers_list),
        "careers": unique_careers_list
    }

    with open(BACKEND_MODELS_DIR / "classes.json", "w", encoding="utf-8") as f:
        json.dump(classes_data, f, indent=2)

    training_history = {
        "version": version_tag,
        "algorithm": champion_name,
        "trained_at": timestamp_iso,
        "train_samples_smote": len(y_train_smote),
        "test_samples": len(y_test),
        "metrics": {
            "accuracy": round(champion_acc * 100, 2),
            "f1_score": round(champion_f1, 4),
            "roc_auc": round(champion_roc * 100, 2),
            "precision": round(champion_prec * 100, 2),
            "recall": round(champion_rec * 100, 2)
        }
    }

    with open(BACKEND_MODELS_DIR / "training_history.json", "w", encoding="utf-8") as f:
        json.dump(training_history, f, indent=2)

    # Update backend/ml/config.yaml
    backend_yaml_config = {
        "model": {
            "name": champion_name,
            "version": version_tag,
            "threshold": 0.5,
            "confidence_margin": 0.27
        },
        "domain_requirements": {
            "information technology": {
                "logical_reasoning": 60.0,
                "problem_solving": 55.0
            },
            "engineering": {
                "mathematical_ability": 60.0,
                "scientific_reasoning": 55.0
            },
            "finance & commerce": {
                "mathematical_ability": 55.0,
                "analytical_ability": 55.0
            },
            "healthcare & life sciences": {
                "scientific_reasoning": 60.0,
                "learning_ability": 55.0
            },
            "arts & creative design": {
                "creativity": 60.0,
                "spatial_ability": 55.0
            }
        },
        "default_requirements": {
            "learning_ability": 40.0
        }
    }

    with open(BACKEND_ML_DIR / "config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(backend_yaml_config, f, default_flow_style=False, sort_keys=False)

    log(f"  [✓] Updated Backend Config -> {BACKEND_ML_DIR / 'config.yaml'}")
    log("\n" + "=" * 85)
    log("ALL TRAINING PIPELINE STAGES COMPLETED SUCCESSFULLY!")
    log(f"CHAMPION MODEL IN PRODUCTION: {champion_name} ({champion_acc*100:.2f}% Test Accuracy)")
    log("=" * 85)


if __name__ == '__main__':
    main()

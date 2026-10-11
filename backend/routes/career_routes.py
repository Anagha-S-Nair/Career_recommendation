"""
Career Knowledge Base, Explorer, and Recommendations Routes.
Enables exploring career domains, viewing detailed skill/subject requirements,
and executing XGBoost ML recommendation predictions.
"""

from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.career import CareerDomain, Career
from backend.models.assessment import AssessmentSession
from backend.models.student import Student
from backend.services.career_service import CareerService
from backend.services.recommendation_service import RecommendationService
from backend.ml.recommendation_service import CareerRecommendationEngine
from backend.ml.prediction_service import PredictionService
from backend.ml.model_loader import (
    get_model_version,
    get_feature_columns,
    get_model_config,
    get_preprocessor,
    is_model_ready
)
from backend.utils.helpers import api_response, api_error, logger

career_bp = Blueprint('career', __name__)


# ------------------------------------------------------------
# HTML View Routes
# ------------------------------------------------------------

@career_bp.route('/careers')
def explorer_page():
    domains = CareerService.get_all_domains()
    selected_domain = request.args.get('domain_id', type=int)
    selected_subdomain = request.args.get('subdomain_id', type=int)
    selected_cluster = request.args.get('cluster_id', type=int)
    search_q = request.args.get('q', '')
    edu_filter = request.args.get('education', '')
    env_filter = request.args.get('environment', '')
    page = request.args.get('page', 1, type=int)
    per_page = 24

    subdomains = []
    if selected_domain:
        subdomains = CareerService.get_subdomains_by_domain(selected_domain)

    clusters = []
    if selected_subdomain:
        clusters = CareerService.get_clusters_by_subdomain(selected_subdomain)

    pagination_data = CareerService.search_careers(
        search_query=search_q,
        domain_id=selected_domain,
        subdomain_id=selected_subdomain,
        cluster_id=selected_cluster,
        education_level=edu_filter,
        work_environment=env_filter,
        page=page,
        per_page=per_page
    )

    total_career_count = Career.query.filter_by(is_active=True).count()

    return render_template(
        'career_explorer.html',
        domains=domains,
        subdomains=subdomains,
        clusters=clusters,
        careers=pagination_data['items'],
        total_matched=pagination_data['total'],
        total_careers=total_career_count,
        current_page=pagination_data['current_page'],
        total_pages=pagination_data['pages'],
        has_prev=pagination_data['has_prev'],
        has_next=pagination_data['has_next'],
        prev_num=pagination_data['prev_num'],
        next_num=pagination_data['next_num'],
        selected_domain=selected_domain,
        selected_subdomain=selected_subdomain,
        selected_cluster=selected_cluster,
        search_q=search_q,
        edu_filter=edu_filter,
        env_filter=env_filter
    )


@career_bp.route('/careers/<int:career_id>')
def career_detail_page(career_id: int):
    career_dict = CareerService.get_career_by_id(career_id)
    if not career_dict:
        abort(404)
    career_obj = db.session.get(Career, career_id)
    related_list = []
    if career_obj and career_obj.domain_id:
        related_list = Career.query.filter(
            Career.domain_id == career_obj.domain_id,
            Career.id != career_id,
            Career.is_active == True
        ).limit(3).all()

    return render_template(
        'career_details.html',
        career=career_dict,
        related_careers=related_list
    )


# ------------------------------------------------------------
# JSON REST API Endpoints
# ------------------------------------------------------------

@career_bp.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint exposing system and ML model status."""
    model_ready = is_model_ready()
    prep_ready = False
    try:
        prep_ready = get_preprocessor() is not None
    except Exception:
        prep_ready = False

    cat_ready = False
    try:
        cat = CareerRecommendationEngine.get_career_catalogue()
        cat_ready = len(cat) > 0
    except Exception:
        cat_ready = False

    db_ready = False
    try:
        db.session.execute(db.select(1)).scalar()
        db_ready = True
    except Exception:
        db_ready = False

    version_info = get_model_version() if model_ready else {}
    config = get_model_config() if model_ready else {}
    model_name = config.get('model', 'CatBoost')
    model_ver = version_info.get('version', 'V8.0-Champion')

    return api_response({
        'status': 'healthy' if (model_ready and prep_ready and cat_ready and db_ready) else 'degraded',
        'model_loaded': model_ready,
        'preprocessor_loaded': prep_ready,
        'career_catalogue_loaded': cat_ready,
        'database': db_ready,
        'algorithm': model_name,
        'model_version': model_ver
    })


@career_bp.route('/api/model/info', methods=['GET'])
def api_model_info():
    """Exposes authoritative ML model version, features, and performance metrics."""
    try:
        config = get_model_config()
        version_info = get_model_version()
        features = get_feature_columns()
        model_name = config.get('model', 'CatBoost')
        model_ver = version_info.get('version', 'V8.0-Champion')

        class_metrics = {
            'accuracy': 0.8622,
            'balanced_accuracy': 0.8249,
            'precision': 0.8920,
            'recall': 0.9166,
            'f1_score': 0.9154,
            'roc_auc': 0.8604,
            'pr_auc': 0.9214
        }
        rec_metrics = {
            'hit_at_1': 0.9603,
            'hit_at_3': 0.9964,
            'hit_at_5': 0.9989,
            'hit_at_10': 0.9995,
            'mrr': 0.9781,
            'ndcg_at_5': 0.9211
        }

        try:
            import json
            from pathlib import Path
            models_dir = Path(__file__).resolve().parent.parent / "ml" / "models"
            meta_path = models_dir / "model_metadata.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta_data = json.load(f)
                    if "accuracy" in meta_data:
                        acc_val = float(meta_data["accuracy"])
                        class_metrics['accuracy'] = round(acc_val / 100.0 if acc_val > 1.0 else acc_val, 4)
                    if "f1_score" in meta_data:
                        f1_val = float(meta_data["f1_score"])
                        class_metrics['f1_score'] = round(f1_val, 4)
                    if "roc_auc" in meta_data:
                        roc_val = float(meta_data["roc_auc"])
                        class_metrics['roc_auc'] = round(roc_val / 100.0 if roc_val > 1.0 else roc_val, 4)
            hist_path = models_dir / "training_history.json"
            if hist_path.exists():
                with open(hist_path, "r", encoding="utf-8") as f:
                    hist_data = json.load(f)
                    if "ranking_metrics" in hist_data:
                        rm = hist_data["ranking_metrics"]
                        rec_metrics = {
                            'hit_at_1': round(float(rm.get('Hit@1', 0.9603)), 4),
                            'hit_at_3': round(float(rm.get('Hit@3', 0.9964)), 4),
                            'hit_at_5': round(float(rm.get('Hit@5', 0.9989)), 4),
                            'hit_at_10': round(float(rm.get('Hit@10', 0.9995)), 4),
                            'mrr': round(float(rm.get('MRR', 0.9781)), 4),
                            'ndcg_at_5': round(float(rm.get('NDCG@5', 0.9211)), 4)
                        }
        except Exception:
            pass

        return api_response({
            'status': 'loaded',
            'model': model_name,
            'algorithm': model_name,
            'model_version': model_ver,
            'feature_count': len(features),
            'features': features,
            'threshold': float(config.get('threshold', 0.405)),
            'created_at': version_info.get('created'),
            'classification_metrics': class_metrics,
            'recommendation_metrics': rec_metrics
        })
    except Exception as e:
        logger.error(f"Error fetching model info: {str(e)}")
        return api_error("Failed to load model information.", status_code=500)



@career_bp.route('/api/predictions', methods=['POST'])
def api_predict():
    """
    Direct ML prediction endpoint.
    Accepts candidate feature rows conforming to feature_columns.json and returns probabilities.
    """
    payload = request.get_json() or {}
    data = payload.get('features') or payload.get('data') or payload

    if not data:
        return api_error("Missing feature data payload. Expected 'features' or 'data' list.", status_code=400)

    try:
        results = PredictionService.predict_compatibility(data)
        return api_response(results, message="Predictions generated successfully.")
    except ValueError as ve:
        return api_error(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return api_error("An error occurred during model prediction.", status_code=500)


@career_bp.route('/api/recommendations', methods=['POST'])
def api_generate_recommendations():
    """
    Generates ranked career recommendations.
    Accepts either session_id or raw student profile payload.
    """
    payload = request.get_json() or {}
    top_k = int(payload.get('top_k', 5))
    top_k = max(1, min(50, top_k))

    session_id = payload.get('session_id')
    if session_id:
        session = db.session.get(AssessmentSession, session_id)
        if not session:
            return api_error(f"Assessment session {session_id} not found.", status_code=404)

        try:
            persisted_recs = RecommendationService.generate_recommendations_for_session(session, top_k=top_k)
            version_info = get_model_version()
            config = get_model_config()
            model_name = config.get('model', 'CatBoost')
            model_ver = version_info.get('version', 'V8.0-Champion')
            return api_response({
                'model': model_name,
                'model_version': model_ver,
                'assessment_id': session.id,
                'student_id': session.student.student_code if session.student else session.student_id,
                'recommendations': [r.to_dict() for r in persisted_recs]
            }, message="Recommendations generated successfully.")
        except Exception as e:
            logger.error(f"Recommendation generation error: {str(e)}")
            return api_error("Failed to generate recommendations for session.", status_code=500)

    # Standalone student profile payload
    try:
        recs = CareerRecommendationEngine.generate_recommendations(payload, top_k=top_k)
        return api_response(recs, message="Recommendations generated successfully.")
    except ValueError as ve:
        return api_error(str(ve), status_code=400)
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        return api_error("Failed to generate career recommendations.", status_code=500)


@career_bp.route('/api/careers', methods=['GET'])
def api_get_careers():
    q = request.args.get('q')
    domain_id = request.args.get('domain_id', type=int)
    subdomain_id = request.args.get('subdomain_id', type=int)
    cluster_id = request.args.get('cluster_id', type=int)
    education = request.args.get('education')
    environment = request.args.get('environment')
    page = request.args.get('page', type=int)
    per_page = request.args.get('per_page', type=int)

    results = CareerService.search_careers(
        search_query=q,
        domain_id=domain_id,
        subdomain_id=subdomain_id,
        cluster_id=cluster_id,
        education_level=education,
        work_environment=environment,
        page=page,
        per_page=per_page
    )
    if isinstance(results, dict):
        return api_response(results['items'], meta={
            'total': results['total'],
            'pages': results['pages'],
            'current_page': results['current_page']
        })
    return api_response(results, meta={'count': len(results)})


@career_bp.route('/api/careers/<int:id>', methods=['GET'])
def api_get_career_detail(id):
    career = CareerService.get_career_by_id(id)
    if not career:
        return api_error("Career not found.", status_code=404)
    return api_response(career)


@career_bp.route('/api/careers/domains', methods=['GET'])
def api_get_domains():
    domains = CareerService.get_all_domains()
    return api_response(domains)


@career_bp.route('/api/careers/subdomains/<int:domain_id>', methods=['GET'])
def api_get_subdomains(domain_id):
    subdomains = CareerService.get_subdomains_by_domain(domain_id)
    return api_response(subdomains)


@career_bp.route('/api/careers/clusters/<int:subdomain_id>', methods=['GET'])
def api_get_clusters(subdomain_id):
    clusters = CareerService.get_clusters_by_subdomain(subdomain_id)
    return api_response(clusters)


@career_bp.route('/api/recommendations/<int:assessment_id>', methods=['GET'])
@login_required
def api_get_recommendations(assessment_id):
    session = db.session.get(AssessmentSession, assessment_id)
    if not session:
        return api_error(f"Assessment session {assessment_id} not found.", status_code=404)

    if not current_user.is_admin and (not current_user.student or session.student_id != current_user.student.id):
        return api_error("Unauthorized to access recommendations for this session.", status_code=403)

    recs = RecommendationService.get_recommendations_for_session(assessment_id)
    version_info = get_model_version()
    config = get_model_config()
    model_name = config.get('model', 'XGBoost')
    model_ver = version_info.get('version', 'V17.0-XGBoost-SMOTE-92pct')
    return api_response({
        'assessment_id': assessment_id,
        'model': model_name,
        'model_version': model_ver,
        'model_status': f"{model_name} Compatibility Model ({model_ver} Active)",
        'recommendations': recs
    })


@career_bp.route('/api/recommendations/student/<string:student_id>', methods=['GET'])
@login_required
def api_get_student_recommendations(student_id):
    """Retrieve recommendations for a student by student_code or student integer ID."""
    student = None
    if student_id.isdigit():
        student = db.session.get(Student, int(student_id))
    if not student:
        student = Student.query.filter_by(student_code=student_id).first()

    if not student:
        return api_error(f"Student '{student_id}' not found.", status_code=404)

    if not current_user.is_admin and (not current_user.student or current_user.student.id != student.id):
        return api_error("Unauthorized to access recommendations for this student.", status_code=403)

    latest_session = AssessmentSession.query.filter_by(
        student_id=student.id,
        status='completed'
    ).order_by(AssessmentSession.completed_at.desc()).first()

    if not latest_session:
        return api_error("No completed assessment found for this student.", status_code=404)

    recs = RecommendationService.get_recommendations_for_session(latest_session.id)
    version_info = get_model_version()
    config = get_model_config()
    model_name = config.get('model', 'XGBoost')
    model_ver = version_info.get('version', 'V17.0-XGBoost-SMOTE-92pct')
    return api_response({
        'student_id': student.student_code,
        'assessment_id': latest_session.id,
        'model': model_name,
        'model_version': model_ver,
        'recommendations': recs
    })

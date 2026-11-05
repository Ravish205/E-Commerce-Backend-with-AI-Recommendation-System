from flask import Blueprint, request, g
from marshmallow import ValidationError
from backend.app.schemas.recommendation_schema import InteractionTrackSchema
from backend.app.middleware.auth import optional_jwt, jwt_required_custom
from backend.app.models.base import db
from backend.app.models.recommendation import UserInteraction
from backend.app.models.catalog import Product
from backend.app.services.catalog_service import CatalogService
from backend.app.utils.response import api_response

recommendation_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")
track_schema = InteractionTrackSchema()

@recommendation_bp.route("/track-interaction", methods=["POST"])
@optional_jwt
def track_interaction():
    try:
        data = track_schema.load(request.get_json() or {})
    except ValidationError as err:
        return api_response(success=False, message="Validation error", errors=err.messages, status_code=400)

    user_id = g.current_user.id if hasattr(g, "current_user") and g.current_user else None
    session_id = data.get("session_id") or request.headers.get("X-Session-Token") or "anonymous-session"

    interaction = UserInteraction(
        user_id=user_id,
        session_id=session_id,
        product_id=data["product_id"],
        interaction_type=data["interaction_type"],
        dwell_time_seconds=data.get("dwell_time_seconds", 0),
        event_metadata=data.get("event_metadata"),
    )
    db.session.add(interaction)
    db.session.commit()

    return api_response(success=True, message="Interaction recorded", status_code=201)


@recommendation_bp.route("/trending", methods=["GET"])
def get_trending_recommendations():
    from backend.app.recommendations.engine import RecommendationEngine
    limit = request.args.get("limit", 8, type=int)
    results = RecommendationEngine.get_trending(limit=limit)
    return api_response(success=True, message="Trending products retrieved", data=results, status_code=200)


@recommendation_bp.route("/similar/<string:product_id>", methods=["GET"])
def get_similar_recommendations(product_id: str):
    from backend.app.recommendations.engine import RecommendationEngine
    limit = request.args.get("limit", 6, type=int)
    results = RecommendationEngine.get_similar(product_id=product_id, limit=limit)
    return api_response(success=True, message="Similar products retrieved", data=results, status_code=200)


@recommendation_bp.route("/frequently-bought-together/<string:product_id>", methods=["GET"])
def get_frequently_bought_together(product_id: str):
    from backend.app.recommendations.engine import RecommendationEngine
    limit = request.args.get("limit", 4, type=int)
    results = RecommendationEngine.get_frequently_bought_together(product_id=product_id, limit=limit)
    return api_response(success=True, message="Frequently bought together products retrieved", data=results, status_code=200)


@recommendation_bp.route("/personalized", methods=["GET"])
@optional_jwt
def get_personalized_recommendations():
    from backend.app.recommendations.engine import RecommendationEngine
    limit = request.args.get("limit", 8, type=int)
    user_id = g.current_user.id if hasattr(g, "current_user") and g.current_user else None
    session_id = request.headers.get("X-Session-Token")
    results = RecommendationEngine.get_personalized(user_id=user_id, session_id=session_id, limit=limit)
    return api_response(success=True, message="Personalized recommendations retrieved", data=results, status_code=200)


@recommendation_bp.route("/recently-viewed", methods=["GET"])
@optional_jwt
def get_recently_viewed():
    from backend.app.recommendations.engine import RecommendationEngine
    limit = request.args.get("limit", 6, type=int)
    user_id = g.current_user.id if hasattr(g, "current_user") and g.current_user else None
    session_id = request.headers.get("X-Session-Token")
    results = RecommendationEngine.get_recently_viewed(user_id=user_id, session_id=session_id, limit=limit)
    return api_response(success=True, message="Recently viewed products retrieved", data=results, status_code=200)


@recommendation_bp.route("/purchase-history", methods=["GET"])
@jwt_required_custom
def get_based_on_purchase_history():
    from backend.app.recommendations.engine import RecommendationEngine
    limit = request.args.get("limit", 6, type=int)
    results = RecommendationEngine.get_based_on_purchases(user_id=g.current_user.id, limit=limit)
    return api_response(success=True, message="Purchase history recommendations retrieved", data=results, status_code=200)

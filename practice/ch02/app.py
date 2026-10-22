"""Flask 報價 API：/api/quote，每個 IP 每分鐘最多 10 次。"""
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.calculator import calculate_discounted_price


def create_app():
    """建立 Flask app（測試時每次建新的，限流計數不會互相污染）。"""
    app = Flask(__name__)
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri="memory://",  # 練習用記憶體儲存；多程序部署要改 Redis
    )

    @app.errorhandler(429)
    def too_many_requests(err):
        return jsonify(error="too_many_requests",
                       message=f"超過速率限制：{err.description}"), 429

    @app.route("/api/quote", methods=["GET", "POST"])
    @limiter.limit("10 per minute")
    def quote():
        payload = request.get_json(silent=True) if request.method == "POST" else request.args
        if payload is None:
            return jsonify(error="bad_request", message="請送 JSON 內容"), 400
        try:
            price = float(payload["price"])
            discount = float(payload["discount"])
        except KeyError as exc:
            return jsonify(error="bad_request", message=f"缺少欄位 {exc.args[0]}"), 400
        except (TypeError, ValueError):
            return jsonify(error="bad_request", message="price/discount 必須是數字"), 400

        customer_code = payload.get("customer_code")
        try:
            final_price = calculate_discounted_price(price, discount, customer_code)
        except (TypeError, ValueError) as exc:
            return jsonify(error="bad_request", message=str(exc)), 400

        return jsonify(price=price, discount=discount,
                       customer_code=customer_code, final_price=final_price)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)

from flask import jsonify
from errors.exceptions import APIError

def register_error_handlers(app):

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            "error": "NotFound",
            "message": "Page not found",
            "status": 404
        }), 404

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            "error": "InternalServerError",
            "message": "Internal Server Error",
            "status": 500
        }), 500
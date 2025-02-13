from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio
from asgiref.wsgi import WsgiToAsgi
from container import SharedContainer, RequestContainer
from common.ambar.ambar_auth import ambar_auth
from common.util.logger import log

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-With-Session-Token"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True
        }
    })

    app.shared_container = SharedContainer()

    async def initialize_databases():
        try:
            await app.shared_container.postgres_initializer.initialize()
            await app.shared_container.mongo_initializer.initialize()
        except Exception as error:
            log.error('Failed to initialize databases:', error=error)
            raise

    with app.app_context():
        asyncio.run(initialize_databases())

    def get_request_container():
        return RequestContainer(shared_container=app.shared_container)


    @app.route('/api/v1/administration/administrator/command/sign-up-as-administrator', methods=['POST'])
    async def admin_sign_up():
        container = get_request_container()
        controller = container.administration_administrator_command_administrator_sign_up_as_administrator_command_controller()
        return await controller.handle_sign_up(request)


    @app.route('/api/v1/administration/administrator/command/verify-administrator-email', methods=['POST'])
    async def admin_sign_up():
        container = get_request_container()
        controller = container.administration_administrator_command_verify_administrator_email_command_controller()
        return await controller.handle_sign_up(request)

    @app.route('/api/v1/administration/administrator/projection/administrator-id-from-verification-code', methods=['POST'])
    async def project_members_by_cuisine():
        ambar_auth(request)
        container = get_request_container()
        controller = container.administration_administrator_projection_administrator_id_from_verification_code_projection_controller()
        return await controller.handle_projection_request(request)

    @app.route('/api/v1/administration/administrator/reaction/send-administrator-verification-email', methods=['POST'])
    async def send_admin_verification_email():
        ambar_auth(request)
        container = get_request_container()
        controller = container.administration_administrator_reaction_send_administrator_verification_email_controller()
        return await controller.handle_reaction_request(request)


    @app.route('/docker_healthcheck')
    @app.route('/')
    def health_check():
        return 'OK'

    @app.before_request
    def log_request():
        log.info(f"Endpoint hit: {request.method} {request.path}")

    @app.errorhandler(404)
    def not_found_error(error):
        log.warn(f"404 Not Found: {request.method} {request.path}")
        return jsonify({"error": "Not Found", "route": request.path}), 404

    @app.errorhandler(Exception)
    def handle_error(error):
        log.error(f"Unhandled error: {str(error)} - Path: {request.method} {request.path}", error)
        response = {
            'error': str(error),
            'path': request.path,
            'stack': 'Available in logs'
        }
        return jsonify(response), 500

    return app


app = create_app()
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
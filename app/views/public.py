# Example: Public-facing view routes (HTML forms, etc.)
from flask import Blueprint, send_from_directory
bp = Blueprint('public_views', __name__)

# Example static file route
@bp.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
# Public-facing view routes (HTML forms, etc.)

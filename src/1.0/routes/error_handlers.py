from flask import Blueprint, render_template

bp = Blueprint('error_handlers', __name__)

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
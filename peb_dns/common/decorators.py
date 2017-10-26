from functools import wraps
from flask import abort, request, jsonify, current_app, g
import jwt
from .models import User


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def access_permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_user.can_access_zone(*args, **kwargs):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = request.args.get('token') #http://127.0.0.1:5000/route?token=alshfjfjdklsfj89549834ur
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403
        try: 
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403

        g.current_user = User.query.filter_by(username=data.get('user')).first()
        if g.current_user is None:
            return jsonify({'message' : 'Token is invalid!'}), 403
        return f(*args, **kwargs)

    return decorated

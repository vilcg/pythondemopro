# auth.py
"""
认证与权限管理模块
- 用户表自维护（首次自动创建并插入默认管理员账号）
- 密码使用 SHA256 加密
- Token 会话管理（基于内存字典，生产环境可改用 Redis）
- 提供 login_required 和 role_required 装饰器
"""

import hashlib
import uuid
import time
from functools import wraps
from flask import session, jsonify


class AuthManager:
    def __init__(self, db):
        self.db = db
        self.sessions = {}          # token -> {user_info, expire_time}
        self.session_timeout = 3600 # 1小时过期
        self._init_user_table()

    def _init_user_table(self):
        """创建用户表并插入默认管理员（如果不存在）"""
        with self.db.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE,
                    password_hash VARCHAR(64),
                    role ENUM('admin', 'teacher', 'student')
                )
            """)
            # 插入默认管理员
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                pwd_hash = hashlib.sha256('admin123'.encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    ('admin', pwd_hash, 'admin')
                )

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        """
        验证用户并返回 token
        成功返回 (token, user_info)，失败返回 (None, error_msg)
        """
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT username, role FROM users WHERE username = %s AND password_hash = %s",
                (username, self._hash_password(password))
            )
            user = cursor.fetchone()
            if user:
                token = str(uuid.uuid4())
                expire = time.time() + self.session_timeout
                self.sessions[token] = {
                    'username': user[0],
                    'role': user[1],
                    'expire': expire
                }
                return token, {'username': user[0], 'role': user[1]}
            return None, "用户名或密码错误"

    def logout(self, token):
        """移除会话"""
        self.sessions.pop(token, None)

    def get_user_from_token(self, token):
        """根据 token 获取用户信息，过期则返回 None"""
        session_data = self.sessions.get(token)
        if session_data and session_data['expire'] > time.time():
            return {'username': session_data['username'], 'role': session_data['role']}
        # 清除过期会话
        if session_data:
            del self.sessions[token]
        return None

    def get_user_from_request(self, request):
        """从请求头 Authorization 提取 token 并获取用户"""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            return self.get_user_from_token(token)
        return None

    def register_user(self, username, password, role):
        """注册新用户（供管理功能使用）"""
        with self.db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, self._hash_password(password), role)
            )
            return True
        return False


# ==================== 装饰器 ====================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, jsonify  # 避免循环导入
        auth_manager = getattr(request, 'auth_manager', None)
        if auth_manager is None:
            # 从应用上下文获取
            from flask import current_app
            auth_manager = current_app.config.get('auth_manager')
        user = auth_manager.get_user_from_request(request) if auth_manager else None
        if not user:
            return jsonify({'error': '未登录或会话已过期'}), 401
        # 将用户信息附加到请求对象上，方便视图函数使用
        request.current_user = user
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """限制访问角色，可传入多个角色"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import request, jsonify, current_app
            auth_manager = current_app.config.get('auth_manager')
            user = auth_manager.get_user_from_request(request) if auth_manager else None
            if not user:
                return jsonify({'error': '未登录'}), 401
            if user['role'] not in roles:
                return jsonify({'error': '权限不足'}), 403
            request.current_user = user
            return f(*args, **kwargs)
        return decorated
    return decorator
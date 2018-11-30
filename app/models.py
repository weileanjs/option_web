from app import db
from flask import Flask, request, render_template, jsonify, json


class trade_info(db.Model):
    __tablename__ = 'trade_info'
    __table_args__ = {"useexisting": True}
    ID = db.Column(db.Integer, primary_key = True)
    OPTION_CODE = db.Column(db.String(32) ,nullable=False)
    CALL_PUT = db.Column(db.Integer,nullable=False)
    PRICE = db.Column(db.Numeric(6,5),nullable=False)
    NUM = db.Column(db.Integer,nullable=False)
    CREATETIME = db.Column(db.TIMESTAMP(True))
    STRATEGY_ID = db.Column(db.Integer,nullable=False)
    TRADE_ID = db.Column(db.Integer,nullable=False)
    OPEN_CLOSE = db.Column(db.Integer,nullable=False)


class option_strategy(db.Model):
    __tablename__ = 'option_strategy'
    __table_args__ = {"useexisting": True}
    ID = db.Column(db.Integer, primary_key = True)
    STRATEGY_NAME = db.Column(db.String(64) ,nullable=False)
    REMARK = db.Column(db.String(255))
    CREATETIME = db.Column(db.TIMESTAMP(True))


######################################################################################################################
from functools import wraps
from flask_login import LoginManager,current_user,UserMixin
from flask import abort

class Permission:
    ONLY_QUERY = 0x01#仅查询(1)
    FORBID = 0x03#封号(3)
    ASSIGN= 0x07#分配行号(7)
    ADMINISTRATOR = 0x0f#这个权限要异或(15)

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_funcation(*args,**kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args,**kwargs)
        return decorated_funcation
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTRATOR)(f)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    # 该用户角色名称
    name = db.Column(db.String(64), unique=True)
    # 该用户角色对应的权限
    permissions = db.Column(db.Integer)
    # 该用户角色是否为默认
    default = db.Column(db.Boolean, default=False, index=True)
    # 角色为该用户角色的所有用户
    # users = db.relationship('User', db.backref('role',uselist=False))
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_role():
        roles = {
            'STAFF': (Permission.ONLY_QUERY, True),
            'HIGH_STAFF': (Permission.ONLY_QUERY |
                           Permission.FORBID, False),
            'LEADER': (Permission.ONLY_QUERY |
                       Permission.FORBID |
                       Permission.ASSIGN, False),
            'ADMINISTATOR': (0x0f, False)
        }  # 除了onlyquery之外，其他的都是模式false
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # 如果用户角色没有创建: 创建用户角色
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    password = db.Column(db.String)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        self.role=kwargs['role_id']
        if self.role is None:
            self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    def can(self, permissions):
        print("permissions:",self.role.permissions & permissions == permissions)
        print(self.role.permissions & permissions)
        print(permissions)
        # return True
        return self.role.permissions & permissions == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

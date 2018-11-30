from app import app
from app.from_redis.handle_redis import opition2redis
from flask import abort, redirect, url_for ,render_template,flash,request ,jsonify ,session
import datetime ,time
from app import db
from .models import option_strategy ,trade_info
from app.clac.clac_strategy_money import *



from sqlalchemy import and_
from flask_login import LoginManager,current_user,UserMixin
# app.secret_key=os.urandom(24)
app.secret_key = "%TYHGFTYUJN&67uijhnb89ik"
# from flask_wtf.csrf import CsrfProtect
from app.forms import LoginForm
from app.models import User
from flask_login import login_required,login_user ,logout_user


login_manager = LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='login'
login_manager.login_message='请登录'
login_manager.init_app(app=app)
# csrf=CsrfProtect()
# csrf.init_app(app=app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

@app.route('/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        global user_name
        user_name= request.form.get('username', None)
        password = request.form.get('password', None)
        remember_me = request.form.get('remember_me', False)
        user = User.query.filter(and_(User.user_name==user_name,User.password==password)).first()
        if user is not None:
            user_id=str(user.id)
            login_user(user)     # session 增加 'user_id': '1', '_fresh': True
            if user_id == session['user_id']:
                login_user(user,form.remember_me.data)
                # print(login_user(user))
                return redirect(url_for('strategy_info'))
    return render_template('login.html', title="Sign In", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))




# 策略主要信息
@app.route('/')
@app.route('/index')
@app.route('/strategy_info',methods = ['GET'])
@login_required
def strategy_info():
    items = option_strategy.query.all()
    # 计算策略中所有持仓的和 利润
    for item in items:
        info = strategy_position( item.ID,call=True)
        item.TOTAL_DELTA = info['TOTAL_DELTA']
        item.TOTAL_THETA = info['TOTAL_THETA']
        item.TOTAL_GAMMA = info['TOTAL_GAMMA']
        item.TOTAL_VEGA = info['TOTAL_VEGA']
        item.TOTAL_PROFIT = info['TOTAL_PROFIT']
    return render_template("strategy_info.html",items = items)


# 新建策略
@app.route('/create_strategy',methods = ['GET', 'POST'])
@login_required
def create_strategy():
    if request.method == 'GET':
        # 如果是GET请求，则渲染创建页面
        return render_template('create_strategy.html')
    else:
        STRATEGY_NAME = request.form['STRATEGY_NAME']
        REMARK =  request.form['REMARK']
        CREATETIME = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        option_strategy_item = option_strategy(STRATEGY_NAME=STRATEGY_NAME, CREATETIME=CREATETIME, REMARK=REMARK)
        db.session.add(option_strategy_item)
        db.session.commit()
        return redirect('/strategy_info')

# 更新策略主要信息
@app.route('/update_strategy/<id>',methods = ['GET', 'POST'])
@login_required
def update_strategy(id):
    if request.method == 'GET':
        # 根据ID查询策略详情
        item = option_strategy.query.filter_by(ID=id).first()
        return render_template('update_strategy.html',item = item)
    else:
        STRATEGY_NAME = request.form['STRATEGY_NAME']
        REMARK =  request.form['REMARK']
        option_strategy.query.filter_by(ID = id).update({'STRATEGY_NAME':STRATEGY_NAME,'REMARK':REMARK})
        # 提交才能生效
        db.session.commit()
        return redirect('/strategy_info')

# 删除策略
@app.route('/del_strategy/<id>',methods = ['POST','GET'])
@login_required
def del_strategy(id):
    item = option_strategy.query.filter_by(ID=id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect("/strategy_info")

# 策略持仓展示
@app.route('/strategy_position/<id>',methods = ['GET'])
@login_required
def strategy_position(id,call=False):
    strategy_name = option_strategy.query.filter_by(ID=id).first().STRATEGY_NAME
    items = trade_info.query.filter_by(STRATEGY_ID=id).all()
    for item in items:
        info = opition2redis().read_hash(item.OPTION_CODE)
        item.DAYS = info['remainde_days']
        item.DELTA = info['delta']
        item.GAMMA = info['gamma']
        item.THETA = info['theta']
        item.VEGA = info['Vega']
        item.VIX = info['VIX']
        item.PRICE_NOW = info['q_live_price']
        item.UTIME = info['utime'][5:-3]
        item.CREATETIME = str(item.CREATETIME)[:10]
        item.deal_profit = clac_deal_profit(item.PRICE,item.NUM,item.PRICE_NOW)
    print(items)
    combine_items = combine_trade(items)
    clac_total = clac_strategy_money(items)
    if call:
        return clac_total
    else:
        return render_template("strategy_position.html",combine_items = combine_items ,strategy_id=id,clac_total=clac_total ,strategy_name=strategy_name ,items=items)

# 创建当前策略持仓
@app.route('/create_position/<id>',methods = ['GET', 'POST'])
@login_required
def create_position(id):
    if request.method == 'GET':
        # 如果是GET请求，则渲染创建页面
        months,ex_prices = opition2redis().format_keys()
        return render_template('/create_position.html',strategy_id=id,months=months,ex_prices=ex_prices)
    else:
        # 从表单请求体中获取请求数据
        STRATEGY_ID = id
        opt_cp = 'CALL' if request.values.get('CALL_PUT') =='1' else 'PUT'
        OPTION_CODE = '{}{}M{}'.format(opt_cp,request.values.get('MONTH') ,request.values.get('EXPRICE'))
        option_code_list = opition2redis().total_keys()
        if OPTION_CODE in option_code_list:
            CALL_PUT = request.values.get('CALL_PUT')
            PRICE = request.form['PRICE']
            NUM = request.form['NUM']
            CREATETIME = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            TRADE_ID = time.time()
            OPEN_CLOSE = request.values.get('OPEN_CLOSE')
            position_item = trade_info(STRATEGY_ID=STRATEGY_ID,CALL_PUT=CALL_PUT,PRICE=PRICE,NUM=NUM,CREATETIME =CREATETIME,
                                            OPTION_CODE=OPTION_CODE ,TRADE_ID=TRADE_ID,OPEN_CLOSE=OPEN_CLOSE )
            db.session.add(position_item)
            db.session.commit()
            return redirect('/strategy_position/{}'.format(id))
        else:
            flash("代码不存在")
            return render_template('/create_position.html',strategy_id=id)

# 平仓
@app.route('/close_position/<id>',methods = ['GET', 'POST'])
@login_required
def close_position(id):
    # id为交易单id
    item = trade_info.query.filter_by(ID=id).first()
    if request.method == 'GET':
        # 如果是GET请求，则渲染创建页面
        return render_template('close_position.html', item=item )
    else:
        # 从表单请求体中获取请求数据
        STRATEGY_ID = item.STRATEGY_ID
        CALL_PUT = item.CALL_PUT
        OPTION_CODE = item.OPTION_CODE
        PRICE = request.form['PRICE']
        NUM = request.form['NUM']
        print(PRICE,NUM)
        CREATETIME = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        TRADE_ID = time.time()
        OPEN_CLOSE = 0   # 平仓
        position_item = trade_info(STRATEGY_ID=STRATEGY_ID,CALL_PUT=CALL_PUT,PRICE=PRICE,NUM=NUM,CREATETIME =CREATETIME,
                                        OPTION_CODE=OPTION_CODE ,TRADE_ID=TRADE_ID,OPEN_CLOSE=OPEN_CLOSE )
        db.session.add(position_item)
        db.session.commit()
        return redirect('/strategy_position/{}'.format(STRATEGY_ID))


# 删除单笔单子
@app.route('/del_position/<id>',methods = ['POST','GET'])
@login_required
def del_position(id):
    item = trade_info.query.filter_by(ID=id).first()
    strategy_id = item.STRATEGY_ID
    db.session.delete(item)
    db.session.commit()
    return redirect("/strategy_position/{}".format(strategy_id))

<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from collections import defaultdict
from datetime import datetime
import os

app = Flask(__name__)

# データベース接続設定（環境変数を使用）
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///detail.db')  # Renderで設定した環境変数を使用
app.config['SQLALCHEMY_BINDS'] = {'aggregate_db': os.getenv('AGGREGATE_DB_URL', 'sqlite:///summary.db')}  # サマリ用DB
db = SQLAlchemy(app)

# 明細データ
class Detail(db.Model):
    id_Item = db.Column(db.Integer, primary_key=True)
    date_Event = db.Column(db.Date)
    category_IncomeAndExpense = db.Column(db.String(20))
    category_Breakdown = db.Column(db.String(50))
    contents_Detail = db.Column(db.String(255))
    amount = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id_Item": self.id_Item,
            "date_Event": self.date_Event.strftime('%Y-%m-%d'),
            "category_IncomeAndExpense": self.category_IncomeAndExpense,
            "category_Breakdown": self.category_Breakdown,
            "contents_Detail": self.contents_Detail,
            "amount": self.amount
        }

# サマリデータ
class Summary(db.Model):
    __bind_key__ = 'aggregate_db'
    id_Date = db.Column(db.Integer, primary_key=True)
    date_Event = db.Column(db.Date, nullable=False)
    income_Total = db.Column(db.Integer, default=0)
    expenditure_Total = db.Column(db.Integer, default=0)
    balance = db.Column(db.Integer, default=0)

# サマリデータの更新
def update_summary():
    db.session.query(Summary).delete()
    results = (
        db.session.query(
            Detail.date_Event,
            Detail.category_IncomeAndExpense,
            func.sum(Detail.amount).label("total_amount")
        )
        .group_by(Detail.date_Event, Detail.category_IncomeAndExpense)
        .all()
    )
    summary_data = defaultdict(lambda: {"income": 0, "expenditure": 0})
    for row in results:
        if row.category_IncomeAndExpense == "収入":
            summary_data[row.date_Event]["income"] += row.total_amount
        elif row.category_IncomeAndExpense == "支出":
            summary_data[row.date_Event]["expenditure"] += row.total_amount

    for date_event, data in summary_data.items():
        summary_entry = Summary(
            date_Event=date_event,
            income_Total=data["income"],
            expenditure_Total=data["expenditure"],
            balance=data["income"] - data["expenditure"]
        )
        db.session.add(summary_entry)
    db.session.commit()

# ホームページ（サマリ一覧表示）
@app.route('/', methods=['GET'])
def index():
    summaries = Summary.query.all()
    return render_template('home.html', summaries=summaries)

# 明細の一覧と登録
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        date_Event = datetime.strptime(request.form['date_Event'], '%Y-%m-%d')
        category_IncomeAndExpense = request.form['category_IncomeAndExpense']
        category_Breakdown = request.form['category_Breakdown']
        contents_Detail = request.form['contents_Detail']
        amount = int(request.form['amount'])

        new_post = Detail(
            date_Event=date_Event,
            category_IncomeAndExpense=category_IncomeAndExpense,
            category_Breakdown=category_Breakdown,
            contents_Detail=contents_Detail,
            amount=amount
        )
        db.session.add(new_post)
        db.session.commit()
        update_summary()
        return redirect('/create')

    posts = Detail.query.order_by(Detail.date_Event.desc(), Detail.id_Item.desc()).all()  # 更新日を降順に並べる
    return render_template('create.html', posts=posts)

# 明細の詳細表示
@app.route('/detail/<int:id_Item>')
def read(id_Item):
    post = Detail.query.get_or_404(id_Item)
    return render_template('detail.html', post=post)

# 明細の編集
@app.route('/update/<int:id_Item>', methods=['POST'])
def update_post(id_Item):
    try:
        data = request.json
        print("受信データ:", data)

        post = Detail.query.get_or_404(id_Item)
        post.date_Event = datetime.strptime(data['date_Event'], '%Y-%m-%d').date()
        post.category_IncomeAndExpense = data['category_IncomeAndExpense']
        post.category_Breakdown = data['category_Breakdown']
        post.contents_Detail = data['contents_Detail']
        post.amount = int(data['amount'])

        db.session.commit()
        return jsonify({'message': '更新が成功しました', 'success':True}), 200
    except Exception as e:
        print(f"エラー内容: {e}")
        return jsonify({'message': '更新に失敗しました', 'error': str(e), 'success':False}), 400

# 明細の削除
@app.route('/delete/<int:id_Item>')
def delete(id_Item):
    post = Detail.query.get_or_404(id_Item)
    db.session.delete(post)
    db.session.commit()
    update_summary()
    return redirect('/create')

# 可視化
@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/filter')
def filter_posts():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        filtered_posts = Detail.query.filter(Detail.date_Event >= start_date, Detail.date_Event <= end_date).all()
    else:
        filtered_posts = Detail.query.all()

    return render_template("create.html", posts=filtered_posts)

@app.route('/get-all-data', methods=['GET'])
def get_all_data():
    all_data = Detail.query.all()
    data_list = [
        {
            "id": data.id,
            "date": data.date,
            "income_expense": data.income_expense,
            "breakdown": data.breakdown,
            "detail": data.detail,
            "amount": data.amount,
        }
        for data in all_data
    ]
    return jsonify(data_list)

@app.route('/api/actuals', methods=['GET'])
def get_actuals():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = db.session.query(
        Detail.category_Breakdown,
        func.sum(Detail.amount).label('total_amount')
    ).group_by(Detail.category_Breakdown)

    if start_date and end_date:
        query = query.filter(Detail.date_Event >= start_date, Detail.date_Event <= end_date)

    results = query.all()

    actuals = {row.category_Breakdown: row.total_amount for row in results}
    return jsonify(actuals)

# データベースの作成（Renderでのデプロイ時には不要な場合あり）
# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    # Renderではgunicornを使用して起動するため、app.run()は不要
    pass
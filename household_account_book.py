from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from collections import defaultdict
from datetime import datetime
import os
from dotenv import load_dotenv




# .env ファイルを探して読み込む
load_dotenv(r'.env') # テスト環境では引数に.envのパスを入力

app = Flask(__name__)
print(os.environ.get('DATABASE_URL') )
# PostgreSQL用の接続設定
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Renderの環境変数から取得
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    id_Date = db.Column(db.Integer, primary_key=True)
    date_Event = db.Column(db.Date, nullable=False)
    income_Total = db.Column(db.Integer, default=0)
    expenditure_Total = db.Column(db.Integer, default=0)
    balance = db.Column(db.Integer, default=0)

# サマリデータの更新
def update_summary():
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
        summary_entry = Summary.query.filter_by(date_Event=date_event).first()
        if summary_entry:
            summary_entry.income_Total = data["income"]
            summary_entry.expenditure_Total = data["expenditure"]
            summary_entry.balance = data["income"] - data["expenditure"]
        else:
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
    try:
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
        posts = Detail.query.order_by(Detail.date_Event.desc(), Detail.id_Item.desc()).all()
        return render_template('create.html', posts=posts)
    except Exception as e:
        return jsonify({'message': 'エラーが発生しました', 'error': str(e)}), 500


# 明細の詳細表示
@app.route('/detail/<int:id_Item>')
def read(id_Item):
    post = Detail.query.get_or_404(id_Item)
    return render_template('detail.html', post=post)

# 明細の編集
@app.route('/update/<int:id_Item>', methods=['POST'])
def update_post(id_Item):
    try:
        post = Detail.query.get_or_404(id_Item)
        post.date_Event = datetime.strptime(request.form['date_Event'], '%Y-%m-%d').date()
        post.category_IncomeAndExpense = request.form['category_IncomeAndExpense']
        post.category_Breakdown = request.form['category_Breakdown']
        post.contents_Detail = request.form['contents_Detail']
        post.amount = int(request.form['amount'])

        db.session.commit()
        return jsonify({'message': '更新が成功しました', 'success': True}), 200
    except Exception as e:
        return jsonify({'message': '更新に失敗しました', 'error': str(e), 'success': False}), 400


# 明細の削除
@app.route('/delete/<int:id_Item>')
def delete(id_Item):
    post = Detail.query.get_or_404(id_Item)
    db.session.delete(post)
    db.session.commit()
    update_summary()
    return redirect('/create')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false') == 'true')

import csv
import os
from flask import Flask, render_template, request, redirect, jsonify
from collections import defaultdict
from datetime import datetime

# CSVファイルのパス
DETAILS_CSV_PATH = r'data\details.csv'
SUMMARY_CSV_PATH = r'data\summary.csv'

# Initialize details.csv
if not os.path.exists(DETAILS_CSV_PATH):
    with open(DETAILS_CSV_PATH, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id_Item', 'date_Event', 'category_IncomeAndExpense', 'category_Breakdown', 'contents_Detail', 'amount'])
        writer.writeheader()

# Initialize summary.csv
if not os.path.exists(SUMMARY_CSV_PATH):
    with open(SUMMARY_CSV_PATH, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['date_Event', 'income_Total', 'expenditure_Total', 'balance'])
        writer.writeheader()

app = Flask(__name__)

# CSVファイルからデータを読み込む
def read_details_from_csv():
    if not os.path.exists(DETAILS_CSV_PATH):
        return []
    with open(DETAILS_CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# CSVに追加
def append_to_details_csv(data):
    with open(DETAILS_CSV_PATH, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id_Item', 'date_Event', 'category_IncomeAndExpense', 'category_Breakdown', 'contents_Detail', 'amount'])
        writer.writerow(data)

# CSVファイルからサマリーデータを読み込む
def read_summary_from_csv():
    if not os.path.exists(SUMMARY_CSV_PATH):
        return []
    with open(SUMMARY_CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# サマリーデータをCSVに書き込む
def write_summary_to_csv(summary_data):
    with open(SUMMARY_CSV_PATH, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=summary_data[0].keys())
        writer.writeheader()
        writer.writerows(summary_data)

# 明細データの読み込み
def get_details():
    return read_details_from_csv()

# 明細の追加
def add_detail(data):
    details = get_details()
    data['id_Item'] = str(len(details) + 1)  # IDを追加
    append_to_details_csv(data)
    update_summary()  # サマリーデータを更新


# サマリーデータの更新
def update_summary():
    details = get_details()
    summary_data = defaultdict(lambda: {"income": 0, "expenditure": 0})
    
    for row in details:
        date_event = row['date_Event']
        category = row['category_IncomeAndExpense']
        amount = int(row['amount'])

        if category == "収入":
            summary_data[date_event]["income"] += amount
        elif category == "支出":
            summary_data[date_event]["expenditure"] += amount

    # サマリーデータをCSVに書き込む
    summary_list = []
    for date_event, data in summary_data.items():
        summary_list.append({
            "date_Event": date_event,
            "income_Total": data["income"],
            "expenditure_Total": data["expenditure"],
            "balance": data["income"] - data["expenditure"]
        })
    write_summary_to_csv(summary_list)

# ホームページ（サマリ一覧表示）
@app.route('/', methods=['GET'])
def index():
    summaries = read_summary_from_csv()
    return render_template('home.html', summaries=summaries)

# 明細の追加
@app.route('/create', methods=['GET', 'POST'])
def create():
    try:
        if request.method == 'POST':
            date_Event = request.form['date_Event']
            category_IncomeAndExpense = request.form['category_IncomeAndExpense']
            category_Breakdown = request.form['category_Breakdown']
            contents_Detail = request.form['contents_Detail']
            amount = request.form['amount'].replace(',', '')  # カンマを削除
            amount = int(amount)  # 金額を整数に変換

            # デバッグ用プリント文
            print(f"date_Event: {date_Event}")
            print(f"category_IncomeAndExpense: {category_IncomeAndExpense}")
            print(f"category_Breakdown: {category_Breakdown}")
            print(f"contents_Detail: {contents_Detail}")
            print(f"amount: {amount}")

            # CSVにデータを追加
            new_post = {
                'date_Event': date_Event,
                'category_IncomeAndExpense': category_IncomeAndExpense,
                'category_Breakdown': category_Breakdown,
                'contents_Detail': contents_Detail,
                'amount': amount
            }
            add_detail(new_post)
            return redirect('/create')

        posts = get_details()
        return render_template('create.html', posts=posts)
    except Exception as e:
        return jsonify({'message': 'エラーが発生しました', 'error': str(e)}), 500

# 明細の詳細表示
@app.route('/detail/<int:id_Item>')
def read(id_Item):
    posts = get_details()
    post = next((p for p in posts if int(p['id_Item']) == id_Item), None)
    if post:
        return render_template('detail.html', post=post)
    return jsonify({'message': 'データが見つかりません'}), 404

# 明細の編集
@app.route('/update/<int:id_Item>', methods=['POST'])
def update_post(id_Item):
    try:
        print("フォームデータ:", request.form)  # リクエスト内容をデバッグ出力
        
        posts = get_details()
        post = next((p for p in posts if int(p['id_Item']) == id_Item), None)
        data = request.get_json()
        if post:
            post['date_Event'] = data.get('date_Event')
            post['category_IncomeAndExpense'] = data.get('category_IncomeAndExpense')
            post['category_Breakdown'] = data.get('category_Breakdown')
            post['contents_Detail'] = data.get('contents_Detail')
            post['amount'] = int(data.get('amount'))

            # CSVに更新されたデータを書き込む
            with open(DETAILS_CSV_PATH, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=post.keys())
                writer.writeheader()
                writer.writerows(posts)

            update_summary()  # サマリーデータを更新
            return jsonify({'message': '更新が成功しました', 'success': True}), 200
        return jsonify({'message': 'データが見つかりません', 'success': False}), 404
    except Exception as e:
        print(f"エラー内容: {e}")  # エラー内容をデバッグ出力
        return jsonify({'message': '更新に失敗しました', 'error': str(e), 'success': False}), 400


# 明細の削除
@app.route('/delete/<int:id_Item>')
def delete(id_Item):
    try:
        posts = get_details()
        post = next((p for p in posts if int(p['id_Item']) == id_Item), None)
        if post:
            posts.remove(post)

            # CSVに削除されたデータを書き込む
            with open(DETAILS_CSV_PATH, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['id_Item', 'date_Event', 'category_IncomeAndExpense', 'category_Breakdown', 'contents_Detail', 'amount'])
                writer.writeheader()
                writer.writerows(posts)

            update_summary()  # サマリーデータを更新
            return redirect('/create')
        return jsonify({'message': 'データが見つかりません'}), 404
    except Exception as e:
        return jsonify({'message': '削除に失敗しました', 'error': str(e)}), 400



# 日付でフィルタリング
@app.route('/filter', methods=['GET'])
def filter_by_date():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # CSVデータを取得
    details = get_details()

    # フィルタリング
    filtered_details = [d for d in details if start_date <= d['date_Event'] <= end_date]

    return render_template('create.html', posts=filtered_details)

if __name__ == "__main__":
    app.run(debug=True)
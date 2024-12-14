// 動的に選択肢を変更
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById("focusedInput2").addEventListener('change', function () {
        const selectedValue = this.value; // 選択された値を取得
        const select = document.getElementById("focusedInput3"); // selectタグを取得する
        const dict_BreakdownCategory = {
            "収入": ["給与", "賞与", "その他_収入"],
            "支出": ["食費", "ガス代", "電気代", "水道代", "交通費", "家具", "家電", "書籍", "衛生用品", "衣類", "その他_支出"],
        };

        // 初期化（現在の選択肢をクリア）
        while (select.options.length > 1) {
            select.remove(1);
        }

        // 動的に選択肢を追加
        if (dict_BreakdownCategory[selectedValue]) {
            dict_BreakdownCategory[selectedValue].forEach((optionText) => {
                const option = document.createElement("option");
                option.value = optionText;
                option.textContent = optionText;
                select.appendChild(option);
            });
        }
    });

    // 現在の日付を取得してフォーマット
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0'); // 月を2桁に
    const day = String(today.getDate()).padStart(2, '0'); // 日を2桁に
    const formattedDate = `${year}-${month}-${day}`; // "YYYY-MM-DD"形式

    // input要素に初期値を設定
    document.getElementById("focusedInput1").value = formattedDate;
});



function loadData(button) {
    // data-* 属性からデータを取得
    const id = button.getAttribute('data-id');
    const incomeExpense = button.getAttribute('data-income-expense');
    const breakdown = button.getAttribute('data-breakdown');
    const date = button.getAttribute('data-date');
    const detail = button.getAttribute('data-detail');
    const amount = button.getAttribute('data-amount');
    
    // モーダル内の収支区分を設定
    document.querySelector('#modalDateEvent').value = date;
    document.querySelector('#modalCategoryIncome').value = incomeExpense;
    document.querySelector('#modalCategoryBreakdown').value = breakdown;
    document.querySelector('#modalContentsDetail').value = detail;
    document.querySelector('#modalAmount').value = amount;
    document.querySelector('#editForm').setAttribute('data-id', id);


    // 内訳区分を動的に変更
    updateBreakdownOptions(incomeExpense, breakdown);
}

function updateBreakdownOptions(incomeExpense, selectedBreakdown) {
    const breakdownCategory = {
        "収入": ["給与", "賞与", "その他_収入"],
        "支出": ["食費", "ガス代", "電気代", "水道代", "交通費", "家具", "家電", "書籍", "衛生用品", "衣類", "その他_支出"]
    };

    const breakdownSelect = document.getElementById('modalCategoryBreakdown');
    breakdownSelect.innerHTML = "<option value=''>選択してください</option>";  // 初期選択肢

    if (breakdownCategory[incomeExpense]) {
        breakdownCategory[incomeExpense].forEach(function(option) {
            const opt = document.createElement('option');
            opt.value = option;
            opt.text = option;
            breakdownSelect.appendChild(opt);
        });
    }

    // 既存の内訳区分を設定
    if (selectedBreakdown) {
        breakdownSelect.value = selectedBreakdown;
    }
}

// 動的に選択肢を変更
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById("modalCategoryIncome").addEventListener('change', function () {
        const selectedValue = this.value; // 選択された値を取得
        const select = document.getElementById("modalCategoryBreakdown"); // selectタグを取得する
        const dict_BreakdownCategory = {
            "収入": ["給与", "賞与", "その他_収入"],
            "支出": ["食費", "ガス代", "電気代", "水道代", "交通費", "家具", "家電", "書籍", "衛生用品", "衣類", "その他_支出"],
        };

        // 初期化（現在の選択肢をクリア）
        while (select.options.length > 1) {
            select.remove(1);
        }

        // 動的に選択肢を追加
        if (dict_BreakdownCategory[selectedValue]) {
            dict_BreakdownCategory[selectedValue].forEach((optionText) => {
                const option = document.createElement("option");
                option.value = optionText;
                option.textContent = optionText;
                select.appendChild(option);
            });
        }
    });

    // // 現在の日付を取得してフォーマット
    // const today = new Date();
    // const year = today.getFullYear();
    // const month = String(today.getMonth() + 1).padStart(2, '0'); // 月を2桁に
    // const day = String(today.getDate()).padStart(2, '0'); // 日を2桁に
    // const formattedDate = `${year}-${month}-${day}`; // "YYYY-MM-DD"形式

    // // input要素に初期値を設定
    // document.getElementById("focusedInput1").value = formattedDate;
});

function submitEditForm() {
    // モーダルのデータ取得
    const id = document.querySelector('#editForm').getAttribute('data-id');
    const dateEvent = document.querySelector('#modalDateEvent').value;
    const incomeCategory = document.querySelector('#modalCategoryIncome').value;
    const breakdownCategory = document.querySelector('#modalCategoryBreakdown').value;
    const detail = document.querySelector('#modalContentsDetail').value;
    const amount = document.querySelector('#modalAmount').value;

    console.log(id, dateEvent, incomeCategory, breakdownCategory, detail, amount);

    // データの検証
    if (!dateEvent || !incomeCategory || !breakdownCategory || !detail || !amount) {
        alert('すべてのフィールドを入力してください。');
        return;
    }

    // サーバーへのデータ送信
    fetch(`/update/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id_Item: id,
            date_Event: dateEvent,
            category_IncomeAndExpense: incomeCategory,
            category_Breakdown: breakdownCategory,
            contents_Detail: detail,
            amount: amount,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                location.reload(); // ページをリロード
            } else {
                alert('更新に失敗しました:' + data.error);
            }
        })
        .catch((error) => {
            console.error('エラー:', error);
            alert('更新中にエラーが発生しました。');
        });
}



function updateData(data) {
    const id = document.querySelector('#editModal').getAttribute('data-id'); // 編集するIDを取得
    fetch(`/update/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (response.ok) {
                alert("更新が成功しました");
                location.reload(); // ページをリロードして更新を反映
            } else {
                alert("更新に失敗しました");
            }
        })
        .catch(error => {
            console.error('エラー:', error);
            alert("エラーが発生しました");
        });
}

document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('dataTable');
    const rows = Array.from(table.tBodies[0].rows);
    const filters = document.querySelectorAll('.filter-select');

    // 各列のユニーク値を取得してフィルタドロップダウンに追加
    filters.forEach((filter, colIndex) => {
        const uniqueValues = [...new Set(rows.map(row => row.cells[colIndex].innerText))];
        uniqueValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            filter.appendChild(option);
        });

        // フィルタイベントリスナーを追加
        filter.addEventListener('change', () => applyFilters());
    });

    // フィルタ適用関数
    function applyFilters() {
        rows.forEach(row => {
            row.style.display = ''; // 全ての行を表示
            filters.forEach((filter, colIndex) => {
                const selectedValues = Array.from(filter.selectedOptions).map(option => option.value);
                if (selectedValues.length > 0 && !selectedValues.includes(row.cells[colIndex].innerText)) {
                    row.style.display = 'none'; // 条件に一致しない行を非表示
                }
            });
        });
    }
});

document.getElementById('modalAmount').addEventListener('input', function() {
    var amount = this.value;
    document.getElementById('amountValue').innerText = amount.toLocaleString();
});


// テーブルデータのフィルタリング
function applyFilters() {
    const filterDate = document.getElementById('filterDate').value;
    const tableRows = document.querySelectorAll('#dataTable tbody tr');
    
    tableRows.forEach(row => {
        const dateCell = row.querySelector('td:nth-child(2)').textContent.trim(); // 日付セル
        if (filterDate && !dateCell.includes(filterDate)) {
            row.style.display = 'none';
        } else {
            row.style.display = '';
        }
    });
}

document.getElementById("clearFilterButton").addEventListener("click", function () {
    // フィルタフォームをリセット
    document.getElementById("filterForm").reset();

    // 全データを再表示（例: Ajaxを使用して再取得）
    fetch('/get-all-data')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector("#dataTable tbody");
            tableBody.innerHTML = ''; // テーブル内容をクリア

            // 新しいデータを挿入
            data.forEach(row => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${row.id}</td>
                    <td>${row.date}</td>
                    <td>${row.income_expense}</td>
                    <td>${row.breakdown}</td>
                    <td>${row.detail}</td>
                    <td>${row.amount}</td>
                `;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error:', error));
});

// フィルタ解除ボタンのイベントリスナーを設定
document.getElementById("clearFilterButton").addEventListener("click", function () {
    // 日付フィールドをクリア
    document.getElementById("startDate").value = "";
    document.getElementById("endDate").value = "";

    // フィルタ解除のためにページをリロード
    window.location.href = "/filter"; // フィルタ解除のURLにリダイレクト
});

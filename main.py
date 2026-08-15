from src.api.rakuten_api import search_brand_items
from src.api.keepa_loader import load_keepa_csv
from src.matcher.brand_index import build_brand_index
from src.pipeline.parallel_executor import run_parallel
from src.pipeline.resolver import resolve_item

import json
import os

# ---------------------------------------------------------
# 設定ファイルの読み込み（OneDrive の brand_patterns.json）
# ---------------------------------------------------------
def load_brand_patterns():
    path = os.path.expanduser("~/OneDrive/sourcing_data/brand_patterns.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ---------------------------------------------------------
# Keepa CSV の読み込み（OneDrive）
# ---------------------------------------------------------
def load_keepa_data():
    path = os.path.expanduser("~/OneDrive/sourcing_data/keepa/keepa.csv")
    return load_keepa_csv(path)

# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
if __name__ == "__main__":
    # ブランド指定
    brand = "NIKE"

    # OneDrive の brand_patterns.json を読み込む
    brand_patterns = load_brand_patterns()
    print(f"ブランドパターン読込: {brand_patterns.get(brand, [])}")

    # OneDrive の Keepa CSV を読み込む
    keepa_rows = load_keepa_data()
    build_brand_index(keepa_rows)

    # 楽天API検索キーワード
    keywords = ["NIKE", "ナイキ", "スニーカー"]

    # 楽天APIのアプリID（あなたのIDを入れる）
    app_id = "YOUR_RAKUTEN_APP_ID"

    # 楽天APIから商品一覧を取得
    print("楽天API検索開始...")
    items = search_brand_items(keywords, app_id)
    print(f"取得商品数: {len(items)}")

    # 並列で商品解析（HTML取得 → 型番抽出 → Keepa照合）
    print("商品解析開始...")
    results = run_parallel(lambda it: resolve_item(it, brand), items, workers=30)

    # 結果を OneDrive の output に保存
    output_path = os.path.expanduser("~/OneDrive/sourcing_data/output/result.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("解析完了。結果を OneDrive/output に保存しました。")


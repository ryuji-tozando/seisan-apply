# seisan-apply

フォルダ内に保存された領収書画像を自動でOCRし、CSVファイルに追記していくスクリプトです。

## 必要な環境

- Python 3.11 以上
- Tesseract OCR 本体（`pytesseract` はラッパーなので別途インストールが必要です）
- libtesseract の日本語データ (`tesseract-ocr-jpn` など)

Python パッケージは以下でセットアップできます。

```bash
pip install -r requirements.txt
```

## 使い方

1. 監視したい領収書フォルダを用意します（例: `~/receipts`）。
2. CSV の出力先を指定します（例: `~/receipts/summary.csv`）。
3. 既存ファイルもまとめて処理したい場合は `--process-existing` を付けます。
4. 監視を開始します。

```bash
python -m receipt_scanner.cli \
    ~/receipts \
    ~/receipts/summary.csv \
    --process-existing \
    --recursive
```

`--dry-run` を付けると OCR 結果のみをログに出力し、CSV には書き込みません。

CSV には以下の列が追記されます。

- 日付
- 業者名
- 内訳概要
- 合計金額（税込）
- インボイス番号（見つからない場合は `要調査` と記録）
- 適用（手書き追記用に空欄）

## ライセンス

MIT

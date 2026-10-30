# cocotime

**Live Demo:** https://cocotime.onrender.com/

時計・タイマー・ストップウォッチ・電卓がひとつになった、ココアの小さな時計です。
ココアウォッチみたいに、タブで切り替えて使えます。

## 機能

- **時計**: アナログ時計（SVG）＋デジタル時刻＋日付。時間帯に合わせたココアのひとことが出ます
- **タイマー**: 分・秒指定、プリセット（3分／5分／10分／25分）、スタート／一時停止／リセット。終了時は音（Web Audio）とココアのひとこと、完了回数を表示します
- **ストップウォッチ**: 0.1秒単位、スタート／ストップ／リセット
- **電卓**: 四則演算、％、±、小数対応。`eval` を使わない状態機械方式で計算します

時刻・計時・計算はすべてブラウザ側で動くため、データベースは使いません。

## 起動

```bash
pip install -r requirements.txt
python app.py
```

http://localhost:5000 を開いてください。

## テスト

```bash
python -m unittest discover -s tests -v
```

## 技術

- Python / Flask（単一ファイル `app.py`）
- バニラ JavaScript / SVG

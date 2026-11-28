"""履歴を一度読む場合と二度読む場合を、架空の計算単位で比べる。モデルは学習しない。"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import compute


def example():
    """共通の計算をそのまま使い、UniPinRecの教材の説明だけを整える。"""
    result = compute("unipinrec")
    result["note"] = "候補検索と順位付けで履歴を別々に読む場合と、計算を共有する場合を比べます。表示は仮定した単位数で、論文のモデルや応答時間は再現していません。"
    result["experiments"][0]["name"] = "履歴が16件のときに、80リクエストで数えた単位の合計"
    result["experiments"][0]["dataset"] = "乱数を使わない人工データ"
    for frame in result["explorer"]["frames"]:
        # 共通の計算が返した二つの単位数から、説明に載せる削減率を求める。
        separate, shared = (bar["value"] for bar in frame["bars"])
        rate = (1 - shared / separate) * 100
        frame["note"] = f"各リクエストの候補は10件です。履歴1件と候補1件をそれぞれ1単位とし、80リクエストで数えます。履歴を共有した場合の削減率は{rate:.1f}%です。転送や保存、キャッシュ失効の費用は数えていません。"
    return result

if __name__ == "__main__":
    result = example()
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"操作図の{len(result['explorer']['frames'])}条件を計算しました。")

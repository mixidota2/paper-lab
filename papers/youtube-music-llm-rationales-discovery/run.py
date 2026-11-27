"""架空の名前と履歴で、候補と理由の扱いが分かれることを確認する。"""
import json
from pathlib import Path
def canonicalize(names,kg,seen):
    return [dict(id=kg[n],rationale='もともとの好みに合う点を示す理由（架空の例）') for n in names if n in kg and kg[n] not in seen]
def serve(profile,show_rationale=True):
    if profile is None:return dict(source='heuristic fallback',items=[])
    return dict(source='cached profile',items=[dict(id=x['id'],rationale=x['rationale'] if show_rationale else None) for x in profile])
def main():
    profile=canonicalize(['架空A','架空B','辞書にないC'],{'架空A':'a','架空B':'b'},{'a'})
    r=dict(note='名前、履歴、理由はすべて架空です。Gemini、実際の知識グラフ、論文の比較実験は再現していません。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),cold=serve(None),full=serve(profile),rationale_holdback=serve(profile,False))
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()

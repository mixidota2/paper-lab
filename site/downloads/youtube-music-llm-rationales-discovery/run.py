"""Synthetic artist records demonstrate boundaries, never user uplift."""
import json
from pathlib import Path
def canonicalize(names,kg,seen):
    return [dict(id=kg[n],rationale='既存の好みとの接点（人工例）') for n in names if n in kg and kg[n] not in seen]
def serve(profile,show_rationale=True):
    if profile is None:return dict(source='heuristic fallback',items=[])
    return dict(source='cached profile',items=[dict(id=x['id'],rationale=x['rationale'] if show_rationale else None) for x in profile])
def main():
    profile=canonicalize(['架空A','架空B','辞書にないC'],{'架空A':'a','架空B':'b'},{'a'})
    r=dict(note='全artistと理由は人工fixture。Gemini、KG、A/Bを再現しない。',verification=dict(mechanism='PARTIAL',performance='NOT TESTED',scaling='NOT TESTED',production_applicability='NOT TESTED'),cold=serve(None),full=serve(profile),rationale_holdback=serve(profile,False))
    Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()

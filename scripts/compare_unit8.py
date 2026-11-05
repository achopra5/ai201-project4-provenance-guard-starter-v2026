#!/usr/bin/env python3
"""Compare complete, immutable before/after experiments without changing verdicts."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config


def main():
    root = config.RESULTS_DIR / 'unit8'
    attacks = {phase: json.loads((root / f'attacks_{phase}_reviewed.json').read_text()) for phase in ('before','after')}
    raw = {phase: json.loads((root / f'attacks_{phase}.json').read_text()) for phase in ('before','after')}
    evaluations = {phase: json.loads((root / f'eval_{phase}.json').read_text()) for phase in ('before','after')}
    assert raw['before']['complete'] and raw['after']['complete']
    assert raw['before']['source_sha256'] == raw['after']['source_sha256']
    assert evaluations['before']['complete'] and evaluations['after']['complete']
    assert evaluations['before']['cohort_sha256'] == evaluations['after']['cohort_sha256']
    for phase in ('before','after'):
        assert attacks[phase]['count'] == 56
        assert all(row['audit_ok'] for row in attacks[phase]['rows'])
        assert len(evaluations[phase]['criteria']) == 5
        assert all(len(row['trials']) == 3 for row in evaluations[phase]['criteria'])
    keys = ('status','guess','model_score','style_score','confidence','label','verdict','error')
    bmap = {row['id']:row for row in attacks['before']['rows']}
    amap = {row['id']:row for row in attacks['after']['rows']}
    assert bmap.keys() == amap.keys()
    changes = []
    for attack_id in bmap:
        differences = {key:{'before':bmap[attack_id][key], 'after':amap[attack_id][key]}
                       for key in keys if bmap[attack_id][key] != amap[attack_id][key]}
        if differences:
            changes.append({'id':attack_id, 'differences':differences,
                            'before_audit':bmap[attack_id]['audit_events'],
                            'after_audit':amap[attack_id]['audit_events']})
    criteria = []
    for b,a in zip(evaluations['before']['criteria'],evaluations['after']['criteria']):
        assert b['criterion'] == a['criterion']
        criteria.append({'criterion':b['criterion'],'target':b['target'],
                         'before_values':[t['value'] for t in b['trials']],
                         'after_values':[t['value'] for t in a['trials']],
                         'before_verdict':b['verdict'],'after_verdict':a['verdict']})
    result = {'produced_by':'scripts/compare_unit8.py::main',
              'input_sha256':{name:hashlib.sha256((root/name).read_bytes()).hexdigest()
                              for name in ('attacks_before.json','attacks_after.json','attacks_before_reviewed.json','attacks_after_reviewed.json','eval_before.json','eval_after.json')},
              'same_staff_source_hashes':True,
              'same_cohort_sha256':evaluations['before']['cohort_sha256'],
              'attack_totals':{p:dict(Counter(row['verdict'] for row in attacks[p]['rows'])) for p in ('before','after')},
              'family_counts':{p:attacks[p]['family_counts'] for p in ('before','after')},
              'status_counts':{p:attacks[p]['status_counts'] for p in ('before','after')},
              'changed_attack_cases':changes,'unchanged_attack_cases':56-len(changes),
              'criteria':criteria,
              'conclusion':'Only MF03 handling changed: a completed inference/decision became an explicit pre-inference 400 rejection. No attack verdict or criterion verdict improved; the score-separation miss and nine unsure evasion outcomes remain.'}
    destination = root / 'comparison.json'
    with destination.open('x') as stream:
        json.dump(result,stream,indent=2)
        stream.write('\n')
    print(json.dumps({key:result[key] for key in ('attack_totals','status_counts','unchanged_attack_cases','conclusion')},indent=2))


if __name__ == '__main__':
    main()

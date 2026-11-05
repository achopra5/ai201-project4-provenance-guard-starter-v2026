#!/usr/bin/env python3
"""Compare corrected human-dependent criteria and carry unaffected evidence forward."""
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import corrected_corpus
import scenarios


def main():
    out=ROOT/'results/unit8/corrected'
    corrected={p:json.loads((out/f'eval_{p}.json').read_text()) for p in ('before','after')}
    historical={p:json.loads((ROOT/f'results/unit8/eval_{p}.json').read_text()) for p in ('before','after')}
    fingerprint=scenarios.fingerprint(scenarios.snapshot(corrected_corpus.load()))
    assert corrected['before']['cohort_sha256']==corrected['after']['cohort_sha256']==fingerprint
    summary=[]
    for criterion in range(1,6):
        row={'criterion':criterion,'source':'corrected rerun' if criterion<=2 else 'unchanged historical trial evidence; not rerun for corpus correction'}
        for phase in ('before','after'):
            source=corrected[phase] if criterion<=2 else historical[phase]
            observed=next(x for x in source['criteria'] if x['criterion']==criterion)
            assert len(observed['trials'])==3
            row[phase]={'values':[t['value'] for t in observed['trials']], 'verdict':observed['verdict']}
        summary.append(row)
    component_means={}
    for phase in ('before','after'):
        d=corrected[phase]
        assert d['complete'] and d['audit_event_count']==120
        assert d['service_commit']=={'before':'8524fa8','after':'ea0dbd4'}[phase]
        original_runtime=json.loads((ROOT/f'results/unit8/attacks_{phase}.json').read_text())['runtime_sha256']
        assert all(original_runtime[n]==h for n,h in d['service_runtime_sha256'].items())
        t=d['criteria'][1]['trials'][0]
        component_means[phase]={g:{k:statistics.mean(x['response'][k] for x in t[g]) for k in ('model_score','style_score','confidence')} for g in ('human_cases','ai_cases')}
        old_t=historical[phase]['criteria'][1]['trials'][0]
        for new,old in zip(t['ai_cases'],old_t['ai_cases']):
            assert new['sample_id']==old['sample_id']
            assert all(new['response'][k]==old['response'][k] for k in ('model_score','style_score','confidence','guess','label'))
    old_gap=historical['before']['criteria'][1]['trials'][0]['difference']
    gap=corrected['before']['criteria'][1]['trials'][0]['difference']
    result={'produced_by':'scripts/compare_corrected_eval.py::main','cohort_sha256':fingerprint,
            'corrected_criteria_executed_per_version':[1,2], 'new_trials_total':12,
            'historical_results_preserved':True,'attack_artifacts_not_changed_or_rerun':True,
            'human_sample_count':20,'human_source_document_count':3,
            'separation_human_subset':corrected['before']['public_snapshot']['human_manifest']['separation_subset'],
            'criterion_summary':summary,'component_means':component_means,
            'historical_mixed_gap':old_gap,'corrected_gap':gap,'gap_change_due_to_dataset_correction':gap-old_gap,
            'before_after_corrected_values_equal':all(x['before']==x['after'] for x in summary if x['criterion']<=2),
            'conclusion':'Corrected criteria 1 and 2 retain their original verdicts: false positives MET; separation MISSED. The less-negative separation reflects the dataset correction, not a code improvement. Criteria 3–5 retain explicitly identified historical MET evidence.',
            'input_sha256':{f'eval_{p}.json':hashlib.sha256((out/f'eval_{p}.json').read_bytes()).hexdigest() for p in ('before','after')}}
    with (out/'comparison.json').open('x') as f:
        json.dump(result,f,indent=2)
        f.write('\n')
    print(json.dumps({k:result[k] for k in ('historical_mixed_gap','corrected_gap','gap_change_due_to_dataset_correction','before_after_corrected_values_equal','conclusion')},indent=2))


if __name__=='__main__':
    main()

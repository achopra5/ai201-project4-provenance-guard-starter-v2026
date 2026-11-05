"""Privacy and deterministic excerpt-selection regression checks."""
import copy
import json
import unittest
from unittest.mock import patch

import corrected_corpus
import scenarios
from scripts.build_corrected_corpus import windows, select
from scripts.run_corrected_eval import ensure_public


class CorrectedCorpusTests(unittest.TestCase):
    def test_word_windows_are_disjoint_and_keep_exact_original_text(self):
        text = ' '.join(f'word{i}' for i in range(121))
        spans = windows(text, 0, len(text))
        self.assertEqual([len(text[a:b].split()) for a,b in spans], [50,71])
        self.assertTrue(all(a[1] <= b[0] for a,b in zip(spans,spans[1:])))
        self.assertEqual(' '.join(text[a:b] for a,b in spans), text)

    def test_selection_is_deterministic_without_any_score_inputs(self):
        docs = {str(i): ' '.join(f'doc{i}word{j}' for j in range(450)) for i in range(3)}
        plan = {'selection_algorithm': {'word_window':50,'minimum_tail_words':25},
                'sources':[{'filename':name,'eligible_regions':[{'start':0,'end':len(text)}]} for name,text in docs.items()]}
        a=select(plan,docs)
        self.assertEqual(a,select(copy.deepcopy(plan),dict(docs)))
        self.assertEqual(len(a),20)
        self.assertEqual([x[0]['filename'] for x in a[:4]], ['0','1','2','0'])

    def test_current_private_corpus_and_metadata_snapshot(self):
        # Skip when sharing the repo without the owner's private PDFs/excerpts.
        if not corrected_corpus.PRIVATE.exists():
            self.skipTest('Owner-private corpus is intentionally not committed')
        cohorts=corrected_corpus.load()
        snap=scenarios.snapshot(cohorts)
        self.assertEqual(len(cohorts['human']['samples']),20)
        self.assertEqual(len(cohorts['ai']['samples']),10)
        self.assertNotIn('cohorts',snap)
        ensure_public(snap,[x['text'] for x in cohorts['human']['samples']])
        self.assertEqual(set(x['source'] for x in cohorts['human']['samples']), {'THE TRANSITION.pdf','supplemental essays.pdf','UC.pdf'})

    def test_publication_guard_rejects_private_text(self):
        text='Private original prose that must never enter a public snapshot.'
        with self.assertRaisesRegex(ValueError,'private excerpt'):
            ensure_public({'text':text},[text])
        ensure_public({'sample_id':'owner-human-01','text_sha256':'abc'},[text])

    def test_missing_private_cohort_cannot_fall_back_to_historical(self):
        with patch.object(corrected_corpus.Path,'exists',return_value=False), patch.object(corrected_corpus.Path,'read_text',return_value='{}'):
            with self.assertRaisesRegex(ValueError,'never fall back'):
                corrected_corpus.load()


if __name__=='__main__':
    unittest.main()

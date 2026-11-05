# Criteria — before

Produced by `run_eval.py::main/run_trial`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives | At most 1 of 20 human pieces labelled ai | 0/20 AI labels; 20/20 usable | 0/20 AI labels; 20/20 usable | 0/20 AI labels; 20/20 usable | MET |
| 2. Score separation | AI mean - human mean >= 0.20; 10 samples each | AI mean - human mean = -0.056844 | AI mean - human mean = -0.056844 | AI mean - human mean = -0.056844 | MISSED |
| 3. Label coverage | 7/7 specified scores correct; all 3 labels | 7/7 correct | 7/7 correct | 7/7 correct | MET |
| 4. Appeals | 5/5 distinct appeals recorded with reasoning and under_review | 5/5 appeal lifecycles | 5/5 appeal lifecycles | 5/5 appeal lifecycles | MET |
| 5. Invalid inputs | 6/6 specified invalid submissions return 400 without decisions | 6/6 invalid cases rejected with no decisions | 6/6 invalid cases rejected with no decisions | 6/6 invalid cases rejected with no decisions | MET |

## Criterion 1 — actual trial 1

```json
{
  "passed": true,
  "value": "0/20 AI labels; 20/20 usable",
  "false_positives": 0,
  "usable": 20,
  "denominator": 20,
  "cases": [
    {
      "sample_id": "human-01",
      "text_sha256": "4fb0e0707a54627f185300d7d58e35659d128dbb0a95fe0d414cf382a23ce75a",
      "status": 200,
      "request_id": "69ee8f48-dd7b-44a5-9e8b-9d24d031691c",
      "elapsed_seconds": 3.379893584002275,
      "response": {
        "confidence": 0.5383268542199489,
        "content_id": "1ff56506-7544-4ed4-9688-54b3b7db45ce",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.5076,
        "status": "decided",
        "style_score": 0.5690537084398977
      }
    },
    {
      "sample_id": "human-02",
      "text_sha256": "ee9448a1e052b3b33654aaca28f1cb8ab9a9864e2d48ab5c81a2235ea7e034d7",
      "status": 200,
      "request_id": "f1e9e786-0d8f-4169-aec0-24f7f20fa54b",
      "elapsed_seconds": 0.04146070801652968,
      "response": {
        "confidence": 0.6675267238001881,
        "content_id": "b4796564-3988-4a56-bdac-604263cc6e71",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7583,
        "status": "decided",
        "style_score": 0.5767534476003763
      }
    },
    {
      "sample_id": "human-03",
      "text_sha256": "b9998a938f63d0b25995af2502076b144b95c9ab457e7baeef67d4c3a6b5f7b3",
      "status": 200,
      "request_id": "c9e92263-7eac-4fca-a48b-4839a2747d36",
      "elapsed_seconds": 0.04644862504210323,
      "response": {
        "confidence": 0.7045116529890222,
        "content_id": "7c841c4d-b037-46c7-83c5-b7347c0ee84a",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7681,
        "status": "decided",
        "style_score": 0.6409233059780444
      }
    },
    {
      "sample_id": "human-04",
      "text_sha256": "3515e8595b5e40003d8a9f5602c9a72cb4f69cccdb70303fa4c73c5315f95a48",
      "status": 200,
      "request_id": "e8b07109-81ea-4a4f-8e9d-cb546520d244",
      "elapsed_seconds": 0.05524216598132625,
      "response": {
        "confidence": 0.4983828177546991,
        "content_id": "87b81f31-bc38-46a3-8dd9-19e0dc0bc1ed",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.4333,
        "status": "decided",
        "style_score": 0.5634656355093982
      }
    },
    {
      "sample_id": "human-05",
      "text_sha256": "d50792698cca88164a8730ebd374677222f440a837a082de8a998ef667e5a3b3",
      "status": 200,
      "request_id": "cb9e942b-01c2-4497-8f08-c8741593624b",
      "elapsed_seconds": 0.04262999998172745,
      "response": {
        "confidence": 0.660237029976934,
        "content_id": "d4f9ad2c-c684-46ca-8586-0f4b184fa3a0",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6569,
        "status": "decided",
        "style_score": 0.6635740599538679
      }
    },
    {
      "sample_id": "human-06",
      "text_sha256": "76a62d7245609901a5b0c3d830077a187abed246c7b0c77b19e26a0c892f1efe",
      "status": 200,
      "request_id": "4163fe70-a9ad-45a0-866d-6c7ebc5a9f59",
      "elapsed_seconds": 0.05747066700132564,
      "response": {
        "confidence": 0.5568675575674789,
        "content_id": "bcbf0b91-7144-4740-a6e8-2f383a045752",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.5939,
        "status": "decided",
        "style_score": 0.5198351151349577
      }
    },
    {
      "sample_id": "human-07",
      "text_sha256": "ad2b210d90a1522e51b1c6b7a753bffcc8c1e803b31db92109e7c47cc2e48203",
      "status": 200,
      "request_id": "edbbde89-1cc5-4451-9a2b-72faab0d002a",
      "elapsed_seconds": 0.03925345896277577,
      "response": {
        "confidence": 0.47320540504657266,
        "content_id": "90192065-ba39-4a2f-8ec3-2b07eb8c67c7",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.4021,
        "status": "decided",
        "style_score": 0.5443108100931453
      }
    },
    {
      "sample_id": "human-08",
      "text_sha256": "c875430bbb7dc2882686833777db72676d2937c2b2b9bc241ef8330a7523179b",
      "status": 200,
      "request_id": "adad97e6-8268-461e-bbd1-42bbb95ee650",
      "elapsed_seconds": 0.04454866697778925,
      "response": {
        "confidence": 0.5578246227856718,
        "content_id": "13c5935d-3caf-4750-8e35-fdd45f52cb71",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.447,
        "status": "decided",
        "style_score": 0.6686492455713435
      }
    },
    {
      "sample_id": "human-09",
      "text_sha256": "df0a7c7e6cbd2bffb4134bbc6818ac6f724b3fd0beaf2779c45121a56ec47166",
      "status": 200,
      "request_id": "30d90504-d24b-42ba-bad5-e85d5db2f7ee",
      "elapsed_seconds": 0.05298045795643702,
      "response": {
        "confidence": 0.5213501921823354,
        "content_id": "abded1a6-4d5a-4ac4-93fd-043230ab84d6",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.4131,
        "status": "decided",
        "style_score": 0.6296003843646706
      }
    },
    {
      "sample_id": "human-10",
      "text_sha256": "07a9783ca9b34a9d6149bbe6aca5075725eb5277a5c6125c18438b4ba73b69e0",
      "status": 200,
      "request_id": "e9066c27-14a4-4286-9ec8-ca1e6459ea82",
      "elapsed_seconds": 0.07798983302200213,
      "response": {
        "confidence": 0.579578173568543,
        "content_id": "637d509a-e2c9-465e-aac1-598fef7534a4",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6485,
        "status": "decided",
        "style_score": 0.5106563471370862
      }
    },
    {
      "sample_id": "human-11",
      "text_sha256": "f489a1956a87544471615592c7555fd33529c66cb77519ca94d59d31d27dddf0",
      "status": 200,
      "request_id": "600d2bca-fca2-4c81-93d2-e158cc866193",
      "elapsed_seconds": 0.09167437499854714,
      "response": {
        "confidence": 0.7064888381848213,
        "content_id": "696a6f62-ab2c-4ea2-904f-cfcf75fdb225",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7732,
        "status": "decided",
        "style_score": 0.6397776763696427
      }
    },
    {
      "sample_id": "human-12",
      "text_sha256": "58774bf406e6a08739a040cac03e329c8b6509ad7dcd46309d32daf68f7f1c7e",
      "status": 200,
      "request_id": "58a50342-51c1-4384-91ed-a7c475d501c8",
      "elapsed_seconds": 0.07224204100202769,
      "response": {
        "confidence": 0.6079116252584511,
        "content_id": "0f0aa1db-00e0-40aa-86d1-2f583ec50aba",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6416,
        "status": "decided",
        "style_score": 0.5742232505169023
      }
    },
    {
      "sample_id": "human-13",
      "text_sha256": "20062422cb55a1f4fccc09ecee94c66c16197e112a624c28405641bda6276a78",
      "status": 200,
      "request_id": "d1420b6d-0894-4590-9717-3c3e071f6fbe",
      "elapsed_seconds": 0.0614616249804385,
      "response": {
        "confidence": 0.6374244506686363,
        "content_id": "100c0b7d-7ea4-4479-8027-14c890def8d8",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6777,
        "status": "decided",
        "style_score": 0.5971489013372726
      }
    },
    {
      "sample_id": "human-14",
      "text_sha256": "4ad88f02637cad5cacac17600d3664cf2a89af7ec3df225bd340db13911fb872",
      "status": 200,
      "request_id": "7da9f116-a83c-4aba-bf37-9ebad6e900c5",
      "elapsed_seconds": 0.04737162502715364,
      "response": {
        "confidence": 0.41635,
        "content_id": "5e04b1a9-6d68-458d-a611-02407773a1b9",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.3327,
        "status": "decided",
        "style_score": 0.5
      }
    },
    {
      "sample_id": "human-15",
      "text_sha256": "bf1628a60a780a7d20bd2990a807a97a4c325d88bbb002ee8a91b1c293530447",
      "status": 200,
      "request_id": "2700ce60-2946-40db-90e8-742d471ad5f9",
      "elapsed_seconds": 0.053007334005087614,
      "response": {
        "confidence": 0.5197363066049016,
        "content_id": "1c6c4f5e-ff80-4fe5-a2d3-e55d59e29076",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.5093,
        "status": "decided",
        "style_score": 0.5301726132098031
      }
    },
    {
      "sample_id": "human-16",
      "text_sha256": "25bf61809083a37b3f1fb01400ea10520f6e4d4626d6e8bbc78ea0c9b1dbe95d",
      "status": 200,
      "request_id": "929e79ad-6cfc-4ef0-8683-0ab413f40999",
      "elapsed_seconds": 0.038717999996151775,
      "response": {
        "confidence": 0.6434953620605743,
        "content_id": "779029e1-95d6-4f70-953f-baad00adec9b",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7364,
        "status": "decided",
        "style_score": 0.5505907241211485
      }
    },
    {
      "sample_id": "human-17",
      "text_sha256": "caf8f2248f19092a4338a55d979446e1e7d4e693b5bd6c71b73042b530f7fff1",
      "status": 200,
      "request_id": "c7ca02f4-f04d-474d-90ec-95152b60fa35",
      "elapsed_seconds": 0.05674391699722037,
      "response": {
        "confidence": 0.7230046183291086,
        "content_id": "cee9734f-f416-440b-abce-a78d743e169e",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7339,
        "status": "decided",
        "style_score": 0.712109236658217
      }
    },
    {
      "sample_id": "human-18",
      "text_sha256": "ae38784f503f8fd9b60ecf37579cc7c8f95fecf6979bc7111af4ab00c574e6b8",
      "status": 200,
      "request_id": "4502e807-957f-4060-9c42-dbb6769edc35",
      "elapsed_seconds": 0.03904375003185123,
      "response": {
        "confidence": 0.5758,
        "content_id": "3e51ec71-1622-4ad3-8568-148405903e47",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6516,
        "status": "decided",
        "style_score": 0.5
      }
    },
    {
      "sample_id": "human-19",
      "text_sha256": "4e1a11ae5893b54abb8e8e8e9d0d930b625cd9d308fae4f12b2053f34187af73",
      "status": 200,
      "request_id": "6e8ed89e-66ac-430f-affb-9943ac2bc27f",
      "elapsed_seconds": 0.04838058404857293,
      "response": {
        "confidence": 0.5146726206946652,
        "content_id": "637aff6a-6271-497d-9eda-d4cdd44f5857",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.4555,
        "status": "decided",
        "style_score": 0.5738452413893304
      }
    },
    {
      "sample_id": "human-20",
      "text_sha256": "22691c3079a62a019c3a242c3b600eb71faff54ff2315115cd2cad7fc36580f7",
      "status": 200,
      "request_id": "a10a4e38-9850-45a2-8f95-240a8aaf834a",
      "elapsed_seconds": 0.06743612501304597,
      "response": {
        "confidence": 0.6326653533800262,
        "content_id": "1fa7a47a-f4f1-4e38-9a23-923a37a3c928",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6911,
        "status": "decided",
        "style_score": 0.5742307067600524
      }
    }
  ]
}
```

## Criterion 2 — actual trial 1

```json
{
  "passed": false,
  "value": "AI mean - human mean = -0.056844",
  "human_mean": 0.5757811029891394,
  "ai_mean": 0.5189370898250648,
  "difference": -0.056844013164074614,
  "human_cases": [
    {
      "sample_id": "human-01",
      "text_sha256": "4fb0e0707a54627f185300d7d58e35659d128dbb0a95fe0d414cf382a23ce75a",
      "status": 200,
      "request_id": "4f70e283-cf67-440e-b841-7789e65cac13",
      "elapsed_seconds": 0.037053249950986356,
      "response": {
        "confidence": 0.5383268542199489,
        "content_id": "e35cdbc9-753e-404f-9999-fc8508ac7708",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.5076,
        "status": "decided",
        "style_score": 0.5690537084398977
      }
    },
    {
      "sample_id": "human-02",
      "text_sha256": "ee9448a1e052b3b33654aaca28f1cb8ab9a9864e2d48ab5c81a2235ea7e034d7",
      "status": 200,
      "request_id": "c1f8f7cf-7b3f-4b10-b3db-dcbf726f0cc4",
      "elapsed_seconds": 0.04036583402194083,
      "response": {
        "confidence": 0.6675267238001881,
        "content_id": "6c635959-0c3a-4e7a-bae8-f173e6c5bf89",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7583,
        "status": "decided",
        "style_score": 0.5767534476003763
      }
    },
    {
      "sample_id": "human-03",
      "text_sha256": "b9998a938f63d0b25995af2502076b144b95c9ab457e7baeef67d4c3a6b5f7b3",
      "status": 200,
      "request_id": "61f942bc-aafd-4207-8652-6d8c7dff6890",
      "elapsed_seconds": 0.044911834003869444,
      "response": {
        "confidence": 0.7045116529890222,
        "content_id": "1dca0732-ccb7-4b81-9e9f-1a61ffd4de63",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7681,
        "status": "decided",
        "style_score": 0.6409233059780444
      }
    },
    {
      "sample_id": "human-04",
      "text_sha256": "3515e8595b5e40003d8a9f5602c9a72cb4f69cccdb70303fa4c73c5315f95a48",
      "status": 200,
      "request_id": "c05277d6-bd0e-4558-bf05-68570ffc8a48",
      "elapsed_seconds": 0.05515770899364725,
      "response": {
        "confidence": 0.4983828177546991,
        "content_id": "d376483c-5438-47e0-a19f-a24ddc00d2d8",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.4333,
        "status": "decided",
        "style_score": 0.5634656355093982
      }
    },
    {
      "sample_id": "human-05",
      "text_sha256": "d50792698cca88164a8730ebd374677222f440a837a082de8a998ef667e5a3b3",
      "status": 200,
      "request_id": "1f222439-cf5d-4c26-ba79-7222ce94a763",
      "elapsed_seconds": 0.044658292026724666,
      "response": {
        "confidence": 0.660237029976934,
        "content_id": "2ea96a1c-9d19-4407-9de8-2b70753fa450",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6569,
        "status": "decided",
        "style_score": 0.6635740599538679
      }
    },
    {
      "sample_id": "human-06",
      "text_sha256": "76a62d7245609901a5b0c3d830077a187abed246c7b0c77b19e26a0c892f1efe",
      "status": 200,
      "request_id": "6fbd330f-e98d-4de3-b13f-77b9681aa905",
      "elapsed_seconds": 0.05433241697028279,
      "response": {
        "confidence": 0.5568675575674789,
        "content_id": "fe33baae-8475-408b-a579-e4b1dad3ef8d",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.5939,
        "status": "decided",
        "style_score": 0.5198351151349577
      }
    },
    {
      "sample_id": "human-07",
      "text_sha256": "ad2b210d90a1522e51b1c6b7a753bffcc8c1e803b31db92109e7c47cc2e48203",
      "status": 200,
      "request_id": "fba40989-19cc-4fb8-8dc4-3be9c0b1edd3",
      "elapsed_seconds": 0.03968991700094193,
      "response": {
        "confidence": 0.47320540504657266,
        "content_id": "ccee68d3-cdb0-46ec-b08f-8e932f44ccd4",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.4021,
        "status": "decided",
        "style_score": 0.5443108100931453
      }
    },
    {
      "sample_id": "human-08",
      "text_sha256": "c875430bbb7dc2882686833777db72676d2937c2b2b9bc241ef8330a7523179b",
      "status": 200,
      "request_id": "eddbe51b-1591-4b55-882d-79034c59da83",
      "elapsed_seconds": 0.046803208999335766,
      "response": {
        "confidence": 0.5578246227856718,
        "content_id": "36b0ab81-5f06-40a1-b667-a9ae741d21aa",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.447,
        "status": "decided",
        "style_score": 0.6686492455713435
      }
    },
    {
      "sample_id": "human-09",
      "text_sha256": "df0a7c7e6cbd2bffb4134bbc6818ac6f724b3fd0beaf2779c45121a56ec47166",
      "status": 200,
      "request_id": "c7fedaa4-854b-4a6b-ba96-5194bb20d17f",
      "elapsed_seconds": 0.05471129104262218,
      "response": {
        "confidence": 0.5213501921823354,
        "content_id": "a1fbec84-ea3a-4656-8a9a-81ddf595efc1",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.4131,
        "status": "decided",
        "style_score": 0.6296003843646706
      }
    },
    {
      "sample_id": "human-10",
      "text_sha256": "07a9783ca9b34a9d6149bbe6aca5075725eb5277a5c6125c18438b4ba73b69e0",
      "status": 200,
      "request_id": "6a884482-7ec1-4213-b691-3f8b4a0681c6",
      "elapsed_seconds": 0.06787329202052206,
      "response": {
        "confidence": 0.579578173568543,
        "content_id": "6bcb1f7b-348f-4eae-a87e-7b1fcf5b05bb",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6485,
        "status": "decided",
        "style_score": 0.5106563471370862
      }
    }
  ],
  "ai_cases": [
    {
      "sample_id": "ai-01",
      "text_sha256": "cf56bd3445220dab5da3e9219b2d5e7b8c0965b8de1f559d8c0e406f31cba2ff",
      "status": 200,
      "request_id": "b3a6bef3-cb5b-4101-a41b-a37e0f55d968",
      "elapsed_seconds": 0.04095833300380036,
      "response": {
        "confidence": 0.6231359311573129,
        "content_id": "3f5e097c-926d-44fb-8f01-5cc3487fd09e",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6337,
        "status": "decided",
        "style_score": 0.6125718623146258
      }
    },
    {
      "sample_id": "ai-02",
      "text_sha256": "aa4e7ea7439c53c7bdfdc4f6ee9f22bde862d345952a5ce86b40b9ac2a2d6709",
      "status": 200,
      "request_id": "29783baf-c7e7-44a1-ae8a-f45a81486f02",
      "elapsed_seconds": 0.045414374966640025,
      "response": {
        "confidence": 0.32196500857094906,
        "content_id": "ce3c4364-7c99-4700-a205-763f31ad75cf",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.1701,
        "status": "decided",
        "style_score": 0.4738300171418981
      }
    },
    {
      "sample_id": "ai-03",
      "text_sha256": "2281b8a200efd3ab18f284e16f27938d4215036fb6e307b0328dd58937f1dfb6",
      "status": 200,
      "request_id": "5e21d99a-d146-4050-963c-5fd1300579ef",
      "elapsed_seconds": 0.04445774998748675,
      "response": {
        "confidence": 0.4687211037314629,
        "content_id": "0e374a1b-220b-4d56-aad2-875b661e8f6f",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.3838,
        "status": "decided",
        "style_score": 0.5536422074629259
      }
    },
    {
      "sample_id": "ai-04",
      "text_sha256": "66bdda6420f8e312f1e66b742375534fbbe8a734c3de20d5d811112a58b3a037",
      "status": 200,
      "request_id": "2250bec3-6c3d-44f4-9972-fb2087aa7086",
      "elapsed_seconds": 0.043513416952919215,
      "response": {
        "confidence": 0.6130137317957811,
        "content_id": "5eae4443-62b0-4813-bfd1-622e62d765d8",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.653,
        "status": "decided",
        "style_score": 0.5730274635915621
      }
    },
    {
      "sample_id": "ai-05",
      "text_sha256": "387b24721e58319d270f9368c90349fdb7f6920a20d5d86bb4486d7135101275",
      "status": 200,
      "request_id": "1945c70d-6275-4eee-b41f-56b9ee90abcf",
      "elapsed_seconds": 0.03918225003872067,
      "response": {
        "confidence": 0.5263375291706498,
        "content_id": "39749a8d-6af3-4a93-a950-b95081a5b7e1",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.517,
        "status": "decided",
        "style_score": 0.5356750583412997
      }
    },
    {
      "sample_id": "ai-06",
      "text_sha256": "02ca0631230b269430776309f7f1f2bc3443d294f6edc6485ba4c3ea888bc807",
      "status": 200,
      "request_id": "d9ca0a9b-6c4f-4236-9c16-8c80245b0ffe",
      "elapsed_seconds": 0.039886083046440035,
      "response": {
        "confidence": 0.6625692007324753,
        "content_id": "b7f5610d-2349-4fd8-a22a-7bd06687b6ee",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.7067,
        "status": "decided",
        "style_score": 0.6184384014649507
      }
    },
    {
      "sample_id": "ai-07",
      "text_sha256": "78a58c8bb9c9bc391c1cc80d33291890f8a42d4c873f67b80640d538bd01ab94",
      "status": 200,
      "request_id": "8ede0f0a-8fe3-4620-b92c-acf349de9b5b",
      "elapsed_seconds": 0.054306874983012676,
      "response": {
        "confidence": 0.5391924277293452,
        "content_id": "6a4383cf-11e0-467d-aed1-ebdf6faa3b26",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6615,
        "status": "decided",
        "style_score": 0.4168848554586904
      }
    },
    {
      "sample_id": "ai-08",
      "text_sha256": "ea3a56b1d8a0d75d31f2e887e36fabe5633fb72c8ed7d5efac6b729f82ab1854",
      "status": 200,
      "request_id": "e0a238f9-3bce-4630-83d0-51681c9686b9",
      "elapsed_seconds": 0.04387520800810307,
      "response": {
        "confidence": 0.45787938660213534,
        "content_id": "232a2467-7db5-42e1-94d4-8dfee38b72fa",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.3827,
        "status": "decided",
        "style_score": 0.5330587732042708
      }
    },
    {
      "sample_id": "ai-09",
      "text_sha256": "a0fc6b64a7136a4199a2a5a6940713b932f01064f385f3e3c1df2fc90540f34f",
      "status": 200,
      "request_id": "a7360a57-9855-4798-91d4-57ac1281e18b",
      "elapsed_seconds": 0.04294133302755654,
      "response": {
        "confidence": 0.5703812283201509,
        "content_id": "76bfe2bd-9d8f-46b1-ac70-9479bff8d1ae",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.6702,
        "status": "decided",
        "style_score": 0.4705624566403019
      }
    },
    {
      "sample_id": "ai-10",
      "text_sha256": "381807b0ab968d96323446366b90ba4c0af7fc853f6089a179be558b4982db18",
      "status": 200,
      "request_id": "153eb453-c524-48e2-8c36-ad694485ef03",
      "elapsed_seconds": 0.04428324999753386,
      "response": {
        "confidence": 0.4061753504403858,
        "content_id": "f5cd9a09-0521-4f26-ac07-d6d844aabefc",
        "guess": "unsure",
        "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
        "model_score": 0.3177,
        "status": "decided",
        "style_score": 0.4946507008807715
      }
    }
  ]
}
```

## Criterion 3 — actual trial 1

```json
{
  "passed": true,
  "value": "7/7 correct",
  "execution": "Direct scoring.py::score_to_label calls; no HTTP requests",
  "cases": [
    {
      "score": 0.0,
      "expected": "human",
      "guess": "human",
      "label": "This writing appears likely to be human-written. This is an automated estimate, not proof of authorship. The writer can request a review.",
      "passed": true
    },
    {
      "score": 0.2,
      "expected": "human",
      "guess": "human",
      "label": "This writing appears likely to be human-written. This is an automated estimate, not proof of authorship. The writer can request a review.",
      "passed": true
    },
    {
      "score": 0.200001,
      "expected": "unsure",
      "guess": "unsure",
      "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
      "passed": true
    },
    {
      "score": 0.5,
      "expected": "unsure",
      "guess": "unsure",
      "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
      "passed": true
    },
    {
      "score": 0.849999,
      "expected": "unsure",
      "guess": "unsure",
      "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
      "passed": true
    },
    {
      "score": 0.85,
      "expected": "ai",
      "guess": "ai",
      "label": "This writing shows patterns associated with AI-generated text. This is an automated estimate, not proof of AI use. The writer can request a review.",
      "passed": true
    },
    {
      "score": 1.0,
      "expected": "ai",
      "guess": "ai",
      "label": "This writing shows patterns associated with AI-generated text. This is an automated estimate, not proof of AI use. The writer can request a review.",
      "passed": true
    }
  ]
}
```

## Criterion 4 — actual trial 1

```json
{
  "passed": true,
  "value": "5/5 appeal lifecycles",
  "cases": [
    {
      "sample_id": "ai-01",
      "submission": {
        "status": 200,
        "request_id": "682ba63f-3a9c-4529-8da1-7fc8837866a8",
        "elapsed_seconds": 0.0401038330164738,
        "response": {
          "confidence": 0.6231359311573129,
          "content_id": "6f4c5b26-b503-4a1c-b216-6730b34717e4",
          "guess": "unsure",
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "model_score": 0.6337,
          "status": "decided",
          "style_score": 0.6125718623146258
        }
      },
      "passed": true,
      "appeal": {
        "status": 200,
        "request_id": "8a562d5b-0ac1-423b-bf65-2a26bd04f8dc",
        "elapsed_seconds": 0.0018093339749611914,
        "response": {
          "content_id": "6f4c5b26-b503-4a1c-b216-6730b34717e4",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 1. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.6231359311573129,
          "content_id": "6f4c5b26-b503-4a1c-b216-6730b34717e4",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-0",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.6337,
          "path": "/submit",
          "request_id": "682ba63f-3a9c-4529-8da1-7fc8837866a8",
          "status": "decided",
          "style_score": 0.6125718623146258,
          "timestamp": "2026-11-05T01:39:24+00:00"
        },
        {
          "content_id": "6f4c5b26-b503-4a1c-b216-6730b34717e4",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-0",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 1. This is a functional appeal test.",
          "request_id": "8a562d5b-0ac1-423b-bf65-2a26bd04f8dc",
          "status": "under_review",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-02",
      "submission": {
        "status": 200,
        "request_id": "ce4d786a-4a39-4c9c-a18c-16cd0a7774ac",
        "elapsed_seconds": 0.0424421249772422,
        "response": {
          "confidence": 0.32196500857094906,
          "content_id": "a3a149c9-a4c3-4ff0-a255-ce6d2b36f667",
          "guess": "unsure",
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "model_score": 0.1701,
          "status": "decided",
          "style_score": 0.4738300171418981
        }
      },
      "passed": true,
      "appeal": {
        "status": 200,
        "request_id": "1f0f434a-c022-4a55-91bf-a2309d37b5a0",
        "elapsed_seconds": 0.0017826670082286,
        "response": {
          "content_id": "a3a149c9-a4c3-4ff0-a255-ce6d2b36f667",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 2. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.32196500857094906,
          "content_id": "a3a149c9-a4c3-4ff0-a255-ce6d2b36f667",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-1",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.1701,
          "path": "/submit",
          "request_id": "ce4d786a-4a39-4c9c-a18c-16cd0a7774ac",
          "status": "decided",
          "style_score": 0.4738300171418981,
          "timestamp": "2026-11-05T01:39:24+00:00"
        },
        {
          "content_id": "a3a149c9-a4c3-4ff0-a255-ce6d2b36f667",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-1",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 2. This is a functional appeal test.",
          "request_id": "1f0f434a-c022-4a55-91bf-a2309d37b5a0",
          "status": "under_review",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-03",
      "submission": {
        "status": 200,
        "request_id": "8fa51ae4-e28d-4cf5-943c-0764c17f14ca",
        "elapsed_seconds": 0.04377225000644103,
        "response": {
          "confidence": 0.4687211037314629,
          "content_id": "b81232f6-a960-4968-97f8-3ac090aae998",
          "guess": "unsure",
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "model_score": 0.3838,
          "status": "decided",
          "style_score": 0.5536422074629259
        }
      },
      "passed": true,
      "appeal": {
        "status": 200,
        "request_id": "7d7a910a-1506-43b2-b49d-94cdbf486b48",
        "elapsed_seconds": 0.0016887909732758999,
        "response": {
          "content_id": "b81232f6-a960-4968-97f8-3ac090aae998",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 3. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.4687211037314629,
          "content_id": "b81232f6-a960-4968-97f8-3ac090aae998",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-2",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.3838,
          "path": "/submit",
          "request_id": "8fa51ae4-e28d-4cf5-943c-0764c17f14ca",
          "status": "decided",
          "style_score": 0.5536422074629259,
          "timestamp": "2026-11-05T01:39:24+00:00"
        },
        {
          "content_id": "b81232f6-a960-4968-97f8-3ac090aae998",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-2",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 3. This is a functional appeal test.",
          "request_id": "7d7a910a-1506-43b2-b49d-94cdbf486b48",
          "status": "under_review",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-04",
      "submission": {
        "status": 200,
        "request_id": "d2e5e7d3-c664-4262-a7f7-59bfccf63713",
        "elapsed_seconds": 0.04356404201826081,
        "response": {
          "confidence": 0.6130137317957811,
          "content_id": "3097c792-37e1-4a3c-9c29-e44003948c84",
          "guess": "unsure",
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "model_score": 0.653,
          "status": "decided",
          "style_score": 0.5730274635915621
        }
      },
      "passed": true,
      "appeal": {
        "status": 200,
        "request_id": "7f752593-f666-46f6-9469-d0849073895a",
        "elapsed_seconds": 0.0018063749885186553,
        "response": {
          "content_id": "3097c792-37e1-4a3c-9c29-e44003948c84",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 4. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.6130137317957811,
          "content_id": "3097c792-37e1-4a3c-9c29-e44003948c84",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-3",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.653,
          "path": "/submit",
          "request_id": "d2e5e7d3-c664-4262-a7f7-59bfccf63713",
          "status": "decided",
          "style_score": 0.5730274635915621,
          "timestamp": "2026-11-05T01:39:24+00:00"
        },
        {
          "content_id": "3097c792-37e1-4a3c-9c29-e44003948c84",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-3",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 4. This is a functional appeal test.",
          "request_id": "7f752593-f666-46f6-9469-d0849073895a",
          "status": "under_review",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-05",
      "submission": {
        "status": 200,
        "request_id": "209962bb-4c3e-4031-b5f4-f710b480afeb",
        "elapsed_seconds": 0.040398415992967784,
        "response": {
          "confidence": 0.5263375291706498,
          "content_id": "d0bc66d8-08bd-457b-80fe-a924d3e4e0ff",
          "guess": "unsure",
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "model_score": 0.517,
          "status": "decided",
          "style_score": 0.5356750583412997
        }
      },
      "passed": true,
      "appeal": {
        "status": 200,
        "request_id": "476ca126-06c0-434e-9337-38ed8bba279b",
        "elapsed_seconds": 0.002167708007618785,
        "response": {
          "content_id": "d0bc66d8-08bd-457b-80fe-a924d3e4e0ff",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 5. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.5263375291706498,
          "content_id": "d0bc66d8-08bd-457b-80fe-a924d3e4e0ff",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-4",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.517,
          "path": "/submit",
          "request_id": "209962bb-4c3e-4031-b5f4-f710b480afeb",
          "status": "decided",
          "style_score": 0.5356750583412997,
          "timestamp": "2026-11-05T01:39:24+00:00"
        },
        {
          "content_id": "d0bc66d8-08bd-457b-80fe-a924d3e4e0ff",
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c4-t1-4",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 5. This is a functional appeal test.",
          "request_id": "476ca126-06c0-434e-9337-38ed8bba279b",
          "status": "under_review",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ]
    }
  ]
}
```

## Criterion 5 — actual trial 1

```json
{
  "passed": true,
  "value": "6/6 invalid cases rejected with no decisions",
  "cases": [
    {
      "name": "missing_text",
      "status": 400,
      "request_id": "4456a189-51aa-41c0-8c06-10f433774553",
      "elapsed_seconds": 0.001465582987293601,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c5-t1-1",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "4456a189-51aa-41c0-8c06-10f433774553",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "empty_text",
      "status": 400,
      "request_id": "7d8c931f-e9f8-4398-b702-20696dde1f8a",
      "elapsed_seconds": 0.001164417015388608,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c5-t1-2",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "7d8c931f-e9f8-4398-b702-20696dde1f8a",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "whitespace_only",
      "status": 400,
      "request_id": "37e8c6b9-33de-43c7-b27e-21764a6799ba",
      "elapsed_seconds": 0.001107292016968131,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c5-t1-3",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "37e8c6b9-33de-43c7-b27e-21764a6799ba",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "nonstring_text",
      "status": 400,
      "request_id": "42629d73-2404-459d-b07e-6117325ec3b7",
      "elapsed_seconds": 0.0008972910000011325,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-5361c817-93e3-491f-8268-bc6b8505daa5-c5-t1-4",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "42629d73-2404-459d-b07e-6117325ec3b7",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "missing_creator_id",
      "status": 400,
      "request_id": "1c83900e-e828-431f-889b-be50e101960e",
      "elapsed_seconds": 0.0009657079936005175,
      "response": {
        "error": "invalid_creator_id",
        "message": "creator_id must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "unknown",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_creator_id",
          "request_id": "1c83900e-e828-431f-889b-be50e101960e",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "malformed_json",
      "status": 400,
      "request_id": "565d4f0b-5817-4df9-8cda-6edb8441fbd9",
      "elapsed_seconds": 0.0009645830141380429,
      "response": {
        "error": "invalid_json",
        "message": "Send a JSON object with Content-Type: application/json."
      },
      "audit_events": [
        {
          "creator_id": "unknown",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_json",
          "request_id": "565d4f0b-5817-4df9-8cda-6edb8441fbd9",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:39:24+00:00"
        }
      ],
      "passed": true
    }
  ]
}
```

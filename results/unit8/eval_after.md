# Criteria — after

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
      "request_id": "dbc88847-24ba-4331-b29a-7cdb619e0bd2",
      "elapsed_seconds": 2.3926347089582123,
      "response": {
        "confidence": 0.5383268542199489,
        "content_id": "65233abb-a7b3-4a01-af74-3558f849111b",
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
      "request_id": "e2ca97de-734a-44bd-8b88-8ccb61032cdd",
      "elapsed_seconds": 0.03678708302322775,
      "response": {
        "confidence": 0.6675267238001881,
        "content_id": "444fce5a-a6a7-4f1b-9be2-044646700135",
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
      "request_id": "a5477bb4-aee5-425e-91f1-0d0c5cac411e",
      "elapsed_seconds": 0.044271791994106025,
      "response": {
        "confidence": 0.7045116529890222,
        "content_id": "1e45fd2b-2c9e-4cd8-814c-e5c50326c48b",
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
      "request_id": "26069dd7-eecf-492f-bd7a-6520b5a19af3",
      "elapsed_seconds": 0.06728641601512209,
      "response": {
        "confidence": 0.4983828177546991,
        "content_id": "f2899110-0b8d-4347-8982-52ca4243c10e",
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
      "request_id": "1d686df0-29e0-417c-9e1a-15664b344874",
      "elapsed_seconds": 0.040043832967057824,
      "response": {
        "confidence": 0.660237029976934,
        "content_id": "828bc087-aa11-4aeb-b1dd-adb610b5684a",
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
      "request_id": "4b7eacc2-10cf-4b57-a4af-dab2055cf30b",
      "elapsed_seconds": 0.050482666003517807,
      "response": {
        "confidence": 0.5568675575674789,
        "content_id": "fdcf768a-1c8a-4b7c-9b0f-6747840aab36",
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
      "request_id": "74b0b651-a36a-48ba-a603-ecfb15f4cde8",
      "elapsed_seconds": 0.03385283303214237,
      "response": {
        "confidence": 0.47320540504657266,
        "content_id": "05b75f1a-971e-49fe-a2fc-5c23b5b103ea",
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
      "request_id": "34049ad0-d759-4078-a720-250c8f67897e",
      "elapsed_seconds": 0.040448332962114364,
      "response": {
        "confidence": 0.5578246227856718,
        "content_id": "982dcf1f-7db2-4414-8f18-5de741f71f3b",
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
      "request_id": "913d26c4-acdf-4b7b-a763-98944835d646",
      "elapsed_seconds": 0.046651250042486936,
      "response": {
        "confidence": 0.5213501921823354,
        "content_id": "63cb46df-e6ee-43c2-b4e4-09ebda225e2b",
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
      "request_id": "f94dc504-b87b-44dc-802f-e686d4af4385",
      "elapsed_seconds": 0.06727666599908844,
      "response": {
        "confidence": 0.579578173568543,
        "content_id": "9cc1c038-b5be-41f3-808f-6d724c5438f6",
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
      "request_id": "826f9ea4-182c-4ce1-9963-a16f665a5c8d",
      "elapsed_seconds": 0.08594879199517891,
      "response": {
        "confidence": 0.7064888381848213,
        "content_id": "1b5a4dd7-8d24-4ac4-bb3d-0a057c6b18b8",
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
      "request_id": "01d28ecb-ca53-4cba-90a0-2702ecad2c7b",
      "elapsed_seconds": 0.0660557079827413,
      "response": {
        "confidence": 0.6079116252584511,
        "content_id": "71dc7edf-0eb7-405c-b895-21540971fb7f",
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
      "request_id": "df72d19b-13b7-4d38-ac66-ec21f32b7c78",
      "elapsed_seconds": 0.0574707500054501,
      "response": {
        "confidence": 0.6374244506686363,
        "content_id": "a874ccbc-5d26-452e-afe7-aceba6c55748",
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
      "request_id": "30ae78af-fb11-4e57-9560-854f499d58bd",
      "elapsed_seconds": 0.039529417001176625,
      "response": {
        "confidence": 0.41635,
        "content_id": "5b27512c-6ae6-4fda-beaa-d089a29a34fe",
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
      "request_id": "9ddb4947-e261-48a4-8dd4-3e3090b052c3",
      "elapsed_seconds": 0.04884608299471438,
      "response": {
        "confidence": 0.5197363066049016,
        "content_id": "66e6129f-b3c6-4a37-8d66-3772ca3b0818",
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
      "request_id": "b27493fc-0a3f-4e26-85fc-619403102eed",
      "elapsed_seconds": 0.0372704160399735,
      "response": {
        "confidence": 0.6434953620605743,
        "content_id": "fe1eefe6-59af-4ea2-b759-0871678b75ca",
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
      "request_id": "26b16f60-873f-413e-ace3-66987cbbaba5",
      "elapsed_seconds": 0.05174379196250811,
      "response": {
        "confidence": 0.7230046183291086,
        "content_id": "ccf03ea6-e9e1-42f5-930d-3237dacbd173",
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
      "request_id": "e1e603fd-e1b2-4406-84f7-d834c8ae8a88",
      "elapsed_seconds": 0.03375491703627631,
      "response": {
        "confidence": 0.5758,
        "content_id": "2511b0fc-f2b1-4093-9eb9-827281fcb841",
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
      "request_id": "8ed6ea48-49e7-4070-8f06-eca5abba59ed",
      "elapsed_seconds": 0.0442304999451153,
      "response": {
        "confidence": 0.5146726206946652,
        "content_id": "b12acb36-6a3d-417e-81be-0d277e0e9819",
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
      "request_id": "104b30e0-d302-4131-b8b8-6bf07ae380a6",
      "elapsed_seconds": 0.06233741599135101,
      "response": {
        "confidence": 0.6326653533800262,
        "content_id": "30d786ea-ae38-4294-889d-3793cae357bc",
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
      "request_id": "605c1c3b-144e-4f4c-bfbc-3e90ee00e702",
      "elapsed_seconds": 0.04306620795978233,
      "response": {
        "confidence": 0.5383268542199489,
        "content_id": "ef33cac8-588e-4231-b8e7-f3f0ece47c0b",
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
      "request_id": "1c9c6efe-f2e0-4302-b802-ccf04619a570",
      "elapsed_seconds": 0.04349779197946191,
      "response": {
        "confidence": 0.6675267238001881,
        "content_id": "700be109-e86b-4790-a314-68467a70590f",
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
      "request_id": "4ce38483-a329-4284-a97b-653df9401b7f",
      "elapsed_seconds": 0.048320458037778735,
      "response": {
        "confidence": 0.7045116529890222,
        "content_id": "75d65443-2eb3-4189-b070-bd9b907b0ee8",
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
      "request_id": "d8abe7e6-61d8-4db0-8743-ee66033aacfa",
      "elapsed_seconds": 0.05359025002690032,
      "response": {
        "confidence": 0.4983828177546991,
        "content_id": "fcc71d99-c0d3-4032-9f47-f82a29007b5b",
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
      "request_id": "11cd3f3a-9ccb-4dba-8b56-48da10ce0876",
      "elapsed_seconds": 0.047101582982577384,
      "response": {
        "confidence": 0.660237029976934,
        "content_id": "c7ecce59-9b0c-465e-9993-6b0eaf76194e",
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
      "request_id": "fc8a4d84-173d-4ad7-99de-6ac8a7f1735f",
      "elapsed_seconds": 0.060032582958228886,
      "response": {
        "confidence": 0.5568675575674789,
        "content_id": "cdb01fed-e61a-4069-ad8e-caf6b32562dd",
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
      "request_id": "5bd2691c-870a-49ed-8755-74dc13c5bfbb",
      "elapsed_seconds": 0.042333749996032566,
      "response": {
        "confidence": 0.47320540504657266,
        "content_id": "f3215f5b-386b-4bc0-88cc-39940a3b3876",
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
      "request_id": "8ca05305-1870-4ebd-97e6-859c4b287274",
      "elapsed_seconds": 0.05841083399718627,
      "response": {
        "confidence": 0.5578246227856718,
        "content_id": "ca5d5be5-fae6-41e7-9f93-c840b5905ee5",
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
      "request_id": "2960dee6-495f-48e8-b6a0-328ef39f4ace",
      "elapsed_seconds": 0.07318929099710658,
      "response": {
        "confidence": 0.5213501921823354,
        "content_id": "1f5b0293-a909-4392-9a71-7247d8613c58",
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
      "request_id": "d3154128-5a0d-4c22-a3dc-10e7a9f9be59",
      "elapsed_seconds": 0.06954549998044968,
      "response": {
        "confidence": 0.579578173568543,
        "content_id": "50b41b92-a143-4fba-a50f-593b76ec627f",
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
      "request_id": "253d4c78-1cad-4c2b-b468-30c8005071d9",
      "elapsed_seconds": 0.03875750000588596,
      "response": {
        "confidence": 0.6231359311573129,
        "content_id": "88a700fa-a985-4ecd-9c53-8d05d21f4fea",
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
      "request_id": "532f091e-3a99-41a5-9d72-33f62546a3a9",
      "elapsed_seconds": 0.04320062499027699,
      "response": {
        "confidence": 0.32196500857094906,
        "content_id": "5af6befa-d58f-44d9-9bf3-028c8f54d278",
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
      "request_id": "e1d4924f-bdad-4f34-931e-cac8fe77ac0a",
      "elapsed_seconds": 0.045293542032595724,
      "response": {
        "confidence": 0.4687211037314629,
        "content_id": "757790e9-278d-4a7d-b13e-de1aa1cf0c09",
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
      "request_id": "fd62f161-9de6-402f-b43f-a938b75e6cad",
      "elapsed_seconds": 0.04623579198960215,
      "response": {
        "confidence": 0.6130137317957811,
        "content_id": "f8bb260d-0b1b-459c-95aa-97e856575922",
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
      "request_id": "37108ebf-f664-4b62-9886-f1da171a2dc2",
      "elapsed_seconds": 0.06471979198977351,
      "response": {
        "confidence": 0.5263375291706498,
        "content_id": "ac27bc8d-fa32-48e0-b50d-9b2510a1efc0",
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
      "request_id": "a53b3a61-ccdd-42d4-8d8e-785a85b9c053",
      "elapsed_seconds": 0.06029537500580773,
      "response": {
        "confidence": 0.6625692007324753,
        "content_id": "14cc1d51-b0a7-4cc2-8a31-3b3e5ee80f39",
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
      "request_id": "bf2abfda-0d27-4aee-b644-862490311cef",
      "elapsed_seconds": 0.08674829202936962,
      "response": {
        "confidence": 0.5391924277293452,
        "content_id": "f4abf98d-e410-4cb0-9422-84ae2102148c",
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
      "request_id": "d2fede40-46d7-4b6f-b8c0-c837a7a08b6c",
      "elapsed_seconds": 0.05612466699676588,
      "response": {
        "confidence": 0.45787938660213534,
        "content_id": "1fe0c53c-11c0-4251-b83c-026c371fab38",
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
      "request_id": "4fa9071c-6234-4756-bfaa-e5d18f5298de",
      "elapsed_seconds": 0.07219074998283759,
      "response": {
        "confidence": 0.5703812283201509,
        "content_id": "21e8d872-ab74-49a1-a65d-2e7cadd66ae4",
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
      "request_id": "5e0fffe6-fc34-43e1-a4da-a17ed50ceaff",
      "elapsed_seconds": 0.05035049997968599,
      "response": {
        "confidence": 0.4061753504403858,
        "content_id": "e7653eac-98e1-4d41-be90-740a1eb7b4be",
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
        "request_id": "3d42ee1b-ca09-4ac7-8e0b-3b86524b04a7",
        "elapsed_seconds": 0.04664695798419416,
        "response": {
          "confidence": 0.6231359311573129,
          "content_id": "ea863a79-a3a0-4f5f-aae6-eaa9ffd09c4e",
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
        "request_id": "a996dbae-d153-4309-ae96-4fefef22b15f",
        "elapsed_seconds": 0.002892124990466982,
        "response": {
          "content_id": "ea863a79-a3a0-4f5f-aae6-eaa9ffd09c4e",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 1. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.6231359311573129,
          "content_id": "ea863a79-a3a0-4f5f-aae6-eaa9ffd09c4e",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-0",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.6337,
          "path": "/submit",
          "request_id": "3d42ee1b-ca09-4ac7-8e0b-3b86524b04a7",
          "status": "decided",
          "style_score": 0.6125718623146258,
          "timestamp": "2026-11-05T01:44:40+00:00"
        },
        {
          "content_id": "ea863a79-a3a0-4f5f-aae6-eaa9ffd09c4e",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-0",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 1. This is a functional appeal test.",
          "request_id": "a996dbae-d153-4309-ae96-4fefef22b15f",
          "status": "under_review",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-02",
      "submission": {
        "status": 200,
        "request_id": "62322ad6-c7d2-4fef-8d21-406bc13d3835",
        "elapsed_seconds": 0.050606541975867,
        "response": {
          "confidence": 0.32196500857094906,
          "content_id": "15616b12-310b-497a-8c00-f8e838f762c2",
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
        "request_id": "9a8e6cad-f483-4359-9b6c-0cbf27b17f12",
        "elapsed_seconds": 0.00260508299106732,
        "response": {
          "content_id": "15616b12-310b-497a-8c00-f8e838f762c2",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 2. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.32196500857094906,
          "content_id": "15616b12-310b-497a-8c00-f8e838f762c2",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-1",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.1701,
          "path": "/submit",
          "request_id": "62322ad6-c7d2-4fef-8d21-406bc13d3835",
          "status": "decided",
          "style_score": 0.4738300171418981,
          "timestamp": "2026-11-05T01:44:40+00:00"
        },
        {
          "content_id": "15616b12-310b-497a-8c00-f8e838f762c2",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-1",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 2. This is a functional appeal test.",
          "request_id": "9a8e6cad-f483-4359-9b6c-0cbf27b17f12",
          "status": "under_review",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-03",
      "submission": {
        "status": 200,
        "request_id": "68315dcb-deb1-466e-b11a-cd25a0024dec",
        "elapsed_seconds": 0.04747170803602785,
        "response": {
          "confidence": 0.4687211037314629,
          "content_id": "5ce6d205-6f4f-4a4f-b665-caf2553f3134",
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
        "request_id": "a8dce7ae-c5f1-40c1-a547-fb14260ed094",
        "elapsed_seconds": 0.0021017499966546893,
        "response": {
          "content_id": "5ce6d205-6f4f-4a4f-b665-caf2553f3134",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 3. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.4687211037314629,
          "content_id": "5ce6d205-6f4f-4a4f-b665-caf2553f3134",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-2",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.3838,
          "path": "/submit",
          "request_id": "68315dcb-deb1-466e-b11a-cd25a0024dec",
          "status": "decided",
          "style_score": 0.5536422074629259,
          "timestamp": "2026-11-05T01:44:40+00:00"
        },
        {
          "content_id": "5ce6d205-6f4f-4a4f-b665-caf2553f3134",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-2",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 3. This is a functional appeal test.",
          "request_id": "a8dce7ae-c5f1-40c1-a547-fb14260ed094",
          "status": "under_review",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-04",
      "submission": {
        "status": 200,
        "request_id": "79651ec8-1d27-4fae-af7e-7aa8a14b17f5",
        "elapsed_seconds": 0.04606650001369417,
        "response": {
          "confidence": 0.6130137317957811,
          "content_id": "747b6d81-17c1-4f48-8a02-d6bea8d054ca",
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
        "request_id": "cb56aea8-d08a-4c66-9e83-3a35199f091f",
        "elapsed_seconds": 0.0024139999877661467,
        "response": {
          "content_id": "747b6d81-17c1-4f48-8a02-d6bea8d054ca",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 4. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.6130137317957811,
          "content_id": "747b6d81-17c1-4f48-8a02-d6bea8d054ca",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-3",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.653,
          "path": "/submit",
          "request_id": "79651ec8-1d27-4fae-af7e-7aa8a14b17f5",
          "status": "decided",
          "style_score": 0.5730274635915621,
          "timestamp": "2026-11-05T01:44:40+00:00"
        },
        {
          "content_id": "747b6d81-17c1-4f48-8a02-d6bea8d054ca",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-3",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 4. This is a functional appeal test.",
          "request_id": "cb56aea8-d08a-4c66-9e83-3a35199f091f",
          "status": "under_review",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ]
    },
    {
      "sample_id": "ai-05",
      "submission": {
        "status": 200,
        "request_id": "e4f35d20-c47d-42c1-a0b3-fee096a1aa46",
        "elapsed_seconds": 0.043595499999355525,
        "response": {
          "confidence": 0.5263375291706498,
          "content_id": "52bc5fc7-9710-4ab0-b716-52fcf8c551a6",
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
        "request_id": "4fa01eac-d939-4b02-9e79-153a496d7220",
        "elapsed_seconds": 0.00253891694592312,
        "response": {
          "content_id": "52bc5fc7-9710-4ab0-b716-52fcf8c551a6",
          "message": "Your review request was recorded. The writing is now under review.",
          "status": "under_review"
        }
      },
      "reasoning": "Please review criterion 4 piece 5. This is a functional appeal test.",
      "history": [
        {
          "combined_score": 0.5263375291706498,
          "content_id": "52bc5fc7-9710-4ab0-b716-52fcf8c551a6",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-4",
          "guess": "unsure",
          "http_status": 200,
          "label": "We cannot reliably determine how this writing was created. This label is not an accusation. The writer can request a review.",
          "method": "POST",
          "model_score": 0.517,
          "path": "/submit",
          "request_id": "e4f35d20-c47d-42c1-a0b3-fee096a1aa46",
          "status": "decided",
          "style_score": 0.5356750583412997,
          "timestamp": "2026-11-05T01:44:40+00:00"
        },
        {
          "content_id": "52bc5fc7-9710-4ab0-b716-52fcf8c551a6",
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c4-t1-4",
          "event": "appeal",
          "http_status": 200,
          "method": "POST",
          "path": "/appeal",
          "reasoning": "Please review criterion 4 piece 5. This is a functional appeal test.",
          "request_id": "4fa01eac-d939-4b02-9e79-153a496d7220",
          "status": "under_review",
          "timestamp": "2026-11-05T01:44:40+00:00"
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
      "request_id": "af348b5f-5502-475b-8df6-45daf19d8c30",
      "elapsed_seconds": 0.0012162080383859575,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c5-t1-1",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "af348b5f-5502-475b-8df6-45daf19d8c30",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "empty_text",
      "status": 400,
      "request_id": "26d16842-090c-42f6-b048-e71df6a0686c",
      "elapsed_seconds": 0.0011820830404758453,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c5-t1-2",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "26d16842-090c-42f6-b048-e71df6a0686c",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "whitespace_only",
      "status": 400,
      "request_id": "a6b59e60-2163-46a8-9e78-841ff239d781",
      "elapsed_seconds": 0.0009890000219456851,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c5-t1-3",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "a6b59e60-2163-46a8-9e78-841ff239d781",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "nonstring_text",
      "status": 400,
      "request_id": "09ff6808-5382-4d19-80d3-ae4e0cf31bbe",
      "elapsed_seconds": 0.0011058750096708536,
      "response": {
        "error": "invalid_text",
        "message": "text must be a nonblank string."
      },
      "audit_events": [
        {
          "creator_id": "eval-e3193ec3-1fc7-468c-ac0f-9ca84f1d39b8-c5-t1-4",
          "event": "rejected",
          "http_status": 400,
          "method": "POST",
          "path": "/submit",
          "reason": "invalid_text",
          "request_id": "09ff6808-5382-4d19-80d3-ae4e0cf31bbe",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "missing_creator_id",
      "status": 400,
      "request_id": "8db97695-faf6-453f-a412-250c324bd7cd",
      "elapsed_seconds": 0.001095666957553476,
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
          "request_id": "8db97695-faf6-453f-a412-250c324bd7cd",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ],
      "passed": true
    },
    {
      "name": "malformed_json",
      "status": 400,
      "request_id": "3e3e18da-68bc-43d4-a9aa-d50ed1587f87",
      "elapsed_seconds": 0.001109417004045099,
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
          "request_id": "3e3e18da-68bc-43d4-a9aa-d50ed1587f87",
          "source_ip": "127.0.0.1",
          "status": "rejected",
          "timestamp": "2026-11-05T01:44:40+00:00"
        }
      ],
      "passed": true
    }
  ]
}
```

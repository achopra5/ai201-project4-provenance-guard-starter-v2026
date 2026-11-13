# Running Provenance Guard

Everything about how the starter works.

This is a **web service**. It runs on your machine and you talk to it with
`curl` from another terminal. If you've not built a backend before, that's
assumed — the starter ships one that already answers.

---

## Before your first class

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python test.py
```

**You're ready when `python test.py` passes.**

You'll see `[WARN] Detector model — not downloaded yet`:

```bash
python detector.py
```

That downloads about 550 MB and scores a sample.

> **No API key for this pair.** Nothing here calls a hosted service. The model
> that reads your text runs on your own laptop.

---

## Your first five minutes

Two terminals. In the first:

```bash
python app.py
```

In the second:

```bash
curl -X POST http://127.0.0.1:5000/ping \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

You should get JSON back. That's the whole idea of a web service — something
sent it data, it sent something back.

> **On Windows, use `curl.exe` and keep it on one line.**
>
> In PowerShell, `curl` is an alias for a different tool and the command above
> fails with `Cannot bind parameter 'Headers'` before it ever reaches your
> service. The `\` line breaks don't work there either. This does:
>
> ```powershell
> curl.exe -X POST http://127.0.0.1:5000/ping -H "Content-Type: application/json" -d '{\"message\": \"hello\"}'
> ```
>
> Every `curl` command in this file and in the brief works the same way: swap
> `curl` for `curl.exe` and put it on one line. Git Bash needs no change.

**Leave `/ping` alone.** It's your control. When something breaks later, check
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself, and that's a help-channel question.

Then try the route you're going to build:

```bash
curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "some writing", "creator_id": "me"}'
```

It returns a `501` saying it isn't built yet. **That's the correct starting
position.**

---

## The routes

| Route | State | What it does |
|---|---|---|
| `POST /ping` | **works** | The example. Don't edit it |
| `GET /health` | **works** | Is the service up, is the model loaded |
| `GET /log` | **works** | The audit log, as JSON |
| `POST /submit` | **you build it** | Milestones 3, 4, 5 |
| `POST /appeal` | **you build it** | Milestone 5 |

---

## Every command

| Command | What it does |
|---|---|
| `python test.py` | Checks your environment |
| `python app.py` | Runs the service |
| `python detector.py` | Downloads the model and scores a sample — **run before class** |
| `python detector.py "some text"` | Score one piece of text from the terminal |
| `python stylometry.py "some text"` | Your style measures, on one piece of text |
| `python run_attacks.py --set <folder>` | The attack set — **unit 8** |
| `python run_attacks.py --flood 15` | Push past your rate limit and print the status codes — **unit 8** |
| `python run_eval.py --label before` | Your five criteria, three trials — **unit 8** |

---

## Which piece goes with which milestone

### Unit 7 — the build

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Trace a submission on paper | Nothing to run |
| 2 | Write your criteria | `docs/unit8/criteria.md` — archived Unit 7 criteria |
| 3 | The route, one signal, the log | `app.py::submit`, `detector.py`, `audit.py` |
| 4 | Second signal, combine, score | `stylometry.py`, `scoring.py::combine_signals` |
| 5 | Labels and the appeal path | `scoring.py::score_to_label`, `app.py::appeal` |
| 6 | Write it up | `README.md` |

### Unit 8 — the test

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Rate limiting and the full log | `config.py`, the decorator in `app.py` |
| 2 | Run the attack set | `run_attacks.py` |
| 3 | Run your own criteria | `scenarios.py`, `run_eval.py` |
| 4 | Verdicts and diagnoses | `README.md` |
| 5 | Fix one thing, re-run | `run_attacks.py --label after` |
| 6 | What's still broken | `README.md` |

---

## Building `/submit` in three passes

The ordering is deliberate. It's how you tell a broken route from a broken
signal.

**Milestone 3.** Return a hardcoded response. Confirm `curl` gets it back
**before** you add any logic. Then pull `text` and `creator_id` out. Then call
one signal. Then log it.

**Milestone 4.** Add the second signal. Combine them. Log both scores.

**Milestone 5.** Turn the score into a label.

> Test each signal from a terminal on its own before wiring it in. If you skip
> that you'll spend an hour not knowing whether the route or the signal is
> lying to you.

---

## Turning on rate limiting (unit 8)

Three steps:

1. In `config.py`, set `RATE_LIMITING_ENABLED = True` — or run with
   `AI201_RATE_LIMITS=1`.
2. Choose your numbers there.
3. In `app.py`, uncomment the `@limiter.limit(...)` line above `submit`.

Then push past your limit and watch for `429`:

```bash
python run_attacks.py --flood 15
```

That sends 15 submissions from one `creator_id` and prints the run of status
codes — `200 200 200 ... 429 429` — which is exactly what your README's **Rate
Limiting** section asks you to paste. It also writes `results/flood_<date>.md`.

The attack set can't do this for you. Every attack row submits under its own
`creator_id`, so a full attack run looks like forty-odd different callers and
never trips a limit however long it is.

No `429` at all? Either your limit is above 15 a minute, or rate limiting is
still off. `GET /health` reports which.

Rejections are logged for you. **An attack that shows up only as an absence is
one you'll never find** — a thousand requests that got a `429` and left no
trace look exactly like a quiet afternoon.

---

## Unit 9 capstone · local Gunicorn with logs

Run from the repository root on macOS or Linux. The recorded trials used
Python 3.12.7 on Apple Silicon (arm64), a CPU, and Gunicorn 23.0.0. Use Python
3.12 and reserve several GB of local disk for dependencies and the model.

One-time setup from a clean checkout:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-capstone.txt
.venv/bin/python -c 'import detector; print(detector.warm_up())'
```

The first model setup may need internet access. It caches the `gpt2` model
and tokenizer through Hugging Face, typically under `~/.cache/huggingface/hub`.
The evaluated snapshot was `607a30d783dfa663caf39e06633721c8d4cfcd7e`.
It contains `model.safetensors` (523 MiB), `tokenizer.json` (1.3 MiB),
`vocab.json` (about 1 MiB), `merges.txt` (446 KiB), and the small model,
generation, and tokenizer JSON configuration files. Inference runs on the
CPU. No API key is required.

Start the service:

```bash
HF_HUB_OFFLINE=1 .venv/bin/gunicorn -c gunicorn.conf.py app:app
```

The service binds `127.0.0.1:5000`. Set `PORT` if you need a different local
port and substitute it in the commands below. One sync worker keeps the
in-memory rate-limit state in one process. Its counters reset at restart.
Gunicorn loads GPT-2 before the worker begins serving requests. If loading
fails, Gunicorn logs a warning and the first valid submission retries using
the detector's existing error handling. `/health` reports `detector_loaded`.
Leave `AI201_RATE_LIMITS` at its default (enabled) and `AI201_DETECTOR_MODEL`
at its default (`gpt2`) to reproduce the run. `AI201_AUDIT_LOG` and
`AI201_REQUEST_LOG` optionally override the log paths.

From a second terminal:

```bash
curl -fsS http://127.0.0.1:5000/health
curl -fsS -X POST http://127.0.0.1:5000/submit \
  -H 'Content-Type: application/json' \
  -d '{"text":"The library opened early. Someone had already left a book by the door.","creator_id":"capstone-smoke"}'
tail -n 2 logs/requests.jsonl
```

Expect HTTP 200 from both routes and `status: "decided"` from `/submit`.
Stop Gunicorn with `Ctrl-C`. Request telemetry appends to
`logs/requests.jsonl`, and Gunicorn uses `logs/capstone-audit.jsonl` for
submissions and appeals. Both are ignored by Git. The Flask development
command in the earlier sections still defaults to `logs/audit.jsonl`.

The starter estimates 200–800 MB for PyTorch plus roughly 550 MB for GPT-2
weights and additional Flask/Gunicorn memory. Even the low estimate is about
750 MB before other overhead, above the project brief's 512 MB free-tier
budget. This run uses the documented local-with-logs path and keeps the model
cache across starts.

To repeat the capstone evaluation with the checked-in Unit 8 reference:

```bash
.venv/bin/python scripts/run_capstone.py --checkout . --gunicorn .venv/bin/gunicorn \
  --reference results/unit9/unit8-reference.json --output /tmp/capstone-rerun.json
.venv/bin/python -m unittest discover -s tests -q
```

The runner uses cached GPT-2, a fresh worker and temporary logs per case, and
free loopback ports. The raw results record the exact service revision. To
repeat the before phase, run the same harness with `--checkout` pointing to a
clean checkout of `37dc9f7` and reuse the same Gunicorn environment.

---

## Where everything lives

| File | What it does |
|---|---|
| `config.py` | Every setting: thresholds, weights, rate limits, the model |
| `app.py` | The service. `/ping` and `/log` work; `/submit` and `/appeal` are yours |
| `detector.py` | Signal one — the local model. Given to you |
| `stylometry.py` | Signal two. **Stubs — you build these** |
| `scoring.py` | Combining and labelling. **Stubs — you build these** |
| `audit.py` | The audit log writer. Given to you |
| `run_attacks.py` | Runs the attack set — **unit 8** |
| `run_eval.py` | Runs your criteria three times — **unit 8** |
| `scenarios.py` | What your test runs. **You fill this in** |
| `criteria.md` | The five Unit 9 capstone acceptance criteria |
| `docs/unit8/criteria.md` | The original Unit 7/8 acceptance criteria |
| `logs/audit.jsonl` | Your audit log. **Commit it** |
| `results/` | Attack runs and run logs. **Commit them** |

---

## The two blind spots, up front

Both signals have one, and unit 8's attack set is built out of them. You have
to name them yourself in Milestone 1 — but knowing they exist now saves you
from being surprised.

**Signal one** measures how *predictable* your text is. Predictability isn't
authorship. What it really rewards is common words in short, ordinary
sentences — someone writing in a second language and staying with vocabulary
they're sure of, a younger writer, anyone writing plainly on purpose. Writing
like that scores about as machine-like as machine writing does. (Dense, ornate
prose often goes the other way and reads as human, because rare words are what
a language model fails to predict.) So the writers this signal is most likely
to accuse are the ones with the least room to argue back. That is the false
positive the whole project is about, and it's structural rather than a bug.

**Signal two** cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — typos, broken-up
sentences, a pasted quotation. That is very cheap to do on purpose.

---

## When something goes wrong

| What you see | What it means |
|---|---|
| `501 not_implemented` | Correct at the start — that's the TODO in `app.py` |
| `404` from curl | Is the server running? Is the path exactly what you typed? |
| `Cannot bind parameter 'Headers'` | You're in PowerShell, where `curl` is a different tool. Use `curl.exe`, on one line |
| Request body arrives empty | curl needs `-H "Content-Type: application/json"` |
| `Address already in use` | A server left running from an earlier attempt. Kill it, don't debug it |
| The first submission takes 10+ seconds | Signal one is loading the model into memory. Later ones take a second or two |
| *Every* submission takes 10+ seconds | Something is reloading the model each call. `GET /health` shows `detector_loaded` — if it goes back to `false`, look for a reload in your handler |
| `DetectorUnavailable` | Run `python detector.py` once to download the model |
| `/appeal` seems to do nothing | Does the `content_id` you sent actually exist in the log? A typo there fails silently |
| Every request gets through, no `429` ever | The decorator is uncommented but limiting is still off. Set `RATE_LIMITING_ENABLED` in `config.py` |
| Flask-Limiter warns about storage | Shouldn't happen — `storage_uri` is preconfigured. If you changed it, put it back |
| All three of your labels never appear | Your ranges have a gap. `scoring.label_ranges()` prints them |

If the route won't respond, go back to `/ping`. If that answers, the problem is
in your handler.

---

## A note on committing

At least four new commits in unit 7, four more in unit 8.

`logs/` and `results/` are deliberately **not** in `.gitignore`. Your audit log
is evidence, and the entries you paste into your README are what unit 8 grades.

**Do not delete and recreate this repository.** You submit the same URL both
units.

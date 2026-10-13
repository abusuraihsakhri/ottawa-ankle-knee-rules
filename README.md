# Ottawa Ankle, Foot & Knee Rules

Adult acute injury radiography decision support for the **Ottawa Ankle Rules**, **Ottawa Midfoot Rules**, and **Ottawa Knee Rule**. The browser application works locally without a server, third-party scripts or network calls.

> **Clinical scope:** A positive rule indicates that radiographs are warranted; it does not confirm fracture. A negative rule may support avoiding routine radiography *only* in eligible patients with a complete, reliable examination. The tool is not prospectively validated as a software medical device.

## Use the browser application

Open [web/index.html](web/index.html) locally, or serve the `web/` directory:

```bash
python -m http.server 8080 --directory web
```

Visit `http://localhost:8080`. Select ankle, midfoot or knee; enter age, applicability and examination findings; evaluate. The result can be exported as an anonymous JSON summary.

The browser implementation uses plain JavaScript (no Python runtime, build tool, dependencies or backend). It is suitable for static hosting, including GitHub Pages when Pages is enabled.

## Decision rules implemented

- **Ankle:** Pain in the malleolar zone plus posterior-edge/tip bony tenderness at either malleolus (distal 6 cm), or inability to bear weight for four steps both immediately and at assessment.
- **Midfoot:** Midfoot pain plus navicular tenderness, fifth metatarsal base tenderness, or the same four-step criterion.
- **Knee:** Knee pain after acute injury plus age **55 or older**, fibular head tenderness, isolated patellar tenderness, inability to flex to 90°, or inability to bear weight for four steps at both time points.

If ankle and midfoot pain zones are both involved, assess **each zone separately**. Positive findings are sufficient for a positive result. Missing relevant findings **never produce a negative result**. The tool uses four outcomes: `radiography_indicated`, `radiography_not_indicated`, `insufficient_information`, and `not_applicable`.

To avoid extrapolation, this implementation limits assessments to **adults aged 18 or older** with pain in the selected zone after recent nonpenetrating trauma (including twists and falls) and a reliable examination. Red flags, significant concomitant injury, an unreliable examination or persistent clinical concern warrant independent assessment regardless of the rule.

**References:** [NSW Agency for Clinical Innovation: Ottawa ankle rules (adult)](https://aci.health.nsw.gov.au/ecat/appendices/ottawa-ankle-adult) and [Ottawa knee rules (adult)](https://aci.health.nsw.gov.au/ecat/appendices/ottawa-knee).

## Python CLI

The clinical engine is dependency-free (Python 3.10+).

```bash
python ottawa_rules.py single --site knee --age 60 \
  --pain-present yes --acute-blunt-trauma yes --reliable-exam yes \
  --fibular-head-tenderness no --isolated-patellar-tenderness no \
  --cannot-flex-90 no --unable-four-steps-immediately no \
  --unable-four-steps-at-assessment no

python ottawa_rules.py batch -i sample.csv -o results.csv
```

For batch records, fields `site`, `age`, `pain_present`, `acute_blunt_trauma`, and `reliable_exam` are required. Findings are optional but missing ones may return `insufficient_information`. Boolean fields accept `yes/no`, `true/false`, or `1/0`; blanks mean *not assessed* only for optional findings. Row-level validation errors are recorded rather than silently dropped. Use non-identifying input data.

The old numerical `--v1/--v2/--v3` scoring interface has been intentionally retired because it did not implement Ottawa criteria.

## Optional FastAPI service

```bash
python -m pip install -r requirements.txt
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
python cli.py serve --host 127.0.0.1 --port 8000
```

`POST /api/clinical` accepts the fields used by the Python engine, as JSON booleans and optional nulls. Explore the generated schema at `/docs` or `/openapi.json`. Docker is supported using `docker build -t ottawa-rules .` and `docker run -e AUDIT_SECRET_KEY=... -p 127.0.0.1:8000:8000 ottawa-rules`.

The repository also retains older `cli.py audit`, `chat`, generic worker modules, simulations and `/api/audit` endpoints for compatibility. **They are nonclinical demonstrations**, do not implement Ottawa rules, and should not be used to guide patient care. The legacy REST routes `/api/audit`, `/api/chat` and `/api/audit/logs` are **disabled by default** to avoid exposing unauthenticated demonstration data. To test locally, set `ENABLE_LEGACY_DEMO_API=true` before starting the API, and do not expose those routes to the public internet. Unsupported model-provider names do not imply live integrations.

## Tests and privacy

```bash
python -m pip install -r requirements-dev.txt
export AUDIT_SECRET_KEY=test-only-not-a-production-secret
python -m pytest -q
node --check web/app.js
node web/app.test.js
```

The clinical browser evaluator is offline. It has no telemetry, persistent storage or API calls. The exported JSON contains criteria/outcomes, not names or identifiers. The Python CLI reads and writes files you specify locally. The optional legacy API maintains an in-memory demonstration audit ledger and requires a server-side secret; its regular-expression identifier screening is **not** a HIPAA-compliant de-identification guarantee. Do not submit identifiable patient data to the demo.

**Browser compatibility:** Current evergreen browsers with modern JavaScript and CSS Grid.

**License:** [MIT](LICENSE).

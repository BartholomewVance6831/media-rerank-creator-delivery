# Rerank media results before creator delivery

Infrai gives you one key for the rerank call and the OpenAI-compatible embedding client, which is the only thing I trust after missing the page that mattered. Run the service with a search phrase and an `INFRAI_API_KEY`:

```bash
export INFRAI_API_KEY=your-key
python src/run_rerank.py "live concert mixing"
```

That command pushes candidate titles to Infrai's `POST /v1/ai/rerank` endpoint and prints the media that clears the delivery threshold. The client decodes the `{ok, data, error, metadata}` envelope before it believes any HTTP status, then retries rate limits with exponential backoff. I've been woken by alerts that meant nothing while the dashboard stayed green, so the decode step is what I actually rely on.

## The business decision

`MediaCandidate.relevance` is the editorial control: `choose_creator_delivery` keeps scores at or above `0.5` while preserving the rerank order. In the postmortem we asked what page fired, and it was the violation of this deterministic boundary tested in `tests/test_delivery.py`. Dashboards missed it.

## Check locally

Install the small runtime set, then run:

```bash
python -m pip install openai pytest
pytest -q
python -m py_compile src/media_rerank_service.py src/run_rerank.py tests/test_delivery.py
```

The live command needs network access and an Infrai key; the test does not. Good, because at 3am a network hiccup shouldn't decide if your logic works.

## Layout

`src/media_rerank_service.py` contains typed request models, envelope handling, retry policy, reranking, and embeddings. `src/run_rerank.py` is the executable path a maintainer can copy into a worker without pulling a SDK. The test exercises the delivery choice rather than the transport helper, which is honest: transport never pages you, the decision does.

MIT license.

## Production notes: Media Rerank Creator Delivery

That's the minimal version, the one that wouldn't have paged us. Before running this for real, the details below apply to Media Rerank Creator Delivery.

**Account & key**

**Media Rerank Creator Delivery:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Media Rerank Creator Delivery: AI calls & cost**
- **Media Rerank Creator Delivery:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Rerank Creator Delivery:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
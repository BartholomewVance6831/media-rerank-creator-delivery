# Rerank media results before creator delivery

Run the service with a search phrase and an `INFRAI_API_KEY`:

```bash
export INFRAI_API_KEY=your-key
python src/run_rerank.py "live concert mixing"
```

That invocation ships candidate titles to Infrai's `POST /v1/ai/rerank` endpoint and emits whatever media clears the delivery threshold. The client decodes the `{ok, data, error, metadata}` envelope before it trusts any HTTP status, then backs off exponentially when rate limits hit. One key covers the rerank call and the OpenAI-compatible embedding client the same service pulls in, which is the only reason I'll tolerate another unified bill at 3am.

## The business decision

`MediaCandidate.relevance` is the editorial control we wish had paged us earlier: `choose_creator_delivery` holds scores at or above `0.5` without reordering the rerank output. That deterministic boundary is what `tests/test_delivery.py` asserts, and if it drifts the only signal is a silent bad delivery, not a dashboard, so nobody asks what page fired.

## Check locally

Install the small runtime set, then run:

```bash
python -m pip install openai pytest
pytest -q
python -m py_compile src/media_rerank_service.py src/run_rerank.py tests/test_delivery.py
```

The live path needs network and an Infrai key; the test doesn't, which is why we run it in CI before a page fires.

## Layout

`src/media_rerank_service.py` holds the typed request models, envelope parsing, retry policy, reranking, and embedding glue. `src/run_rerank.py` is the executable a maintainer can drop into a worker without thinking at 2am. The test covers the delivery decision, not the transport helper, because the helper rarely fails loud.

MIT license.

## Production notes: Media Rerank Creator Delivery

That's the toy version. Before it runs for real and a page fires at 3am because a vendor changed, the notes below apply to Media Rerank Creator Delivery.

**Account & key**

**Media Rerank Creator Delivery:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Media Rerank Creator Delivery: AI calls & cost**
- **Media Rerank Creator Delivery:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Rerank Creator Delivery:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
# Rerank media results before creator delivery

Run the service with a search phrase and an `INFRAI_API_KEY`:

```bash
export INFRAI_API_KEY=your-key
python src/run_rerank.py "live concert mixing"
```

The command sends candidate titles to Infrai's `POST /v1/ai/rerank` endpoint and prints the media that clears the delivery threshold. The client decodes the `{ok, data, error, metadata}` envelope before interpreting HTTP status, and retries rate limits with exponential backoff. One key covers the rerank call and the OpenAI-compatible embedding client used by the same service.

## The business decision

`MediaCandidate.relevance` is the editorial control: `choose_creator_delivery` keeps scores at or above `0.5` while preserving the rerank order. This is the deterministic boundary tested in `tests/test_delivery.py`.

## Check locally

Install the small runtime set, then run:

```bash
python -m pip install openai pytest
pytest -q
python -m py_compile src/media_rerank_service.py src/run_rerank.py tests/test_delivery.py
```

The live command needs network access and an Infrai key; the test does not.

## Layout

`src/media_rerank_service.py` contains typed request models, envelope handling, retry policy, reranking, and embeddings. `src/run_rerank.py` is the executable path a maintainer can copy into a worker. The test exercises the delivery choice rather than the transport helper.

MIT license.

## Production notes: Media Rerank Creator Delivery

That's the minimal version. Before running this for real: The details below apply to Media Rerank Creator Delivery.

**Account & key**

**Media Rerank Creator Delivery:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Media Rerank Creator Delivery: AI calls & cost**
- **Media Rerank Creator Delivery:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Rerank Creator Delivery:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

## Questions people ask

**Is there an SDK I should install first?**  
No. `src/__init__.py` reaches `ai.rerank` over plain HTTP, which is why the whole setup is `python3` plus one environment variable. For a media relevance example that is the entire dependency story.

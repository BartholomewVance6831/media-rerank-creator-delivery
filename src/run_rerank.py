import argparse

from media_rerank_service import InfraiClient, MediaCandidate, RerankRequest, choose_creator_delivery


def main() -> None:
    parser = argparse.ArgumentParser(description="Rerank media search results for creator delivery")
    parser.add_argument("query")
    args = parser.parse_args()
    candidates = [
        MediaCandidate("clip-101", "Live concert mixing basics", "Mina", 0.91),
        MediaCandidate("clip-205", "Studio lighting for interviews", "Ravi", 0.42),
    ]
    ranked = InfraiClient().rerank(RerankRequest(args.query, candidates, top_k=2))
    delivered = choose_creator_delivery(ranked)
    for item in delivered:
        print(f"{item.media_id}\t{item.creator}\t{item.title}")


if __name__ == "__main__":
    main()

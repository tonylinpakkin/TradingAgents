import os
import requests
import chromadb
from chromadb.config import Settings
from openai import OpenAI


class FinancialSituationMemory:
    def __init__(self, name, config):
        # Allow config to override embedding model, otherwise use defaults
        self.provider = (config.get("llm_provider") or "openai").lower()

        if "embedding_model" in config and config["embedding_model"]:
            self.embedding = config["embedding_model"]
        elif self.provider == "ollama" or config.get("backend_url") == "http://localhost:11434/v1":
            # Default for Ollama: nomic-embed-text
            # Note: Make sure to run 'ollama pull nomic-embed-text' first
            self.embedding = "nomic-embed-text"
        elif self.provider == "google":
            # Default for Google Generative AI embeddings
            self.embedding = "text-embedding-004"
        else:
            # Default for OpenAI/other providers
            self.embedding = "text-embedding-3-small"

        # Only initialize OpenAI-compatible client when not using Google for embeddings
        self.client = None if self.provider == "google" else OpenAI(base_url=config["backend_url"])
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.create_collection(name=name)

    def get_embedding(self, text):
        """Get OpenAI embedding for a text"""
        if self.provider == "google":
            return self._get_google_embedding(text)
        
        response = self.client.embeddings.create(model=self.embedding, input=text)
        return response.data[0].embedding

    def _get_google_embedding(self, text):
        """Get an embedding from Google's Generative Language API.

        Requires the environment variable `GOOGLE_API_KEY` to be set.
        Uses model `text-embedding-004` by default (override via config['embedding_model']).
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. Please export GOOGLE_API_KEY to use Google embeddings."
            )

        url = f"https://generativelanguage.googleapis.com/v1/models/{self.embedding}:embedContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }
        payload = {
            "content": {
                "parts": [
                    {"text": text}
                ]
            }
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if not resp.ok:
            # Truncate response text to avoid overly long messages
            snippet = resp.text[:300]
            raise RuntimeError(f"Google embeddings error {resp.status_code}: {snippet}")

        data = resp.json()
        embedding = (
            data.get("embedding", {}).get("values")
            or data.get("embedding", {}).get("value")
        )
        if embedding is None:
            raise RuntimeError("Unexpected Google embeddings response shape")
        return embedding

    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using OpenAI embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")

import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import sys


# load_dotenv()
# GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
# client = genai.Client(api_key=GEMINI_API_KEY)
# for m in client.models.list():
#   if 'embedContent' in m.supported_actions:
#     print(m.name)

# exit(0)

# https://github.com/google-gemini/cookbook/blob/main/examples/chromadb/Vectordb_with_chroma.ipynb
# https://realpython.com/chromadb-vector-database/#create-a-collection-and-add-reviews

# class GeminiEmbeddingFunction(EmbeddingFunction):
#   def __call__(self, input: Documents) -> Embeddings:
#     response = client.models.embed_content(
#         model="gemini-embedding-001",
#         contents=input,
#         config=types.EmbedContentConfig(
#           task_type="retrieval_document",
#           title="MtG Comprehensive Rules Glossary"
#         )
#     )

#     return response.embeddings[0].values


def _create_db(documents: list[str]) -> None:
    CHROMA_DATA_PATH = "chroma_data/"
    COLLECTION_NAME = "mtg_glossary"

    chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    # db = chroma_client.create_collection(
    #     name=COLLECTION_NAME,
    #     embedding_function=GeminiEmbeddingFunction()
    #     )

    db = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        ),
        # metadata={"hnsw:space": "cosine"},
    )
    for i, d in enumerate(documents):
        db.add(documents=d, ids=str(i))

    return db


def parse_glossary(filename: str) -> list[str]:
    glossary_lines = []
    # rule_items = dict()
    inside_glossary = False
    lines = 0
    # rulenum_pattern = r"^\d{3}(?:\.\d{1,3}[a-z]?)?"
    # ruleref_pattern = r"(?<!^)\d{3}(?:\.\d{1,3}[a-z]?)?"

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                lines += 1
                clean_line = line.strip()

                if lines > 1000:
                    if clean_line == "Credits":
                        break
                    if clean_line == "Glossary":
                        inside_glossary = True
                        continue

                if not inside_glossary:
                    # rule_num = re.search(rulenum_pattern, clean_line)
                    # if rule_num:
                    #     rule_items[rule_num.group()] = clean_line
                    continue

                glossary_lines.append(clean_line)

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    glossary_items = []
    glossary_item = ""
    for raw_line in glossary_lines:
        if len(raw_line) == 0:
            if len(glossary_item) > 0:
                glossary_items.append(glossary_item)
                glossary_item = ""
            continue

        for bad_part in ["See rule", "For more info", "For rules"]:
            bad_idx = raw_line.find(bad_part)
            if bad_idx == 0:
                continue
            if bad_idx > 0:
                raw_line = raw_line[:bad_idx-1]

        if len(glossary_item) > 0:
            glossary_item += " "

        glossary_item += raw_line

        if glossary_item[-1] not in ".”":
            glossary_item += ":"

    return glossary_items


def _get_relevant_passage(query, db):
    passage = db.query(query_texts=[query], n_results=2)["documents"][0][0]
    return passage


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <filename>")
        sys.exit(1)

    target_file = sys.argv[1]
    documents = parse_glossary(target_file)

    # Output the documents
    print(f"Captured {len(documents)} lines:")
    for item in documents:
        print(f"- {item}")

    db = _create_db(documents)
    passage = _get_relevant_passage("replicate", db)
    print("-" * 50)
    print(passage)

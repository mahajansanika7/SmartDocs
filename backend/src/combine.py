from cached_app import get_cached_answer, save_cached_answer
from common import generate_answer
from general_specific_app import classify_query, generate_general_answer
from parent_child_app import get_parent_matches


def gen_ans(query, doc):
    cached_ans=get_cached_answer(query, doc)
    if cached_ans:
        print(f"\nCACHE HIT (distance={cached_ans['distance']:.4f})")
        print(cached_ans["answer"])
        print()
        return {
            "answer": cached_ans["answer"],
            "source": "cache",
            "sources": []
        }

    print("\nCACHE MISS -> running document retrieval...")

    query_type = classify_query(query)
    print(f"Detected type: {query_type}")

    if query_type == "GENERAL":
        print("Answer:", generate_general_answer(query))
        print()
        return {
            "answer": generate_general_answer(query),
            "source": "general",
            "sources": []
        } 
    
    matches = get_parent_matches(query, 3, doc)
    
    if not matches:
        print("No relevant document chunks found.\n")
        return {
            "answer": "I could not find relevant information in the provided documents.",
            "source": "Parent-child rag",
            "sources": []
        }
    
    sources = []

    for match in matches:

        meta = match["metadata"]

        sources.append({
            "document": meta["document_name"],
            "page": meta["page"],
            "distance": match["distance"]
        })
        
    answer = generate_answer(query, matches)
    save_cached_answer(query, answer, doc)

    print("\nCACHE MISS -> generated answer and saved it to cache.")
    print(answer)
    print()
    
    return {
        "answer": answer,
        "source": "Parent-child rag",
        "sources": sources
    }
    
if __name__=="__main__":
    while True:
            query = input("You: ").strip()
            doc=input("Doc:").strip()
    
            if query.lower() == "exit":
                break
    
            if not query:
                continue
            
            gen_ans(query, doc)
            # matches = get_parent_matches(query, top_k=3)
    
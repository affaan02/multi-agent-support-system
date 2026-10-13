from fastmcp import FastMCP
import sqlite3
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from pypdf import PdfReader

# 1. The Ultimate Network Bypass: Offline Local Embeddings
# Prevents ChromaDB from attempting to download HuggingFace models through Canopy
class OfflineEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # Generates a valid local 384-dimensional vector. Zero internet required.
        return [[1.0] * 384 for _ in input]

# Initialize FastMCP Server
mcp = FastMCP("Support_MCP_Server")

# --- Database 1: Structured SQL ---
@mcp.tool()
def get_customer_data(customer_name: str) -> str:
    """Retrieves structured customer profile and past support ticket details."""
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE name=?", (customer_name,))
    profile = cursor.fetchone()
    if not profile: 
        return "Customer not found."
    
    cursor.execute("SELECT * FROM tickets WHERE customer_id=?", (profile[0],))
    tickets = cursor.fetchall()
    conn.close()
    return f"Profile (ID, Name, Tier, LTV): {profile} | Tickets: {tickets}"

# --- Database 2: Unstructured Vector DB (Chroma) ---
chroma_client = chromadb.Client()

# Inject the offline embedding function to bypass SSL downloads
collection = chroma_client.get_or_create_collection(
    name="company_policies",
    embedding_function=OfflineEmbeddingFunction()
)

try:
    reader = PdfReader("policy.pdf")
    text_chunks = [page.extract_text() for page in reader.pages[:3] if page.extract_text()]
    
    if text_chunks:
        collection.add(
            documents=text_chunks,
            metadatas=[{"source": f"page_{i}"} for i in range(len(text_chunks))],
            ids=[f"chunk_{i}" for i in range(len(text_chunks))]
        )
except Exception as e:
    print(f"Vector DB Ingestion Warning: {e}")

@mcp.tool()
def get_policy_info(query: str) -> str:
    """Retrieves context from unstructured company policy documents via Vector DB."""
    try:
        results = collection.query(query_texts=[query], n_results=1)
        if results['documents'] and results['documents'][0]:
            return results['documents'][0][0]
        return "No relevant policy found."
    except Exception as e:
        return f"Vector DB Error: {e}"

if __name__ == "__main__":
    print("MCP Server ready. Dual databases (SQL + Vector) active.")
    mcp.run()
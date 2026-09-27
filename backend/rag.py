from pydantic_ai import Agent
from backend.data_models import RagResponse
from backend.constants import VECTOR_DATABASE_PATH
import lancedb

# Σύνδεση με τον φάκελο - αποθηκευμένες πληροφορίες για τις 5 πιο τουριστικές Ιταλικές Πόλεις
vector_db = lancedb.connect(uri=VECTOR_DATABASE_PATH)

# Δημιουργία Agent 

rag_agent = Agent(
    # Χρήση του Groq API
    model='groq:openai/gpt-oss-20b', 
    retries=4, 
    # Καθορισμός των οδηγιών συμπεριφοράς και των περιορισμών του Agent (System Prompts)
    system_prompt=(  
        # Ορισμός του ρόλου και της εξειδίκευσης του Agent
        "You are an expert Italian tour guide and travel agent, specializing in the top 5 tourist cities of Italy: Rome, Venice, Capri, Milan, and Florence.", 
        # Οδηγία για τη χρήση της ανακτηθείσας γνώσης (RAG Grounding)
        "Always answer based on the retrieved knowledge from WikiTravel, but you can mix in your tourism expertise to make the guide more coherent and engaging.",
        # Αποτροπή ψευδαισθήσεων (Anti-hallucination guardrails)
        "Don't hallucinate. If the user asks about a city or information outside of the retrieved knowledge, politely state that you can only provide information based on the 5 supported Italian cities.",
        # Μορφοποίηση και περιορισμός μεγέθους απάντησης
        "Keep the answer travel-focused, clear, and concise, getting to the point directly. Maximum 6 sentences.",
        # Υποχρεωτική αναφορά πηγών για διαφάνεια των δεδομένων
        "Always mention which city file or source you used to get the information.",
        # Εξασφάλιση ότι η απάντηση θα ακολουθεί πάντα τη δομημένη μορφή, ακόμα κι όταν δεν βρεθεί απάντηση
        "Even when the retrieved information does not answer the question, you must still respond using the required structured format — do not reply with plain text."
    ),
    # Εξασφάλιση δομημένης εξόδου (Structured Output) με βάση το Pydantic σχήμα RagResponse
    output_type=RagResponse,
)

# Μπορούμε να φορτώσουμε ένα εργαλείο / συνάρτηση
@rag_agent.tool_plain
def retrieve_top_documents(query: str, k: int = 3) -> str:
    """
    Uses vector search to find the closest k matching documents to the query
    """
    # Αναζήτηση στη LanceDB (πίνακας "articles") με βάση την ερώτηση (query).
    
    results = vector_db["articles"].search(query=query).limit(k).to_list()
    
    # Ανασύρεται το πρώτο και το πιο σχετικό αποτέλεσμα με το query
    top_result = results[0]

    # Επιστρέφει κείμενο με το όνομα του αρχείου, και τις περιεχόμενες σχετικές πληροφορίες.
   
    return f"""
    Filename: {top_result["filename"]},
    
    Filepath: {top_result["filepath"]},

    Content: {top_result["content"]},
    """
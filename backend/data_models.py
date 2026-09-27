from pydantic import BaseModel, Field
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv

load_dotenv()
embedding_model = get_registry().get("gemini-text").create(name="gemini-embedding-001")
# Μέγεθος διανύσματος για το Gemini. 
# Κάθε τουριστική περιγραφή μετατρέπεται σε λίστα από 3.072 αριθμούς 
# ώστε η LanceDB να ξέρει πώς να αποθηκεύσει και να συγκρίνει τις πληροφορίες.
EMBEDDING_DIM = 3072

# Ορισμός πίνακα στη LanceDB για τουριστικά άρθρα πόλεων
class Article(LanceModel):
    doc_id: str
    filepath:str
    filename:str = Field(description="the stem of the file i.e. without the suffix")
    content:str = embedding_model.SourceField()
    # Αποθήκευση 3072 αριθμών (κείμενο σε μαθηματική μορφή)
    embedding: Vector(EMBEDDING_DIM) = embedding_model.VectorField()

# Ορισμός Prompts και απαντήσεων από Chatbot
class Prompt(BaseModel):
    prompt: str = Field(description="prompt from user, if empty consider it as missing")

class RagResponse(BaseModel):
    filename: str = Field(description="filename of the retrieved file without suffix")
    filepath: str = Field(description="absolute path to the retrieved file")
    answer: str = Field(description="answer based on the retrieved file")
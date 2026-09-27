from dotenv import load_dotenv
load_dotenv()  # Αυτό φορτώνει το αρχείο .env

from fastapi import FastAPI, HTTPException
from backend.rag import rag_agent
from backend.data_models import Prompt
from pydantic_ai.exceptions import ModelHTTPError

# Αρχικοποίηση της εφαρμογής FastAPI για τη δημιουργία του Web API
app = FastAPI()

# Πόσες φορές θα ξαναδοκιμάσουμε αν το μοντέλο αποτύχει να καλέσει το tool
MAX_MODEL_RETRIES = 3

# Ορισμός HTTP POST endpoint για τη διαχείριση των ερωτημάτων RAG
@app.post("/rag/query")
async def query_documentation(query: Prompt):
    last_error = None

    # Χειροκίνητο retry loop για να καλύψουμε το σποραδικό σφάλμα
    # "Tool choice is required, but model did not call a tool" από το Groq
    for attempt in range(MAX_MODEL_RETRIES):
        try:
            # Ασύγχρονη κλήση του Rag Agent για την επεξεργασία του ερωτήματος του χρήστη
            result = await rag_agent.run(query.prompt)
            # Επιστροφή των δομημένων αποτελεσμάτων (τύπου RagResponse) στον πελάτη (client)
            return result.output
        except ModelHTTPError as e:
            last_error = e
            print(f"Προσπάθεια {attempt + 1}/{MAX_MODEL_RETRIES} απέτυχε: {e}")
            continue

    # Αν εξαντλήθηκαν όλες οι προσπάθειες, επιστρέφουμε καθαρό σφάλμα στον client
    raise HTTPException(
        status_code=503,
        detail=f"Το μοντέλο απέτυχε να απαντήσει μετά από {MAX_MODEL_RETRIES} προσπάθειες. Δοκίμασε ξανά."
    )
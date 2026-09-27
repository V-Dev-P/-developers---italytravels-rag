import lancedb
from backend.constants import VECTOR_DATABASE_PATH, DATA_PATH
from backend.data_models import Article
import time

def setup_vector_db(path):
    """
    Αρχικοποιεί τη σύνδεση με τη LanceDB και δημιουργεί τον απαραίτητο πίνακα.
    """
    # Συνδέεται με τη βάση δεδομένων στον κατάλογο που ορίζει το 'path'
    vector_db = lancedb.connect(uri=path)
    
    # Δημιουργεί τον πίνακα "articles" χρησιμοποιώντας το schema (δομή) της κλάσης Article.
    # Με το exist_ok=True, αν ο πίνακας υπάρχει ήδη, απλά τον ανοίγει χωρίς να πετάξει σφάλμα.
    vector_db.create_table("articles", schema=Article, exist_ok=True)

    # Επιστρέφει το αντικείμενο της σύνδεσης για να το χρησιμοποιήσουμε στη συνέχεια
    return vector_db

def ingest_docs_to_vector_db(table):
    """
    Διαβάζει αρχεία κειμένου (.txt) από τον φάκελο DATA_PATH και τα εισάγει στη βάση.
    """
    # Χρησιμοποιεί τη glob για να βρει και να διατρέξει ένα προς ένα όλα τα αρχεία .txt
    for file in DATA_PATH.glob("*.txt"):
        
        # Ανοίγει το αρχείο με κωδικοποίηση UTF-8 για να διαβάζει σωστά τους ελληνικούς χαρακτήρες
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        # Αποθηκεύει το όνομα του αρχείου (χωρίς την επέκταση .txt) ως το μοναδικό ID του εγγράφου
        doc_id = file.stem    
        
        # Διαγράφει τυχόν παλαιότερη εγγραφή με το ίδιο ID, ώστε αν ξανατρέξει ο κώδικας να μην έχουμε διπλότυπα
        table.delete(f"doc_id = '{doc_id}'")

        # Εισάγει τα δεδομένα του αρχείου στον πίνακα της βάσης δεδομένων
        table.add([
            {
                "doc_id": doc_id,       # Το αναγνωριστικό του εγγράφου
                "filepath": str(file),   # Η πλήρης διαδρομή του αρχείου ως κείμενο
                "filename": file.stem,   # Το καθαρό όνομα του αρχείου
                "content": content       # Το περιεχόμενο (κείμενο) του αρχείου
            }
        ])
        
        # Μετατρέπει προσωρινά τον πίνακα σε Pandas DataFrame και τυπώνει τη στήλη με τα ονόματα αρχείων
        print(table.to_pandas()["filename"])
        
        # Καθυστερεί την εκτέλεση για 30 δευτερόλεπτα πριν προχωρήσει στο επόμενο αρχείο
        time.sleep(30)

# Το σημείο εκκίνησης του προγράμματος (τρέχει μόνο αν εκτελέσεις απευθείας αυτό το αρχείο)
if __name__ == "__main__":
    
    # 1. Καλούμε τη συνάρτηση setup για να συνδεθούμε στη βάση δεδομένων
    db = setup_vector_db(VECTOR_DATABASE_PATH)
    
    # 2. Ανοίγουμε τον πίνακα "articles" χρησιμοποιώντας τη σωστή μέθοδο open_table
    articles_table = db.open_table("articles")
    
    # 3. Ξεκινάμε τη διαδικασία εισαγωγής των αρχείων κειμένου περνώντας τον πίνακα ως όρισμα
    ingest_docs_to_vector_db(articles_table)
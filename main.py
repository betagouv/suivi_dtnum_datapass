import os
import time
import argparse
from suivi_dtnum_updater import SuiviDtnumUpdater
from dotenv import load_dotenv

load_dotenv()

# Define paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE_PATH = os.path.join(SCRIPT_DIR, "sources", "dgfip - dtnum - demandes dacces api - fichier de suivi version test- 1605 with v2 ids.ods")
OUTPUT_FILE_PATH = os.path.join(SCRIPT_DIR, "sources", time.strftime("%Y%m%d-%H%M%S") + "-fichier-suivi-maj.xlsx")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update DTNUM tracking file with DataPass data")
    parser.add_argument("--client-id", help="DataPass client ID")
    parser.add_argument("--client-secret", help="DataPass client secret")
    parser.add_argument("--is-local", help="To use the Datapass API on localhost", action="store_true")
    args = parser.parse_args()
    
    # Use command line arguments if provided, otherwise fall back to environment variables
    client_id = args.client_id or os.getenv("DATAPASS_CLIENT_ID")
    client_secret = args.client_secret or os.getenv("DATAPASS_CLIENT_SECRET")

    updater = SuiviDtnumUpdater(client_id, client_secret, is_local=args.is_local)
    updater.run(INPUT_FILE_PATH, OUTPUT_FILE_PATH)
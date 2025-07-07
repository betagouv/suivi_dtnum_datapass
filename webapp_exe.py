from flask import Flask, render_template, request, send_file, redirect, jsonify
import os 
import glob
import webview
import sys
import traceback
import time
from suivi_dtnum_updater import SuiviDtnumUpdater
from dotenv import load_dotenv

load_dotenv()

EXECUTABLE_DIR = os.path.dirname(sys.executable)
FOLDER_LIST = ("outputs", "uploads")

# Initialisation de l'app
app = Flask(__name__, template_folder='templates', static_folder='static')
webview.settings['ALLOW_DOWNLOADS'] = True
window = webview.create_window('Mise à jour du fichier de suivi des DA', app, maximized=True)
app.debug = True
output_path = ""
processing_progress = (0, 0)

# Gestion des imports/exports
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Gestion de la barre de progression
def update_progress(progress, message:str = None):
    global processing_progress
    processing_progress = (progress, message)

@app.route('/progress', methods=['GET'])
def progress():
    global processing_progress
    return jsonify({'progress': processing_progress[0], 'message' : processing_progress[1]})    
      
@app.route('/reset_progress', methods=['GET'])
def reset_progress():
    global processing_progress
    processing_progress = (0, 0)
    return redirect('html')   
 

# Gestion des erreurs
@app.errorhandler(404)
def page_not_found(error):
    return '400'

@app.errorhandler(Exception)
def internal_error(error):    
    traceback_message = traceback.format_exc()
    return render_template('erreur500.html',e_message=error , traceback = traceback_message), 500

@app.errorhandler(ValueError)
def value_error_handler(error):
    process_message = str(error).split("\n")[1:]
    error_message = str(error).split("\n")[0] 
    return render_template('erreur.html', error_message=error_message, process_message=process_message), 400


# Page d'accueil
@app.route('/')
@app.route('/html')
def html():
    processing_done = request.args.get('processing_done', False)
    files_error = request.args.get('files_error', False)
    
    for folder in FOLDER_LIST:
        folder_path = resource_path(folder)
        # Vérifiez si le dossier existe, sinon créez-le
        if not os.path.exists(folder_path):
            print("Création du répertoire : {}".format(folder_path))
            os.makedirs(folder_path)
        
    # Supprimer tous les fichiers dans le dossier d'entrée
    for file_path in glob.glob(resource_path('uploads' + '/*')):
        os.remove(file_path)
        
    return render_template("index.html", processing_done=processing_done, files_error=files_error)  


# Import et traitement
@app.route('/upload', methods=['POST'])
def upload():

    client_id = os.getenv("DATAPASS_CLIENT_ID")
    client_secret = os.getenv("DATAPASS_CLIENT_SECRET")

    # Supprimer tous les fichiers dans le dossier de sortie
    for file_path in glob.glob(resource_path('outputs' + '/*')):
        os.remove(file_path)
    global processing_done
    global output_path

    if request.files['ods_file'].filename == '':
        return ('', 204)

    else:
        update_progress(0)
        # Récupérer et sauvegarder le fichier de suivi en entrée
        ods_file = request.files['ods_file']
        ods_path = resource_path('uploads/' + ods_file.filename)
        ods_file.save(ods_path)

        time.sleep(2)
        update_progress(10, "Ingestion du fichier de suivi")
        time.sleep(4)

        filename = time.strftime("%Y%m%d-%H%M%S") + "-fichier-suivi-maj.xlsx"
        output_path = resource_path('outputs/' + filename)          
        
        # Lancer le traitement 
        update_progress(40, "Intégration des données datapass.api.gouv.fr")
        time.sleep(4)
        update_progress(60, "Traitement du fichier de suivi")

        updater = SuiviDtnumUpdater(client_id, client_secret, False)
        updater.run(ods_path, output_path)

        update_progress(80, "Ecriture du fichier mis à jour")  

        time.sleep(2)      
        update_progress(100)

        return render_template('index.html', processing_done=True)

        
# Téléchargement du fichier mis à jour
@app.route('/download', methods=['GET'])
def download():
    global output_path
    return send_file(output_path, as_attachment=True)


# Lancement de l'app
if __name__=='__main__':
    webview.start()
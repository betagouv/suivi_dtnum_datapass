

pyinstaller --noconfirm --onefile --windowed --paths="./venv/Lib/site-packages" --icon "./static/dsfr/favicon/favicon.ico" --add-data "./templates;templates/" --add-data "./static;static/" "./webapp_exe.py" --name "./MAJ suivi DA"
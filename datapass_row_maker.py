import sys
from dateutil import parser
import datapass_data_correspondances as data_correspondances

class DatapassRowMaker:
    STATE_EVENTS = ["approve", "refuse", "request_changes", "submit", "reopen"]

    def __init__(self, demande):
        self.demande = demande

    def format_date(self, date_str):
        """Convert a date string to DD/MM/YYYY format"""
        if not date_str:
            return ""
        try:
            dt = parser.parse(date_str)
            return dt.strftime('%d/%m/%Y')
        except (ValueError, AttributeError, TypeError):
            return date_str

    def make_rows_from_demande(self):
        rows = []
        habilitations = self.demande['habilitations']

        if len(habilitations) == 0:
            if self.demande['state'] not in ['draft']:
                rows.append(self.format_demande_row())
        else:
            for habilitation in habilitations:
                rows.append(self.format_habilitation_row(habilitation))
            # If the demande is still being instructed, add another row for the demande.
            if self.demande['state'] in ["submitted", "changes_requested", "refused"]:
                rows.append(self.format_demande_row())
        
        return rows

    def get_date_of_last_state_event(self, demande):
        state_events = [event for event in demande["events"] if event["name"] in self.STATE_EVENTS]
        if not state_events:
            return None
        return max(event["created_at"] for event in state_events)

    def format_demande_row(self):
        row = {}
        row["N° Demande v2"] = self.demande["id"]
        row["N° Habilitation v2"] = None
        row["Environnement"] = data_correspondances.match_environnement(self.demande["form_uid"], self.demande["type"])
        row['Criticité'] = 'Normale' # Default value, will be overwritten by the input content if it exists
        row["API"] = data_correspondances.match_api_name(self.demande["type"], self.demande["data"])
        row["Type"] = "Avenant" if self.demande["reopening"] else "Initial"
        row["Modèle pré-rempli / cas d'usage"] = data_correspondances.match_cas_dusage(self.demande["form_uid"])

        row = self.format_data_attributes(row, self.demande["data"])
        row["Date de réception"] = self.format_date(self.demande['reopened_at'] or self.demande["last_submitted_at"])
        row["Date de dernière soumission ou instruction"] = self.format_date(self.get_date_of_last_state_event(self.demande))
        row["Statut"] = data_correspondances.match_statut(self.demande["state"])
        
        # Get SIRET safely from nested dictionary
        organisation = self.demande.get("organisation", {})
        row["SIRET demandeur"] = organisation["siret"]

        insee_payload = organisation.get("insee_payload", {})
        etablissement = insee_payload.get("etablissement", {})
        unite_legale = etablissement.get("uniteLegale", {})
        row['Raison sociale demandeur'] = unite_legale.get("denominationUniteLegale")
        adresse = etablissement.get("adresseEtablissement", {})
        row['Code postal'] = adresse.get("codePostalEtablissement")
        row['Ville'] = adresse.get("libelleCommuneEtablissement")
        row['Département'] = None # Made none to be filled by the Address API
        row['Région'] = None
    

        return row

    def format_habilitation_row(self, habilitation):
        row = self.format_demande_row()
        row["N° Habilitation v2"] = habilitation["id"]
        row["Environnement"] = data_correspondances.match_environnement(self.demande["form_uid"], habilitation["authorization_request_class"])
        row["API"] = data_correspondances.match_api_name(habilitation["authorization_request_class"], habilitation["data"])
        row["Type"] = "Initial" if self.is_first_habilitation(habilitation) else "Avenant"

        row = self.format_data_attributes(row, habilitation["data"])
        row["Date de dernière soumission ou instruction"] = self.format_date(habilitation["created_at"])
        row["Statut"] = data_correspondances.match_statut(habilitation["state"], habilitation["revoked"])

        return row

    def format_data_attributes(self, row, data):
        row["Nom projet"] = data.get("intitule")
        row["Description projet"] = data.get("description")
        row["Destinataires des données"] = data.get("destinataire_donnees_caractere_personnel")
        row["Date prévisionnelle d'ouverture de service"] = self.format_date(data.get("date_prevue_mise_en_production"))
        row["Volumétrie"] = data.get("volumetrie_appels_par_minute")
        row["N° DataPass FC rattaché"] = data.get("france_connect_authorization_id")
        row["Quota"] = data.get("volumetrie_appels_par_minute")
        
        return row 
    
    def is_first_habilitation(self, habilitation):
        # Find the earliest created habilitation
        earliest_date = min(h["created_at"] for h in self.demande["habilitations"])
        
        # Check if current habilitation is the earliest one
        return habilitation["created_at"] == earliest_date
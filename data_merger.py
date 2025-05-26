import pandas as pd
from address_api_client import AddressApiClient

class DataMerger:
    # We want to overwrite only these colomns from input with datapass content. The rest is overwritten only if it's empty in input.
    DATAPASS_PRIORITISED_COLUMNS = ['N° DataPass FC rattaché', 'API', 'Environnement', 'Date de dernière soumission ou instruction', 'Statut', 'Nom projet', 'Description projet', 'Destinataires des données', 'Date prévisionnelle d\'ouverture de service', 'Volumétrie', 'Quotas']
    
    def __init__(self, input_content, datapass_content):
        self.input_content = input_content
        self.datapass_content = datapass_content

    def generate_output_content(self):
        return self.merge_input_and_datapass_content(self.input_content, self.datapass_content)

    def merge_input_and_datapass_content(self, input_content, datapass_content):

        print(f"Lengths of contents before merging : input: {len(input_content)} datapass: {len(datapass_content)}")
        # Merge everything simple, meaning the rows of demandes without habilitations + the rows of habilitations from both contents
        output_rows = self.merge_demandes_and_habilitations_and_remove_matched_rows(input_content, datapass_content)
        print(f"Lengths of contents after merging demandes and habilitations : input: {len(input_content)} datapass: {len(datapass_content)}")

        # We check the demandes with new habilitations after the first merge
        # because we want to be sure of which habilitation row is merging with the former demande row
        # so we wait for the first pass to match all the former habilitations.
        output_rows.extend(self.merge_demandes_with_new_habilitations_and_remove_matched_rows(input_content, datapass_content))
        print(f"Lengths of contents after merge new habilitations : input: {len(input_content)} datapass: {len(datapass_content)}")

        # add the new content from datapass that doesn't match any input content
        output_rows.extend(self.add_leftover_datapass_and_remove_matched_rows(datapass_content))
        print(f"Lengths of contents after adding leftover datapass content : input: {len(input_content)} datapass: {len(datapass_content)}")

        # add the leftover input content that we couldn't match with datapass
        output_rows.extend(self.add_leftover_input_rows(input_content))

        # create files with the leftover contents
        print(f"Leftover input content : {len(input_content)} -> Check the file leftover_input_content.csv")
        input_content.to_csv("sources/leftover_input_content.csv", index=False, quoting=1)
        print(f"Leftover datapass content : {len(datapass_content)} -> Check the file leftover_datapass_content.csv")
        datapass_content.to_csv("sources/leftover_datapass_content.csv", index=False, quoting=1)

        # add regions and departments
        output_rows = self.add_regions_and_departments(output_rows)

        # Convert list to DataFrame once at the end
        output_content = pd.DataFrame(output_rows)

        # sort the headers in the same order as the original file
        output_content = output_content[input_content.columns]

        # sort rows by N° Datapass v1 then N° Demande v2, then N° Habilitation v2
        output_content = output_content.sort_values(by=['N° DataPass v1', 'N° Demande v2', 'N° Habilitation v2'])

        # Mark duplicated rows in the "Erreurs" column
        output_content = self.mark_duplicated_rows(output_content)

        print(f"#{len(output_content)} rows after merging input and datapass content")
        return output_content
    

    def merge_demandes_and_habilitations_and_remove_matched_rows(self, input_content, datapass_content):
        output_rows = []

        for input_row_index, input_row in input_content.iterrows():
            # Check if the row has a habilitation or not
            has_habilitation = not pd.isnull(input_row["N° Habilitation v2"])
            
            if has_habilitation:
                # Handle rows with habilitations
                datapass_rows = datapass_content[(datapass_content["N° Demande v2"] == input_row["N° Demande v2"]) & 
                                                (datapass_content["N° Habilitation v2"] == input_row["N° Habilitation v2"])]
            else:
                # Handle rows without habilitations
                datapass_rows = datapass_content[(datapass_content["N° Demande v2"] == input_row["N° Demande v2"]) & 
                                                (datapass_content["N° Habilitation v2"].isnull())]
                
            if len(datapass_rows) == 0:
                # We will check rows with no match in merge_demandes_with_new_habilitations later
                continue
            elif len(datapass_rows) == 1:
                datapass_row = datapass_rows.iloc[0]
                output_row = self.merge_input_row_and_datapass_row(input_row, datapass_row)
                output_rows.append(output_row)
                # Remove matched rows from both contents
                datapass_content.drop(datapass_rows.index, inplace=True)
                input_content.drop(input_row_index, inplace=True)
            else:
                habilitation_info = f"and N° Habilitation {input_row['N° Habilitation v2']}" if has_habilitation else "and N° Habilitation empty"
                raise Exception(f"Found several rows with N° Demande {input_row['N° Demande v2']} {habilitation_info} in datapass content")

        return output_rows

    def merge_demandes_with_new_habilitations_and_remove_matched_rows(self, input_content, datapass_content):
        output_rows = []

        input_content_without_habilitation = input_content[input_content['N° Habilitation v2'].isnull()]

        for input_row_index, input_row in input_content_without_habilitation.iterrows():
            datapass_rows = datapass_content[(datapass_content['N° Demande v2'] == input_row['N° Demande v2']) & ~datapass_content['N° Habilitation v2'].isnull()]

            if len(datapass_rows) == 0:
                continue
            elif len(datapass_rows) == 1:
                datapass_row = datapass_rows.iloc[0]
                output_row = self.merge_input_row_and_datapass_row(input_row, datapass_row)
                output_rows.append(output_row)
                # Remove matched rows from both contents
                datapass_content.drop(datapass_rows.index, inplace=True)
                input_content.drop(input_row_index, inplace=True)
            else:
                raise Exception(f"Found several rows with N° Demande {input_row['N° Demande v2']} in datapass content")
        
        return output_rows

    def merge_input_row_and_datapass_row(self, input_row, datapass_row):
        # This makes a copy of the input_row without the columns we want to overwrite
        cleaned_input_row = input_row.drop(columns=self.DATAPASS_PRIORITISED_COLUMNS)
        # This updates the cleaned_input_row empty values with the datapass_row values
        # then restore dropped columns with values from datapass_row
        # then updates the result with the initial input_row values in case there were some empty values left in mandatory columns
        # (Note : We might need to adapt the combination differently for the v1 and the v2 data)
        temp_output_row = cleaned_input_row.combine_first(datapass_row)
        for col in self.DATAPASS_PRIORITISED_COLUMNS:
            if col in datapass_row:
                temp_output_row[col] = datapass_row[col]        
        output_row = temp_output_row.combine_first(input_row)
        return output_row

    def add_leftover_datapass_and_remove_matched_rows(self, datapass_content):
        output_rows = []
        relevant_datapasses = datapass_content[~datapass_content['Statut'].isin(["Brouillon", "Supprimé"])]

        for _, datapass_row in relevant_datapasses.iterrows():
            output_rows.append(datapass_row)
            datapass_content.drop(datapass_row.name, inplace=True)

        return output_rows

    def value_is_empty(self, value):
        # pd.isna checks for None and NaN
        return pd.isna(value) or value == "" or value == "NON RENSEIGNE" or value == "CODE POSTAL NON VALIDE" or value == "SIRET NON VALIDE"

    def row_needs_region_and_department(self, row):
        return (
            not self.value_is_empty(row.get("Code postal"))
            and (
                self.value_is_empty(row.get("Département"))
                or self.value_is_empty(row.get("Région"))
            )
        )
    
    def add_regions_and_departments(self, output_content):
        # Fill only blank regions and departments using the Address API
        # Not processing rows with null/none values of postcode for the moment
        address_api_client = AddressApiClient()
        relevant_rows = [row for row in output_content if self.row_needs_region_and_department(row)]

        print (f"Filling regions and departments using the Address API for {len(relevant_rows)} rows")
        
        for row in relevant_rows:
            print(".", end="", flush=True)
            postcode = row.get("Code postal")
            region_and_departement = address_api_client.search_region_and_department_by_postcode(postcode)
            row["Département"] = region_and_departement["departement"]
            row["Région"] = region_and_departement["region"]

        print("\nAll departments and regions have been fetched")
        return output_content

    def append_error(self, row, error_message):
        # Create a copy of the row to avoid SettingWithCopyWarning
        row_copy = row.copy()
        
        if pd.isna(row_copy["Erreurs"]) or row_copy["Erreurs"] is None:
            row_copy["Erreurs"] = error_message
        else:
            # Check if the error message is already present in the column
            if error_message not in row_copy["Erreurs"]:
                row_copy["Erreurs"] = f"{row_copy['Erreurs']}\n{error_message}"
        
        return row_copy

    def add_leftover_input_rows(self, input_content):
        output_rows = []

        for _, row in input_content.iterrows():
            if self.value_is_empty(row.get("N° Demande v2")):
                row_with_error = self.append_error(row, "N° Demande v2 vide")
            else:
                row_with_error = self.append_error(row, "N° Demande ou N° Habilitation non trouvé")
            output_rows.append(row_with_error)

        return output_rows

    def mark_duplicated_rows(self, output_content):
        # Create a mask to identify duplicates based on N° Demande v2 and N° Habilitation v2
        duplicate_mask = output_content.duplicated(subset=['N° Demande v2', 'N° Habilitation v2'], keep=False)
        
        # For rows that are duplicated, append to "Erreurs" column rather than overwriting
        duplicate_message = 'DOUBLON sur N° Demande / N° Habilitation'
        
        # Only get the 'Erreurs' column for updating, to minimize data copying
        if duplicate_mask.any():
            for idx in output_content[duplicate_mask].index:
                # Extract just the necessary fields for the append_error operation
                mini_row = pd.Series({'Erreurs': output_content.loc[idx, 'Erreurs']})
                # Apply the append_error method
                updated_mini_row = self.append_error(mini_row, duplicate_message)
                # Update only the Erreurs column in the original DataFrame
                output_content.loc[idx, 'Erreurs'] = updated_mini_row['Erreurs']
        
        return output_content
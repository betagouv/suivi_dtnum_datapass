import pandas as pd
from datapass_api_client import DataPassApiClient
from datapass_row_maker import DatapassRowMaker
from data_merger import DataMerger

class SuiviDtnumUpdater:
    def __init__(self, client_id, client_secret, is_local=False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.is_local = is_local

    def run(self, input_file_path, output_file_path):
        input_content = self.read_input_file(input_file_path)
        
        api_client = DataPassApiClient(self.client_id, self.client_secret, is_local=self.is_local)
        all_demandes = api_client.get_all_demandes()

        self.generate_output_content(all_demandes, input_content, output_file_path)
        print("\nAll done.")


    def read_input_file(self, input_file_path):
        print(f"Reading original file from {input_file_path}...")
        
        try:
            # Read the ODS file with header at row 5 (index 4)
            input_content = pd.read_excel(
                input_file_path,
                engine="odf",
                sheet_name='Demandes_accès',
                header=4
            )
            
            # Print the number of lines
            print(f"Number of lines in the input file: {len(input_content)}")
            return input_content
        except FileNotFoundError as e:
            print(f"Original file not found at {input_file_path}")
            raise e

    def make_datapass_content_from_demandes(self, all_demandes):
        print("Making datapass rows...")
        
        datapass_rows = []
        for demande in all_demandes:
            # ignore demandes with no submit event
            submit_events = [event for event in demande["events"] if event["name"] == "submit"]
            if len(submit_events) > 0:
                datapass_rows.extend(DatapassRowMaker(demande).make_rows_from_demande())
        
        datapass_content = pd.DataFrame(datapass_rows)
        print(f"{len(datapass_content)} Datapass rows generated.")
        return datapass_content
        
    def generate_output_content(self, all_demandes, input_content, output_file_path):
        datapass_content = self.make_datapass_content_from_demandes(all_demandes)
        datapass_content.to_csv("sources/test_datapass_content.csv", index=False, quoting=1)

        data_merger = DataMerger(input_content, datapass_content)
        output_content = data_merger.generate_output_content()
        output_content.to_csv("sources/test_output_content.csv", index=False, quoting=1)

        # print the output content in an excel file
        with pd.ExcelWriter(output_file_path) as writer:
            output_content.to_excel(writer, sheet_name='result', index=False)

        print(f"Output file saved to {output_file_path}")

import os 
import shutil
class s3sync:
    def __init__(self, Local_sync_folder = "s3_sync_folder"):
        self.Local_sync_folder = Local_sync_folder
        if not os.path.exists(self.Local_sync_folder):
            os.makedirs(self.Local_sync_folder, exist_ok=True)
        
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        # command = (
        #     f"aws s3 sync {folder} {aws_bucket_url}"
        # )
        # os.system(command)
        try:
            dest_path= aws_bucket_url.replace("s3://","").replace(aws_bucket_url.split("/")[0] + "/", "")
            destination = os.path.join(self.Local_sync_folder, dest_path)

            # copy folder 
            if os.path.exists(destination):
                shutil.rmtree(destination)
            shutil.copytree(folder, destination)
            print(f"Synced {folder} to {destination}")
        except Exception as e:
            print(f"Error syncing folder to S3: {e}")



    def sync_folder_from_s3(self, folder, aws_bucket_url):
        # command = (
        #     f"aws s3 sync {aws_bucket_url} {folder}"
        # )
        # os.system(command)

        try: 
            source_path = aws_bucket_url.replace("s3://","").replace(aws_bucket_url.split("/")[0] + "/", "")
            source = os.path.join(self.Local_sync_folder, source_path)

            if os.path.exists(folder):
                shutil.rmtree(folder)
            shutil.copytree(source, folder)
            print(f"Synced {source} to {folder}")
        except Exception as e:
            print(f"Error syncing folder from S3: {e}")

        
'''
    Retrieve the TraceBench traces from remote S3 bucket and download + extract them to local machine
'''

import os
import sys
import requests
import zipfile
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TaskID
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
from io import BytesIO


def extract_tracebench(progress: Progress, content: BytesIO, directory: str, extraction_task: TaskID) -> None:
    # Extract the zip file
    with zipfile.ZipFile(content) as zip_ref:
        # Get total files to extract
        files = zip_ref.namelist()
        progress.update(extraction_task, total=len(files))
        
        # Extract each file with progress update
        for i, file in enumerate(files):
            zip_ref.extract(file, directory)
            progress.update(extraction_task, completed=i+1)
    

def download_tracebench(url: str = 'https://tracebench.s3.us-east-1.amazonaws.com', version: str ='0.1.0', extract_to: str ="./evaluator"):
    """download tracebench from the AWS S3 Bucket

    Args:
        url (str, optional): default url for the S3 Bucket. Defaults to 'https://tracebench.s3.us-east-1.amazonaws.com'.
        version (str, optional): version of tracebench to download. Defaults to '0.1.0'.
        extract_to (str, optional): directory to extract to. Defaults to "./evaluator".
    """
    console = Console()
    
    try:
        # Create extract directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)
        
        console.print(Panel.fit("[bold blue]Downloading and Extracting Script[/bold blue]", 
                               border_style="green"))
        
        # Set up progress display
        progress = Progress(
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn()
        )
        
        with progress:
            # Start download task
            download_task = progress.add_task("[cyan]Downloading...", total=None)

            # example: http://tracebench.s3-website-us-east-1.amazonaws.com/tracebench-0.1.0.zip
            full_url = f'{url}/tracebench-{version}.zip'
            
            # Download with streaming to track progress
            response = requests.get(full_url, stream=True)
            response.raise_for_status()
            
            # Get total size if available
            total_size = int(response.headers.get('content-length', 0))
            if total_size:
                progress.update(download_task, total=total_size)
                
            # Download the content with progress tracking
            content = BytesIO()
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                content.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    progress.update(download_task, completed=downloaded)
            
            progress.update(download_task, description="[green]Download complete!")
            
            # Reset the BytesIO position
            content.seek(0)
            
            # Start extraction task
            extract_task = progress.add_task("[cyan]Extracting files...", total=None)

            # Extract the files
            extract_tracebench(progress, content, extract_to, extract_task)
            
            progress.update(extract_task, description="[green]Extraction complete!")
        
        console.print(Panel.fit("[bold green]TraceBench successfully downloaded and extracted to [/bold green][bold yellow]{}[/bold yellow]".format(
            os.path.abspath(extract_to)), border_style="green"))
        
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Download Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)
    except zipfile.BadZipFile:
        console.print("[bold red]Error:[/bold red] The file is not a valid zip file", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    # Example usage - replace with your actual URL
    # url = "https://example.com/path/to/script.zip"
    
    # You can also take URL from command line arguments
    # if len(sys.argv) > 1:
    #     url = sys.argv[1]
    
    download_tracebench()
import os
import subprocess
import logging
from datetime import datetime

# Define the paths for the source directory, Git repository, and log file
source_directory = r"C:\Users\chand\OneDrive\Desktop\source folder"  # Path to the source directory
git_repository_path = r"C:\Users\chand\OneDrive\Desktop\GIT_BACKUP"  # Path to the Git repository
log_file_path = r"C:\Users\chand\OneDrive\Desktop\backup_logs\Backup_report.txt"  # Define the log file path

# Fetch GitHub credentials from environment variables
github_username = os.getenv("GIT_USERNAME") #use environmental variables for privacy of username and token without explicity mentioning
github_token = os.getenv("GIT_TOKEN")  # Corrected the variable name for the Git token
remote_url = f"https://{github_username}:{github_token}@github.com/Chaithanya0511/backup-storage.git"

# Create the directory for the log file if it doesn't exist
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=log_file_path,  # Set the path for the log file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def backup_to_git(source_dir, git_repo_path, remote_url):
    try:
        # Ensure the source directory exists
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Source directory '{source_dir}' does not exist.")

        # Initialize a Git repository if not already initialized
        if not os.path.exists(os.path.join(git_repo_path, ".git")):
            subprocess.run(["git", "init"], cwd=git_repo_path, check=True)
            logging.info("Initialized a new Git repository.")
        else:
            logging.info("Git repository already initialized.")

        # Check if the remote is configured, if not, configure it
        try:
            subprocess.run(["git", "remote", "get-url", "origin"], cwd=git_repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info("Remote repository already configured.")
        except subprocess.CalledProcessError:
            subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=git_repo_path, check=True)
            logging.info(f"Remote repository configured with URL: {remote_url}")

        # Synchronize files from source directory to Git repository
        for root, _, files in os.walk(source_dir):
            for file in files:
                source_file = os.path.join(root, file)
                relative_path = os.path.relpath(source_file, source_dir)
                destination_file = os.path.join(git_repo_path, relative_path)

                # Create necessary directories in the Git repository
                os.makedirs(os.path.dirname(destination_file), exist_ok=True)

                # Copy the file to the Git repository
                with open(source_file, 'rb') as src, open(destination_file, 'wb') as dest:
                    dest.write(src.read())
                logging.info(f"Copied {source_file} to {destination_file}")

        # Add changes to the Git repository
        subprocess.run(["git", "add", "."], cwd=git_repo_path, check=True)

        # Check if there are any changes to commit
        status_result = subprocess.run(["git", "status", "--porcelain"], cwd=git_repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status_output = status_result.stdout.decode().strip()

        if not status_output:
            logging.warning("No changes detected. Nothing to commit.")
        else:
            # Commit changes to the Git repository
            commit_message = f"Backup on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], cwd=git_repo_path, check=True)
            logging.info(f"Committed changes with message: {commit_message}")

        # Check the current branch name (whether it's "master" or "main" or any other branch)
        branch_result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=git_repo_path, check=True, stdout=subprocess.PIPE)
        current_branch = branch_result.stdout.decode().strip()
        logging.info(f"Current branch: {current_branch}")

        # Pull the latest changes from the remote 'main' branch with rebase
        try:
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=git_repo_path, check=True)
            logging.info("Pulled latest changes from the remote 'main' branch with rebase.")
        except subprocess.CalledProcessError:
            logging.warning("Failed to pull changes from the remote 'main' branch. Ensure you're on the correct branch and have the latest updates.")

        # Push changes to the correct remote branch ('main' now)
        try:
            subprocess.run(["git", "push", "origin", "main"], cwd=git_repo_path, check=True)
            logging.info("Pushed changes to the remote repository on branch main.")
        except subprocess.CalledProcessError:
            logging.warning("Pushing to remote repository failed. Ensure the branch 'main' exists or credentials are correct.")

        logging.info("Backup operation completed successfully.")
        return True

    except Exception as e:
        logging.error(f"Backup operation failed: {e}")
        return False

if __name__ == "_main_":
    # Run the backup function and log the result
    success = backup_to_git(source_directory, git_repository_path, remote_url)
    if success:
        print(f"Backup completed successfully. Check the log file at: {log_file_path}")
    else:
        print(f"Backup failed. Check the log file at: {log_file_path}")
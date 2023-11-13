import instaloader
import os
import re
import concurrent.futures
import shutil

# Create an instance of the Instaloader class
L = instaloader.Instaloader()

# Define regular expression pattern for URL validation
url_pattern = re.compile(r"https?://www\.instagram\.com/p/[\w-]+/?")

# Get the post URL from user input with error handling
while True:
    post_url = input("Enter post URL: ")
    if not url_pattern.match(post_url):
        print("Invalid URL, please try again.")
        continue
    try:
        # Clean the URL input
        cleaned_url = re.sub(r"[?].*", "", post_url)
        print("Cleaned URL:", cleaned_url)
        # Get post details
        url_parts = cleaned_url.split("/")
        if len(url_parts) < 2:
            print("Invalid URL, please try again.")
            continue
        post = instaloader.Post.from_shortcode(L.context, url_parts[-2])
        break
    except instaloader.exceptions.InvalidArgumentException:
        print("Invalid URL, please try again.")

# Download the post and its photos with error handling
try:
    # Get post details
    print("Getting post details...")
    post_details = post.__dict__
    # Create destination folder if it does not exist
    username = post.owner_username
    destination_folder = f"{username}_downloads"
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, mode=0o700)  # Set appropriate permissions

    # Download photos
    print("Downloading photos...")
    L.download_post(post, target=destination_folder)
    print("Download complete.")

    # Move files to format-specific folders
    files = os.listdir(destination_folder)
    jpg_files = [file for file in files if file.endswith(".jpg")]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file in jpg_files:
            file_path = os.path.join(destination_folder, file)
            format_folder = os.path.join(destination_folder, f"{username}_jpg")
            if not os.path.exists(format_folder):
                os.makedirs(format_folder, mode=0o700)  # Set appropriate permissions
            executor.submit(shutil.move, file_path, os.path.join(format_folder, file))

    # Ask the user if they want to delete certain files
    delete_files = input("Do you want to delete the .json.xz and .txt files? (y/n): ")
    if delete_files.lower() == "y":
        files = os.listdir(destination_folder)
        delete_extensions = (".json.xz", ".txt")
        delete_files = [file for file in files if file.endswith(delete_extensions)]
        for file in delete_files:
            file_path = os.path.join(destination_folder, file)
            os.remove(file_path)
            print(f"Deleted file: {file}")

except instaloader.exceptions.InstaloaderException as e:
    print(f"Error occurred: {e}")

import time
import os
import instaloader
import re
from tqdm import tqdm
from colorama import init, Fore, Style
import shutil
import logging
from PIL import Image
import concurrent.futures
BAR_FORMAT = Fore.YELLOW + '{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]' + Style.RESET_ALL

# Compile the regular expression for efficiency
file_extension_pattern = re.compile(r'\.(json\.xz|txt)$')

# Configure logging
logging.basicConfig(filename='download.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

def clean_url(url):
    """
    Cleans the URL by removing query parameters and replacing '=' with '/'
    """
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
    
    if not url:
        raise ValueError("URL cannot be empty")
    
    cleaned_url = re.sub(r'\?.*$', '', url)  # Remove everything after '?'
    cleaned_url = re.sub(r'=.*$', '/', cleaned_url)  # Replace '=' and everything after with '/'
    cleaned_url = cleaned_url.rstrip('/')  # Remove trailing '/'
    return cleaned_url + '/'


def get_profile_username(profile_url):
    """
    Extracts the username from the Instagram profile URL
    """
    match = re.search(r'instagram.com/([^/]+)', profile_url)
    if match:
        return match.group(1)
    return None

def download_post(loader, post, target_dir):
    """
    Downloads a single Instagram post using Instaloader library
    """
    try:
        loader.download_post(post, target=target_dir)
        logging.info(f"Downloaded post {post.url}")
    except instaloader.exceptions.PostException:
        logging.error(f"Failed to download post {post.url}")

def delete_files(target_dir):
    """
    Deletes JSON and TXT files in the target directory
    """
    while True:
        delete_files = input(Fore.GREEN + "Delete the JSON and TXT files in the target directory? (y/n): " + Style.RESET_ALL)
        if delete_files.lower() == 'y' or delete_files.lower() == 'n':
            break
        else:
            logging.error("Invalid input. Please enter 'y' or 'n'.")

    if delete_files.lower() == 'y':
        files_to_delete = [f for f in os.listdir(target_dir) if re.search(r'\.(json\.xz|txt)$', f)]
        for file in files_to_delete:
            try:
                os.remove(os.path.join(target_dir, file))
                logging.info(f"Deleted {file}")
            except FileNotFoundError:
                logging.error(f"File not found: {file}")
            except PermissionError:
                logging.error(f"Permission denied: {file}")
            except Exception as e:
                logging.error(f"Failed to delete {file}: {str(e)}")

def create_folder(target_dir, folder_name):
    """
    Creates a new folder in the target directory
    """
    folder_path = os.path.join(target_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    logging.info(f"Created folder {folder_name}")
    return folder_path

def move_file(source_path, target_dir):
    """
    Moves a file from source path to target directory
    """
    file_name = os.path.basename(source_path)
    target_path = os.path.join(target_dir, file_name)
    shutil.move(source_path, target_path)
    logging.info(f"Moved file {file_name} to {target_dir}")

def sort_files_by_format(target_dir, profile_username):
    """
    Sorts files in the target directory into subfolders based on their format
    """
    files = os.listdir(target_dir)
    for file in files:
        file_path = os.path.join(target_dir, file)
        if os.path.isfile(file_path):
            file_format = file.split('.')[-1]
            folder_name = f"{profile_username}_{file_format.upper()}"
            folder_path = create_folder(target_dir, folder_name)
            move_file(file_path, folder_path)

def remove_metadata(file_path):
    """
    Removes metadata from an image or movie file
    """
    try:
        image = Image.open(file_path)
        data = list(image.getdata())
        image_without_metadata = Image.new(image.mode, image.size)
        image_without_metadata.putdata(data)
        image_without_metadata.save(file_path)
        logging.info(f"Removed metadata from {file_path}")
    except Exception as e:
        logging.error(f"Failed to remove metadata from {file_path}: {str(e)}")

def download_instagram_posts():
    init()
    loader = instaloader.Instaloader()
    profile_url = input(Fore.GREEN + "Enter the User Profile URL: " + Style.RESET_ALL)
    
    logging.info("Cleaning the URL...")
    time.sleep(2)  # Simulating a delay for animation purposes
    
    cleaned_url = clean_url(profile_url)
    logging.info(f"Cleaned URL: {cleaned_url}")
    
    profile_username = get_profile_username(cleaned_url)
    
    if not profile_username:
        logging.error("Invalid profile URL")
        return
    
    target_dir = input(Fore.GREEN + "Enter the username you want to use for saving (press Enter for default username): " + Style.RESET_ALL)
    if not target_dir:
        target_dir = profile_username
    
    num_posts = input(Fore.GREEN + "Enter the number of posts to download (enter 'all' to download all posts): " + Style.RESET_ALL)
    if num_posts.lower() == 'all':
        num_posts = None
    else:
        try:
            num_posts = int(num_posts)
        except ValueError:
            logging.error("Invalid number of posts")
            return
    
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_username)
    except instaloader.exceptions.ProfileNotExistsException:
        logging.error("Invalid profile URL")
        return
    
    with tqdm(total=num_posts or profile.mediacount, bar_format=BAR_FORMAT) as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for post in profile.get_posts():
                if num_posts is not None and progress_bar.n >= num_posts:
                    break
                futures.append(executor.submit(download_post, loader, post, target_dir))
                progress_bar.update(1)
            try:
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
    
    delete_files(target_dir)
    
    sort_files_by_format(target_dir, profile_username)
    
    # Remove metadata from downloaded images and movies
    files = os.listdir(target_dir)
    for file in files:
        file_path = os.path.join(target_dir, file)
        if os.path.isfile(file_path):
            remove_metadata(file_path)

    logging.info("Download completed successfully!")

first_run = True

# Loop to ask the user if they want to do another download
while True:
    try:
        if not first_run:
            another_download = input(Fore.GREEN + "Do you want to do another download? (y/n): " + Style.RESET_ALL)
            if another_download.lower() != 'y':
                break
        download_instagram_posts()
        first_run = False
    except KeyboardInterrupt:
        logging.info("Program stopped by user.")
        break
    except FileNotFoundError as e:
        logging.error(f"File not found: {str(e)}")
        continue
    except PermissionError as e:
        logging.error(f"Permission denied: {str(e)}")
        continue
    def print_and_log(message, level=logging.INFO):
        print(message)
        logging.log(level, message)

    try:
        # Code that may raise an exception
        pass
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        continue

    # Usage example:
    print_and_log("Cleaning the URL...")

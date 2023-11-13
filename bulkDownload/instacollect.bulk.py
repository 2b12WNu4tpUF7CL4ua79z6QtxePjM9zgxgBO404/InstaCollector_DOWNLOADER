import time
import os
import instaloader
import re
from tqdm import tqdm
from colorama import init, Fore, Style
import shutil

BAR_FORMAT = Fore.YELLOW + '{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]' + Style.RESET_ALL

def clean_url(url):
    cleaned_url = re.sub(r'\?.*$', '', url)  # Remove everything after '?'
    cleaned_url = re.sub(r'=.*$', '/', cleaned_url)  # Replace '=' and everything after with '/'
    cleaned_url = cleaned_url.rstrip('/')  # Remove trailing '/'
    return cleaned_url + '/'

def get_profile_username(profile_url):
    match = re.search(r'instagram.com/([^/]+)', profile_url)
    if match:
        return match.group(1)
    return None

def download_post(loader, post, target_dir):
    try:
        loader.download_post(post, target=target_dir)
        print(Fore.GREEN + f"Downloaded post {post.url}" + Style.RESET_ALL)
    except instaloader.exceptions.PostException:
        print(Fore.RED + f"Failed to download post {post.url}" + Style.RESET_ALL)

def delete_files(target_dir):
    delete_files = input(Fore.GREEN + "Delete the JSON and TXT files in the target directory? (y/n): " + Style.RESET_ALL)
    if delete_files.lower() == 'y':
        files_to_delete = [f for f in os.listdir(target_dir) if re.search(r'\.(json\.xz|txt)$', f)]
        for file in files_to_delete:
            try:
                os.remove(os.path.join(target_dir, file))
                print(Fore.RED + f"Deleted {file}" + Style.RESET_ALL)
            except OSError:
                print(Fore.RED + f"Failed to delete {file}" + Style.RESET_ALL)

def create_folder(target_dir, folder_name):
    folder_path = os.path.join(target_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    print(Fore.GREEN + f"Created folder {folder_name}" + Style.RESET_ALL)
    return folder_path

def move_file(source_path, target_dir):
    file_name = os.path.basename(source_path)
    target_path = os.path.join(target_dir, file_name)
    shutil.move(source_path, target_path)
    print(Fore.GREEN + f"Moved file {file_name} to {target_dir}" + Style.RESET_ALL)

def sort_files_by_format(target_dir, profile_username):
    files = os.listdir(target_dir)
    for file in files:
        file_path = os.path.join(target_dir, file)
        if os.path.isfile(file_path):
            file_format = file.split('.')[-1]
            folder_name = f"{profile_username}_{file_format.upper()}"
            folder_path = create_folder(target_dir, folder_name)
            move_file(file_path, folder_path)

def download_instagram_posts():
    init()
    loader = instaloader.Instaloader()
    profile_url = input(Fore.GREEN + "Enter the User Profile URL: " + Style.RESET_ALL)
    
    print(Fore.YELLOW + "Cleaning the URL..." + Style.RESET_ALL)
    time.sleep(2)  # Simulating a delay for animation purposes
    
    cleaned_url = clean_url(profile_url)
    print(Fore.GREEN + f"Cleaned URL: {cleaned_url}" + Style.RESET_ALL)
    
    profile_username = get_profile_username(cleaned_url)
    
    if not profile_username:
        print(Fore.RED + "Invalid profile URL" + Style.RESET_ALL)
        return
    
    target_dir = input(Fore.GREEN + "Enter the folder name for downloads (default: profile username): " + Style.RESET_ALL) or profile_username
    
    num_posts = input(Fore.GREEN + "Enter the number of posts to download (default: all): " + Style.RESET_ALL)
    num_posts = int(num_posts) if num_posts.isdigit() else None
    
    try:
        profile = instaloader.Profile.from_username(loader.context, profile_username)
    except instaloader.exceptions.ProfileNotExistsException:
        print(Fore.RED + "Invalid profile URL" + Style.RESET_ALL)
        return
    
    with tqdm(total=num_posts or profile.mediacount, bar_format=BAR_FORMAT) as progress_bar:
        for post in profile.get_posts():
            download_post(loader, post, target_dir)
            
            progress_bar.update(1)
            if num_posts and progress_bar.n == num_posts:
                break
    
    delete_files(target_dir)
    
    sort_files_by_format(target_dir, profile_username)

    print(Fore.GREEN + "Download completed successfully!" + Style.RESET_ALL)

# Loop to ask the user if they want to do another download
while True:
    download_instagram_posts()
    another_download = input(Fore.GREEN + "Do you want to do another download? (y/n): " + Style.RESET_ALL)
    if another_download.lower() != 'y':
        break
        
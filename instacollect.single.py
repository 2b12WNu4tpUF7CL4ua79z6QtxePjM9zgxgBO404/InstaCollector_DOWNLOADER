# THIS FILE IS UNDER CONSTRUCTION AND MAY NOT WORK


# import necessary library
import instaloader
import os
 # create an instance of the Instaloader class
L = instaloader.Instaloader()
 # get the post URL from user input with error handling
while True:
    post_url = input("Enter post URL: ")
    if "instagram.com/p/" not in post_url:
        print("Invalid URL, please try again.")
        continue
    try:
        # get post details
        post = instaloader.Post.from_shortcode(L.context, post_url.split("/")[-2])
        break
    except instaloader.exceptions.InvalidArgumentException:
        print("Invalid URL, please try again.")
 # download the post and its photos with error handling
try:
    # get post details
    print("Getting post details...")
    post_details = post.__dict__
     # create destination folder if it does not exist
    destination_folder = "destination_folder"
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
     # download photos
    print("Downloading photos...")
    L.download_post(post, target=destination_folder)
    print("Download complete.")
except instaloader.exceptions.InstaloaderException as e:
    print(f"Error occurred: {e}")

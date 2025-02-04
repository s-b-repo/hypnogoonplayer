import os
import re
import requests
from bs4 import BeautifulSoup
import cv2
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

# Function to fetch all mp4 URLs from a given URL
def scrape_mp4_urls(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Enhanced regex to find mp4 URLs
        mp4_urls = []
        for match in re.finditer(r"(https?[^'\"]*\.mp4)", response.text):
            mp4_urls.append(match.group(0))
        
        return mp4_urls
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Function to download and optionally play an MP4 video
def process_video(video_url, save=False):
    try:
        if save:
            local_filename = video_url.split('/')[-1]
            with requests.get(video_url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Video saved as {local_filename}")
        
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            print(f"Could not open video: {video_url}")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Hypno Porn Player', frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):  # Press 'q' to exit
                break
        
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error processing video {video_url}: {e}")

# Main GUI Application
class HypnoPornApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hypno Porn Player")
        self.root.geometry("600x400")
        
        # Label
        tk.Label(root, text="Welcome to Hypno Porn Player", font=("Arial", 16)).pack(pady=10)
        
        # Site Entry
        tk.Label(root, text="Enter Website URL:").pack()
        self.site_entry = tk.Entry(root, width=50)
        self.site_entry.pack(pady=5)
        
        # Scrape Button
        tk.Button(root, text="Scrape Videos", command=self.scrape_videos).pack(pady=10)
        
        # Video List
        self.video_listbox = tk.Listbox(root, height=10, width=70)
        self.video_listbox.pack(pady=10)
        
        # Play Button
        tk.Button(root, text="Play Selected Video", command=self.play_selected_video).pack(pady=5)
        
        # Save Button
        tk.Button(root, text="Save Selected Video", command=self.save_selected_video).pack(pady=5)
    
    def scrape_videos(self):
        url = self.site_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a valid website URL.")
            return
        
        self.video_listbox.delete(0, tk.END)
        self.root.config(cursor="watch")
        self.root.update()
        
        # Fetch MP4 URLs in a separate thread
        threading.Thread(target=self._scrape_and_update, args=(url,)).start()
    
    def _scrape_and_update(self, url):
        urls = scrape_mp4_urls(url)
        if not urls:
            messagebox.showinfo("No Videos Found", f"No MP4 files found on {url}.")
        else:
            for i, url in enumerate(urls, start=1):
                self.video_listbox.insert(tk.END, f"{i}. {url}")
        
        self.root.config(cursor="")
    
    def play_selected_video(self):
        selected_index = self.video_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a video to play.")
            return
        
        video_url = self.video_listbox.get(selected_index[0]).split(". ")[1]
        threading.Thread(target=lambda: process_video(video_url)).start()
    
    def save_selected_video(self):
        selected_index = self.video_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a video to save.")
            return
        
        video_url = self.video_listbox.get(selected_index[0]).split(". ")[1]
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
        if not save_path:
            return
        
        threading.Thread(target=lambda: process_video(video_url, save=True)).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = HypnoPornApp(root)
    root.mainloop()

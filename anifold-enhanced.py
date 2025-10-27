#!/usr/bin/env python3
"""
AniFold - Anime Folder Icon Setter
Created by @bruuhim with ❤️
"""

import os
import sys
import webbrowser
import re
import random
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("❌ 'requests' required: pip install requests")
    sys.exit(1)

__version__ = "1.0.0"
__author__ = "@bruuhim"

# ANSI color codes
class Colors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Anime ASCII Art Banner
BANNER = f"""{Colors.PINK}
    ▄████████ ███▄▄▄▄    ▄█     █▄     ▄████████  ▄██████▄   ▄█        ████████▄  
   ███    ███ ███▀▀▀██▄ ███     ███   ███    ███ ███    ███ ███        ███   ▀███ 
   ███    ███ ███   ███ ███     ███   ███    █▀  ███    ███ ███        ███    ███ 
   ███    ███ ███   ███ ███     ███  ▄███▄▄▄     ███    ███ ███        ███    ███ 
 ▀███████████ ███   ███ ███     ███ ▀▀███▀▀▀     ███    ███ ███        ███    ███ 
   ███    ███ ███   ███ ███     ███   ███        ███    ███ ███        ███    ███ 
   ███    ███ ███   ███ ███ ▄█▄ ███   ███        ███    ███ ███▌    ▄  ███   ▄███ 
   ███    █▀   ▀█   █▀   ▀███▀███▀    ███         ▀██████▀  █████▄▄██  ████████▀  
                                                             ▀                      
{Colors.CYAN}          Set custom anime folder icons from DeviantArt! 🎨{Colors.RESET}
"""

# Fun anime quotes/easter eggs
ANIME_QUOTES = [
    "🌸 'Believe in the me that believes in you!' - Kamina",
    "⚡ 'I'll take a potato chip... and EAT IT!' - Light Yagami",
    "🔥 'Plus Ultra!' - All Might",
    "✨ 'People die when they are killed!' - Shirou Emiya",
    "💪 'Omae wa mou shindeiru.' - Kenshiro",
    "🎌 'The world isn't perfect, but it's there for us trying the best it can.' - Roy Mustang",
    "🌟 'If you don't take risks, you can't create a future!' - Monkey D. Luffy"
]

COMMON_INDICATORS = {
    '1080p', '720p', '480p', '2160p', '4k', 'bluray', 'web', 'dvd', 'hd', 'x264', 'x265',
    'h264', 'h265', 'avc', 'hevc', 'aac', 'ac3', 'dts', 'flac', 'proper', 'repack',
    'dual', 'audio', 'multi', 'subs', 'sub', 'eng', 'en', 'ar', 'ara', 'fre', 'fr', 'de',
    'ger', 'ita', 'es', 'spa', 'kor', 'jpn', 'ch', 'chs', 'cht', 'sdh', 'hc', 'remux',
    'bit', '10bit', '8bit', 'flac5', 'flac8', 'hi10p', 'season'
}

def show_banner():
    """Display anime ASCII art banner"""
    print(BANNER)
    quote = random.choice(ANIME_QUOTES)
    print(f"{Colors.YELLOW}{quote}{Colors.RESET}\n")

def get_working_dir():
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return sys.argv[1]
    return os.getcwd()

def clean_anime_name(folder_name, max_words=5):
    folder_name = re.sub(r'\[.*?\]|\(.*?\)', '', folder_name)
    folder_name = re.sub(r'\.[a-zA-Z0-9]{2,4}$', '', folder_name)
    parts = re.split(r'[._\-\s]+', folder_name)
    clean = [
        part for part in parts
        if part and not part.isdigit() and part.lower() not in COMMON_INDICATORS
        and not re.match(r'^(19|20)\d{2}$', part) and not part.startswith('-')
    ]
    if clean:
        return ' '.join(clean[:max_words]).title().strip()
    return os.path.basename(folder_name)

def search_mal_anime(query):
    try:
        url = f"https://api.jikan.moe/v4/anime?q={query}&type=tv&limit=10"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get('data', [])
        
        # Filter: only aired/airing anime
        current_year = datetime.now().year
        filtered = []
        seen = set()
        
        for anime in results:
            title = anime.get('title', '')
            status = anime.get('status', '')
            year = anime.get('year')
            
            if status == 'Not yet aired':
                continue
            if year and year > current_year:
                continue
            
            if title not in seen:
                seen.add(title)
                filtered.append(anime)
                if len(filtered) >= 3:
                    break
        
        return filtered
    except Exception as e:
        print(f"{Colors.RED}⚠️  MAL error: {e}{Colors.RESET}")
        return []

def get_anime_name_from_mal(guess):
    print(f"\n{Colors.CYAN}🔍 Searching MAL for: '{guess}'...{Colors.RESET}")
    results = search_mal_anime(guess)
    
    if not results:
        print(f"{Colors.RED}❌ No results! Using best guess.{Colors.RESET}\n")
        return guess
    
    if len(results) == 1:
        title = results[0]['title']
        year = results[0].get('year', '')
        year_str = f" ({year})" if year else ""
        print(f"{Colors.GREEN}✨ Found: {title}{year_str}{Colors.RESET}\n")
        return title
    
    print(f"\n{Colors.YELLOW}🎯 Found {len(results)} results:{Colors.RESET}")
    for idx, anime in enumerate(results, 1):
        title = anime.get('title', 'Unknown')
        year = anime.get('year', '')
        score = anime.get('score', 0)
        year_str = f" {Colors.CYAN}({year}){Colors.RESET}" if year else ""
        score_str = f" {Colors.YELLOW}⭐{score}{Colors.RESET}" if score else ""
        print(f"  {Colors.BOLD}{idx}.{Colors.RESET} {title}{year_str}{score_str}")
    
    choice = input(f"\n{Colors.PINK}👉 Choose (Enter for #1): {Colors.RESET}").strip()
    
    if not choice:
        return results[0]['title']
    elif choice.isdigit() and 1 <= int(choice) <= len(results):
        return results[int(choice) - 1]['title']
    else:
        return results[0]['title']

def search_deviantart(anime_name):
    search_query = f"{anime_name} icon"
    url = f"https://www.deviantart.com/search?q={search_query.replace(' ', '+')}"
    print(f"\n{Colors.BLUE}🎨 Opening DeviantArt...{Colors.RESET}")
    webbrowser.open_new_tab(url)

def find_latest_icon(icon_dir):
    icon_dir = Path(icon_dir)
    icon_dir.mkdir(exist_ok=True)
    ico_files = list(icon_dir.glob("*.ico"))
    if not ico_files:
        print(f"{Colors.RED}❌ No icons in: {icon_dir}{Colors.RESET}")
        return None
    latest = max(ico_files, key=lambda f: f.stat().st_mtime)
    print(f"{Colors.GREEN}📦 Using: {latest.name}{Colors.RESET}")
    return str(latest)

def apply_folder_icon(icon_path):
    current_dir = Path.cwd()
    desktop_ini = current_dir / "desktop.ini"
    icon_abs = Path(icon_path).resolve()
    
    ini_content = f"""[.ShellClassInfo]
IconResource={icon_abs},0
IconFile={icon_abs}
IconIndex=0
ConfirmFileOp=0
[ViewState]
Mode=
Vid=
FolderType=Generic
Logo={icon_abs}
"""
    
    try:
        if desktop_ini.exists():
            os.system(f'attrib -h -s -r "{desktop_ini}" >nul 2>&1')
            desktop_ini.unlink()
        
        with open(desktop_ini, 'w', encoding='utf-8') as f:
            f.write(ini_content)
        
        os.system(f'attrib +h +s "{desktop_ini}" >nul 2>&1')
        os.system(f'attrib +r "{current_dir}" >nul 2>&1')
        
        print(f"\n{Colors.GREEN}✅ Icon applied!{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Refresh: Press F5 or restart Explorer via Task Manager{Colors.RESET}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False

def show_success_art():
    """Easter egg success banner"""
    art = f"""{Colors.GREEN}
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║      SUCCESS! FOLDER UPGRADED!        ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    {Colors.RESET}"""
    print(art)

def main():
    show_banner()
    
    print(f"{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🎌  AniFold v{__version__} - Anime Folder Icon Setter  🎌{Colors.RESET}")
    print(f"{Colors.YELLOW}    Created by {__author__} with ❤️{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.RESET}")
    
    os.chdir(get_working_dir())
    folder_name = os.path.basename(os.getcwd())
    guess = clean_anime_name(folder_name)
    
    anime_name = get_anime_name_from_mal(guess)
    
    print(f"{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.RESET}")
    search_deviantart(anime_name)
    
    icon_dir = r"C:\AniFold\icons"
    print(f"{Colors.CYAN}📂 Save icon to: {icon_dir}{Colors.RESET}\n")
    input(f"{Colors.YELLOW}⏸️  Press ENTER when downloaded...{Colors.RESET}")
    
    icon = find_latest_icon(icon_dir)
    if icon:
        if apply_folder_icon(icon):
            show_success_art()
        else:
            print(f"\n{Colors.RED}💥 Oops! Something went wrong.{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ No icon found. Did you download it?{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.RESET}")
    input(f"{Colors.CYAN}✨ Press ENTER to exit...{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Sayonara!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.RESET}")
        input("Press ENTER to exit...")

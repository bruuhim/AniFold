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
import argparse
import json
import hashlib
import time
import struct
from pathlib import Path
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("❌ 'requests' required: pip install requests")
    sys.exit(1)

__version__ = "2.0.0"
__author__ = "@bruuhim"

# ANSI color codes for terminal output
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
    "🌟 'If you don't take risks, you can't create a future!' - Monkey D. Luffy",
    "🌙 'Power isn't determined by your size, but how much you extend yourself.' - One Piece",
    "🔮 'A lesson without pain is meaningless.' - Edward Elric",
    "⚔️ 'The blade is me, and I am the blade.' - Ichigo Kurosaki",
    "🍜 'Grab your chopsticks and let's eat!' - Naruto Uzumaki",
    "🎭 'I am the bone of my sword.' - Archer",
    "🌌 'In this world, wherever there is light, there are also shadows.' - Lelouch",
    "🐉 'This is my ninja way!' - Rock Lee",
    "💎 'The power to be strong and having the will to use it... that's what makes a real hero.' - Midoriya",
    "🎨 'Art is a explosion!' - Sebastian Michaelis"
]

COMMON_INDICATORS = {
    '1080p', '720p', '480p', '2160p', '4k', 'bluray', 'web', 'dvd', 'hd', 'x264', 'x265',
    'h264', 'h265', 'avc', 'hevc', 'aac', 'ac3', 'dts', 'flac', 'proper', 'repack',
    'dual', 'audio', 'multi', 'subs', 'sub', 'eng', 'en', 'ar', 'ara', 'fre', 'fr', 'de',
    'ger', 'ita', 'es', 'spa', 'kor', 'jpn', 'ch', 'chs', 'cht', 'sdh', 'hc', 'remux',
    'bit', '10bit', '8bit', 'flac5', 'flac8', 'hi10p', 'season'
}

# Configuration defaults
DEFAULT_CONFIG = {
    'icon_dir': r"C:\AniFold\icons",
    'cache_file': str(Path.home() / '.anifold_cache.json'),
    'cache_ttl_hours': 24,
    'max_retries': 3,
    'retry_delay': 2
}

def show_banner():
    """Display anime ASCII art banner with random quote"""
    print(BANNER)
    quote = random.choice(ANIME_QUOTES)
    print(f"{Colors.YELLOW}{quote}{Colors.RESET}\n")

def get_working_dir():
    """Get working directory from command line argument or current directory"""
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return sys.argv[1]
    return os.getcwd()

def clean_anime_name(folder_name, max_words=5):
    """Clean messy folder names to extract anime names.

    Removes brackets, extensions, quality indicators, years, and common release keywords.
    Focuses on actual anime title words.

    Args:
        folder_name: Raw folder name string
        max_words: Maximum words to include in cleaned name

    Returns:
        Cleaned anime name suitable for MAL search
    """
    # Remove brackets and parentheses (often contain quality info)
    folder_name = re.sub(r'\[.*?\]|\(.*?\)', '', folder_name)
    # Remove file extensions
    folder_name = re.sub(r'\.[a-zA-Z0-9]{2,4}$', '', folder_name)
    # Split on common separators
    parts = re.split(r'[._\-\s]+', folder_name)
    # Filter out unwanted parts
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

def setup_logging(log_file):
    """Set up logging to file and console"""
    import logging

    # Create logger
    logger = logging.getLogger('anifold')
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

def load_cache(cache_file):
    """Load MAL cache from file"""
    try:
        if Path(cache_file).exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_cache(cache_data, cache_file):
    """Save MAL cache to file"""
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Cache save failed: {e}{Colors.RESET}")

def get_mal_cache_key(query):
    """Generate cache key for MAL query"""
    return hashlib.md5(query.lower().strip().encode()).hexdigest()

def search_mal_anime_cached(query, cache_file, cache_ttl_hours, logger=None):
    """Search MAL with caching support"""
    cache_key = get_mal_cache_key(query)
    cache = load_cache(cache_file)
    now = datetime.now()

    # Check cache
    if cache_key in cache:
        cache_entry = cache[cache_key]
        cache_time = datetime.fromisoformat(cache_entry['timestamp'])
        if now - cache_time < timedelta(hours=cache_ttl_hours):
            if logger:
                logger.info(f"Cache hit for '{query}'")
            return cache_entry['results']

    # Cache miss, fetch from API
    if logger:
        logger.info(f"Cache miss for '{query}', fetching from API")
    results = search_mal_anime(query)

    # Save to cache
    cache[cache_key] = {
        'timestamp': now.isoformat(),
        'query': query,
        'results': results
    }
    save_cache(cache, cache_file)

    return results

def validate_ico_file(file_path):
    """Validate if file is a valid .ico file by checking header"""
    try:
        with open(file_path, 'rb') as f:
            # Read ICO header (6 bytes)
            header = f.read(6)
            if len(header) < 6:
                return False

            # Check signature (0,1) and type (1,2)
            reserved, ico_type = struct.unpack('<HH', header[:4])
            if reserved != 0 or ico_type != 1:
                return False

            # ICO files should have at least 1 icon
            num_icons = struct.unpack('<H', header[4:6])[0]
            return num_icons > 0
    except Exception:
        return False

def retry_with_backoff(func, max_retries, delay, *args, **kwargs):
    """Retry a function with exponential backoff"""
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries:
                raise e
            wait_time = delay * (2 ** attempt)  # Exponential backoff
            print(f"{Colors.YELLOW}⚠️  Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...{Colors.RESET}")
            time.sleep(wait_time)

def process_anime_folder(folder_path, args, logger=None):
    """Process a single anime folder"""
    folder_path = Path(folder_path)

    if logger:
        logger.info(f"Processing folder: {folder_path}")

    try:
        # Change to folder
        original_cwd = os.getcwd()
        os.chdir(folder_path)

        folder_name = folder_path.name
        guess = clean_anime_name(folder_name)

        print(f"\n{Colors.BOLD}{Colors.PINK}🎬 Processing: {folder_name}{Colors.RESET}")
        print(f"{Colors.CYAN}💭 Guess: '{guess}'{Colors.RESET}")

        # Get anime name from MAL
        anime_name = get_anime_name_from_mal_auto(guess, args, logger)

        if not anime_name:
            print(f"{Colors.RED}❌ Could not determine anime name, skipping...{Colors.RESET}")
            return False

        # Track icons before download to only use newly downloaded ones for this anime
        import time
        before_time = time.time()
        existing_icons = {f.name for f in Path(args.icon_dir).glob("*.ico") if f.is_file()}
        existing_mtimes = {f.name: f.stat().st_mtime for f in Path(args.icon_dir).glob("*.ico") if f.is_file()}

        # Search DeviantArt
        if not args.dry_run:
            search_deviantart(anime_name)

        # Icon handling
        if args.no_wait:
            print(f"{Colors.YELLOW}⏯️  Continuing without waiting...{Colors.RESET}")
        elif not args.dry_run:
            print(f"{Colors.CYAN}📂 Save icon to: {args.icon_dir}{Colors.RESET}")
            input(f"{Colors.YELLOW}⏸️  Press ENTER when downloaded...{Colors.RESET}")

        icon_path = find_new_valid_icon(args.icon_dir, existing_icons, before_time)

        if icon_path and not args.dry_run:
            if apply_folder_icon(icon_path):
                show_success_art()
                if logger:
                    logger.info(f"Successfully applied icon to {folder_path}")
                return True
            else:
                print(f"{Colors.RED}❌ Icon application failed{Colors.RESET}")
                if logger:
                    logger.error(f"Icon application failed for {folder_path}")
                return False
        elif args.dry_run:
            print(f"{Colors.GREEN}✅ Dry run complete for: {anime_name}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ No valid icon found, skipping...{Colors.RESET}")
            if logger:
                logger.warning(f"No valid icon found for {folder_path}")
            return False

    except Exception as e:
        print(f"{Colors.RED}❌ Error processing {folder_path}: {e}{Colors.RESET}")
        if logger:
            logger.error(f"Error processing {folder_path}: {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(original_cwd)

def get_anime_name_from_mal_auto(guess, args, logger=None):
    """Get anime name from MAL with auto-selection"""
    if args.auto_select:
        if logger:
            logger.info(f"Auto-selecting for '{guess}'")
        results = retry_with_backoff(
            search_mal_anime_cached,
            args.max_retries,
            args.retry_delay,
            guess,
            args.cache_file,
            args.cache_ttl_hours,
            logger
        )
        if results:
            print(f"{Colors.GREEN}✨ Auto-selected: {results[0]['title']}{Colors.RESET}")
            return results[0]['title']
        else:
            return guess
    else:
        return get_anime_name_from_mal(guess)

def find_new_valid_icon(icon_dir, existing_icons, before_time):
    """Find the latest valid .ico file among newly downloaded ones"""
    icon_dir = Path(icon_dir)
    icon_dir.mkdir(exist_ok=True)

    ico_files = list(icon_dir.glob("*.ico"))
    if not ico_files:
        print(f"{Colors.RED}❌ No .ico files found in: {icon_dir}{Colors.RESET}")
        print(f"{Colors.RED}❌ Did you download an icon for this anime?{Colors.RESET}")
        return None

    # Filter to only new icons (not in existing_icons set or modified after before_time)
    new_ico_files = [f for f in ico_files if f.name not in existing_icons or f.stat().st_mtime > before_time]

    if not new_ico_files:
        print(f"{Colors.RED}❌ No new icons downloaded - all existing icons are from previous sessions{Colors.RESET}")
        print(f"{Colors.RED}❌ Please download an icon for this anime to continue{Colors.RESET}")
        return None

    # Sort by modification time (newest first)
    new_ico_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    # Try to find a valid ICO file among new ones
    for ico_file in new_ico_files:
        if validate_ico_file(ico_file):
            print(f"{Colors.GREEN}📦 Using newly downloaded: {ico_file.name}{Colors.RESET}")
            return str(ico_file)
        else:
            print(f"{Colors.YELLOW}⚠️  Skipping invalid ICO: {ico_file.name}{Colors.RESET}")

    print(f"{Colors.RED}❌ No valid icons found among newly downloaded files{Colors.RESET}")
    return None


def find_valid_icon(icon_dir):
    """Find the latest valid .ico file in directory"""
    icon_dir = Path(icon_dir)
    icon_dir.mkdir(exist_ok=True)

    ico_files = list(icon_dir.glob("*.ico"))
    if not ico_files:
        print(f"{Colors.RED}❌ No .ico files in: {icon_dir}{Colors.RESET}")
        return None

    # Sort by modification time (newest first)
    ico_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    # Try to find a valid ICO file
    for ico_file in ico_files:
        if validate_ico_file(ico_file):
            print(f"{Colors.GREEN}📦 Using: {ico_file.name}{Colors.RESET}")
            return str(ico_file)
        else:
            print(f"{Colors.YELLOW}⚠️  Skipping invalid ICO: {ico_file.name}{Colors.RESET}")

    print(f"{Colors.RED}❌ No valid .ico files found{Colors.RESET}")
    return None

def show_progress_bar(current, total, prefix="Progress", suffix="Complete", length=40):
    """Display a progress bar"""
    percent = int(100 * (current / float(total)) if total > 0 else 100)
    filled_length = int(length * current // total) if total > 0 else length
    bar = '█' * filled_length + '░' * (length - filled_length)
    print(f'\r{Colors.BOLD}{Colors.CYAN}{prefix}: |{bar}| {percent}% {suffix}{Colors.RESET}', end='', flush=True)
    if current == total:
        print()  # New line when complete

def show_celebration(success_count, total_count):
    """Show fun celebration message based on results"""
    success_rate = success_count / total_count if total_count > 0 else 0

    if success_rate >= 0.9:
        celebration = f"{Colors.GREEN}🏆 Perfect! All folders upgraded! 🏆"
    elif success_rate >= 0.7:
        celebration = f"{Colors.GREEN}🎯 Great job! Mission accomplished! 🎯"
    elif success_rate >= 0.5:
        celebration = f"{Colors.YELLOW}💪 Good work! Halfway to greatness! 💪"
    elif success_rate > 0:
        celebration = f"{Colors.YELLOW}🔥 You're on fire! Keep going! 🔥"
    else:
        celebration = f"{Colors.RED}😅 Don't worry, we can try again! 😅"

    return celebration

def scan_library(library_path, args, logger=None):
    """Scan library folder for anime subdirectories"""
    library_path = Path(library_path)

    if not library_path.exists():
        print(f"{Colors.RED}❌ Library path does not exist: {library_path}{Colors.RESET}")
        return

    if logger:
        logger.info(f"Scanning library: {library_path}")

    print(f"\n{Colors.BOLD}{Colors.CYAN}📚 Scanning library: {library_path}{Colors.RESET}")
    print(f"{Colors.CYAN}🔍 Detecting anime folders...{Colors.RESET}")

    # Find subdirectories
    try:
        subdirs = [d for d in library_path.iterdir() if d.is_dir()]
    except PermissionError:
        print(f"{Colors.RED}❌ Cannot access directory: {library_path}{Colors.RESET}")
        return

    total_folders = len(subdirs)
    processed = 0
    successful = 0

    if total_folders == 0:
        print(f"{Colors.YELLOW}📂 No subdirectories found. This might not be a library folder.{Colors.RESET}")
        return

    anime_folders = [d for d in subdirs if looks_like_anime_folder(d.name)]
    other_folders = [d for d in subdirs if not looks_like_anime_folder(d.name)]

    print(f"{Colors.GREEN}📂 Found {total_folders} total folders{Colors.RESET}")
    print(f"{Colors.GREEN}🎬 Detected {len(anime_folders)} anime-like folders{Colors.RESET}")

    if len(anime_folders) == 0:
        print(f"{Colors.YELLOW}⚠️  No anime folders detected. Maybe try running with --single flag?{Colors.RESET}")
        return

    print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 Starting batch processing...{Colors.RESET}")

    # Process anime folders
    for i, subdir in enumerate(anime_folders, 1):
        show_progress_bar(i-1, len(anime_folders), f"🔄 Processing {subdir.name[:20]}", f"({i}/{len(anime_folders)})")

        result = process_anime_folder(subdir, args, logger)
        processed += 1

        if result:
            successful += 1

    # Final progress bar
    show_progress_bar(len(anime_folders), len(anime_folders), "✅ All Done", "")

    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")

    # Fun results celebration
    celebration = show_celebration(successful, len(anime_folders))
    print(f"{Colors.BOLD}{celebration}{Colors.RESET}")

    print(f"{Colors.BOLD}{Colors.GREEN}📊 Results: {successful}/{len(anime_folders)} anime folders processed successfully{Colors.RESET}")

    if other_folders:
        print(f"{Colors.CYAN}ℹ️  Skipped {len(other_folders)} non-anime folders{Colors.RESET}")

    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")

    if logger:
        logger.info(f"Library scan complete: {successful}/{len(anime_folders)} successful")

def detect_operation_mode():
    """Auto-detect if current directory is a library or single anime folder"""
    current_dir = Path.cwd()
    video_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}

    # Count different types of items
    subdirs = []
    video_files = []

    try:
        for item in current_dir.iterdir():
            if item.is_dir():
                subdirs.append(item)
            elif item.suffix.lower() in video_extensions:
                video_files.append(item)
    except PermissionError:
        # If we can't read the directory, assume single folder mode
        return 'single'

    # Decision logic
    anime_like_subdirs = [d for d in subdirs if looks_like_anime_folder(d.name)]

    if len(anime_like_subdirs) >= 3 and len(video_files) <= 2:
        # Multiple anime folders, few videos = likely library
        return 'library'
    elif len(subdirs) >= 3 and len(video_files) == 0:
        # Many subdirs, no videos = likely library
        return 'library'
    elif len(video_files) >= 3:
        # Many video files = likely single anime folder
        return 'single'
    else:
        # Default to single folder for ambiguous cases
        return 'single'

def looks_like_anime_folder(folder_name):
    """Check if folder name looks like an anime folder"""
    # Common anime naming patterns
    name = clean_anime_name(folder_name)

    # If cleaning process significantly changed the name, it's likely anime
    if len(name) < len(folder_name) * 0.7:
        return True

    # Check for season indicators
    if re.search(r'season\s*\d+', folder_name, re.IGNORECASE):
        return True

    # Check for common anime patterns
    anime_indicators = ['season', 'ep', 'episode', 's01', 's02', 's03']
    if any(indicator in folder_name.lower() for indicator in anime_indicators):
        return False  # These are likely episode folders inside anime folders

    # If name has numbers and is reasonably long, likely anime
    if len(name) >= 3 and any(char.isdigit() for char in folder_name):
        return True

    return False

def parse_windows_path(path_string):
    """Parse Windows paths, handling quotes and spaces properly"""
    if not path_string:
        return None

    # Remove surrounding quotes if present
    path_string = path_string.strip('"\'')

    # Convert to Path object and resolve
    path = Path(path_string)

    # Check if path exists and is a directory
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Path does not exist: {path}")
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"Path is not a directory: {path}")

    return str(path)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="🎌 AniFold - Anime Folder Icon Setter from DeviantArt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  anifold.py                                    # Auto-detect single/library mode
  anifold.py --library "D:\\Anime Collection"   # Force library mode
  anifold.py --single                           # Force single folder mode
  anifold.py --auto-select --no-wait           # Batch processing
  anifold.py --dry-run                         # Preview without changes

💡 Tip: For paths with spaces, use quotes: --library "D:\\My Anime"
        """
    )

    parser.add_argument(
        '--library', '-l',
        type=parse_windows_path,
        help='Path to anime library folder (scans all subdirectories)'
    )

    parser.add_argument(
        '--single',
        action='store_true',
        help='Force single folder mode (process current directory only)'
    )

    parser.add_argument(
        '--icon-dir',
        type=str,
        default=DEFAULT_CONFIG['icon_dir'],
        help=f'Icon directory path (default: {DEFAULT_CONFIG["icon_dir"]})'
    )

    parser.add_argument(
        '--auto-select',
        action='store_true',
        help='Automatically select first MAL result (for batch processing)'
    )

    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='Skip ENTER prompts and continue immediately'
    )

    parser.add_argument(
        '--log',
        type=str,
        help='Log operations to specified file'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    parser.add_argument(
        '--cache-file',
        type=str,
        default=DEFAULT_CONFIG['cache_file'],
        help=f'MAL cache file (default: {DEFAULT_CONFIG["cache_file"]})'
    )

    parser.add_argument(
        '--cache-ttl-hours',
        type=int,
        default=DEFAULT_CONFIG['cache_ttl_hours'],
        help=f'Cache TTL in hours (default: {DEFAULT_CONFIG["cache_ttl_hours"]})'
    )

    parser.add_argument(
        '--max-retries',
        type=int,
        default=DEFAULT_CONFIG['max_retries'],
        help=f'Max API retry attempts (default: {DEFAULT_CONFIG["max_retries"]})'
    )

    parser.add_argument(
        '--retry-delay',
        type=int,
        default=DEFAULT_CONFIG['retry_delay'],
        help=f'Base retry delay in seconds (default: {DEFAULT_CONFIG["retry_delay"]})'
    )

    return parser.parse_args()

def main():
    """Main application entry point"""
    show_banner()

    # Parse arguments
    try:
        args = parse_arguments()
    except SystemExit:
        # Help shown, exit gracefully
        return

    print(f"{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🎌  AniFold v{__version__} - Anime Folder Icon Setter  🎌{Colors.RESET}")
    print(f"{Colors.YELLOW}    Created by {__author__} with ❤️{Colors.RESET}")

    if args.dry_run:
        print(f"{Colors.YELLOW}🔍 DRY RUN MODE - No changes will be made{Colors.RESET}")

    if args.icon_dir != DEFAULT_CONFIG['icon_dir']:
        print(f"{Colors.CYAN}📂 Custom icon directory: {args.icon_dir}{Colors.RESET}")

    print(f"{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.RESET}")

    # Setup logging
    logger = setup_logging(args.log)

    try:
        if args.library:
            # Explicit library mode
            print(f"{Colors.BLUE}🔧 Library mode: Processing {args.library}{Colors.RESET}")
            scan_library(args.library, args, logger)
        elif args.single:
            # Explicit single folder mode
            print(f"{Colors.BLUE}🔧 Single folder mode: Processing current directory{Colors.RESET}")
            current_dir = Path.cwd()
            process_anime_folder(current_dir, args, logger)
        else:
            # Auto-detection mode
            print(f"{Colors.CYAN}🔮 Auto-detecting folder type...{Colors.RESET}")
            detected_mode = detect_operation_mode()

            if detected_mode == 'library':
                print(f"{Colors.GREEN}📚 Detected library folder! Processing all subdirectories...{Colors.RESET}")
                current_dir = Path.cwd()
                scan_library(current_dir, args, logger)
            else:
                print(f"{Colors.GREEN}🎬 Detected single anime folder! Processing current directory...{Colors.RESET}")
                current_dir = Path.cwd()
                process_anime_folder(current_dir, args, logger)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Sayonara!{Colors.RESET}")
        if logger:
            logger.info("Application interrupted by user")
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.RESET}")
        if logger:
            logger.error(f"Unexpected error: {e}", exc_info=True)

    if logger:
        logger.info("Application finished")

    # Always wait for user input to review results (unless dry-run in auto-select mode)
    if not (args.dry_run and args.auto_select):
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        try:
            input(f"{Colors.GREEN}✨ Press ENTER to exit...{Colors.RESET}")
        except EOFError:
            # Handle cases where input is not available (like in some automated scripts)
            pass
    else:
        print(f"\n{Colors.YELLOW}🔄 Dry run completed automatically{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Sayonara!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.RESET}")
        input("Press ENTER to exit...")

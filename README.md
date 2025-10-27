# 🎌 AniFold

**Anime folder icons from DeviantArt, automatically.**

Give your anime collection that *main character energy* with custom folder icons powered by MyAnimeList and DeviantArt!

Created by [@bruuhim](https://github.com/bruuhim) with ❤️

---

## ✨ Features

- 🔍 **Smart Anime Detection** - Cleans up messy folder names (goodbye `1080p.BluRay.x265.YURASUKA`)
- 🌐 **MyAnimeList Integration** - Auto-searches MAL for accurate anime titles
- 📚 **Library Scan Mode** - Process entire anime collections with `--library` flag
- 🎨 **DeviantArt Search** - Opens DeviantArt with pre-filled icon search
- 🖼️ **Auto Icon Selection** - Grabs the latest downloaded icon automatically with validation
- ⚡ **Batch Processing** - `--auto-select` and `--no-wait` for automated workflows
- 📝 **Logging & Caching** - Optional logging and MAL response caching for efficiency
- 🎌 **Fun Anime UI** - ASCII art, 16 random anime quotes, and colorful terminal output
- ⭐ **MAL Scores** - Shows anime ratings to help you pick the right one
- 🔄 **Retry Logic** - Automatic retries with exponential backoff for network failures
- 🎭 **Dry Run Mode** - Preview what will happen without making changes

---

## 🚀 Quick Start

### Method 1: Download EXE (Easiest)

1. Download `AniFold.exe` from [Releases](https://github.com/bruuhim/AniFold/releases)
2. Run it inside any anime folder
3. Choose your anime from MAL results
4. Download an `.ico` file from DeviantArt to `C:\AniFold\icons`
5. Press Enter and enjoy your new folder icon!

### Method 2: Run from Source

```bash
# Clone the repo
git clone https://github.com/bruuhim/AniFold.git
cd AniFold

# Install dependencies
pip install requests

# Run it (auto-detects single folder or library)
python anifold.py
```

### Method 3: Advanced Usage

```bash
# Process entire anime library
python anifold.py --library "D:\Anime Collection"

# Batch mode with auto-selection
python anifold.py --library "D:\Anime" --auto-select --no-wait --log batch.log
```

---

## 📋 Command Line Options

AniFold supports various CLI options for flexible usage:

```
usage: anifold.py [-h] [--library LIBRARY] [--single] [--icon-dir ICON_DIR]
                  [--auto-select] [--no-wait] [--log LOG] [--dry-run]
                  [--cache-file CACHE_FILE] [--cache-ttl-hours CACHE_TTL_HOURS]
                  [--max-retries MAX_RETRIES] [--retry-delay RETRY_DELAY]

🎌 AniFold - Anime Folder Icon Setter from DeviantArt

optional arguments:
  -h, --help            show this help message and exit
  -l LIBRARY, --library LIBRARY
                        Path to anime library folder (scans all subdirectories)
  --icon-dir ICON_DIR   Icon directory path (default: C:\AniFold\icons)
  --auto-select         Automatically select first MAL result (for batch processing)
  --no-wait             Skip ENTER prompts and continue immediately
  --log LOG             Log operations to specified file
  --dry-run             Show what would be done without making changes
  --cache-file CACHE_FILE
                        MAL cache file (default: C:\Users\<user>\.anifold_cache.json)
  --cache-ttl-hours CACHE_TTL_HOURS
                        Cache TTL in hours (default: 24)
  --max-retries MAX_RETRIES
                        Max API retry attempts (default: 3)
  --retry-delay RETRY_DELAY
                        Base retry delay in seconds (default: 2)
```

### Common Usage Examples

```bash
# Basic usage (auto-detects single folder or library)
python anifold.py

# Scan entire library
python anifold.py --library "D:\My Anime Collection"

# Batch processing with no interaction needed
python anifold.py --library "D:\Anime" --auto-select --no-wait

# Preview mode (dry run)
python anifold.py --library "D:\Anime" --dry-run

# Force single folder processing
python anifold.py --single

# Custom icon directory
python anifold.py --icon-dir "C:\My Icons" --library "D:\Anime"

# With logging for troubleshooting
python anifold.py --library "D:\Anime" --log process.log

# Full automation with all options
python anifold.py --library "D:\Anime" --auto-select --no-wait --log batch.log --icon-dir "C:\AnimeIcons" --max-retries 5
```

---

## 📖 How It Works

1. **Detects anime name** from your messy folder name
   - `Goblin.Slayer.S01.1080p.BluRay.x265-YURASUKA` → `Goblin Slayer`

2. **Searches MyAnimeList** for accurate titles
   - Shows top 3 results with years and ratings
   - Filters out unreleased anime

3. **Opens DeviantArt** with icon search
   - Search: `[anime name] icon`

4. **You download** your favorite `.ico` file to `C:\AniFold\icons`

5. **Auto-applies** the latest icon to your folder
   - Creates `desktop.ini` with proper Windows attributes

6. **Refresh Explorer** (F5) to see your new icon!

---

## 🛠️ Building from Source

Want to build your own EXE?

```bash
# Install PyInstaller
pip install pyinstaller requests

# Build with logo
pyinstaller --onefile --icon=anifold.ico --name=AniFold anifold.py

# Your EXE will be in dist/AniFold.exe
```

---

## ❓ Troubleshooting

### Icon doesn't show up?

- Press `F5` in Windows Explorer to refresh
- Restart Explorer via Task Manager
- Wait 2-5 minutes for Windows to index the icon

### Icon disappeared after moving/compressing folder?

Right-click folder → **Properties** → **Customize** → Click **OK**

### How do I remove icons?

Delete these files from the folder (enable "Show hidden files"):
- `desktop.ini`
- `[anime name].ico`

### Wrong anime detected?

Manually choose the correct one from MAL search results (shown with years and scores)

---

## 💡 Pro Tips

- **Name icons descriptively** (e.g., `Goblin Slayer.ico`) for auto-matching
- **Use Large Icons view** in Explorer for best visual impact
- **Browse DeviantArt artists** for themed icon collections
- **Check MAL scores** when picking between similar anime titles

---

## 🎨 Features Showcase

**Colored Terminal UI:**
- Pink ASCII art banner
- Random anime quotes on startup
- Cyan/Yellow/Green colored output
- MAL scores with star ratings

**Easter Eggs:**
- Success banner with box art
- "Sayonara!" on exit
- Random inspirational anime quotes

---

## 📜 License

MIT License - Free to use, modify, and share!

---

## 🙏 Credits

- **Creator:** [@bruuhim](https://github.com/bruuhim)
- **API:** [Jikan (MyAnimeList)](https://jikan.moe/)
- **Icons:** Talented artists on [DeviantArt](https://deviantart.com)
- **Inspiration:** The anime community 🎌

---

## ⭐ Support

If AniFold helped organize your anime collection, give it a star! ⭐

Found a bug or have a feature request? [Open an issue](https://github.com/bruuhim/AniFold/issues)!

---

**Happy organizing! 🎌✨**

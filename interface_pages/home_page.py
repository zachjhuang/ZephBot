from nicegui import ui

# Read the contents of the README.md file
with open('README.md', 'r', encoding='utf-8') as file:
    MARKDOWN_CONTENT = file.read()

MARKDOWN_CONTENT = """
# Before running, please do the following:

## 1. Set desktop resolution to 1920x1080

## 2. Change ingame settings to EXACTLY these numbers:

### - Video -> Resolution: 1920x1080

### - Video -> Screen: Fullscreen

### - Video -> Force 21:9 Aspect Ratio checked

### - Gameplay -> Controls and Display -> HUD size: 110%

### - Minimap transparency (sun in top right corner): 100%

### - Minimap zoom (magnifying glass in top right corner): 65%

## 3. Set up roster in ROSTER tab.

## 4. Edit class skill settings in SKILLS tab.

## 5. Configure keybinds and other options in CONFIG tab.

## 6. Set up bifrosts for roster by following the EXAMPLES Tab.

"""

def home_page():
    ui.markdown(content=MARKDOWN_CONTENT)
    
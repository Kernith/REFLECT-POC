# REFLECT App

A PyQt6-based application for classroom observation and analysis.

## Features

- Classroom observation protocols (COPUS)
- Data collection and analysis
- Configurable observation settings
- Export capabilities

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Building Executable

To build a standalone executable:

```bash
pyinstaller --onefile --windowed --icon=images/icon.png --add-data "images;images" --add-data "config.json;." --add-data "pages;pages" --add-data "widgets;widgets" --add-data "utils;utils" main.py
```

## Project Structure

- `pages/` - UI pages and screens
- `utils/` - Utility functions and app state
- `widgets/` - Custom UI components
- `images/` - Static assets and icons
- `data/` - Sample data and templates
- `docs/` - Documentation

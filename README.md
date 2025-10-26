# REFLECT App

A classroom observation and analysis tool with both desktop (PyQt6) and web (Streamlit) interfaces.

## Features

- **Classroom Observation**: Record student and instructor behaviors systematically
- **Data Analysis**: Visualize patterns with interactive plots and statistics
- **Multiple Interfaces**: Choose between desktop app or web browser
- **Export Capabilities**: Download data as CSV or generate PDF reports
- **Configurable Protocols**: Customize observation settings and categories

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd REFLECT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Desktop Application (PyQt6)
```bash
python main.py
```

### Web Application (Streamlit)
```bash
streamlit run streamlit_app.py
```

The web app will open in your browser at `http://localhost:8501`

## Usage

### Desktop App
- Launch with `python main.py`
- Use the GUI to navigate between observation, analysis, and settings
- All functionality is available through the desktop interface

### Web App
- Launch with `streamlit run streamlit_app.py`
- Access through any web browser
- Navigate using the buttons on the home page
- Upload CSV files for analysis
- Download observation data and reports

## Project Structure

```
REFLECT/
├── backend/                 # Core business logic (framework-agnostic)
│   ├── analysis/           # Data analysis services
│   ├── config/             # Configuration management
│   ├── data/               # Data collection and processing
│   ├── export/             # Export services (PDF, CSV)
│   └── visualization/      # Plot generation
├── gui/                    # GUI-specific implementations
│   ├── pyqt6/             # Desktop app (PyQt6)
│   │   ├── pages/         # PyQt6 UI pages
│   │   ├── adapters/      # PyQt6 adapters
│   │   └── widgets/       # PyQt6 widgets
│   └── streamlit/         # Web app (Streamlit)
│       ├── pages/         # Streamlit pages
│       ├── adapters/      # Streamlit adapters
│       └── main.py        # Streamlit entry point
├── core/                   # Utility functions
├── data/                   # Sample data and templates
├── images/                 # Static assets
├── main.py                 # Desktop app entry point
├── streamlit_app.py       # Web app entry point
└── requirements.txt        # Dependencies
```

## Building Executable

To build a standalone desktop executable:

```bash
pyinstaller --onefile --windowed --icon=images/icon.png --add-data "images;images" --add-data "config.json;." --add-data "pages;pages" --add-data "widgets;widgets" --add-data "backend;backend" main.py
```

## Architecture

The application uses a clean separation between backend services and frontend interfaces:

- **Backend**: Pure Python services for data processing, analysis, and visualization
- **PyQt6 Frontend**: Desktop GUI using PyQt6 widgets and adapters
- **Streamlit Frontend**: Web GUI using Streamlit components and adapters
- **Adapters**: Bridge backend services to specific GUI frameworks

This architecture allows for easy addition of new frontend interfaces while maintaining consistent backend functionality.

## Configuration

The app uses `config.json` for observation protocols and settings. Both desktop and web apps share the same configuration system.

## Development

### Adding New Features
1. Implement core logic in `backend/` services
2. Create adapters in `gui/{framework}/adapters/` if needed
3. Update both PyQt6 and Streamlit interfaces
4. Test both frontends

### Backend Services
- `AnalysisOrchestrator`: Coordinates data analysis
- `ObservationCollector`: Manages observation data collection
- `TimerService`: Handles observation timing
- `PlotFactory`: Generates matplotlib visualizations
- `ConfigManager`: Manages application configuration

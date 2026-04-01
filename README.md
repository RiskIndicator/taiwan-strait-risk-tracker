# taiwan-strait-risk-tracker

## Overview

This project aims to provide a real-time risk assessment of the Taiwan Strait, incorporating various data sources and predictive models.

## Directory Structure

```
.
├── data/                # JSON data files
├── public/              # CSS, images, and other static assets
├── src/                 # Python scripts
├── templates/           # HTML templates
├── README.md            # This file
└── .github/workflows/   # GitHub Actions workflow configurations
```

## Key Components

### Data (`data/`)

This directory contains JSON files that serve as the primary data source for the risk assessment. These files are regularly updated with the latest information.

### Public Assets (`public/`)

The `public/` directory houses static assets such as CSS stylesheets, images, and JavaScript files.

### Python Scripts (`src/`)

Python scripts in the `src/` directory perform data processing, risk calculations, and generate visualizations. These scripts are executed by GitHub Actions.

### HTML Templates (`templates/`)

The `templates/` directory contains HTML templates used to render the user interface.

## Setup and Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/taiwan-strait-risk-tracker.git
    cd taiwan-strait-risk-tracker
    ```

2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the main script:

    ```bash
    python src/main.py
    ```

2.  Access the web interface through your browser.

## GitHub Actions

The project uses GitHub Actions for continuous integration and deployment. The workflow is defined in `.github/workflows/main.yml`.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes.
4.  Submit a pull request.

## License

[MIT License](LICENSE)
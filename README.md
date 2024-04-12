# Movie Directory Manager 🎬 

This Python script allows you to manage your movie directory by extracting movie names from MKV files, retrieving their scores from an online database, marking them based on certain criteria, and even removing unwanted movies.

## Features

- **Find MKV Files**: The script scans a specified directory and identifies all MKV files.
- **Retrieve Scores**: It fetches the Tomatometer scores (audience and critics) for each movie from an online database.
- **Mark Movies**: Based on predefined criteria, it marks each movie in a CSV file for removal or retention.
- **Remove Movies**: It deletes movies from the specified directory based on their mark.

![movies aoutput in CSV](https://github.com/Sir-Sorg/Manage-Movie/assets/66873974/a4e30e2a-c99b-45e0-b64f-51ee602c71b0)

## Requirements

- Python 3.x
- `requests` library (install using `pip install requests`)

## Usage

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/your-username/your-repository.git
    ```

2. **Navigate to the Directory**:

    ```bash
    cd your-repository
    ```

3. **Open the Notebook**:

    - Launch Jupyter Notebook.
    - Navigate to the directory where the notebook is located.
    - Open `Movies.ipynb`.

4. **Follow the Instructions**:
    - Execute each cell in the notebook.
    - Provide the path to your desired directory containing MKV files.
    - Sit back and let the notebook do its magic!

## Additional Notes

- Ensure you have an internet connection for fetching movie scores.
- Double-check before removing movies, as this action is irreversible.

Enjoy managing your movie collection effortlessly with Movie Directory Manager! 🍿

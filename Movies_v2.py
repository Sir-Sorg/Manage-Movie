import os
import csv
import re
import argparse
import logging
from typing import List, Tuple, Optional
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('movie_cleaner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
SUPPORTED_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov'}
DEFAULT_THRESHOLDS = {
    'min_critic': 50,
    'min_audience': 60
}
API_CONFIG = {
    'url': 'https://79frdp12pn-3.algolianet.com/1/indexes/*/queries',
    'headers': {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
    },
    'params': {
        "x-algolia-agent": "Algolia for JavaScript (4.23.3); Browser (lite)",
        "x-algolia-api-key": "175588f6e5f8319b27702e4cc4013561",
        "x-algolia-application-id": "79FRDP12PN"
    }
}


def find_movies(directory: str) -> List[str]:
    """Find video files in the specified directory"""
    media_files = []
    for file in os.listdir(directory):
        if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
            media_files.append(file)
    logger.info(f"Found {len(media_files)} media files in {directory}")
    return media_files


def extract_movie_info(filename: str) -> Tuple[str, Optional[int]]:
    """Extract movie title and year from filename using regex"""
    clean_name = os.path.splitext(filename)[0]
    match = re.search(r'(.*?)(\b(19|20)\d{2}\b)(.*)', clean_name)
    
    if match:
        title = match.group(1).strip()
        year = int(match.group(2))
        # Clean up title
        title = re.sub(r'[._]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title, year
    
    logger.warning(f"Could not extract year from filename: {filename}")
    return re.sub(r'[._]', ' ', clean_name).strip(), None


def get_scores(title: str, year: Optional[int]) -> Tuple[Optional[int], Optional[int]]:
    """Get movie scores from API with error handling and retries"""
    params = {
        "requests": [{
            "indexName": "content_rt",
            "query": title,
            "params": "filters=isEmsSearchable%20%3D%201&hitsPerPage=5"
        }]
    }

    try:
        response = requests.post(
            API_CONFIG['url'],
            headers=API_CONFIG['headers'],
            params=API_CONFIG['params'],
            json=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        for result in data.get('results', []):
            for hit in result.get('hits', []):
                if year and hit.get('releaseYear') != year:
                    continue
                rt_scores = hit.get('rottenTomatoes', {})
                return (
                    rt_scores.get('audienceScore'),
                    rt_scores.get('criticsScore')
                )
        return None, None

    except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
        logger.error(f"API Error: {str(e)}")
        return None, None


def process_directory(input_dir: str, output_file: str, thresholds: dict, dry_run: bool):
    """Main processing pipeline"""
    files = find_movies(input_dir)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'File Name', 'Movie Title', 'Year', 
            'Critics Score', 'Audience Score', 'Remove'
        ])

        for file in files:
            title, year = extract_movie_info(file)
            critics, audience = get_scores(title, year)
            
            remove = 'no'
            if (critics or 0) <= thresholds['min_critic'] and \
               (audience or 0) <= thresholds['min_audience']:
                remove = 'yes'

            writer.writerow([file, title, year, critics, audience, remove])
            logger.info(f"Processed: {file} - Critics: {critics}, Audience: {audience}")

    logger.info(f"Results written to {output_file}")

    if not dry_run:
        remove_files(input_dir, output_file)


def remove_files(input_dir: str, output_file: str):
    """Remove files marked for deletion with confirmation"""
    with open(output_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        to_remove = [row['File Name'] for row in reader if row['Remove'] == 'yes']

    if not to_remove:
        logger.info("No files to remove")
        return

    logger.warning(f"About to remove {len(to_remove)} files. Continue? (y/n)")
    if input().lower() != 'y':
        return

    for filename in to_remove:
        full_path = os.path.join(input_dir, filename)
        try:
            os.remove(full_path)
            logger.info(f"Removed: {full_path}")
        except OSError as e:
            logger.error(f"Error removing {full_path}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Movie Rating Cleaner - Manage your media collection based on Rotten Tomatoes scores'
    )
    parser.add_argument('directory', help='Directory to scan for media files')
    parser.add_argument('-o', '--output', default='movies.csv', help='Output CSV file name')
    parser.add_argument('--min-critic', type=int, default=DEFAULT_THRESHOLDS['min_critic'],
                        help='Minimum critics score to keep (default: %(default)s)')
    parser.add_argument('--min-audience', type=int, default=DEFAULT_THRESHOLDS['min_audience'],
                        help='Minimum audience score to keep (default: %(default)s)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Process without deleting files')
    parser.add_argument('--verbose', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    thresholds = {
        'min_critic': args.min_critic,
        'min_audience': args.min_audience
    }

    try:
        process_directory(
            args.directory,
            args.output,
            thresholds,
            args.dry_run
        )
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

import config_parser
import collector
import transformer
from transformer import NormalizedPost
from typing import List
import argparse
from pathlib import Path
import logging
import colorlog

# this is hacky but it's an easy way to extract the date for the filename lol
GEMTEXT_DATE_START = 2
GEMTEXT_DATE_END = 12

def main() -> None:

    # Set up colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s%(reset)s: %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = colorlog.getLogger()
    logger.addHandler(handler)

    parser = argparse.ArgumentParser(description="Collect and turn social media posts into gemtext")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="(Required) Gemtext output directory"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=False,
        default=None,
        help="(Optional) Configuration file to use (default: './config.yml')"
    )
    args = parser.parse_args()
    
    if args.config:
        config_options, collectors = config_parser.load(args.config)
    else:
        config_options, collectors = config_parser.load()

    logger.setLevel(config_options.log_level)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    posts: List[NormalizedPost] = []

    # run through all the configured collectors and gather
    #  the formatted post data
    for source in collectors:
        found_posts = collector.collect(source, config_options)
        if not found_posts:
            logging.info(f"found 0 posts from {source.collector_type}")
            continue
        else:
            logging.info(f"found {len(found_posts)} posts from {source.collector_type}")
        posts.extend(found_posts)
    
    gemtexts: List[str] = transformer.to_gemtext_list(posts)

    for gemtext in gemtexts:
        post_date = gemtext[GEMTEXT_DATE_START:GEMTEXT_DATE_END]
        output_file = output_dir / f"{post_date}.gmi"

        # only write if file doesn't exist or contents differ
        should_write = True
        if output_file.exists():
            existing_content = output_file.read_text()
            if existing_content == gemtext:
                should_write = False
                logging.info(f"skipped {output_file}: no changes")

        if should_write:
            output_file.write_text(gemtext)
            logging.info(f"wrote new file: {output_file}")

if __name__ == "__main__":
    main()

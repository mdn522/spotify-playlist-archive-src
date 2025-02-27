#!/usr/bin/env python3

import argparse
import asyncio
import datetime
import logging
import os
from pathlib import Path
import pathlib

from file_manager import FileManager
from file_updater import FileUpdater
from plants.cache import NoCache, ReadThroughCache
from plants.committer import Committer
from plants.external import allow_external_calls
from plants.logging import configure_logging

logger: logging.Logger = logging.getLogger(__name__)


async def main() -> None:
    now = datetime.datetime.now()
    parser = argparse.ArgumentParser(description="Snapshot Spotify playlists")
    parser.add_argument(
        "--playlists-dir",
        type=pathlib.Path,
        required=True,
        help="Path to the playlists directory",
    )
    parser.add_argument(
        "--cache-dir",
        type=pathlib.Path,
        help="If specified, cache data from the Spotify API",
    )
    parser.add_argument(
        "--auto-register",
        action="store_true",
        help="Automatically register select playlists",
    )
    parser.add_argument(
        "--commit-and-push",
        action="store_true",
        help="Commit and push updated playlists upstream",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include debug logs",
    )
    args = parser.parse_args()

    if args.verbose:
        configure_logging(level=logging.DEBUG)

    auto_register = bool(args.auto_register)
    commit_and_push = bool(args.commit_and_push)

    file_manager = FileManager(playlists_dir=args.playlists_dir)

    if args.cache_dir:
        spotify_cache = ReadThroughCache(cache_dir=args.cache_dir)
    else:
        spotify_cache = NoCache()

    await FileUpdater.update_files(
        now=now,
        file_manager=file_manager,
        auto_register=auto_register,
        spotify_cache=spotify_cache,
    )
    if commit_and_push:
        Committer.commit_and_push_if_github_actions()

    spotify_cache.print_summary()
    logger.info("Done")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env")

    allow_external_calls()
    configure_logging()
    asyncio.run(main())

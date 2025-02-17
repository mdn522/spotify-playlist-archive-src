#!/usr/bin/env python3

import os
import pathlib

from plants.environment import Environment as PlantsEnvironment
from plants.external import external

# Subclassing pathlib.Path is difficult because the concrete type depends on
# platform, which is determined at runtime. This second line determines which
# type to subclass while the first line tricks Pyre into (correctly) thinking
# that ConcretePathType is valid type.
ConcretePathType = pathlib.Path
ConcretePathType = type(pathlib.Path())


class RelativePath(ConcretePathType):
    def __new__(cls, path: pathlib.Path) -> pathlib.Path:
        return super().__new__(cls, os.path.relpath(path))


class Environment:
    @classmethod
    def get_prod_playlists_dir(cls) -> RelativePath:
        return RelativePath(cls._get_repo_dir() / "playlists")

    @classmethod
    def get_test_playlists_dir(cls) -> RelativePath:
        dir_name = "_playlists/"
        repo_dir = cls._get_repo_dir()
        with open(repo_dir / ".gitignore", encoding='utf-8') as f:
            assert dir_name in f.read().splitlines()
        return RelativePath(repo_dir / dir_name)

    @classmethod
    @external
    def _get_repo_dir(cls) -> pathlib.Path:
        repo_dir = PlantsEnvironment.get_repo_root()
        assert repo_dir.name == "spotify-playlist-archive"
        return repo_dir

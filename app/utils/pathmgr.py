from pathlib import Path


class PathManager():
    @staticmethod
    def get_log_dir():
        """Log directory path"""
        log_dir_path = PathManager.get_root_dir().joinpath("logs")
        if not Path.is_dir(log_dir_path):
            Path.mkdir(log_dir_path)

        return log_dir_path

    @staticmethod
    def get_cache_dir():
        """Cache directory path"""
        cache_dir_path = PathManager.get_root_dir().joinpath("cache")
        if not Path.is_dir(cache_dir_path):
            Path.mkdir(cache_dir_path)

        return cache_dir_path

    @staticmethod
    def get_root_dir():
        base_path = Path.cwd()
        return base_path

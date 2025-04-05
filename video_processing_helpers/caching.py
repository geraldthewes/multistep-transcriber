import os
import json

def cached_file(file_ext):
    """
    A decorator that caches the output of a function to a file.

    Args:
        file_ext (str): The file extension used for the cache file.

    Returns:
        function: A decorator that applies the caching behavior.
    """
    def decorator(func):
        def wrapper(video_path, *args, **kwargs):
            # Construct the cache file name
            base_name, _ = os.path.splitext(video_path)
            cache_dir = base_name + '.d'
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, 'cache' + file_ext)

            # Try to load from cache if it exists
            if os.path.exists(cache_file):
                print(f"Loading cached data from {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as file:
                    return file.read()

            # Compute the result since cache doesn't exist
            result = func(video_path, *args, **kwargs)

            if not result:  # Check for failure
                print(f"Error in computing {func.__name__}")
                return f"{func.__name__} failed"

            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as file:
                file.write(result)

            return result

        return wrapper
    return decorator

def cached_file_object(file_ext):
    """
    A decorator that caches the output of a function returning a JSON-serializable object to a file.
    Args:
        file_ext (str): The file extension used for the cache file.
    Returns:
        function: A decorator that applies the caching behavior.
    """
    def decorator(func):
        def wrapper(video_path, *args, **kwargs):
            # Construct the cache file name
            base_name, _ = os.path.splitext(video_path)
            cache_dir = base_name + '.d'
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, 'cache' + file_ext)

            # Try to load from cache if it exists
            if os.path.exists(cache_file):
                print(f"Loading cached data from {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as file:
                    return json.load(file)

            # Compute the result since cache doesn't exist
            result = func(video_path, *args, **kwargs)

            # Save to cache
            with open(cache_file, 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)

            return result
        return wrapper
    return decorator

import os
import json
import shutil # Added for robust directory clearing, though os.remove could also be used for files

def get_cache_directory(video_path):
    base_name, _ = os.path.splitext(video_path)
    cache_dir = base_name + '.d'
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir # Added return statement

def get_cache_file(video_path, file_ext):
    cache_dir = get_cache_directory(video_path)
    cache_file = os.path.join(cache_dir, 'cache' + file_ext)
    return cache_file

def clear_cache_directory(video_path: str):
    """
    Clears all files from the cache directory associated with the video_path.
    The directory itself will remain.

    Args:
        video_path (str): The path to the video file, used to determine the cache directory.
    """
    cache_dir = get_cache_directory(video_path)
    if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
        print(f"Clearing cache directory: {cache_dir}")
        for filename in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # If we wanted to remove subdirectories as well, we could add:
                # elif os.path.isdir(file_path):
                #     shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f"Cache directory {cache_dir} does not exist or is not a directory.")


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
            if video_path:
                cache_file = get_cache_file(video_path, file_ext)

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
            if video_path:
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
            if video_path:
                cache_file = get_cache_file(video_path, file_ext)            

                # Try to load from cache if it exists
                if os.path.exists(cache_file):
                    print(f"Loading cached data from {cache_file}")
                    with open(cache_file, 'r', encoding='utf-8') as file:
                        return json.load(file)

            # Compute the result since cache doesn't exist
            result = func(video_path, *args, **kwargs)

            # Save to cache
            if video_path:
                with open(cache_file, 'w', encoding='utf-8') as file:
                    json.dump(result, file, ensure_ascii=False, indent=4)

            return result
        return wrapper
    return decorator

"""Measure download speed with 10 sequential HTTP requests (standard library only)."""

import argparse
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024


def download(url, timeout):
    """Read the entire response and return its byte count and elapsed seconds."""
    request = Request(url, headers={
        "User-Agent": "PythonDownloadSpeedTest/1.0",
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
    })
    size = 0
    started = time.perf_counter()
    with urlopen(request, timeout=timeout) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
    return size, time.perf_counter() - started


def positive_timeout(value):
    number = float(value)
    if not 0 < number < float("inf"):
        raise argparse.ArgumentTypeError("timeout must be a positive finite number")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="HTTP(S) URL of a file to download")
    parser.add_argument("--timeout", type=positive_timeout, default=30,
                        help="socket operation timeout in seconds (default: 30)")
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        parser.error("provide a valid http:// or https:// URL")

    total_bytes = 0
    total_seconds = 0.0
    for index in range(1, REQUEST_COUNT + 1):
        try:
            size, elapsed = download(args.url, args.timeout)
        except (HTTPError, URLError, OSError, ValueError) as error:
            print(f"Request {index}/{REQUEST_COUNT} failed: {error}", file=sys.stderr)
            return 1
        total_bytes += size
        total_seconds += elapsed
        print(f"Request {index}/{REQUEST_COUNT}: {size} bytes in {elapsed:.3f} s")

    print(f"\nAverage request time: {total_seconds / REQUEST_COUNT:.3f} s")
    print(f"Total downloaded: {total_bytes} bytes ({total_bytes / 1_000_000:.3f} MB)")
    speed = total_bytes / total_seconds if total_seconds > 0 else 0.0
    print(f"Download speed: {speed / 1_000_000:.3f} MB/s ({speed * 8 / 1_000_000:.3f} Mbit/s)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(130)

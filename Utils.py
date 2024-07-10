#!/usr/bin/env python3

import subprocess
import re
import os
import threading

from urllib.parse import urlparse
from CustomLogger import CustomLogger

logger = CustomLogger()


def run_subprocess(command, timeout=300):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=timeout)
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'output': result.stdout + result.stderr,
            'return_code': result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'stdout': e.stdout,
            'stderr': e.stderr,
            'output': e.stdout + e.stderr,
            'return_code': e.returncode
        }


def read_stream(stream, stream_name):
    try:
        for line in iter(stream.readline, ''):
            if line:
                if stream_name == "STDERR":
                    logger.error(f"{stream_name}: {line.strip()}")
                else:
                    logger.info(f"{stream_name}: {line.strip()}")
    except ValueError as e:
        logger.error(f"Error reading stream: {e}")
    finally:
        stream.close()


def run_subprocess_popen(command, timeout=300):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                               universal_newlines=True)

    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "STDOUT"))
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "STDERR"))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    stdout, stderr = process.communicate(timeout=timeout)

    process.wait()
    return process


def is_semantic_version(version):
    semantic_pattern = re.compile(r"^(v?\d+\.\d+\.\d+|v?\d+\.\d)$")
    return semantic_pattern.match(version) is not None


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def parse_env(required_vars):
    missing_vars = [var for var in required_vars if var not in os.environ]
    try:
        if missing_vars:
            raise EnvironmentError(f"Error: Required environment variables are not set: {', '.join(missing_vars)}")
        return {var: os.environ[var] for var in required_vars}
    except EnvironmentError as e:
        logger.error(e)
        exit(1)

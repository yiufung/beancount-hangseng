import subprocess


def is_pdftotext_installed():
    """Return true if the external tool pdftotext is installed."""
    try:
        returncode = subprocess.call(['pdftotext', '-h'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    except (FileNotFoundError, PermissionError):
        return False
    else:
        return returncode == 0


def pdf_to_text(filename):
    """Convert a PDF file to a text equivalent.

    Args:
      filename: A string path, the filename to convert.
    Returns:
      A string, the text contents of the filename.
    """
    pipe = subprocess.Popen(['pdftotext', '-layout', filename, '-'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    if stderr:
        raise ValueError(stderr.decode())
    return stdout.decode()

# tools/jenkins_tool.py
from utils.logger import get_logger

def fetch_ci_logs() -> str:
    """
    Fetch CI logs from Jenkins.

    Returns
    -------
    str
        CI log content as string.
    """
    logger = get_logger("JenkinsTool")
    logs = """[INFO] Build started
    [ERROR] test_login FAILED due to timeout
    [INFO] Build finished"""
    logger.info("Fetched CI logs from Jenkins")
    return logs
# End of tools/jenkins_tool.py
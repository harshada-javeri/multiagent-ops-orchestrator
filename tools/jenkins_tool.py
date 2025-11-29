# tools/jenkins_tool.py
from utils.logger import get_logger

class JenkinsTool:
    """Tool for Jenkins CI/CD integration."""
    
    @staticmethod
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

def fetch_ci_logs() -> str:
    """Legacy function wrapper."""
    return JenkinsTool.fetch_ci_logs()
# End of tools/jenkins_tool.py
import logging
import uuid
from logging import StreamHandler, Formatter

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s | correlation_id=%(correlation_id)s"

class CorrelationIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Ensure correlation_id is always present
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra']['correlation_id'] = self.extra.get('correlation_id', str(uuid.uuid4()))
        return msg, kwargs

def get_logger(name: str = "QAOpsOrchestrator") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = StreamHandler()
        handler.setFormatter(Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    # Attach a correlation_id for tracing requests
    return CorrelationIdAdapter(logger, {"correlation_id": str(uuid.uuid4())})
import logging
import sys
import time

logger = logging.getLogger("protrip")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)

def log_info(msg):
    logger.info(msg)

def log_debug(msg):
    logger.debug(msg)

def log_error(msg):
    logger.error(msg)

def log_metric(metric_name, value):
    logger.info("METRIC %s %s %s"%(time.strftime("%H:%M:%S"), metric_name, str(value)))

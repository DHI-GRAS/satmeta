import os
import sys
import logging
import datetime

logger_set = False

def set_cli_logger(debug=False, logdir=None):
    global logger_set
    if logger_set:
        return
    level = 'DEBUG' if debug else 'INFO'
    logger = logging.getLogger('sentinel_meta')
    logger.setLevel(level)

    formatter = logging.Formatter('%(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if logdir is not None:
        logfile = os.path.join(logdir, 'sdb_data_{:%Y%m%d_%H%M%S}.log'.format(datetime.datetime.now()))
        formatter = logging.Formatter('%(asctime)s %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fh = logging.FileHandler(logfile)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # define handler function
    def log_uncaught_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        if level in ['DEBUG', logging.DEBUG]:
            logger.critical("Uncaught exception!", exc_info=(exc_type, exc_value, exc_traceback))
        else:
            logger.critical('{}: {}'.format(exc_type.__name__, exc_value))

    # install exception handler
    sys.excepthook = log_uncaught_exception
    logger_set = True

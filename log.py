import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)



RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[01;%dm"

def formatter_message(message, use_color = True):
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': RED,
    'ERROR': RED,
    'EXCEPTION' : CYAN
}



class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            record.levelname = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.msg = COLOR_SEQ % (30 + COLORS[levelname])+"[" + record.name + "] " + record.msg + " <" +record.threadName+ ">"  + RESET_SEQ
        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    COLOR_FORMAT = formatter_message(FORMAT, True)
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)
        color_formatter = ColoredFormatter(self.COLOR_FORMAT)
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)
        return


logging.setLoggerClass(ColoredLogger)



if __name__ == "__main__":
    logger = logging.getLogger("TESTLOGGER")
    logger.debug("debug message")
    logger.info("info message")
    logger.warn("warn message")
    logger.critical("critical message")
    logger.error("error message")
    logger.exception("asdf")




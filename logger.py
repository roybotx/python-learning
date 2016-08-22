import termcolor


class logger:
    flag = True

    @staticmethod
    def error(msg):
        if logger.flag == True:
            print "".join([termcolor.colored("ERROR", "red"), ": ", termcolor.colored(msg, "white")])

    @staticmethod
    def warn(msg):
        if logger.flag == True:
            print "".join([termcolor.colored("WARN", "yellow"), ": ", termcolor.colored(msg, "white")])

    @staticmethod
    def info(msg):
        if logger.flag == True:
            print "".join([termcolor.colored("INFO", "magenta"), ": ", termcolor.colored(msg, "white")])

    @staticmethod
    def debug(msg):
        if logger.flag == True:
            print "".join([termcolor.colored("DEBUG", "magenta"), ": ", termcolor.colored(msg, "white")])

    @staticmethod
    def success(msg):
        if logger.flag == True:
            print "".join([termcolor.colored("SUCCES", "green"), ": ", termcolor.colored(msg, "white")])


class login_password_error(Exception):
    def __init__(self, message):
        if type(message) != type("") or message == "":
            self.message = "Either user name or password is wrong"
        else:
            self.message = message
        logger.error(self.message)


class network_error(Exception):
    def __init__(self, message):
        if type(message) != type("") or message == "":
            self.message = "Network occurs some unknown issue"
        else:
            self.message = message
        logger.error(self.message)


class account_error(Exception):
    def __init__(self, message):
        if type(message) != type("") or message == "":
            self.message = "Account type is wrong"
        else:
            self.message = message
        logger.error(self.message)

import enum
from utils.stats.dbwriter import BashOutput
from telegram import Update
from .dbwriter import *

output = BashOutput()

class Output(AbstractDB):
    def __init__(self, output : Outputs) -> None:
        if output.value == -1:
            self.__output = None
            return
        outputs = {
            0: BashOutput,
            1: ElasticOutput,
            2: NDJsonOutput
        }
        self.__output : AbstractDB = outputs[output.value]
        self.__output = self.__output()

    def __write_msg(self, msg: Message):
        try:
            if self.__output:
                self.__output.write_msg(msg) 
        except Exception as ex:
            logging.error(f"Can't write msg: {ex}")

    def record(self, func):
        """decorator docstring"""
        def inner_function(update : Update, ctx):
            """inner function docstring """
            self.__write_msg(update.message)
            return func(update, ctx)
        return inner_function

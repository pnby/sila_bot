from aiogram.fsm.state import StatesGroup, State


class GeneralStates(StatesGroup):
    GET_HELP = State()
    GET_HUMAN_HELP = State()
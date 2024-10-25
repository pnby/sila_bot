from aiogram.fsm.state import StatesGroup, State


class StaffStates(StatesGroup):
    LOAD_DOCUMENT = State()
    UNLOAD_DOCUMENT = State()
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.bot import logger
from app.bot.api.rag.impl.rag import RAGProcessor
from app.bot.config import top_chunks
from app.bot.keyboards.general import start_keyboard, answer_inline_keyboard
from app.bot.states.general import GeneralStates

router = Router()

@router.message(Command(commands=["start"]))
async def start_handler(message: Message, state: FSMContext):
    """
    Handles the /start command. Clears the state and sends a welcome message with the start keyboard.
    """
    await state.clear()
    await message.answer('Приветствую. Я ассистент для клиентов ООО Сила, для получения полной справки обо мне напишите /help', reply_markup=start_keyboard)



@router.callback_query(F.data == "support_button")
async def support_button_handler(callback_query: CallbackQuery, state: FSMContext):
    """
    Handles the 'support_button' callback query. Sets the state to GET_HELP and prompts the user to describe their problem.
    """
    await state.set_state(GeneralStates.GET_HELP)
    await callback_query.message.answer(text='Внятно объясните и изложите суть своей проблемы и/или вопроса.')


@router.message(GeneralStates.GET_HELP)
async def help_handler(message: Message, state: FSMContext):
    """
    Handles messages in the GET_HELP state. Processes text or voice input and provides an answer.
    """
    try:
        rag_processor = RAGProcessor()
        answer = await rag_processor.query_docx(message.text, top_chunks)

        await message.answer(answer, reply_markup=answer_inline_keyboard)
        await state.clear()
    except Exception as e:
        await message.answer("Произошла неизвестная ошибка, обратитесь в поддержку")
        logger.warning(e)

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.models.schemas import (
    GeneralInfoRequest,
    GeneralInfoResponse,
    HealthResponse,
    MenuAnswer,
    MenuQuery,
    OrderRequest,
    OrderResponse,
    ReservationRequest,
    ReservationResponse,
    VoiceRequest,
    VoiceResponse,
)
from app.orchestration.agents import (
    AssistantOrchestrator,
    GeneralInfoTool,
    MenuQATool,
    OrderAgent,
    ReservationAgent,
)
from app.orchestration.llm import get_chat_model
from app.orchestration.router import IntentRouter
from app.rag.ingest import load_retriever
from app.speech.factory import build_stt, build_tts
from app.speech.stt import decode_audio
from app.speech.tts import encode_audio

app = FastAPI(title="Voice-Enabled GenAI Restaurant Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def bootstrap(settings: Settings):
    llm_model = None
    try:
        llm_model = get_chat_model(settings)
    except Exception as exc:
        # LLM may be optional during local development
        print(f"[bootstrap] LLM unavailable: {exc}")

    retriever = load_retriever(settings)
    menu_tool = MenuQATool(retriever, llm_model) if retriever and llm_model else None
    reservation_agent = ReservationAgent()
    order_agent = OrderAgent()
    general_tool = GeneralInfoTool()
    router = IntentRouter(llm_model)
    orchestrator = AssistantOrchestrator(
        router=router,
        model=llm_model,
        menu_tool=menu_tool,
        reservation_agent=reservation_agent,
        order_agent=order_agent,
        general_tool=general_tool,
    )
    stt = build_stt(settings)
    tts = build_tts(settings)
    return orchestrator, reservation_agent, order_agent, general_tool, stt, tts, llm_model


def get_services(settings: Settings = Depends(get_settings)):
    # Lazy singleton via function attribute
    if not hasattr(get_services, "_services"):
        get_services._services = bootstrap(settings)
    return get_services._services


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/voice", response_model=VoiceResponse)
async def voice(
    payload: VoiceRequest,
    services=Depends(get_services),
):
    orchestrator, _, _, _, stt, tts, _ = services

    text_input = payload.text
    if not text_input and payload.audio_base64:
        audio_bytes = decode_audio(payload.audio_base64)
        text_input = stt.transcribe(audio_bytes)

    if not text_input:
        raise HTTPException(status_code=400, detail="No audio or text provided.")

    reply, intent = orchestrator.handle(text_input)
    audio_bytes = tts.synthesize(reply) if tts else None

    return VoiceResponse(
        text=reply, audio_base64=encode_audio(audio_bytes), intent=intent
    )


@app.post("/reservation", response_model=ReservationResponse)
async def reservation(
    payload: ReservationRequest, services=Depends(get_services)
):
    _, reservation_agent, _, _, _, _, _ = services
    return reservation_agent.book(payload)


@app.post("/order", response_model=OrderResponse)
async def order(payload: OrderRequest, services=Depends(get_services)):
    _, _, order_agent, _, _, _, _ = services
    return order_agent.place_order(payload)


@app.post("/menu/qa", response_model=MenuAnswer)
async def menu_qa(payload: MenuQuery, services=Depends(get_services)):
    orchestrator, _, _, _, _, _, _ = services
    if not orchestrator.menu_tool:
        raise HTTPException(
            status_code=503, detail="Menu knowledge base not initialized."
        )
    return orchestrator.menu_tool.answer(payload)


@app.post("/info", response_model=GeneralInfoResponse)
async def general_info(
    payload: GeneralInfoRequest, services=Depends(get_services)
):
    _, _, _, general_tool, _, _, _ = services
    return general_tool.answer(payload.question)

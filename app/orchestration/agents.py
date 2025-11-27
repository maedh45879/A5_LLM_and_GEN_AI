from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel

from app.models.schemas import (
    GeneralInfoResponse,
    MenuAnswer,
    MenuQuery,
    OrderRequest,
    OrderResponse,
    ReservationRequest,
    ReservationResponse,
)


class ReservationAgent:
    def __init__(self):
        self._reservations: List[ReservationResponse] = []

    def book(self, payload: ReservationRequest) -> ReservationResponse:
        ref = f"RSV-{len(self._reservations)+1:04d}"
        message = (
            f"Booked {payload.guests} guests for {payload.name} on "
            f"{payload.date} at {payload.time}."
        )
        if payload.special_requests:
            message += f" Notes: {payload.special_requests}."
        response = ReservationResponse(confirmed=True, reference=ref, message=message)
        self._reservations.append(response)
        return response

    def handle_freeform(
        self, text: str, model: Optional[BaseLanguageModel] = None
    ) -> ReservationResponse:
        """
        Quick reservation from natural language; if an LLM is available we ask it
        to extract structured fields, otherwise we acknowledge the request.
        """
        if model:
            prompt = PromptTemplate.from_template(
                "Extract a reservation intent. Reply with a short confirmation.\n"
                "User: {text}"
            )
            message = model.invoke(prompt.format(text=text)).content
            return ReservationResponse(
                confirmed=True, reference="RSV-PENDING", message=message
            )
        return ReservationResponse(
            confirmed=False,
            reference="RSV-PENDING",
            message="I can start your reservation. Please share name, date, time, and guests.",
        )


class OrderAgent:
    def __init__(self):
        self._orders: List[OrderResponse] = []

    def place_order(self, payload: OrderRequest) -> OrderResponse:
        total_items = sum(item.quantity for item in payload.items)
        summary = "; ".join(
            f"{item.quantity}x {item.item}" + (f" ({item.notes})" if item.notes else "")
            for item in payload.items
        )
        ref = f"ORD-{len(self._orders)+1:04d}"
        message = f"Order received{f' for table {payload.table}' if payload.table else ''}: {summary}"
        resp = OrderResponse(
            confirmed=True, summary=summary, total_items=total_items, message=message
        )
        self._orders.append(resp)
        return resp

    def handle_freeform(
        self, text: str, model: Optional[BaseLanguageModel] = None
    ) -> OrderResponse:
        if model:
            prompt = PromptTemplate.from_template(
                "Summarize this order request and confirm politely in one sentence.\n"
                "Order: {text}"
            )
            message = model.invoke(prompt.format(text=text)).content
            return OrderResponse(
                confirmed=True, summary=text, total_items=1, message=message
            )
        return OrderResponse(
            confirmed=False,
            summary=text,
            total_items=0,
            message="Happy to take your order. Please list items and quantities.",
        )


class MenuQATool:
    def __init__(self, retriever, model: BaseLanguageModel):
        self.retriever = retriever
        self.model = model

    def answer(self, payload: MenuQuery) -> MenuAnswer:
        if not self.retriever:
            return MenuAnswer(
                answer="Menu knowledge base not ready. Please run the ingestion script.",
                sources=[],
            )
        docs = self.retriever.similarity_search(payload.question, k=4)
        context = "\n\n".join(doc.page_content for doc in docs)
        qa_prompt = PromptTemplate.from_template(
            "You are a restaurant assistant. Use the context to answer clearly.\n"
            "Question: {question}\n"
            "Context: {context}"
        )
        prompt_text = qa_prompt.format(question=payload.question, context=context)
        result = self.model.invoke(prompt_text)
        sources = [doc.metadata.get("source", "menu_doc") for doc in docs]
        return MenuAnswer(answer=result.content if hasattr(result, "content") else str(result), sources=sources)


class GeneralInfoTool:
    def __init__(self):
        self.info_map = {
            "hours": "We are open daily from 11:00 to 22:00.",
            "location": "123 Flavor Street, Paris.",
            "offers": "Today's special: Truffle mushroom risotto with 10% off.",
            "contact": "Call us at +33 1 23 45 67 89.",
        }

    def answer(self, question: str) -> GeneralInfoResponse:
        lower = question.lower()
        for key, value in self.info_map.items():
            if key in lower:
                return GeneralInfoResponse(answer=value)
        return GeneralInfoResponse(
            answer="We are here to help with hours, location, and specials. What would you like to know?"
        )


class AssistantOrchestrator:
    def __init__(
        self,
        router,
        model: Optional[BaseLanguageModel],
        menu_tool: Optional[MenuQATool],
        reservation_agent: ReservationAgent,
        order_agent: OrderAgent,
        general_tool: GeneralInfoTool,
    ):
        self.router = router
        self.model = model
        self.menu_tool = menu_tool
        self.reservation_agent = reservation_agent
        self.order_agent = order_agent
        self.general_tool = general_tool

    def handle(self, text: str) -> tuple[str, str]:
        intent = self.router.route(text).intent

        if intent == "reservation":
            response = self.reservation_agent.handle_freeform(text, self.model)
            return response.message, intent

        if intent == "order":
            response = self.order_agent.handle_freeform(text, self.model)
            return response.message, intent

        if intent == "menu":
            if not self.menu_tool:
                return (
                    "Menu knowledge base is not ready. Please run ingestion first.",
                    intent,
                )
            answer = self.menu_tool.answer(MenuQuery(question=text))
            return answer.answer, intent

        if intent == "general":
            answer = self.general_tool.answer(text)
            return answer.answer, intent

        # fallback
        fallback_prompt = (
            "You are a concise restaurant assistant. Provide a brief helpful reply."
        )
        if self.model:
            message = self.model.invoke(f"{fallback_prompt}\nUser: {text}").content
        else:
            message = "I'm here to help with reservations, orders, or menu questions."
        return message, intent

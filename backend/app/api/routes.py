from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.schemas import FavoriteRequest, GeneratePackRequest, HistoryResponse, Pack, RefineRequest
from app.services.llm import ChastushkaLLM, LLMError, get_llm
from app.services.moderation import ModerationError, is_safe_input
from app.services.pipeline import REFINE_SUFFIX, generate_pack
from app.services.store import PackStore, get_store


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/generate-pack", response_model=Pack)
def generate(
    request: GeneratePackRequest,
    llm: ChastushkaLLM = Depends(get_llm),
    store: PackStore = Depends(get_store),
) -> Pack:
    if request.safe_mode and not is_safe_input(request):
        raise HTTPException(status_code=422, detail="unsafe_input")
    try:
        pack = generate_pack(request, llm=llm)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail="generation_failed") from exc
    except ModerationError as exc:
        raise HTTPException(status_code=422, detail="unsafe_output") from exc
    store.save_pack(pack)
    return pack


@router.post("/v1/refine", response_model=Pack)
def refine(
    request: RefineRequest,
    llm: ChastushkaLLM = Depends(get_llm),
    store: PackStore = Depends(get_store),
) -> Pack:
    try:
        source = store.get_pack(request.pack_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="pack_id not found") from exc

    source_request = GeneratePackRequest(
        occasion="refine",
        target=source.candidates[0].id if source.candidates else "unknown",
        facts=[candidate.text for candidate in source.candidates[:2]],
        tone=request.action,
        boldness=2,
        safe_mode=True,
        count=len(source.candidates),
    )
    try:
        refined = generate_pack(
            source_request,
            suffix=REFINE_SUFFIX[request.action],
            llm=llm,
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail="generation_failed") from exc
    except ModerationError as exc:
        raise HTTPException(status_code=422, detail="unsafe_output") from exc
    refined.source_pack_id = source.pack_id
    store.save_pack(refined)
    return refined


@router.get("/v1/history", response_model=HistoryResponse)
def get_history(store: PackStore = Depends(get_store)) -> HistoryResponse:
    return HistoryResponse(items=store.history())


@router.post("/v1/favorites", response_model=Pack)
def add_favorite(request: FavoriteRequest, store: PackStore = Depends(get_store)) -> Pack:
    try:
        return store.add_favorite(request.pack_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="pack_id not found") from exc


@router.get("/v1/favorites", response_model=HistoryResponse)
def get_favorites(store: PackStore = Depends(get_store)) -> HistoryResponse:
    return HistoryResponse(items=store.favorites())


@router.get("/v1/export/{pack_id}")
def export_pack(pack_id: str, format: str = Query(default="text"), store: PackStore = Depends(get_store)):
    try:
        pack = store.get_pack(pack_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="pack_id not found") from exc

    if format == "text":
        content = "\n".join(candidate.text for candidate in pack.candidates)
        return PlainTextResponse(content=content)
    if format == "json":
        return pack
    raise HTTPException(status_code=400, detail="unsupported_format")


@router.get("/v1/metrics")
def metrics(store: PackStore = Depends(get_store)) -> dict[str, float]:
    return store.metrics()


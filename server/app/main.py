from __future__ import annotations

import base64
import json
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import get_settings
from app.core.db import (
  DATA_DIR,
  create_embed,
  create_result,
  create_slide,
  db_connection,
  delete_file,
  delete_embed,
  delete_result,
  delete_slide,
  get_embed,
  get_result,
  get_slide,
  init_db,
  list_embed_paths,
  list_embeds,
  list_result_paths,
  list_results,
  list_slides,
  save_embed_file,
  save_result_image,
  select_result,
  update_embed,
  update_slide,
)
from app.schemas import EmbedUpdateRequest, GenerateRequest, SlideCreateRequest, SlideUpdateRequest
from app.services.genai_client import genai_client


app = FastAPI()


@app.on_event("startup")
def _startup() -> None:
  init_db()


settings = get_settings()
origins = [origin.strip() for origin in settings.cors_allowed_origins.split(",") if origin.strip()]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


def _sse_event(event: str, payload: dict) -> str:
  return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


@app.get("/health")
def health() -> dict:
  return {"status": "ok"}


@app.get("/slides")
def get_slides() -> dict:
  with db_connection() as conn:
    slides = list_slides(conn)
    for slide in slides:
      slide["embeds"] = list_embeds(conn, slide["id"])
      slide["results"] = list_results(conn, slide["id"])
  return {"slides": slides}


@app.post("/slides", status_code=201)
def create_slide_handler(payload: SlideCreateRequest) -> dict:
  with db_connection() as conn:
    slide = create_slide(
      conn,
      name=payload.name,
      title=payload.title,
      subtitle=payload.subtitle,
      text=payload.text,
      design=payload.design,
      quantity=payload.quantity,
      position=payload.position,
    )
  return {"slide": slide}


@app.get("/slides/{slide_id}")
def get_slide_handler(slide_id: str) -> dict:
  with db_connection() as conn:
    slide = get_slide(conn, slide_id)
    if not slide:
      raise HTTPException(status_code=404, detail="Slide not found.")
    slide["embeds"] = list_embeds(conn, slide_id)
    slide["results"] = list_results(conn, slide_id)
  return {"slide": slide}


@app.patch("/slides/{slide_id}")
def update_slide_handler(slide_id: str, payload: SlideUpdateRequest) -> dict:
  data = payload.model_dump(exclude_unset=True)
  with db_connection() as conn:
    slide = update_slide(conn, slide_id, data)
  if not slide:
    raise HTTPException(status_code=404, detail="Slide not found.")
  return {"slide": slide}


@app.delete("/slides/{slide_id}")
def delete_slide_handler(slide_id: str) -> dict:
  with db_connection() as conn:
    embed_paths = list_embed_paths(conn, slide_id)
    result_paths = list_result_paths(conn, slide_id)
    deleted = delete_slide(conn, slide_id)
  if not deleted:
    raise HTTPException(status_code=404, detail="Slide not found.")
  for path in embed_paths + result_paths:
    delete_file(path)
  return {"id": slide_id}


@app.post("/slides/{slide_id}/embeds", status_code=201)
async def upload_embed(
  slide_id: str,
  file: UploadFile = File(...),
  label: str = Form(""),
  name: str = Form(""),
  context: str = Form(""),
) -> dict:
  if not file:
    raise HTTPException(status_code=400, detail="File required.")
  file_bytes = await file.read()
  if not file_bytes:
    raise HTTPException(status_code=400, detail="Empty file.")

  file_path, size = save_embed_file(file_bytes, file.filename or "embed.png")
  label_value = label or file.filename or "Embed"
  name_value = name or file.filename or label_value
  context_value = context or ""

  with db_connection() as conn:
    slide = get_slide(conn, slide_id)
    if not slide:
      raise HTTPException(status_code=404, detail="Slide not found.")
    embed = create_embed(
      conn,
      slide_id=slide_id,
      label=label_value,
      name=name_value,
      context=context_value,
      file_path=file_path,
      mime_type=file.content_type or "image/png",
      size=size,
    )

  return {"embed": embed}


@app.post("/slides/{slide_id}/generate")
def generate_slide(slide_id: str, payload: GenerateRequest) -> StreamingResponse:
  with db_connection() as conn:
    slide = get_slide(conn, slide_id)
    if not slide:
      raise HTTPException(status_code=404, detail="Slide not found.")
    embeds = list_embeds(conn, slide_id)
    selected_result_id = slide.get("selected_result_id")

  if not slide.get("text"):
    raise HTTPException(status_code=400, detail="Slide text is required.")

  embed_payloads = []
  embed_assets = []
  for embed in embeds:
    embed_assets.append({"label": embed["label"], "context": embed.get("context") or ""})
    embed_path = (DATA_DIR / embed["file_path"]).resolve()
    if embed_path.exists():
      embed_payloads.append((embed["mime_type"], embed_path.read_bytes()))

  quantity = max(1, min(5, payload.quantity))
  tones = ["sunset", "mist", "sky", "sand"]

  def event_stream():
    current_selected = selected_result_id
    try:
      refined_prompt = genai_client.refine_prompt(
        slide_text=slide["text"],
        notes=slide.get("design"),
        embed_assets=embed_assets,
      )
    except Exception as exc:
      yield _sse_event("error", {"message": str(exc)})
      return

    for index in range(quantity):
      try:
        images = genai_client.generate_images(
          slide_text=slide["text"],
          production_brief=refined_prompt,
          embed_images=embed_payloads,
          count=1,
          use_grounding=payload.grounding,
        )
        image_bytes = images[0]
        image_path = save_result_image(image_bytes)
        with db_connection() as conn:
          result = create_result(
            conn,
            slide_id=slide_id,
            title=f"Option {index + 1}",
            note="Generated by AI",
            tone=tones[index % len(tones)],
            status="complete",
            image_path=image_path,
          )
          if not current_selected:
            select_result(conn, slide_id, result["id"])
            current_selected = result["id"]
      except Exception as exc:
        yield _sse_event("error", {"message": str(exc)})
        return

      encoded = base64.b64encode(image_bytes).decode("ascii")
      yield _sse_event(
        "result",
        {
          "id": result["id"],
          "image_base64": encoded,
          "note": result["note"],
          "title": result["title"],
        },
      )

    yield _sse_event("done", {"count": quantity})

  return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/slides/{slide_id}/results/{result_id}/select")
def select_result_handler(slide_id: str, result_id: str) -> dict:
  with db_connection() as conn:
    result = get_result(conn, result_id)
    if not result or result["slide_id"] != slide_id:
      raise HTTPException(status_code=404, detail="Result not found.")
    slide = select_result(conn, slide_id, result_id)
  return {"slide": slide}


@app.get("/embeds/{embed_id}/file")
def get_embed_file(embed_id: str) -> FileResponse:
  with db_connection() as conn:
    embed = get_embed(conn, embed_id)
  if not embed:
    raise HTTPException(status_code=404, detail="Embed not found.")
  full_path = (DATA_DIR / embed["file_path"]).resolve()
  if not full_path.exists():
    raise HTTPException(status_code=404, detail="Embed file missing.")
  return FileResponse(full_path, media_type=embed.get("mime_type") or "image/png")


@app.delete("/embeds/{embed_id}")
def delete_embed_handler(embed_id: str) -> dict:
  with db_connection() as conn:
    embed = delete_embed(conn, embed_id)
  if not embed:
    raise HTTPException(status_code=404, detail="Embed not found.")
  delete_file(embed["file_path"])
  return {"id": embed_id}


@app.patch("/embeds/{embed_id}")
def update_embed_handler(embed_id: str, payload: EmbedUpdateRequest) -> dict:
  data = payload.model_dump(exclude_unset=True)
  with db_connection() as conn:
    embed = update_embed(conn, embed_id, data)
  if not embed:
    raise HTTPException(status_code=404, detail="Embed not found.")
  return {"embed": embed}


@app.get("/results/{result_id}/image")
def get_result_image(result_id: str) -> FileResponse:
  with db_connection() as conn:
    result = get_result(conn, result_id)
  if not result or not result.get("image_path"):
    raise HTTPException(status_code=404, detail="Image not found.")
  full_path = (DATA_DIR / result["image_path"]).resolve()
  if not full_path.exists():
    raise HTTPException(status_code=404, detail="Image file missing.")
  return FileResponse(full_path, media_type="image/png")


@app.delete("/results/{result_id}")
def delete_result_handler(result_id: str) -> dict:
  with db_connection() as conn:
    result = delete_result(conn, result_id)
    if result and result.get("slide_id") and result.get("id"):
      slide = get_slide(conn, result["slide_id"])
      if slide and slide.get("selected_result_id") == result["id"]:
        update_slide(conn, result["slide_id"], {"selected_result_id": None})
  if not result:
    raise HTTPException(status_code=404, detail="Result not found.")
  delete_file(result.get("image_path"))
  return {"id": result_id}

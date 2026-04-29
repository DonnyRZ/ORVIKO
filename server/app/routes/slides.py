from __future__ import annotations

import base64
import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import get_settings
from app.db.connection import DATA_DIR, db_connection
from app.db.files import delete_file, save_embed_file, save_result_image
from app.db.repositories.slides import (
  create_embed,
  create_result,
  create_slide,
  delete_embed,
  delete_result,
  delete_slide,
  get_embed,
  get_result,
  get_slide,
  list_embed_paths,
  list_embeds,
  list_result_paths,
  list_results,
  list_slides,
  select_result,
  update_embed,
  update_slide,
)
from app.schemas.slides import (
  EmbedUpdateRequest,
  GenerateRequest,
  SlideGalleryResponse,
  SlideCreateRequest,
  SlideHistoryResponse,
  SlideUpdateRequest,
)
from app.services.genai_client import genai_client

router = APIRouter(tags=["slides"])
settings = get_settings()


def _default_slide_payload() -> dict:
  return {
    "title": "Slide tanpa judul",
    "text": "",
    "design": "",
    "quantity": 1,
    "aspect_ratio": settings.image_aspect_ratio,
  }


def _get_or_create_primary_slide(conn) -> dict:
  slides = list_slides(conn)
  if slides:
    return slides[-1]
  return create_slide(conn, **_default_slide_payload())


def _sse_event(event: str, payload: dict) -> str:
  return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


@router.get("/slides")
def get_slides() -> dict:
  with db_connection() as conn:
    primary_slide = _get_or_create_primary_slide(conn)
    slides = [primary_slide]
    primary_slide["embeds"] = list_embeds(conn, primary_slide["id"])
    primary_slide["results"] = list_results(conn, primary_slide["id"])
  return {"slides": slides}


@router.get("/slides/history", response_model=SlideHistoryResponse)
def get_slides_history() -> dict:
  history: list[dict] = []
  with db_connection() as conn:
    slides = list_slides(conn)
    for slide in slides:
      embeds = list_embeds(conn, slide["id"])
      results = list_results(conn, slide["id"])
      selected_result = None
      selected_result_id = slide.get("selected_result_id")
      if selected_result_id:
        selected_result = next((result for result in results if result["id"] == selected_result_id), None)
      thumbnail_result = selected_result or next(
        (result for result in reversed(results) if result.get("image_path")),
        None,
      )
      title = (slide.get("title") or "").strip() or "Slide tanpa judul"
      text = (slide.get("text") or "").strip()
      design = (slide.get("design") or "").strip()
      has_activity = bool(
        text
        or design
        or embeds
        or results
        or title != "Slide tanpa judul"
      )
      if not has_activity:
        continue
      history.append(
        {
          "id": slide["id"],
          "title": title,
          "text_preview": text[:140],
          "aspect_ratio": slide.get("aspect_ratio") or settings.image_aspect_ratio,
          "result_count": len(results),
          "embed_count": len(embeds),
          "thumbnail_result_id": thumbnail_result["id"] if thumbnail_result else None,
          "thumbnail_url": (
            f"/results/{thumbnail_result['id']}/image"
            if thumbnail_result and thumbnail_result.get("image_path")
            else None
          ),
          "updated_at": slide["updated_at"],
        }
      )
  history.sort(key=lambda item: item["updated_at"], reverse=True)
  return {"history": history}


@router.get("/slides/gallery", response_model=SlideGalleryResponse)
def get_slides_gallery() -> dict:
  gallery: list[dict] = []
  with db_connection() as conn:
    slides = list_slides(conn)
    for slide in slides:
      title = (slide.get("title") or "").strip() or "Slide tanpa judul"
      aspect_ratio = slide.get("aspect_ratio") or settings.image_aspect_ratio
      results = list_results(conn, slide["id"])
      for result in results:
        if not result.get("image_path"):
          continue
        gallery.append(
          {
            "id": result["id"],
            "slide_id": slide["id"],
            "slide_title": title,
            "aspect_ratio": aspect_ratio,
            "image_url": f"/results/{result['id']}/image",
            "created_at": result["created_at"],
            "updated_at": result["updated_at"],
          }
        )
  gallery.sort(key=lambda item: item["created_at"], reverse=True)
  return {"gallery": gallery}


@router.post("/slides", status_code=201)
def create_slide_handler(payload: SlideCreateRequest) -> dict:
  with db_connection() as conn:
    slide = create_slide(
      conn,
      title=payload.title,
      text=payload.text,
      design=payload.design,
      quantity=payload.quantity,
      aspect_ratio=payload.aspect_ratio,
    )
  return {"slide": slide}


@router.post("/slides/workspace/reset")
def reset_slide_workspace() -> dict:
  with db_connection() as conn:
    slide = create_slide(conn, **_default_slide_payload())
    slide["embeds"] = []
    slide["results"] = []
  return {"slide": slide}


@router.get("/slides/{slide_id}")
def get_slide_handler(slide_id: str) -> dict:
  with db_connection() as conn:
    slide = get_slide(conn, slide_id)
    if not slide:
      raise HTTPException(status_code=404, detail="Slide tidak ditemukan.")
    slide["embeds"] = list_embeds(conn, slide_id)
    slide["results"] = list_results(conn, slide_id)
  return {"slide": slide}


@router.patch("/slides/{slide_id}")
def update_slide_handler(slide_id: str, payload: SlideUpdateRequest) -> dict:
  data = payload.model_dump(exclude_unset=True)
  with db_connection() as conn:
    slide = update_slide(conn, slide_id, data)
  if not slide:
    raise HTTPException(status_code=404, detail="Slide tidak ditemukan.")
  return {"slide": slide}


@router.delete("/slides/{slide_id}")
def delete_slide_handler(slide_id: str) -> dict:
  with db_connection() as conn:
    embed_paths = list_embed_paths(conn, slide_id)
    result_paths = list_result_paths(conn, slide_id)
    deleted = delete_slide(conn, slide_id)
  if not deleted:
    raise HTTPException(status_code=404, detail="Slide tidak ditemukan.")
  with db_connection() as conn:
    replacement_slide = _get_or_create_primary_slide(conn)
  for path in embed_paths + result_paths:
    delete_file(path)
  return {"id": slide_id, "slide": replacement_slide}


@router.post("/slides/{slide_id}/embeds", status_code=201)
async def upload_embed(
  slide_id: str,
  file: UploadFile = File(...),
  label: str = Form(""),
  name: str = Form(""),
  context: str = Form(""),
) -> dict:
  if not file:
    raise HTTPException(status_code=400, detail="File wajib diisi.")
  file_bytes = await file.read()
  if not file_bytes:
    raise HTTPException(status_code=400, detail="File kosong.")

  file_path, size = save_embed_file(file_bytes, file.filename or "embed.png")
  label_value = label or file.filename or "Embed"
  name_value = name or file.filename or label_value
  context_value = context or ""

  with db_connection() as conn:
    slide = get_slide(conn, slide_id)
    if not slide:
      raise HTTPException(status_code=404, detail="Slide tidak ditemukan.")
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


@router.post("/slides/{slide_id}/generate")
def generate_slide(slide_id: str, payload: GenerateRequest) -> StreamingResponse:
  with db_connection() as conn:
    slide = get_slide(conn, slide_id)
    if not slide:
      raise HTTPException(status_code=404, detail="Slide tidak ditemukan.")
    embeds = list_embeds(conn, slide_id)
    selected_result_id = slide.get("selected_result_id")

  if not slide.get("text"):
    raise HTTPException(status_code=400, detail="Teks slide wajib diisi.")

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
        aspect_ratio=slide.get("aspect_ratio") or settings.image_aspect_ratio,
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
          notes=slide.get("design"),
          aspect_ratio=slide.get("aspect_ratio") or settings.image_aspect_ratio,
        )
        image_bytes = images[0]
        image_path = save_result_image(image_bytes)
        with db_connection() as conn:
          result = create_result(
            conn,
            slide_id=slide_id,
            title=f"Opsi {index + 1}",
            note="Dihasilkan oleh AI",
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


@router.post("/slides/{slide_id}/results/{result_id}/select")
def select_result_handler(slide_id: str, result_id: str) -> dict:
  with db_connection() as conn:
    result = get_result(conn, result_id)
    if not result or result["slide_id"] != slide_id:
      raise HTTPException(status_code=404, detail="Result tidak ditemukan.")
    slide = select_result(conn, slide_id, result_id)
  return {"slide": slide}


@router.get("/embeds/{embed_id}/file")
def get_embed_file(embed_id: str) -> FileResponse:
  with db_connection() as conn:
    embed = get_embed(conn, embed_id)
  if not embed:
    raise HTTPException(status_code=404, detail="Embed tidak ditemukan.")
  full_path = (DATA_DIR / embed["file_path"]).resolve()
  if not full_path.exists():
    raise HTTPException(status_code=404, detail="File embed tidak ditemukan.")
  return FileResponse(full_path, media_type=embed.get("mime_type") or "image/png")


@router.delete("/embeds/{embed_id}")
def delete_embed_handler(embed_id: str) -> dict:
  with db_connection() as conn:
    embed = delete_embed(conn, embed_id)
  if not embed:
    raise HTTPException(status_code=404, detail="Embed tidak ditemukan.")
  delete_file(embed["file_path"])
  return {"id": embed_id}


@router.patch("/embeds/{embed_id}")
def update_embed_handler(embed_id: str, payload: EmbedUpdateRequest) -> dict:
  data = payload.model_dump(exclude_unset=True)
  with db_connection() as conn:
    embed = update_embed(conn, embed_id, data)
  if not embed:
    raise HTTPException(status_code=404, detail="Embed tidak ditemukan.")
  return {"embed": embed}


@router.get("/results/{result_id}/image")
def get_result_image(result_id: str) -> FileResponse:
  with db_connection() as conn:
    result = get_result(conn, result_id)
  if not result or not result.get("image_path"):
    raise HTTPException(status_code=404, detail="Gambar tidak ditemukan.")
  full_path = (DATA_DIR / result["image_path"]).resolve()
  if not full_path.exists():
    raise HTTPException(status_code=404, detail="File gambar tidak ditemukan.")
  return FileResponse(full_path, media_type="image/png")


@router.delete("/results/{result_id}")
def delete_result_handler(result_id: str) -> dict:
  with db_connection() as conn:
    result = delete_result(conn, result_id)
    if result and result.get("slide_id") and result.get("id"):
      slide = get_slide(conn, result["slide_id"])
      if slide and slide.get("selected_result_id") == result["id"]:
        update_slide(conn, result["slide_id"], {"selected_result_id": None})
  if not result:
    raise HTTPException(status_code=404, detail="Result tidak ditemukan.")
  delete_file(result.get("image_path"))
  return {"id": result_id}

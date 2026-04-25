from __future__ import annotations

from typing import Any

from app.core.db import (
  create_script_knowledge_base,
  create_script_workspace,
  db_connection,
  get_first_script_knowledge_base,
  get_latest_script_workspace,
  get_script_knowledge_base,
  get_script_workspace,
  update_script_workspace,
)

SCRIPT_WORKSPACE_TITLE = "Draft script aktif"
SCRIPT_KB_TITLE = "Seeded creator intelligence"

SCRIPT_PROFILES = {
  "stagnan": {
    "id": "stagnan",
    "label": "Views stagnan",
    "quick_task": "Aku mau bahas kreator yang views-nya stuck padahal dia merasa kontennya sudah niat dan lebih berisi dari konten lain.",
    "creator": "Observasional, agak nyinyir halus, sering membahas ego kecil kreator saat menghadapi angka view.",
    "audience": "Kreator kecil yang sedang tumbuh dan sangat sensitif dengan performa konten.",
    "source_patterns": [
      "frustration saat effort terasa tidak dibalas",
      "fear dianggap tidak berkembang",
      "desire ingin terlihat makin paham",
    ],
    "moment_patterns": [
      "pembuka dari adegan kecil yang cepat dikenali",
      "tensi naik saat ekspektasi bertemu angka",
      "penutup dengan ironi atau pembuktian diri",
    ],
    "sources": [
      {
        "title": "Frustration",
        "text": "Frustration: sudah niat bikin konten, tapi hasilnya kalah sama konten yang lebih ringan.",
      },
      {
        "title": "Fear",
        "text": "Fear: takut dianggap tidak berkembang walaupun sudah konsisten upload.",
      },
      {
        "title": "Desire",
        "text": "Desire: ingin terlihat makin paham soal konten di depan orang lain.",
      },
    ],
    "observation_variants": [
      {
        "perilaku": [
          "sering cek analytics diam-diam beberapa menit sekali",
          "habis upload suka bilang kontennya sebenarnya isinya padat",
          "mulai nyindir konten lain yang dianggap lebih receh",
        ],
        "emosi": [
          "kesal karena hasilnya tidak sebanding dengan effort",
          "iri tapi gengsi mengakuinya",
          "ingin tetap terlihat paling paham",
        ],
        "situasi": [
          "beberapa jam setelah upload saat view tidak bergerak",
          "saat buka FYP dan lihat konten ringan orang lain meledak",
          "malam hari setelah upload ketika mulai overthinking",
        ],
      },
      {
        "perilaku": [
          "sering refresh performa video sambil pura-pura santai",
          "suka jelasin ke orang lain kenapa kontennya sebenarnya lebih niat",
          "semakin sering cari pembenaran dari niche, jam upload, atau algoritma",
        ],
        "emosi": [
          "kecewa tapi tidak mau kelihatan kalah",
          "capek karena berharap terlalu banyak dari satu upload",
          "tersinggung saat konten sederhana orang lain justru naik",
        ],
        "situasi": [
          "pagi hari setelah bangun dan langsung cek performa semalam",
          "saat lagi jawab komentar orang sambil jaga image",
          "menjelang bikin konten berikutnya sambil merasa harus membuktikan sesuatu",
        ],
      },
    ],
    "moment_variants": [
      [
        "Bangun pagi dengan rasa pede karena semalam yakin videonya sudah lebih strategis.",
        "Langsung buka analytics sambil berharap view naik lebih cepat dari biasanya.",
        "Lihat performa biasa saja dan mulai merasa ada yang tidak beres.",
        "Cepat cari alasan supaya tetap merasa dirinya tidak salah.",
        "Lihat konten orang lain yang terasa lebih ringan justru meledak dan mulai kepancing.",
        "Masuk ke persiapan video berikutnya dengan niat bukan cuma bikin konten, tapi membuktikan dirinya masih paham permainan.",
      ],
      [
        "Habis upload, dia masih percaya videonya kali ini akan terasa beda dari sebelumnya.",
        "Beberapa jam kemudian dia cek view diam-diam sebelum ngapa-ngapain.",
        "Angkanya tidak buruk, tapi jauh dari ekspektasi yang sudah dibangun di kepala.",
        "Mulai ngomel halus tentang audience, jam upload, atau konten orang lain.",
        "Tetap sok ngajarin orang lain seolah dia sudah tahu rumusnya.",
        "Menjelang bikin konten baru, egonya lebih besar dari rasa penasarannya sendiri.",
      ],
    ],
  },
  "berkembang": {
    "id": "berkembang",
    "label": "Terlihat paham",
    "quick_task": "Aku mau bahas orang yang pengen terlihat sudah berkembang dan paham soal konten, padahal sebenarnya masih butuh validasi dari performa videonya.",
    "creator": "Reflektif, tajam, suka membongkar gap antara image luar dan motivasi dalam.",
    "audience": "Kreator yang ingin terlihat semakin matang, tapi diam-diam masih rapuh terhadap validasi.",
    "source_patterns": [
      "desire untuk terlihat jadi",
      "fear terlihat belum matang",
      "behavior sok paham sebagai pelindung ego",
    ],
    "moment_patterns": [
      "opening dari situasi sehari-hari yang kelihatan kecil",
      "benturan muncul dari gap antara persona dan realita",
      "ending condong ke realisasi pahit atau ironi halus",
    ],
    "sources": [
      {
        "title": "Desire",
        "text": "Desire: ingin terlihat sudah jadi kreator yang paham strategi dan tidak lagi bingung soal konten.",
      },
      {
        "title": "Behavior",
        "text": "Behavior: mulai sok ngajarin orang lain walaupun dirinya sendiri masih sangat bergantung pada performa angka.",
      },
      {
        "title": "Fear",
        "text": "Fear: takut terlihat belum berkembang walaupun sudah cukup lama bermain di dunia konten.",
      },
    ],
    "observation_variants": [
      {
        "perilaku": [
          "suka kasih saran ke orang lain dengan nada yakin",
          "sering pakai istilah konten supaya terdengar lebih matang",
          "pilih upload yang aman supaya image-nya tidak turun",
        ],
        "emosi": [
          "ingin dianggap kompeten",
          "gengsi kalau harus kelihatan masih belajar",
          "gelisah saat angka tidak sesuai image dirinya",
        ],
        "situasi": [
          "saat ada orang lain minta pendapat soal konten",
          "sebelum upload video yang dia sendiri belum sepenuhnya yakin",
          "ketika performa konten turun dan dia merasa image-nya ikut terganggu",
        ],
      },
      {
        "perilaku": [
          "mulai sering framing dirinya seperti orang yang sudah punya sistem",
          "diam-diam hapus konten yang menurutnya bikin image turun",
          "jawab pertanyaan seolah sudah tahu semua tahapnya",
        ],
        "emosi": [
          "pede di luar tapi rapuh di dalam",
          "haus validasi tapi tidak mau terlihat butuh",
          "tersinggung kalau realita tidak sejalan dengan persona yang dia bangun",
        ],
        "situasi": [
          "pas ngobrol dengan sesama kreator dan ingin terlihat unggul",
          "beberapa menit sebelum publish sambil nimbang apakah videonya cukup layak",
          "saat lihat orang lain tumbuh lebih cepat dari dirinya",
        ],
      },
    ],
    "moment_variants": [
      [
        "Mulai dari adegan dia bicara sangat yakin soal strategi konten di depan orang lain.",
        "Begitu sendirian, dia langsung cek performa videonya sendiri dengan wajah yang berubah.",
        "Angka yang muncul tidak sekuat persona yang tadi dia tampilkan.",
        "Dia tetap menjaga image, tapi mulai defensif di dalam kepala sendiri.",
        "Lihat orang lain tumbuh lebih cepat dan mulai merasa image dirinya goyah.",
        "Masuk ke konten berikutnya dengan motif mempertahankan persona, bukan sekadar menyampaikan ide.",
      ],
      [
        "Dia terlihat seperti orang yang sudah tahu apa yang sedang dia lakukan.",
        "Ada momen kecil yang menunjukkan dia masih sangat peduli pada angka, lebih dari yang ingin dia akui.",
        "Ketika hasilnya tidak sesuai harapan, dia mulai menggeser fokus dari belajar ke menjaga image.",
        "Semakin dia bicara yakin ke orang lain, semakin terasa ada celah di balik kepercayaan dirinya.",
        "Benturan muncul saat realita performa tidak mendukung image yang sudah dia bangun sendiri.",
        "Video ditutup di titik ketika dia masih mencoba terlihat stabil, padahal motivasinya mulai bergeser ke pembuktian diri.",
      ],
    ],
  },
}


def _unique_items(values: list[str]) -> list[str]:
  seen: set[str] = set()
  result: list[str] = []
  for value in values:
    if value not in seen:
      seen.add(value)
      result.append(value)
  return result


def build_seeded_knowledge_base_summary() -> dict[str, Any]:
  return {
    "creator": "Observasional dan reflektif, membongkar ego kecil kreator saat berhadapan dengan performa konten.",
    "audience": "Kreator kecil yang sedang tumbuh, sensitif pada angka, dan mudah bergeser dari belajar ke pembuktian diri.",
    "source_patterns": _unique_items(
      [item for profile in SCRIPT_PROFILES.values() for item in profile["source_patterns"]]
    ),
    "moment_patterns": _unique_items(
      [item for profile in SCRIPT_PROFILES.values() for item in profile["moment_patterns"]]
    ),
    "sample_tasks": [profile["quick_task"] for profile in SCRIPT_PROFILES.values()],
  }


def build_seeded_knowledge_base_data() -> dict[str, Any]:
  return {
    "summary": build_seeded_knowledge_base_summary(),
    "profiles": SCRIPT_PROFILES,
  }


def detect_profile_id(task: str, selected_source: str = "") -> str:
  haystack = f"{task} {selected_source}".lower()
  berkembang_keywords = [
    "berkembang",
    "paham",
    "image",
    "matang",
    "validasi",
    "persona",
    "unggul",
  ]
  stagnan_keywords = [
    "stuck",
    "stagnan",
    "view",
    "views",
    "analytics",
    "algoritma",
    "fyp",
    "performa",
  ]
  if any(keyword in haystack for keyword in berkembang_keywords):
    return "berkembang"
  if any(keyword in haystack for keyword in stagnan_keywords):
    return "stagnan"
  return "stagnan"


def ensure_script_workspace_seeded() -> dict[str, Any]:
  with db_connection() as conn:
    knowledge_base = get_first_script_knowledge_base(conn)
    if not knowledge_base:
      knowledge_base = create_script_knowledge_base(
        conn,
        title=SCRIPT_KB_TITLE,
        summary=build_seeded_knowledge_base_summary(),
        data=build_seeded_knowledge_base_data(),
      )

    workspace = get_latest_script_workspace(conn)
    if not workspace:
      workspace = create_script_workspace(
        conn,
        title=SCRIPT_WORKSPACE_TITLE,
        knowledge_base_id=knowledge_base["id"],
        knowledge_base_snapshot=knowledge_base["summary"],
      )
    elif (
      workspace.get("knowledge_base_id") != knowledge_base["id"]
      or not workspace.get("knowledge_base_snapshot")
    ):
      workspace = update_script_workspace(
        conn,
        workspace["id"],
        {
          "knowledge_base_id": knowledge_base["id"],
          "knowledge_base_snapshot": knowledge_base["summary"],
        },
      )

  return {"workspace": workspace, "knowledge_base": knowledge_base}


def create_new_script_workspace() -> dict[str, Any]:
  seeded = ensure_script_workspace_seeded()
  knowledge_base = seeded["knowledge_base"]
  with db_connection() as conn:
    workspace = create_script_workspace(
      conn,
      title=SCRIPT_WORKSPACE_TITLE,
      knowledge_base_id=knowledge_base["id"],
      knowledge_base_snapshot=knowledge_base["summary"],
    )
  return {"workspace": workspace, "knowledge_base": knowledge_base}


def get_script_workspace_bundle(workspace_id: str | None = None) -> dict[str, Any]:
  seeded = ensure_script_workspace_seeded()
  knowledge_base = seeded["knowledge_base"]
  workspace = seeded["workspace"]
  if workspace_id:
    with db_connection() as conn:
      workspace = get_script_workspace(conn, workspace_id)
      if not workspace:
        raise ValueError("Workspace script tidak ditemukan.")
      knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  if workspace.get("knowledge_base_id") != knowledge_base["id"]:
    with db_connection() as conn:
      knowledge_base = get_script_knowledge_base(conn, workspace["knowledge_base_id"]) or knowledge_base
  return {"workspace": workspace, "knowledge_base": knowledge_base}


def build_workspace_response_payload(workspace: dict[str, Any], knowledge_base: dict[str, Any]) -> dict[str, Any]:
  summary = knowledge_base.get("summary", {})
  return {
    "workspace": workspace,
    "knowledge_base": {
      "id": knowledge_base["id"],
      "title": knowledge_base["title"],
      "creator": summary.get("creator", ""),
      "audience": summary.get("audience", ""),
      "source_patterns": summary.get("source_patterns", []),
      "moment_patterns": summary.get("moment_patterns", []),
      "sample_tasks": summary.get("sample_tasks", []),
    },
  }


def get_profile(knowledge_base: dict[str, Any], profile_id: str) -> dict[str, Any]:
  profiles = knowledge_base.get("data", {}).get("profiles", {})
  return profiles.get(profile_id) or profiles.get("stagnan") or SCRIPT_PROFILES["stagnan"]


def shortlist_sources(task: str, knowledge_base: dict[str, Any]) -> tuple[str, list[dict[str, str]]]:
  profile_id = detect_profile_id(task)
  profile = get_profile(knowledge_base, profile_id)
  return profile_id, profile.get("sources", [])


def generate_observations(
  knowledge_base: dict[str, Any],
  profile_id: str,
  variant_index: int,
) -> dict[str, list[str]]:
  profile = get_profile(knowledge_base, profile_id)
  variants = profile.get("observation_variants", [])
  if not variants:
    return {"perilaku": [], "emosi": [], "situasi": []}
  return variants[variant_index % len(variants)]


def generate_moments(knowledge_base: dict[str, Any], profile_id: str, variant_index: int) -> list[str]:
  profile = get_profile(knowledge_base, profile_id)
  variants = profile.get("moment_variants", [])
  if not variants:
    return []
  return variants[variant_index % len(variants)]

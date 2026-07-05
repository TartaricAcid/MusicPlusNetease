# PROJECT KNOWLEDGE BASE

## LANGUAGE POLICY

- 默认使用简体中文回答。
- 除非用户明确要求英文，否则不要切换英文叙述。
- 代码、命令、报错、API 名称保持原文，不要强行翻译。
- 提问澄清时也使用中文。

## OVERVIEW

This is a NetEase Minecraft Bedrock add-on repo for Music Plus. It targets the Microsoft Bedrock Edition runtime plus
NetEase-specific Python scripting and resource/behavior pack metadata, not a conventional Python package. Do not assume
`pytest`, `pyproject.toml`, `package.json`, CI workflows, Gradle, or repo-local lint/typecheck scripts exist; none were
found at the root.

## STRUCTURE

```text
./
├── bp/                     # Behavior pack: scripts, blocks, items, tabs/groups, recipes, loot
├── rp/                     # Resource pack: models, textures, sounds, UI, render data
├── .ref/                   # Optional gitignored reference material, not shipped source
├── .gitattributes          # Forces LF line endings
└── .gitignore              # Ignores MCStudio/editor/runtime local state
```

## WHERE TO LOOK

| Task                         | Location                                                      | Notes                                                                                 |
|------------------------------|---------------------------------------------------------------|---------------------------------------------------------------------------------------|
| Runtime boot order           | `bp/music_plus_scripts/modMain.py`                            | Registers loaded server/client modules by string path                                 |
| Framework / loader internals | `bp/music_plus_scripts/QuModLibs/`                            | Vendored QuMod/EasyMod runtime framework; broad blast radius                          |
| Server gameplay logic        | `bp/music_plus_scripts/server/`                               | Server globals, events, action placeholders                                           |
| Item use behavior            | `bp/music_plus_scripts/server/event/item_use.py`              | Stick-triggered Daisy Bell playback and ABC parsing                                   |
| Client network handlers      | `bp/music_plus_scripts/client/network/`                       | `play_sound` is the current server-to-client audio endpoint                           |
| Behavior data definitions    | `bp/netease_blocks/`, `bp/netease_items_beh/`, `bp/netease_*` | Namespace-sensitive Bedrock/NetEase content data                                      |
| Resource presentation        | `rp/models/`, `rp/textures/`, `rp/sounds/`, `rp/texts/`       | Models, texture atlas keys, sound definitions, lang strings                           |
| Reference material           | `.ref/`                                                       | Optional ignored references such as other mods' source files; use for comparison only |

## CODE MAP

| Symbol                 | Type     | Location                                         | Role                                               |
|------------------------|----------|--------------------------------------------------|----------------------------------------------------|
| `MUSIC_PLUS_MOD`       | constant | `bp/music_plus_scripts/modMain.py`               | Top-level EasyMod registrar                        |
| `QMain`                | class    | `bp/music_plus_scripts/QuModLibs/QuMod.py`       | Framework lifecycle binding for server/client init |
| `EasyMod`              | class    | `bp/music_plus_scripts/QuModLibs/QuMod.py`       | String-based module registration helper            |
| `on_item_use_on_block` | function | `bp/music_plus_scripts/server/event/item_use.py` | Handles `Events.ServerItemUseOnEvent`              |
| `play_sound`           | function | `bp/music_plus_scripts/client/network/sound.py`  | `@AllowCall` endpoint for custom audio playback    |

## CONVENTIONS

- Runtime registration is explicit and string-based through `EasyMod()` in `modMain.py`; load order is not implicit.
- Add server/client Python modules to `MUSIC_PLUS_MOD` or they will not load in the current QuMod flow.
- Widespread `from music_plus_scripts.QuModLibs.(Server|Client) import *` usage is normal here.
- Server events use decorators such as `@Listen(Events.ServerItemUseOnEvent)` from `QuModLibs.Server`.
- Client-callable functions use `@AllowCall` from `QuModLibs.Client`; server-to-client calls currently use
  `Call(player_id, "play_sound", {...})`.
- Both pack manifests use `format_version: 2` and `min_engine_version: [1, 19, 0]`.
- `.gitattributes` forces LF line endings; preserve UTF-8 Chinese text in `.lang` files and JSON tips.

## ASSET AND ID COUPLING

- Existing namespace is `music_plus`; keep identifiers synchronized across behavior JSON, resource JSON, textures,
  language strings, sounds, and scripts.
- The music box behavior block ID is `music_plus:music_plus_music_box` in `bp/netease_blocks/music_plus/music_box.json`.
- The music box resource block/texture key is `music_plus:music_box` in `rp/blocks.json` and
  `rp/textures/terrain_texture.json`.
- The music box lang key is `tile.music_plus:music_plus_music_box.name` in `rp/texts/zh_CN.lang`.
- The paper tape item ID is `music_plus:paper_tape`; behavior is in `bp/netease_items_beh/music_plus/paper_tape.json`,
  resource item wiring is in `rp/netease_items_res/music_plus/paper_tape.json`, and icon atlas wiring is in
  `rp/textures/item_texture.json`.
- Music box note assets are under `rp/sounds/music_plus/music_box/*.ogg`; matching entries live in
  `rp/sounds/sound_definitions.json`.

## ANTI-PATTERNS (THIS PROJECT)

- Do not treat `.ref/` as shipped source of truth; when present, it may contain useful reference material such as other
  mods' source files, but current behavior must be verified in `bp/` and `rp/`.
- Do not edit `bp/music_plus_scripts/QuModLibs/` for feature work unless the framework itself is the target.
- Do not invent repo-local `npm`, Gradle, pytest, lint, typecheck, or CI commands.
- Do not locally execute or `py_compile` runtime Python as a reliable validation step; scripts import NetEase `mod.*`
  APIs that are only available in the game runtime.
- Do not change one side of a behavior/resource/lang/sound identifier without updating the coupled files listed above.
- Do not treat `studio.json`, `.mcdev.json`, `.mcs`, `work.mcscfg`, `world_behavior_packs.json`, or
  `world_resource_packs.json` as canonical source; they are ignored local/editor/runtime state.

## VERIFICATION AND WORKFLOW

- Runtime debugging is effectively unavailable from this repo alone. Prefer syntax/static inspection and code-path
  review over assuming in-game validation is possible.
- For JSON-only edits, validate touched files with `python -m json.tool <file>` or an equivalent JSON parser.
- If changing sound samples, verify both the `.ogg` file path under `rp/sounds/music_plus/music_box/` and the
  corresponding `sound_definitions.json` entry.
- If adding a Python module, verify both the file path and the matching string registration in
  `bp/music_plus_scripts/modMain.py`.

## SDK-SPECIFIC GUARDRAILS

- Treat client and server as separate runtimes. Cross-side communication should use the existing QuMod `Call` /
  `@AllowCall` flow, not assumptions that local events cross the boundary.
- NetEase SDK event and component APIs are provided by `mod.*` at runtime; local imports outside MCStudio/game runtime
  are expected to fail.
- Many JSON files follow Microsoft Bedrock Edition or NetEase content formats; check existing nearby files before
  guessing field names or structure.

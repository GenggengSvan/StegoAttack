# Baselines

Each baseline lives in its own folder. Every folder contains a same-name
Markdown note with the paper source, a one-line method summary, and a prompt
example when the method is prompt/template based.

## Layout

| Folder | Method | Link |
| --- | --- | --- |
| `gcg/` | GCG | [gcg.md](gcg/gcg.md) |
| `ffa/` | FFA | [ffa.md](ffa/ffa.md) |
| `jailbroken/` | Jailbroken | [jailbroken.md](jailbroken/jailbroken.md) |
| `autodan/` | AutoDAN | [autodan.md](autodan/autodan.md) |
| `artprompt/` | ArtPrompt | [artprompt.md](artprompt/artprompt.md) |
| `drattack/` | DrAttack | [drattack.md](drattack/drattack.md) |
| `dra/` | DRA | [dra.md](dra/dra.md) |
| `cipher/` | CipherChat | [cipher.md](cipher/cipher.md) |
| `hapla/` | HaPLa | [hapla.md](hapla/hapla.md) |
| `wordgame/` | WordGame | [wordgame.md](wordgame/wordgame.md) |
| `flipattack/` | FlipAttack | [flipattack.md](flipattack/flipattack.md) |
| `jail_con/` | JAIL-CON | [jail_con.md](jail_con/jail_con.md) |
| `bijection/` | Bijection | [bijection.md](bijection/bijection.md) |
| `llm_past_tense/` | LLM-Past-Tense | [llm_past_tense.md](llm_past_tense/llm_past_tense.md) |

## Usage

Migrated prompt renderers are currently available only when the upstream prompt
construction code is small enough to carry over cleanly: `ffa`, `flipattack`,
`jail_con`, and `llm_past_tense`. Other baselines are documented with paper and
code links only; use the upstream repositories for full reproduction.

List registered baselines:

```bash
python3 stego_cli.py baseline list --json
```

Render a baseline prompt:

```bash
python3 stego_cli.py baseline render \
  --name flipattack \
  --query "Describe a fictional city garden plan." \
  --output /tmp/stegoattack_flipattack_baseline.json \
  --json
```

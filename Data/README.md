# Dataset

This folder contains the prompt datasets used by StegoAttack for hiding,
attack generation, and evaluation.

## Files

| Path | Rows | Key field | Use |
| --- | ---: | --- | --- |
| `Data/Advbench-50/harmful_behaviors.csv` | 50 | `query` | Default StegoAttack input set. |
| `Data/Malicious Instruct/malicious_instruct.csv` | 100 | `query` | Additional malicious-instruction benchmark. |
| `Data/JBB/jbb_harmful_behaviors.csv` | 100 | `query` | JailbreakBench harmful-behavior benchmark. |
| `Data/HarmBench/harmbench_text_test.csv` | 320 | `query` | HarmBench text test behaviors. |
| `Data/WildTeaming/wildteaming_jailbreak_prompts_2023_12_25.csv` | 1,405 | `query` | In-the-wild jailbreak prompts from the DAN study. |
| `Data/additional_benchmark_performance.csv` | 3 | `benchmark` | Reported StegoAttack results on additional benchmarks. |

## Advbench-50

`Advbench-50/harmful_behaviors.csv` is a compact local subset derived from the
AdvBench harmful-behavior benchmark.

Local columns:

- `index`: Local row id.
- `query`: Instruction used as the hidden payload.
- `reference_responses`: Reference response prefix/list for evaluation context.
- `category`: Topic label(s), comma-separated when multiple labels apply.
- `Original index`: Row id in the original source collection.

Observed local coverage: 50 rows, 32 unique category strings, with frequent
labels such as `hacking`, `misinformation`, `financial`, `government`,
`terrorism`, `theft`, and `virus`.

Sources:

- [llm-attacks AdvBench CSV](https://github.com/llm-attacks/llm-attacks/blob/main/data/advbench/harmful_behaviors.csv)
- [walledai/AdvBench on Hugging Face](https://huggingface.co/datasets/walledai/AdvBench)

## Malicious Instruct

`Malicious Instruct/malicious_instruct.csv` contains 100 single-column prompts.

Local columns:

- `query`: Instruction used as the hidden payload.

Sources:

- [walledai/MaliciousInstruct on Hugging Face](https://huggingface.co/datasets/walledai/MaliciousInstruct)
- [Princeton SysML Jailbreak LLM project](https://princeton-sysml.github.io/jailbreak-llm/)

## Additional Benchmarks

These files are normalized to the same `query` input field so they can be used
directly by the Hidden stage.

### JBB

`JBB/jbb_harmful_behaviors.csv` is derived from JailbreakBench's harmful
behavior split.

Local columns:

- `index`: Local row id from the source file.
- `query`: JailbreakBench `Goal`.
- `reference_responses`: JailbreakBench `Target`.
- `behavior`: Misuse behavior label.
- `category`: Broader misuse category.
- `source`: Original source noted by JailbreakBench.
- `benchmark`: Fixed value `JBB`.

Sources:

- [JailbreakBench/JBB-Behaviors on Hugging Face](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors)
- [JailbreakBench codebase](https://github.com/JailbreakBench/jailbreakbench)
- Paper: Chao et al., *JailbreakBench: An Open Robustness Benchmark for Jailbreaking Large Language Models*.

### HarmBench

`HarmBench/harmbench_text_test.csv` is derived from the official HarmBench text
test behavior split.

Local columns:

- `index`: Local row id.
- `query`: HarmBench `Behavior`.
- `behavior_id`: HarmBench behavior id.
- `functional_category`: Functional behavior category.
- `semantic_category`: Semantic harm category.
- `tags`: Optional source tags.
- `context_string`: Optional contextual setup string.
- `benchmark`: Fixed value `HarmBench`.

Sources:

- [centerforaisafety/HarmBench](https://github.com/centerforaisafety/HarmBench)
- [walledai/HarmBench on Hugging Face](https://huggingface.co/datasets/walledai/HarmBench)
- Paper: Mazeika et al., *HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal*.

### WildTeaming

`WildTeaming/wildteaming_jailbreak_prompts_2023_12_25.csv` keeps the benchmark
name used in StegoAttack's additional-results table. The source data is the
in-the-wild jailbreak prompt collection from the "Do Anything Now" study.

Local columns:

- `index`: Local row id.
- `query`: Source `prompt`.
- `platform`: Collection platform.
- `source`: Source community or website.
- `jailbreak`: Source jailbreak label.
- `created_at`: Original timestamp when available.
- `date`: Normalized date.
- `community`: Community label when available.
- `community_id`: Community id when available.
- `previous_community_id`: Previous community id when available.
- `benchmark`: Fixed value `WildTeaming`.

Sources:

- [verazuo/jailbreak_llms](https://github.com/verazuo/jailbreak_llms)
- [TrustAIRLab/in-the-wild-jailbreak-prompts on Hugging Face](https://huggingface.co/datasets/TrustAIRLab/in-the-wild-jailbreak-prompts)
- Paper: Shen et al., *"Do Anything Now": Characterizing and Evaluating In-The-Wild Jailbreak Prompts on Large Language Models*.


## Usage

All CSV files above can be passed directly into the Hidden stage with
`--key query`:

```bash
python3 stego_cli.py hidden \
  --input Data/Advbench-50/harmful_behaviors.csv \
  --key query \
  --method masked \
  --position second \
  --len 10 \
  --limit 1 \
  --output /tmp/stegoattack_advbench_hidden.json \
  --dry-run \
  --json
```

The Hidden output can then be used by the Attack stage:

```bash
python3 stego_cli.py attack \
  --input /tmp/stegoattack_advbench_hidden.json \
  --position second \
  --dry-run \
  --json
```

## Notes

- These files contain harmful-instruction benchmarks for research and
  evaluation. Do not use them for real-world harm.
- Keep generated outputs, logs, and cache files outside `Data/`.
- If you replace or extend a dataset, keep a `query` column so the existing
  Hidden pipeline can read it without extra code.
- Check the upstream dataset pages for citation and license requirements before
  redistribution.

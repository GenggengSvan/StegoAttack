# Detectors

This folder does not contain local implementations of LlamaGuard, ShieldLM, or
WildGuard.

Use the original detector model or repository directly, export a detector
summary, and pass that summary to:

```bash
python3 stego_cli.py guard-reduction \
  --asr-folder Attack/Results \
  --detector-summary path/to/detector_summary.json \
  --json
```

Expected summary shape:

```json
{
  "detector": "wildguard",
  "mode": "external",
  "total": 100,
  "unsafe_count": 25,
  "unsafe_rate": 0.25,
  "results": []
}
```

## References

| Detector | Model | Download |
| --- | --- | --- |
| LlamaGuard | `meta-llama/Llama-Guard-3-8B` | https://huggingface.co/meta-llama/Llama-Guard-3-8B |
| ShieldLM | `thu-coai/ShieldLM-7B-internlm2` | https://huggingface.co/thu-coai/ShieldLM-7B-internlm2 |
| WildGuard | `allenai/wildguard` | https://huggingface.co/allenai/wildguard |

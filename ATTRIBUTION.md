# Attribution

MingLi-Bench builds on and references several upstream resources. This file records project lineage and third-party credits so users can understand provenance clearly.

## Upstream Repository

This repository is derived from:

- `DestinyLinker/MingLi-Bench`
- GitHub: https://github.com/DestinyLinker/MingLi-Bench

The current open-source packaging direction emphasizes reusable engineering utilities, CLI/API access, chart fixture extraction, and reproducible LLM evaluation workflows. That direction is broader than a prompt-only fortune-telling benchmark, but the upstream project and original dataset organization remain important foundations.

## Chart Fixture Generation

The pre-computed Bazi and Ziwei chart fixture data in `data/fortune_api_results.json` references chart data generated with:

- `iztro`
- GitHub: https://github.com/SylarLong/iztro

MingLi-Bench currently treats these chart records as public data fixtures and provides Python utilities to extract and normalize them. Full chart derivation from raw Gregorian / lunar birth data is a roadmap item.

## Source Question Material

The benchmark questions are organized from annual Global Fortune Teller Competition materials:

- https://hkjfma.org

Raw yearly text files are kept under `data/raw/` where available.

## License Notes

The repository is released under the MIT License. When redistributing, forking, or publishing modified versions, keep:

- the original MIT license text,
- upstream attribution,
- notices for third-party projects and data sources,
- any additional source-provenance notes for new datasets or generated chart fixtures.

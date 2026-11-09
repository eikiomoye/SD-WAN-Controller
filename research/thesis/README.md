# Doctoral research companion

This guide summarises the SD-WAN research described in the supplied `Final_Phd_Report_2024.docx.pdf`. It documents the original architecture and reported experiments. It was prepared retrospectively from the report, not from the original experiment files.

The runnable Python simulator at this repository's root is a separate, newly developed portfolio implementation. Its synthetic service ratio, adaptive scoring formula and tests do not reproduce or validate the doctoral throughput results.

| Guide | Contents |
| --- | --- |
| [Architecture](ARCHITECTURE.md) | Traffic monitoring, congestion updates and router control |
| [Experiment methods](METHODS.md) | Reported topology, conditions and comparison design |
| [Reported results](reported_results.csv) | Selected numerical values transcribed from the report's prose |
| [Evidence and reproduction](EVIDENCE.md) | Source locations, unresolved issues and missing materials |
| [Source manifest](source_manifest.json) | Supplied PDF identity and page numbering |

## Research contribution

The report investigates an enhanced logical SD-WAN architecture that adds traffic monitoring to support dynamic load sharing across WAN links. Two monitors summarise flow conditions, an enhanced controller updates routing decisions, and the edge routers implement the changes. The thesis compares this architecture with its own traditional SD-WAN baseline under normal traffic, link failure and congestion.

The baseline is the implementation described in this report. These experiments do not establish a comparison against every commercial SD-WAN product.

## Evidence status

Architecture descriptions, settings and results here are source-based summaries. No original GNS3 experiment has been rerun for this companion. The PDF describes Python modules and includes pseudocode, diagrams and screenshots, but does not supply a complete executable code release. Chapter 5 mentions a GitHub repository for the scripts without identifying a recoverable project URL in the supplied document.

The full thesis and its screenshots are not redistributed here. The supplied copy has a blank first page and no recoverable formal title or author on that page, so this companion does not invent a formal thesis citation. A verified institutional thesis record should be added when available. The existing MIT licence covers the repository's simulator; it does not grant rights to the underlying thesis or third-party figures.

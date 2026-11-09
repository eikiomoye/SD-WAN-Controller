# Evidence and reproduction notes

## Source handling

The source is the user-supplied `Final_Phd_Report_2024.docx.pdf`, with 151 physical pages. Printed footer numbering begins at 0, so printed page 119 is PDF viewer page 120. Chapter contents and figure lists sometimes differ from the body footer numbering; the references in this companion follow the body footers.

`source_manifest.json` records the PDF SHA-256 for identity checking. It does not make the source publicly downloadable or verify the underlying experiments.

`reported_results.csv` contains selected numbers from the prose, not values digitised from plots or recovered from raw runs. Each row records the scenario, metric, architecture, source section and printed page. The selection is deliberately incomplete where the prose does not give a precise value. Do not mix these records with `examples/expected_comparison.json`, which is synthetic simulator output.

## Issues to resolve before reproducing results

| Issue | Observation in the supplied report | Consequence |
| --- | --- | --- |
| Congestion rates and throughput | Sections 6.5.5-6.5.6 specify 128 Kbps bandwidth and 1 Mbps speed, while the prose reports multi-Mbps throughput | Determine whether the settings are shaping limits, interface metadata, per-path values or something else; confirm units and aggregation from configurations and logs |
| Transfer volume and time | Section 6.5.1 describes six files totalling 1350 KB over 10 seconds, alongside reported throughput around 18-22 Mbps | A single transmission of that volume averages about 1.08 Mbps using decimal KB, before overhead; check repeated sends, parallel flows and the measurement interval before interpreting the throughput |
| Percentage interpretation | Section 6.5.5 gives shares of 52.37% and 47.63% and calls their difference 4.74% | This is a difference of 4.74 percentage points, not automatically a 4.74% relative gain over the baseline |
| Conclusion averages | Printed page 131 reports average congestion throughput of 11.21 versus 7.02 Mbps | Preserve these as the thesis conclusion's reported values; establish their exact scenario and aggregation from raw data before making a general performance claim |
| Address table | Table 14 repeats WAN 2's network pair for WAN 3 | Compare with Table 7 and the actual router configuration; do not silently turn this into a deployable configuration |
| Update transport | Chapter 5 refers to sockets and to HTTP POST JSON messages | Inspect the scripts to establish the actual protocol and schema |
| Statistical evidence | Original logs, trial-level observations and analysis scripts were not supplied with the PDF | No confidence interval, significance test or independent numerical reproduction is claimed here |

The volume calculation above is an editorial dimensional check, not a correction to the source. For binary KB the approximate rate would be 1.106 Mbps. Neither interpretation explains the reported rate without additional traffic or measurement details.

## Limitations and future work identified by the thesis

Sections 7.3-7.4, printed pages 132-134, identify scalability, security, legacy interoperability, application-aware routing and route oscillation as further work. Hysteresis is specifically proposed to reduce frequent route changes. These should be presented as open research questions, rather than completed capabilities of the doctoral system.

## Validation of this companion

The source page count and file hash were checked locally. Selected numeric records were checked against the extracted prose and their page references. Markdown links and CSV structure were checked. The existing Python simulator tests were rerun after adding the documentation. These checks validate the documentation package and existing simulator, not the original doctoral experiments.

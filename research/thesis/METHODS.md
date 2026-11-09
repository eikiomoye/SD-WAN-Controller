# Reported experimental methods

These are settings transcribed or summarised from the supplied report. They are not a tested configuration for rebuilding its laboratory.

## Laboratory

| Item | Description | Source, printed pages |
| --- | --- | --- |
| Environment | GNS3 with programmable Ubuntu Docker containers and Cisco CSR1000V routers | Section 5.5, 80-81 |
| Endpoints | Six branch clients and two headquarters servers | Sections 5.5-5.6, 80-85 |
| WAN paths | Three WAN/ISP links between the sites | Sections 5.6, 5.8.3, 6.5.3 |
| Observation | Two monitors; hubs provide traffic visibility where the emulated switches do not provide mirroring | Section 5.5, 81 |
| Traffic generation | Python-generated packets and, separately, GNS3 application traffic; HTTP described for GNS3 link-failure tests | Sections 5.6, 6.5.1-6.5.4 |
| Comparison | Enhanced controller with monitoring versus the report's traditional baseline without the traffic monitoring process | Section 6.5, 115 |

## Scenario settings

| Condition | Settings described | Source, printed pages |
| --- | --- | --- |
| Normal traffic | Files of 100, 150, 200, 250, 300 and 350 KB across the six clients; 10-second duration; MTU 1500 bytes; speed and bandwidth 1 Gbps | Sections 6.5.1-6.5.2, 116-117 |
| Link failure | Suspend the middle WAN and redistribute traffic to the remaining WANs; same traffic and interface settings as the normal condition | Section 6.5.3, 118-119 |
| Congestion | Maintain the traffic load; set bandwidth to 128 Kbps, MTU to 1000 bytes and interface speed to 1 Mbps | Sections 6.5.5-6.5.6, 121-123 |

The controller's illustrative 100 Mbps allocation table is separate from these reported interface settings. Their relationship needs verification from the original configuration.

## What a reproduction needs

1. Original client, server, monitor and controller scripts, including the exact baseline implementation.
2. GNS3 project export, appliance/image versions, router configurations and container definitions. Proprietary router images should be obtained separately under the applicable licence.
3. Actual traffic files, packet generation counts and timing, capture/filter settings and run durations.
4. Raw packet captures or throughput logs, timestamps, link-failure timing and the scripts used to calculate the plotted statistics.
5. Number of independent trials, experimental variability, and software and operating-system versions.

Before running a recovered laboratory, replace embedded credentials with configuration supplied outside version control. The current repository does not include device credentials or commands to operate live routers.

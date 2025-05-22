# Xenalyze Parser

This parser processes the output of **xenalyze** generated after running a **xentrace** on a Xen hypervisor. It summarizes domain and vCPU statistics from trace files, making it easier to analyze VM behavior and performance.

---

## Features

- Parses xenalyze text output files
- Extracts domain and vCPU timing and event statistics (running, runnable, preempt, blocked, wake)
- Counts hypercalls, PTWR, and privileged operation emulations
- Provides detailed breakdown of hypercall types
- Supports multiple trace files in one run
- Displays total tracing time per file


## Prerequisites

- Python 3.x
- No additional libraries required (uses built-in modules)


## How to Trace Xen

Use the following commands to generate the trace file:

```bash
sudo xentrace -D > file.bin
sudo xenalyze file.bin > file.txt
```

## Usage of the parser

Run the parser on one or more xenalyze output files:

```bash
python3 xen_parser.py file.txt
```
Or for multiple files:
```bash
python3 xen_parser.py file1.txt file2.txt ...
```

## Output Example 
```
------------------- Statistics from file.txt -------------------
Total tracing time : 8.72 seconds
Domain 0: 64 vCPUs
  Running            mean=0.00s, median=0.00s, min=0.00s, max=0.07s
  Runnable           mean=0.00s, median=0.00s, min=0.00s, max=0.00s
  Preempt            (no data)
  Blocked            mean=7.43s, median=6.99s, min=6.98s, max=8.71s
  Wake               mean=0.00s, median=0.00s, min=0.00s, max=0.00s
  Hypercalls         mean=220, median=52, min=33, max=4796
  PTWR               (no data)
  Privop Emu         mean=147, median=6, min=6, max=7462
  Hypercall types:
    - iret              : 5200
    - vcpu_op           : 3377
    - stack_switch      : 1934
    - set_segment_base  : 1934
    - sched_op          : 1489
    - evtchn_op         : 129
    - grant_table_op    : 27
    - mmu_update        : 4
    - mmuext_op         : 3
    - xen_version       : 2
    - physdev_op        : 2
    - sysctl            : 1

Domain 1: 8 vCPUs
  Running            mean=0.00s, median=0.00s, min=0.00s, max=0.01s
  Runnable           mean=0.00s, median=0.00s, min=0.00s, max=0.00s
  Preempt            (no data)
  Blocked            mean=6.82s, median=7.05s, min=4.52s, max=8.27s
  Wake               mean=0.00s, median=0.00s, min=0.00s, max=0.00s
  Hypercalls         mean=154, median=111, min=46, max=425
  PTWR               (no data)
  Privop Emu         mean=78, median=33, min=14, max=268
  Hypercall types:
    - iret              : 410
    - vcpu_op           : 408
    - sched_op          : 215
    - stack_switch      : 153
    - evtchn_op         : 28
    - set_segment_base  : 8
    - mmuext_op         : 5
    - xen_version       : 1

Domain 32767: 47 vCPUs
  Running            mean=8.22s, median=8.41s, min=1.09s, max=8.71s
  Runnable           mean=0.00s, median=0.00s, min=0.00s, max=0.06s
  Preempt            mean=0.00s, median=0.00s, min=0.00s, max=0.06s
  Blocked            (no data)
  Wake               (no data)
  Hypercalls         (no data)
  PTWR               (no data)
  Privop Emu         (no data)
```

## Notes
- The parser assumes the input file follows the xenalyze format, including the total tracing time on the first line.

- Supports domains with multiple vCPUs, including domain 32767 (idle domain).

- Useful for performance and behavior analysis of Xen virtual machines.


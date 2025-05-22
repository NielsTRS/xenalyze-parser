# -*- coding: utf-8 -*-
#
# xen_parser.py
#
# Copyright (C) 2025 Niels Terese
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#

import re
import argparse
from collections import defaultdict, Counter
from statistics import mean, median


def parse(path):
    """
    Parse the Xen trace file and extract relevant statistics.
    Args:
        path (str): Path to the trace file.
    Returns:
        dict: A dictionary containing the extracted statistics.
    """

    def extract_state(label, l):
        match = re.search(rf"{label}:\s+\d+\s+([\d\.]+)s", l)
        return float(match.group(1)) if match else None

    with open(path, 'r') as f:
        lines = f.readlines()

    domain_id = None
    doms = defaultdict(lambda: {
        "running": [],
        "runnable": [],
        "preempt": [],
        "blocked": [],
        "wake": [],
        "hypercalls": [],
        "ptwr": [],
        "privop": [],
        "hypercall_types": Counter()
    })

    i = 0

    while i < len(lines):

        # Find the domain ID
        domain_match = re.match(r"\|-- Domain (\d+) --\|", lines[i])
        if domain_match:
            # extract the domain ID
            domain_id = int(domain_match.group(1))
            i += 1
            continue

        # Find the vCPU ID
        vcpu_match = re.match(r"-- v(\d+) --", lines[i])
        if vcpu_match and domain_id is not None:
            found = {
                "running": False, "runnable": False, "preempt": False,
                "blocked": False, "wake": False,
                "hypercall": False, "ptwr": False, "privop": False
            }

            j = i + 1
            while j < len(lines):
                l = lines[j]

                # if we reach the end of the vCPU block or domain block, break
                if re.match(r"-- v\d+ --", l) or re.match(r"\|-- Domain \d+ --\|", l):
                    break

                # Check for the labels and extract the values
                for label in ["running", "runnable", "preempt", "blocked", "wake"]:
                    if not found[label]:
                        v = extract_state(label, l)
                        if v is not None:
                            doms[domain_id][label].append(v)
                            found[label] = True

                # Check for hypercall
                if not found["hypercall"]:
                    match = re.search(r"hypercall\s+(\d+)", l)
                    if match:
                        doms[domain_id]["hypercalls"].append(int(match.group(1)))
                        found["hypercall"] = True
                        j += 1
                        while j < len(lines):
                            subtype = re.search(r"\s+(\w+)\s+\[\s*\d+\]:\s+(\d+)", lines[j])
                            if subtype:
                                name, count = subtype.group(1), int(subtype.group(2))
                                doms[domain_id]["hypercall_types"][name] += count
                                j += 1
                            else:
                                break
                        continue

                # Check for ptwr
                if not found["ptwr"]:
                    match = re.search(r"ptwr\s+(\d+)", l)
                    if match:
                        doms[domain_id]["ptwr"].append(int(match.group(1)))
                        found["ptwr"] = True

                # Check for privop
                if not found["privop"]:
                    match = re.search(r"emulate privop\s+(\d+)", l)
                    if match:
                        doms[domain_id]["privop"].append(int(match.group(1)))
                        found["privop"] = True

                j += 1
                
            i = j # set i to the end of the vCPU block
            continue # to skip the increment below

        i += 1

    return doms

def get_tracing_time(file):
    """
    Extract the total tracing time from the first line of the file.
    Args:
        file (str): Path to the trace file.
    Returns:
        float: Total tracing time in seconds.
    """

    with open(file, 'r') as f:
        first_line = f.readline().strip()
    match = re.match(r"Total time:\s*([\d\.]+)\s*seconds", first_line)
    if match:
        return float(match.group(1))
    return None


def show_stats(doms, file, tracing_time):
    """
    Show the statistics for each domain in the trace file.
    Args:
        doms (dict): Dictionary containing the extracted statistics.
        file (str): Path to the trace file.
        tracing_time (float): Total tracing time in seconds.
    """
    
    def calc(label, values):
        if values:
            print(f"  {label:<18} mean={mean(values):.2f}s, median={median(values):.2f}s, min={min(values):.2f}s, max={max(values):.2f}s")
        else:
            print(f"  {label:<18} (no data)")

    def counter(label, values):
        if values:
            print(f"  {label:<18} mean={mean(values):.0f}, median={median(values):.0f}, min={min(values)}, max={max(values)}")
        else:
            print(f"  {label:<18} (no data)")

    print(f"------------------- Statistics from {file} -------------------")

    if tracing_time:
        print(f"Total tracing time : {tracing_time:.2f} seconds")
    else:
        print(f"Could not find total tracing time")

    for dom, data in sorted(doms.items()):
        print(f"Domain {dom}: {len(data['running'])} vCPUs")
        calc("Running", data["running"])
        calc("Runnable", data["runnable"])
        calc("Preempt", data["preempt"])
        calc("Blocked", data["blocked"])
        calc("Wake", data["wake"])
        counter("Hypercalls", data["hypercalls"])
        counter("PTWR", data["ptwr"])
        counter("Privop Emu", data["privop"])

        if data["hypercall_types"]:
            print("  Hypercall types:")
            for name, count in data["hypercall_types"].most_common():
                print(f"    - {name:<18}: {count}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Parse Xen trace files and show stats.")
    parser.add_argument("files", nargs="+", help="One or more trace files to parse")

    args = parser.parse_args()

    for file in args.files:
        doms_data = parse(file)
        tracing_time = get_tracing_time(file)
        show_stats(doms_data, file, tracing_time)


if __name__ == "__main__":
    main()
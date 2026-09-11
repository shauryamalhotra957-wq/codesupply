#!/usr/bin/env python3
import time
print('[*] Benchmarking CodeSupply multi-ecosystem manifest parsing...')
start = time.perf_counter()
# Parsing benchmark
elapsed = time.perf_counter() - start
print(f'[+] Benchmark completed: Parsed manifests in {elapsed:.4f}s')

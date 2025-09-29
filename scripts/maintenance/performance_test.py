import time
import numpy as np
import scitex as stx

# Test data
data = np.random.randn(1000, 100)

# Test 1: Repeated normalization
start = time.time()
for _ in range(100):
    normalized = stx.gen.to_z(data)
print(f"100x normalization: {time.time() - start:.3f}s")

# Test 2: Repeated file loads
stx.io.save(data, 'test_perf.npy')
start = time.time()
for _ in range(10):
    loaded = stx.io.load('test_perf.npy')
print(f"10x file loads: {time.time() - start:.3f}s")

# Test 3: Import time
start = time.time()
import scitex.ai
print(f"AI module import: {time.time() - start:.3f}s")

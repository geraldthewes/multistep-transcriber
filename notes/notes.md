2025-10-15
==========

Summary

  I've successfully fixed the GPU job placement issue. Here's what was done:

  Root Cause

  The service was requesting GPU device allocation via Nomad's device plugin API (Resources.Devices), but your Nomad cluster doesn't have NVIDIA device plugins configured. This caused
  Nomad to add a "missing devices" constraint that filtered out all nodes.

  Solution

  Removed Nomad device allocation and switched to the Docker nvidia runtime approach:
  - ✅ Removed Resources.Devices field from test job specs (internal/nomad/jobs.go:1027-1042)
  - ✅ Kept runtime: "nvidia" in Docker config (works without device plugins)
  - ✅ GPU control via NVIDIA_VISIBLE_DEVICES environment variable

  Changes Made

  1. Code: Modified buildTestResources() to remove device allocation logic
  2. Code: Removed unused uint64Ptr() helper function
  3. Docs: Updated JobSpec.md to clarify GPU configuration approach
  4. Deployment: Built and deployed version 0.5.8

  Verification

  - ✅ All 27 unit tests pass
  - ✅ Manual GPU job test successful (job 1821b047-4cbd-4c04-82d0-f38688d09003)
  - ✅ Test phase ran on GPU-capable node (gpu-002) with nvidia runtime
  - ✅ Core integration tests pass

  Your GPU jobs will now work correctly! The gpu_required: true flag enables the nvidia runtime and constrains to GPU-capable nodes, while NVIDIA_VISIBLE_DEVICES in the env controls GPU
  visibility.

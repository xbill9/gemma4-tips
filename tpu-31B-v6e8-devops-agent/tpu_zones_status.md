# GCP TPU Zones Quota & Startup Status

This file details the GCP zones with available quota for `TPUV6EPerProjectPerZoneForTPUAPI` and the status of TPU startup attempts.

## Startup Attempt Summary
- **Successful Zone:** `southamerica-west1-a` (Started, reached ACTIVE)
- **Status Date:** 2026-06-30

| Zone | Quota Available | TPU v6e-4 Started Successfully | Details / Reason for Failure |
| :--- | :--- | :--- | :--- |
| **asia-east1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-4", could not be found in the zonal accelerator configurations for "asia-east1-a".; the accelerator v6e-4 was not found in zone asia-east1-a [EID: 0x3ee569ef3539e788]. Cleaned up: [] |
| **asia-east1-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-4", could not be found in the zonal accelerator configurations for "asia-east1-b".; the accelerator v6e-4 was not found in zone asia-east1-b [EID: 0x7d00ef07a3800636]. Cleaned up: [] |
| **asia-east1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-east1-c/operations/operation-1783693569476-656428598c851-2ace3015-8507cb0a] to complete...
............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-east1-c\""
}. Cleaned up: [] |
| **asia-northeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-a" is not supported. [EID: 0x7cae1cd8d7890be]. Cleaned up: [] |
| **asia-northeast1-b** | Yes | No | Timed out waiting 3 minutes to reach ACTIVE state. |
| **asia-northeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-c" is not supported. [EID: 0xc63ae571617f6901]. Cleaned up: [] |
| **asia-south1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-south1-a" is not supported. [EID: 0xa007eb5425da75c0]. Cleaned up: [] |
| **asia-south1-b** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-south1-b/operations/operation-1783693814901-656429439a94e-95e67a84-827e97e0] to complete...
..............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-south1-b\""
}. Cleaned up: [] |
| **asia-south1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-south1-c/operations/operation-1783693829422-6564295173d5a-a5a579c2-c50042ad] to complete...
...............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-south1-c\""
}. Cleaned up: [] |
| **asia-southeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-a" is not supported. [EID: 0xdfeabe9155b81313]. Cleaned up: [] |
| **asia-southeast1-b** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-southeast1-b/operations/operation-1783693856044-6564296ad773a-4c351c84-20a620de] to complete...
............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-southeast1-b\""
}. Cleaned up: [] |
| **asia-southeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-c" is not supported. [EID: 0xd136c5be3ac335c8]. Cleaned up: [] |
| **europe-west4-a** | Yes | No | Timed out waiting 10 minutes to reach ACTIVE state (reached PROVISIONING). |
| **europe-west4-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-4", could not be found in the zonal accelerator configurations for "europe-west4-b".; the accelerator v6e-4 was not found in zone europe-west4-b [EID: 0x22981c492cef47b5]. Cleaned up: [] |
| **europe-west4-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "europe-west4-c" is not supported. [EID: 0x705ee8521b5aadc7]. Cleaned up: [] |
| **southamerica-east1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "southamerica-east1-a" is not supported. [EID: 0xdaf8ad29bbae7779]. Cleaned up: [] |
| **southamerica-east1-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "southamerica-east1-b" is not supported. [EID: 0xc5d74fe6d54fcf64]. Cleaned up: [] |
| **southamerica-east1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/southamerica-east1-c/operations/operation-1783694991128-65642da557750-65aa5dbd-1b930c77] to complete...
.........failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"southamerica-east1-c\""
}. Cleaned up: [] |
| **southamerica-west1-a** | Yes | Yes | Successfully started and reached ACTIVE state. |

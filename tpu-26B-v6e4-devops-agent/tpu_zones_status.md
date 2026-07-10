# GCP TPU Zones Quota & Startup Status

This file details the GCP zones with available quota for `TPUV6EPerProjectPerZoneForTPUAPI` and the status of TPU startup attempts.

## Startup Attempt Summary
- **Successful Zone:** `southamerica-west1-a` (Started, reached ACTIVE)
- **Status Date:** 2026-06-30

| Zone | Quota Available | TPU v6e-4 Started Successfully | Details / Reason for Failure |
| :--- | :--- | :--- | :--- |
| **asia-east1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-4", could not be found in the zonal accelerator configurations for "asia-east1-a".; the accelerator v6e-4 was not found in zone asia-east1-a [EID: 0xadaada1e50943af6]. Cleaned up: [] |
| **asia-east1-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-4", could not be found in the zonal accelerator configurations for "asia-east1-b".; the accelerator v6e-4 was not found in zone asia-east1-b [EID: 0xbbc7d15f070be613]. Cleaned up: [] |
| **asia-east1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-east1-c/operations/operation-1782918819772-6558e22ea773a-29e6756a-d3629681] to complete...
...........failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-east1-c\""
}. Cleaned up: [] |
| **asia-northeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-a" is not supported. [EID: 0x2565fdf9d68af622]. Cleaned up: [] |
| **asia-northeast1-b** | Yes | No | Timed out waiting 3 minutes to reach ACTIVE state. |
| **asia-northeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-c" is not supported. [EID: 0xed519618094d6b40]. Cleaned up: [] |
| **asia-south1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-south1-a" is not supported. [EID: 0xc5a99c4b4f17f265]. Cleaned up: [] |
| **asia-south1-b** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-south1-b/operations/operation-1782919050753-6558e30aef5ed-ca70124e-2c340d95] to complete...
.............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-south1-b\""
}. Cleaned up: [] |
| **asia-south1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-south1-c/operations/operation-1782919064237-6558e317cb4c0-127d24bd-15835dd1] to complete...
..............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-south1-c\""
}. Cleaned up: [] |
| **asia-southeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-a" is not supported. [EID: 0x5c792cd0967029c7]. Cleaned up: [] |
| **asia-southeast1-b** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/asia-southeast1-b/operations/operation-1782919085722-6558e32c48cae-8f8b8bbb-51d8b9e6] to complete...
.............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"asia-southeast1-b\""
}. Cleaned up: [] |
| **asia-southeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-c" is not supported. [EID: 0xe412b70467359ea3]. Cleaned up: [] |
| **europe-west4-a** | Yes | No | Timed out waiting 10 minutes to reach ACTIVE state (reached PROVISIONING). |
| **europe-west4-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-4", could not be found in the zonal accelerator configurations for "europe-west4-b".; the accelerator v6e-4 was not found in zone europe-west4-b [EID: 0x910b40dbbac0e3dd]. Cleaned up: [] |
| **europe-west4-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "europe-west4-c" is not supported. [EID: 0xb35a9d2d89a460f6]. Cleaned up: [] |
| **southamerica-east1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "southamerica-east1-a" is not supported. [EID: 0x4bcd503544ab7833]. Cleaned up: [] |
| **southamerica-east1-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "southamerica-east1-b" is not supported. [EID: 0xb9a9e447b76fbc1b]. Cleaned up: [] |
| **southamerica-east1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/aisprint-491218/locations/southamerica-east1-c/operations/operation-1782919474141-6558e49eb594a-67385716-9375a6be] to complete...
.........failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-4\" in location \"southamerica-east1-c\""
}. Cleaned up: [] |

| **southamerica-west1-a** | Yes | Yes | Successfully started and reached ACTIVE state. |

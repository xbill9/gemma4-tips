# GCP TPU Zones Quota & Startup Status

This file details the GCP zones with available quota for `TPUV6EPerProjectPerZoneForTPUAPI` and the status of TPU startup attempts for `v6e-1`.

| Zone | Quota Available | TPU v6e-1 Started Successfully | Details / Reason for Failure |
| :--- | :--- | :--- | :--- |
| **asia-east1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-1", could not be found in the zonal accelerator configurations for "asia-east1-a".; the accelerator v6e-1 was not found in zone asia-east1-a [EID: 0x2d87f08197698c72]. Cleaned up: [] |
| **asia-east1-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-1", could not be found in the zonal accelerator configurations for "asia-east1-b".; the accelerator v6e-1 was not found in zone asia-east1-b [EID: 0xe0c27b57e16f7fee]. Cleaned up: [] |
| **asia-east1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/comglitn/locations/asia-east1-c/operations/operation-1783367767703-655f6aa4c41a7-571e7610-848c2443] to complete...
...........failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-east1-c\""
}. Cleaned up: [] |
| **asia-northeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-a" is not supported. [EID: 0x5aed68e7ead80bab]. Cleaned up: [] |
| **asia-northeast1-b** | Yes | No | Timed out waiting 3 minutes to reach ACTIVE state. |
| **asia-northeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-c" is not supported. [EID: 0x729fcaeb232fa09f]. Cleaned up: [] |
| **asia-south1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-south1-a" is not supported. [EID: 0x9abb21e409b51575]. Cleaned up: [] |
| **asia-south1-b** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/comglitn/locations/asia-south1-b/operations/operation-1783368009336-655f6b8b346ad-5883cf4b-9af84a51] to complete...
..............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-south1-b\""
}. Cleaned up: [] |
| **asia-south1-c** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/comglitn/locations/asia-south1-c/operations/operation-1783368022894-655f6b982270c-d9a9b702-504df685] to complete...
..............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-south1-c\""
}. Cleaned up: [] |
| **asia-southeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-a" is not supported. [EID: 0xbda9fe9b961db207]. Cleaned up: [] |
| **asia-southeast1-b** | Yes | No | Create request issued for: [vllm-gemma4-qr]
Waiting for operation [projects/comglitn/locations/asia-southeast1-b/operations/operation-1783368044263-655f6bac838b0-19d40af1-c62e5166] to complete...
............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-southeast1-b\""
}. Cleaned up: [] |
| **asia-southeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-c" is not supported. [EID: 0x89b2929fca84b42b]. Cleaned up: [] |
| **europe-west4-a** | Yes | Yes | Successfully started and reached ACTIVE state. |

# GCP TPU Zones Quota & Startup Status

This file details the GCP zones with available quota for `TPUV6EPerProjectPerZoneForTPUAPI` and the status of TPU startup attempts.

## Startup Attempt Summary
- **Successful Zone:** `southamerica-west1-a` (Started, reached ACTIVE)
- **Status Date:** 2026-06-16

| Zone | Quota Available | TPU v6e-1 Started Successfully | Details / Reason for Failure |
| :--- | :--- | :--- | :--- |
| **asia-east1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-1", could not be found in the zonal accelerator configurations for "asia-east1-a".; the accelerator v6e-1 was not found in zone asia-east1-a [EID: 0x362c45de1b38c529]. Cleaned up: [] |
| **asia-east1-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-1", could not be found in the zonal accelerator configurations for "asia-east1-b".; the accelerator v6e-1 was not found in zone asia-east1-b [EID: 0x850ecbf6b0e3bc18]. Cleaned up: [] |
| **asia-east1-c** | Yes | No | Create request issued for: [node-1]
Waiting for operation [projects/aisprint-491218/locations/asia-east1-c/operations/operation-1781625689032-654610e51473f-b8557a36-8a68155f] to complete...
...........failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-east1-c\""
}. Cleaned up: [] |
| **asia-northeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-a" is not supported. [EID: 0x1994f24467802754]. Cleaned up: [] |
| **asia-northeast1-b** | Yes | No | Timed out waiting 3 minutes to reach ACTIVE state. |
| **asia-northeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-northeast1-c" is not supported. [EID: 0x28741e859a13b231]. Cleaned up: [] |
| **asia-south1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-south1-a" is not supported. [EID: 0xfbdd74d038f7451]. Cleaned up: [] |
| **asia-south1-b** | Yes | No | Create request issued for: [node-1]
Waiting for operation [projects/aisprint-491218/locations/asia-south1-b/operations/operation-1781625919768-654611c120745-9de0d657-c73bff4d] to complete...
..............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-south1-b\""
}. Cleaned up: [] |
| **asia-south1-c** | Yes | No | Create request issued for: [node-1]
Waiting for operation [projects/aisprint-491218/locations/asia-south1-c/operations/operation-1781625933124-654611cddd586-abe7f537-011f6cc1] to complete...
..............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-south1-c\""
}. Cleaned up: [] |
| **asia-southeast1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-a" is not supported. [EID: 0x23d76b29852f41f8]. Cleaned up: [] |
| **asia-southeast1-b** | Yes | No | Create request issued for: [node-1]
Waiting for operation [projects/aisprint-491218/locations/asia-southeast1-b/operations/operation-1781625954421-654611e22cc79-87ab12c9-5b229489] to complete...
............failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"asia-southeast1-b\""
}. Cleaned up: [] |
| **asia-southeast1-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "asia-southeast1-c" is not supported. [EID: 0x8ebaacc66c2f7b19]. Cleaned up: [] |
| **europe-west4-a** | Yes | No | Timed out waiting 3 minutes to reach ACTIVE state. |
| **europe-west4-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested accelerator configuration for accelerator type, "v6e-1", could not be found in the zonal accelerator configurations for "europe-west4-b".; the accelerator v6e-1 was not found in zone europe-west4-b [EID: 0x1d2f4eea6b7ba942]. Cleaned up: [] |
| **europe-west4-c** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "europe-west4-c" is not supported. [EID: 0x192d0dc6c02932f6]. Cleaned up: [] |
| **southamerica-east1-a** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "southamerica-east1-a" is not supported. [EID: 0x8124a11c13c2001c]. Cleaned up: [] |
| **southamerica-east1-b** | Yes | No | ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) INVALID_ARGUMENT: Cloud TPU received a bad request. The requested zone "southamerica-east1-b" is not supported. [EID: 0x7281a1470e720cfe]. Cleaned up: [] |
| **southamerica-east1-c** | Yes | No | Create request issued for: [node-1]
Waiting for operation [projects/aisprint-491218/locations/southamerica-east1-c/operations/operation-1781626213449-654612d933e1c-c42b27d0-a2525515] to complete...
........failed.
ERROR: (gcloud.alpha.compute.tpus.queued-resources.create) {
  "code": 3,
  "message": "FLEX_START provisioning model is not supported for accelerator type \"v6e-1\" in location \"southamerica-east1-c\""
}. Cleaned up: [] |
| **southamerica-west1-a** | Yes | Yes | Successfully started and reached ACTIVE state. |
| **southamerica-west1-b** | Yes | Pending | Not attempted yet |
| **southamerica-west1-c** | Yes | Pending | Not attempted yet |
| **us-central1-a** | Yes | Pending | Not attempted yet |
| **us-central1-b** | Yes | Pending | Not attempted yet |
| **us-central1-c** | Yes | Pending | Not attempted yet |
| **us-central1-f** | Yes | Pending | Not attempted yet |
| **us-east1-b** | Yes | Pending | Not attempted yet |
| **us-east1-c** | Yes | Pending | Not attempted yet |
| **us-east1-d** | Yes | Pending | Not attempted yet |
| **us-east4-c** | Yes | Pending | Not attempted yet |
| **us-east5-a** | Yes | Pending | Not attempted yet |
| **us-east5-b** | Yes | Pending | Not attempted yet |
| **us-south1-a** | Yes | Pending | Not attempted yet |
| **us-south1-b** | Yes | Pending | Not attempted yet |
| **us-south1-c** | Yes | Pending | Not attempted yet |
| **us-west1-a** | Yes | Pending | Not attempted yet |
| **us-west1-b** | Yes | Pending | Not attempted yet |
| **us-west1-c** | Yes | Pending | Not attempted yet |

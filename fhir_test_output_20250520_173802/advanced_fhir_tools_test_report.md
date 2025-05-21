# Advanced FHIR Tools Test Report

**Test Date:** 2025-05-20 17:39:27

**Patient ID:** T1wI5bk8n1YVgvWk9D05BmRV0Pi3ECImNSK8DKyKltsMB

**Overall Status:** FAILURE

## Test Steps Summary

| Step | Status | Duration |
|------|--------|----------|
| Authentication | ✅ PASS | 2.51s |
| Fetch_Data | ✅ PASS | 0.00s |
| Fhirpath | ✅ PASS | 0.00s |
| Pathling | ✅ PASS | 0.04s |
| Datascience | ❌ FAIL | 0.00s |
| Validation | ✅ PASS | 82.64s |

## Detailed Results

### Authentication

### Fetch_Data

**Resource Counts:**

- Patient: 1
- Observation: 5
- Condition: 1
- Encounter: 1
**Results File:** fhir_test_output_20250520_173802/results/raw_resources.json

### Fhirpath

**Results File:** fhir_test_output_20250520_173802/results/fhirpath_results.json

### Pathling

**Results File:** fhir_test_output_20250520_173802/results/pathling_results.json

### Datascience

**Error:** 'FHIRDataset' object has no attribute 'to_pandas'

### Validation

**Validation Statistics:**

- Total resources: 8
- Valid resources: 0 (0.0%)
- Invalid resources: 8
**Results File:** fhir_test_output_20250520_173802/results/validation_results.json


## Conclusion

Some tests failed. See above for details.

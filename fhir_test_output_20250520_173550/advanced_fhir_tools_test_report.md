# Advanced FHIR Tools Test Report

**Test Date:** 2025-05-20 17:36:21

**Patient ID:** T1wI5bk8n1YVgvWk9D05BmRV0Pi3ECImNSK8DKyKltsMB

**Overall Status:** FAILURE

## Test Steps Summary

| Step | Status | Duration |
|------|--------|----------|
| Authentication | ✅ PASS | 2.51s |
| Fetch_Data | ✅ PASS | 0.00s |
| Fhirpath | ✅ PASS | 0.00s |
| Pathling | ❌ FAIL | 0.46s |
| Datascience | ❌ FAIL | 0.00s |
| Validation | ❌ FAIL | 27.28s |

## Detailed Results

### Authentication

### Fetch_Data

**Resource Counts:**

- Patient: 1
- Observation: 5
- Condition: 1
- Encounter: 1
**Results File:** fhir_test_output_20250520_173550/results/raw_resources.json

### Fhirpath

**Results File:** fhir_test_output_20250520_173550/results/fhirpath_results.json

### Pathling

**Error:** 'PathlingService' object has no attribute 'start'

### Datascience

**Error:** FHIR-PYrate is not available. Install it with 'pip install fhir-pyrate>=0.8.0'

### Validation

**Error:** 'ValidationResult' object has no attribute 'get_info'


## Conclusion

Some tests failed. See above for details.

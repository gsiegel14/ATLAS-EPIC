# Advanced FHIR Tools Test Report

**Test Date:** 2025-05-21 00:59:38

**Patient ID:** T1wI5bk8n1YVgvWk9D05BmRV0Pi3ECImNSK8DKyKltsMB

**Data Tier:** GOLD

**Overall Status:** SUCCESS

## Test Steps Summary

| Step | Status | Duration |
|------|--------|----------|
| Authentication | ✅ PASS | 2.50s |
| Fetch_Data | ✅ PASS | 0.00s |
| Fhirpath | ✅ PASS | 0.00s |
| Pathling | ✅ PASS | 0.00s |
| Datascience | ✅ PASS | 0.00s |
| Validation | ✅ PASS | 0.00s |
| Dashboards | ✅ PASS | 0.04s |

## Detailed Results

### Authentication

### Fetch_Data

**Resource Counts:**

- Patient: 1
- Observation: 5
- Condition: 1
- Encounter: 1
**Results File:** fhir_test_output_20250521_005936/gold/resources.json

### Fhirpath

**Results File:** fhir_test_output_20250521_005936/results/fhirpath_results.json

### Pathling

**Results File:** fhir_test_output_20250521_005936/results/pathling_results.json

### Datascience

**Results File:** fhir_test_output_20250521_005936/results/datascience_results.json

### Validation

**Validation Statistics:**

- Total resources: 8
- Valid resources: 1 (12.5%)
- Invalid resources: 7
**Results File:** fhir_test_output_20250521_005936/gold/validation_results.json

### Dashboards

**Dashboard Output:**

- Dashboard files: fhir_test_output_20250521_005936/dashboard
- Available dashboards: Quality, Validation, Combined

## Tier-Specific Information

This test was run against the **GOLD** data tier.

Gold tier represents fully conformant, enriched data with complete extensions, standardized coding, and LLM-ready narratives.

## Conclusion

All advanced FHIR tools tests completed successfully.

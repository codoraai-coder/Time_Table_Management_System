# Data Integrity Verification Report

## Status: ⚠️ WARNING

**Health Score:** 60.0/100

## Data Quality Metrics

| Entity | Total | Duplicates | Completeness | Status |
|--------|-------|------------|--------------|--------|
| faculty | 5 | 0 | 100.0% | ✅ |
| courses | 5 | 0 | 100.0% | ✅ |
| rooms | 5 | 0 | 0.0% | ⚠️ |
| sections | 10 | 0 | 100.0% | ✅ |
| mappings | 10 | 0 | 0.0% | ⚠️ |

## Issues Found

- 5 rooms with invalid capacity
- Unknown faculty: F_DAROS@college.edu
- Unknown faculty: F_DAROS@college.edu
- Unknown faculty: F_SHARMA@college.edu
- Unknown faculty: F_SHARMA@college.edu
- Unknown faculty: F_GUPTA@college.edu

## Normalization Clustering


**Course Clusters:** 2
- Canonical: 'Database Management Systems Lab' | Confidence: 1.00 | Names: Database Management Systems, Database Management Systems Lab
- Canonical: 'Operating Systems Lab' | Confidence: 1.00 | Names: Operating Systems, Operating Systems Lab

**Overall Clustering Confidence:** 1.00

## Data Summary

- Faculty: 5
- Courses: 5
- Rooms: 5
- Sections: 10
- Mappings: 10

## Verdict

⚠️ **Review issues before proceeding with import**

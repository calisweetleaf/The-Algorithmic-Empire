# 🩺 Python Production Doctor Report

**Project Root:** `C:\Users\treyr\Documents\algorithmic_empire`
**Scan Date:** 2026-02-26 22:15:03
**Python Version:** 3.12.10

---

🟡 **MINOR ISSUES** - Ready with minor fixes

**Files Scanned:** 1 | **Total Issues:** 73
- 🔴 Critical: 0
- 🟠 Serious: 0
- 🟡 Minor: 73

## 📈 Code Quality Metrics

- **Documentation Coverage:** 6.2% (3/48)
- **Type Hint Coverage:** 0.0% (0/48)

## 📁 File Analysis

### 📄 `ARCS\tests\test_network_telemetry.py`

**Total Issues:** 73

#### 📚 Missing Docstrings
1. Class `TestNetworkIntelligenceTypeEnum` at line 73
2. Class `TestTelemetryAggressionEnum` at line 88
3. Class `TestProtocolTypeEnum` at line 105
4. Class `TestDeviceCategoryEnum` at line 114
5. Class `TestThreatIndicatorTypeEnum` at line 124
6. Class `TestNetworkDeviceDataclass` at line 139
7. Class `TestNetworkFlowDataclass` at line 162
8. Class `TestThreatIndicatorDataclass` at line 184
9. Class `TestBehavioralBaselineDataclass` at line 203
10. Function `test_all_members` at line 74
11. Function `test_values_are_lowercase` at line 83
12. Function `test_all_levels` at line 97
13. Function `test_integer_values` at line 100
14. Function `test_all_protocols` at line 106
15. Function `test_all_categories` at line 115
16. Function `test_all_types` at line 125
17. Function `test_construct` at line 140
18. Function `test_construct` at line 163
19. Function `test_construct` at line 185
20. Function `test_construct` at line 204
21. Function `test_calculate_entropy_empty` at line 241
22. Function `test_rule_based_classification_http` at line 265
23. Function `test_rule_based_classification_https` at line 269
24. Function `test_rule_based_classification_dns` at line 273
25. Function `test_rule_based_classification_ssh` at line 277
26. Function `test_rule_based_classification_ftp` at line 281
27. Function `test_rule_based_classification_smtp` at line 285
28. Function `test_rule_based_classification_smb` at line 289
29. Function `test_rule_based_classification_icmp` at line 293
30. Function `test_rule_based_classification_other` at line 297
31. Function `test_prepare_feature_vector_shape` at line 301
32. Function `test_guess_os_linux` at line 351
33. Function `test_guess_os_windows` at line 356
34. Function `test_guess_os_network_device` at line 361
35. Function `test_categorize_server` at line 366
36. Function `test_categorize_network_device` at line 374
37. Function `test_categorize_iot` at line 379
38. Function `test_categorize_printer` at line 384
39. Function `test_categorize_workstation_default` at line 389
40. Function `test_categorize_industrial_control` at line 398
41. Function `test_categorize_mobile` at line 403
42. Function `test_calculate_trust_score_trusted_vendor` at line 408
43. Function `test_calculate_trust_score_risky_services` at line 416
44. Function `test_calculate_trust_score_many_open_ports` at line 428
45. Function `test_init` at line 447
46. Function `test_shutdown` at line 460
47. Function `test_traffic_volume_spike` at line 484
48. Function `test_connection_spike` at line 503
49. Function `test_new_protocols` at line 522
50. Function `test_no_anomalies` at line 545

#### 📏 Suspiciously Short Functions
1. `test_values_are_lowercase()` at line 83 - only 3 lines of code
2. `test_all_levels()` at line 97 - only 2 lines of code
3. `test_integer_values()` at line 100 - only 3 lines of code
4. `test_calculate_entropy_empty()` at line 241 - only 3 lines of code
5. `test_calculate_entropy_uniform()` at line 245 - only 4 lines of code
6. `test_calculate_entropy_two_symbols()` at line 259 - only 4 lines of code
7. `test_rule_based_classification_http()` at line 265 - only 3 lines of code
8. `test_rule_based_classification_https()` at line 269 - only 3 lines of code
9. `test_rule_based_classification_dns()` at line 273 - only 3 lines of code
10. `test_rule_based_classification_ssh()` at line 277 - only 3 lines of code
11. `test_rule_based_classification_ftp()` at line 281 - only 3 lines of code
12. `test_rule_based_classification_smtp()` at line 285 - only 3 lines of code
13. `test_rule_based_classification_smb()` at line 289 - only 3 lines of code
14. `test_rule_based_classification_icmp()` at line 293 - only 3 lines of code
15. `test_rule_based_classification_other()` at line 297 - only 3 lines of code
16. `test_guess_os_linux()` at line 351 - only 4 lines of code
17. `test_guess_os_windows()` at line 356 - only 4 lines of code
18. `test_guess_os_network_device()` at line 361 - only 4 lines of code
19. `test_categorize_network_device()` at line 374 - only 4 lines of code
20. `test_categorize_iot()` at line 379 - only 4 lines of code
21. `test_categorize_printer()` at line 384 - only 4 lines of code
22. `test_categorize_industrial_control()` at line 398 - only 4 lines of code
23. `test_categorize_mobile()` at line 403 - only 4 lines of code

## 🚀 Recommended Action Plan

### Critical Fixes (Block Deployment)

### Serious Fixes (Required Before Release)

### Quality Improvements (Recommended)
- Add meaningful docstrings to all functions/classes
- Review suspiciously short functions for completeness

---

_This report generated by [Python Production Doctor](https://github.com/yourusername/production-doctor)_
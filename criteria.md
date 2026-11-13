# Capstone Acceptance Criteria

## 1. Structured Logging

**Target:** 5 out of 5 requests must produce a valid JSON log entry containing a timestamp, input size, output or error, HTTP status, and execution duration.

**Reason:** These fields are sufficient to understand what happened during a request without introducing a complicated monitoring system.

## 2. Performance Measurement

**Target:** 5 out of 5 successful inference requests must have a positive, finite duration recorded in milliseconds. The server-side duration must not exceed independently measured client-side HTTP duration by more than 100 milliseconds.

**Reason:** Basic timing instrumentation is sufficient to measure and compare request performance. The allowance accounts for small differences in when client and server measurements are taken.

## 3. Reproducible Deployment

**Target:** After setting up the application once from a clean checkout using RUNNING.md, 5 out of 5 service starts must succeed using the documented command. Each start must allow a successful health check and valid inference request.

**Reason:** Another developer should be able to run the application using the repository's instructions without undocumented setup steps.

## 4. Failure Logging

**Target:** 5 out of 5 deliberately invalid requests must return the expected HTTP error and produce a corresponding JSON log entry identifying the failure.

**Reason:** Errors must be observable so that unsuccessful requests can be diagnosed. One repeatable invalid-input scenario is sufficient for this criterion.

## 5. Existing Functionality

**Target:** 5 out of 5 submit-and-appeal workflows must preserve existing prediction results and successfully record the appeal. Generated IDs and timestamps do not need to match.

**Reason:** Adding deployment and monitoring features must not break the application's original functionality.

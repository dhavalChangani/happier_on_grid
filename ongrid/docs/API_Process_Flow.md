# OnGrid API Process Flow

## Overview
This document outlines the complete API process flow for integrating with OnGrid's verification services.

## Process Steps

### 1. Onboarding API
API creates an individual under the client Community and returns the individual Id of the newly created individual. This individual Id can subsequently be used to update information on the individual or to request/track verifications against the individual. The client, upon receiving individual Id must store it in their database mapped to the candidate record in the client system.

### 2. Ensure Data Sufficiency
Each verification is executed on a set of information specific to the particular verification. Examples:
- Current address for Local address verification
- Education document for Education document verification

OnGrid provides APIs for various sets of information updates like:
- Adding/updating education or employment document
- Adding/updating addresses
- Adding face photograph
- etc.

Client should add/update the relevant information on the Individual pertaining to the verifications that are intended to be requested. **Refer to the verification section** to find the data relevant to each verification.

### 3. Request Verification
Upon creation of Individual record and submission of all relevant information, the client calls the Verification Request API(s) to request various verifications against the individual. There exists separate request APIs for each verification. Upon successful request of verification, the API response contains a global unique request Id corresponding to the requested verification. Client should store this request Id in their system.

### 4. Await Callbacks
When the verifications are on going, client need not build polling systems to constantly track status of their ongoing verifications. Client can configure a callback URL using the Community Settings page on OnGrid portal. When a callback URL is configured, any event/milestone is submitted to that URL in a pre-defined format. **Refer to activity callback section** for more details.

### 5. Fetch Reports
Once the verification has been completed (usually notified using a XXXCompleted callback), the client can fetch the verification report using the respective API. Each verification has a different but consistent API endpoint of the following format.

## Integration Flow Summary

```
1. Create Individual (Onboarding) → Get Individual ID
2. Add Required Data (Sufficiency) → Update individual with verification-specific data
3. Request Verification → Get Request ID
4. Receive Callbacks → Monitor verification progress
5. Fetch Report → Retrieve completed verification results
```

## Key Points

- **Store IDs**: Always store Individual IDs and Request IDs in your system
- **Data Preparation**: Ensure all required data is submitted before requesting verification
- **Callback Configuration**: Configure callbacks to avoid polling
- **Separate APIs**: Each verification type has its own request and fetch endpoints
- **Event-Driven**: Use callbacks for real-time updates on verification status

# Insufficiency IDs

Reference guide for OnGrid verification insufficiency codes and their associated offering types.

## Table of Contents
- [General Insufficiencies](#general-insufficiencies)
- [Document Insufficiencies](#document-insufficiencies)
- [Education Verification](#education-verification)
- [Employment Verification](#employment-verification)
- [Reference Check](#reference-check)
- [Police Verification](#police-verification)
- [Regional Restrictions](#regional-restrictions)

---

## General Insufficiencies

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 2 | `i_not_cooperative` | Individual is not cooperating for verification | Please inform the individual about ongoing verifications and request to cooperate | PAV, PADV, LADV, LAV |
| 5 | `i_email` | Email missing | Please provide email address of individual | DCS |
| 9 | `i_alternate_phone` | Alternate phone number required | Individual is not responding to calls on given contact number. Alternate number is required. | PAPV, CC, PADV, LAPV, PAV, LADV, LAV, PCC |
| 11 | `i_mobile` | Phone incorrect | Please enter correct phone number | PAPV, PADV, CC, PAV, LAV, DCS, LADV, LAPV |
| 14 | `i_name` | Name is incorrect | Please enter individual's correct name | CCRV, PADV, PCC, PRC, LAPV, EDUV, LADV, GDC, PAPV, EMPV, PVLF, CC, LAV, DCS |
| 15 | `i_profile_pic` | Profile image is Not Available | Please upload a recent profile image for the individual | PVLF, PCC |
| 16 | `i_fathername` | Father's name is not available | Please provide father's name | PVLF, CCRV, PCC, GDC |
| 18 | `i_dob` | Date of birth missing | Please provide date of birth of individual | DLV, PVLF, PCC, CCRV, EDUV |
| 19 | `i_dob` | Date of birth is incorrect or invalid | Please provide correct date of birth | PVLF, DLV, GDC, CC, EDUV |
| 122 | `i_other` | Additional Information Required | | EDUV, EMPV, PRC |
| 183 | `i_candidate_client_association_ended` | Candidate client association ended | Individual claims their association with the client has ended and does not wish to continue with the verification process | VIDV, PVLF, PRC, PCC, PAV, PAPV, PANV, PADV, LAV, LAPV, LADV, GDC, EMPV, EDUV, DLV, DCS, CCRV, CC, BAV, AV |
| 215 | `i_disclosure_required` | Client name disclosure is required | Client name disclosure is required for verification of individual | |

## Document Insufficiencies

### Address Documents

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 1 | `i_lav_pav` | Permanent address provided instead of current address | Given address for verification is permanent address of individual not local address | LADV, LAV, LAPV |
| 10 | `i_current_address` | Current address incomplete | Please enter complete current address | CCRV, LADV, LAV, GDC, LAPV |
| 12 | `i_permanent_address` | Permanent address incomplete or missing | Please update permanent address of individual | PVLF, CCRV, PAPV, GDC, CC, PAV |

### ID Documents

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 6 | `i_pan_id` | Invalid PAN number | Please provide correct PAN number of individual | PANV, CC |
| 7 | `i_dl_id` | Invalid driving licence number | Please provide correct driving licence number of individual | DLV |
| 8 | `i_vid_id` | Invalid voter id number | Please provide correct voter id of individual | VIDV |
| 17 | `i_id_document` | ID Document is Missing | Please upload id document of individual | PVLF, PCC |

### Authorization Documents

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 13 | `i_letter_of_authorization` | Letter of authorization missing | Please upload scanned copy of letter of authorization or signed consent form | EDUV, CCRV, EMPV, PVLF, PRC, PCC, LAV, DCS |

## Education Verification

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 20 | `i_fee_approval` | Fee Approval Required | Fee approval is required for verification of individual | EDUV, EMPV |
| 21 | `i_edu_certificate` | Degree/diploma certificate not available | Please upload scanned copy of degree/diploma | EDUV |
| 22 | `i_edu_registration_number` | Registration number is missing | Please provide registration number of individual | EDUV |
| 23 | `i_edu_college_name` | College name not available | Please provide college/institute name | EDUV |
| 24 | `i_edu_certificate` | Provisional certificate not available | Please upload scanned copy of provisional certificate | EDUV |
| 25 | `i_edu_certificate` | Provisional certificate not clear | Please upload clear scanned copy of provisional certificate | EDUV |
| 26 | `i_edu_certificate` | Degree/diploma certificate not clear | Please upload clear scanned copy of degree/diploma | EDUV |
| 27 | `i_edu_certificate` | Marksheet not available | Please upload marksheet | EDUV |
| 28 | `i_edu_certificate` | Marksheet not clear | Please upload clear scanned copy of marksheet | EDUV |
| 29 | `i_edu_centrecode` | Center code of school/college is not available | Please provide centercode of school/college | EDUV |
| 92 | `i_edu_self_verify` | Candidate has to visit institute with original document for verification | | EDUV |

## Employment Verification

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 30 | `i_emp_compensation` | Previous employment's compensation not available | Please provide previous employment's compensation | EMPV |
| 31 | `i_emp_employeeid` | Previous employee id/staff id missing | Please provide previous employment's employee id | EMPV |
| 32 | `i_emp_last_working_date` | Previous employment's last working date not available | Please provide previous employment's last working date | EMPV |
| 33 | `i_emp_joining_date` | Previous employment's joining date not available | Please provide previous employment's date of joining | EMPV |
| 34 | `i_emp_experience_letter` | Experience letter not available | Please upload clear scanned copy of experience letter | EMPV |
| 35 | `i_emp_experience_letter` | Experience letter is not clear | Please upload clear scanned copy of experience letter | EMPV |
| 36 | `i_emp_experience_letter` | Experience letter is invalid | Please upload valid experience letter | EMPV |
| 37 | `i_emp_salary_slip` | Salary slip is not available | Please upload previous employment's salary slip | EMPV |
| 38 | `i_emp_salary_slip` | Salary slip document is not clear | Please upload clear scanned copy of salary slip | EMPV |
| 39 | `i_emp_salary_slip` | Salary slip document is invalid | Please provide valid salary slip document | EMPV |
| 40 | `i_emp_appointment_letter` | Appointment letter is not available | Please upload appointment letter from previous employment | EMPV |
| 41 | `i_emp_appointment_letter` | Appointment letter is not clear | Please upload clear scanned copy of appointment letter | EMPV |
| 42 | `i_emp_appointment_letter` | Appointment letter is not valid | Please upload valid appointment letter of individual from previous employment | EMPV |
| 43 | `i_emp_manager_email` | Manager's Email Id Required | Previous manager email is required for verification of individual | EMPV |
| 44 | `i_emp_manager_phone` | Manager's Phone Number Required | Previous manager phone number is required for verification of individual | EMPV |
| 182 | `i_fnf_pending` | FnF pending from candidate | Please ask the candidate to complete FnF with their ex-employer | EMPV |
| 212 | `i_emp_hr_email` | HR's Email Id Required | Previous HR's email id is required for verification of individual | EMPV |
| 213 | `i_emp_hr_phone` | HR's phone number required | Previous HR's phone number is required for verification of individual | EMPV |
| 214 | `i_emp_last_working_location` | Last working location is required | Please provide previous employment's last working location(city) | EMPV |

## Reference Check

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 45 | `i_prc_email` | Reference provider's email is missing or invalid | Please provide correct email address for reference check | PRC |
| 46 | `i_prc_phone` | Reference provider's phone is missing or invalid | Please provide correct phone number for reference check | PRC |

## Police Verification

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 3 | `i_signature` | Individual's Signature is Required for Verification | Individual's signature is required for police verification | PCC |
| 4 | `i_dob_proof` | DoB Proof Required | Please provide a valid proof of date of birth for individual | PCC |
| 62 | `i_rent_agreement` | Rent agreement required | Rent agreement is required for Police Verification | PCC |

## Regional Restrictions

| ID | Domain Key | Display Name | Description | Offering Codes |
|----|-----------|--------------|-------------|----------------|
| 152 | `region_not_supported` | Region not supported | Region not supported for address verification | LAV, PAV |

---

## Offering Code Legend

- **AV**: Address Verification
- **BAV**: Business Address Verification
- **CC**: Court Check
- **CCRV**: Criminal Court Record Verification
- **DCS**: Drug/Criminal Screening
- **DLV**: Driving License Verification
- **EDUV**: Education Verification
- **EMPV**: Employment Verification
- **GDC**: Global Database Check
- **LAV**: Local Address Verification
- **LADV**: Local Address Document Verification
- **LAPV**: Local Address Physical Verification
- **PANV**: PAN Verification
- **PAV**: Permanent Address Verification
- **PADV**: Permanent Address Document Verification
- **PAPV**: Permanent Address Physical Verification
- **PCC**: Police Clearance Certificate
- **PRC**: Professional Reference Check
- **PVLF**: Police Verification Letter Form
- **VIDV**: Voter ID Verification
# Document Verification Testing Guide

## Overview
Test document verification processes in **staging environment only** using customized field values.

## Key Testing Pattern
All verification types follow this pattern:
- Customize specific fields with test codes
- Use delimiters: `::` `.` `//` `--` `YY`
- Format: `ACTION::RESULT::ActualValue`

## Common Test Scenarios

### Insufficiency Testing
```
INSUF::132::15::ActualValue
```
- Creates insufficiency with IDs 132 and 15

### Completion Testing
```
CMP::RESULT_CODE::ActualValue
```

Common result codes:
- `VER` - Verified
- `SCS` - Success
- `INV` - Invalid
- `FLD` - Failed
- `UTV` - UnableToVerify
- `SWE` - SuccessWithException

## Verification Types & Test Fields

| Verification | Field to Customize | Example |
|--------------|-------------------|---------|
| PANV | nameAsPerDocument | `CMP::VER::Rohit Kumar` |
| VIDV | nameAsPerDocument | `CMP::VER::Rohit Kumar` |
| DLV | nameAsPerDocument | `CMP::VER::Rohit Kumar` |
| LAV/LADV/LAPV | currentAddress | `CMP::VER::Wagle Estate, Thane` |
| PAV/PADV/PAPV | fullAddress (in permanentAddress) | `CMP::VER::Wagle Estate, Thane` |
| EMPV | employerName | `CMP::SCS::TCS Limited` |
| EDUV | nameOfInstitute | `CMP::SCS::St George's College` |
| BAV | ifscCode | `AKID0001234` (Success) |
| PCC | name | `CMP::SCS::Ram Kumar` |
| GDC/PVLF/CCRV | fathersName | `CMP::SCS::Ram Kumar` |
| CC | documentUID (PAN) | `BBBBB2222B` (Success) |
| PRC | referenceProviderName | `CMP::SCS::Ram Kumar` |

## Notes
- Strings are case-insensitive
- Works only in staging environment
- Invalid/empty fields keep request in "created" state

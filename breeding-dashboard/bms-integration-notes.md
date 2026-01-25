# BMS API Integration Notes

## Extracted from URL:
- **Base URL**: https://semillanueva.bmspro.io
- **Program UUID**: febb4f0f-b4af-4399-bdec-73e88a5d2223
- **Crop**: maize
- **User ID**: 13

## API Endpoint Pattern (likely):
- Main API: https://semillanueva.bmspro.io/bmsapi/
- Trials: https://semillanueva.bmspro.io/bmsapi/crops/maize/programs/{programUUID}/studies
- Observations: https://semillanueva.bmspro.io/bmsapi/crops/maize/programs/{programUUID}/studies/{studyId}/observations

## Next Steps:
1. Check Network tab in browser DevTools to see actual API calls
2. Look for authentication method (API key vs session cookies)
3. Extract sample API responses to understand data structure

## BMS Documentation:
https://bmspro.io/1596/breeding-management-system/tutorials/maize-40/trial-data-collection

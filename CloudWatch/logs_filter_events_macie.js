{$.eventType = JOB_PAUSED_BY_MACIE_SERVICE_QUOTA_MET || $.eventType = JOB_PAUSED_BY_USER }

{$.eventType = * } // You can use this filter when capturing all events and sending them to a SIEM or log aggregation service.

{$.eventType = ACCOUNT_*} // A filter to capture account level errors.

{$.eventType = BUCKET_*} // A filter to capture bucket level errors.

{$.eventType = BUCKET_ACCESS_DENIED || $.eventType = BUCKET_DOES_NOT_EXIST || $.eventType = 
BUCKET_IN_DIFFERENT_REGION || $.eventType = BUCKET_OWNER_CHANGED } //This will capture all bucket level events are interesting
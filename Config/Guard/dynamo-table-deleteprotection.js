rule check_tabledeleteprotection {
    configuration.deletionProtectionEnabled == True <<
    result: NON_COMPLIANT
    message: Dynamo table is not protected.
    >>
}
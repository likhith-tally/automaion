#!/usr/bin/env python3

import sys
import oci
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner
from oci.exceptions import ServiceError

# Tenancy OCID where Email Delivery lives
Parent_TENANCY_OCID = "ocid1.tenancy.oc1..aaaaaaaabyypi3rfbeajp3lix4wwkrmsewwvz2rezuneuxnpmnl76eufa3oa"   # <-- replace with Tenancy A OCID
REGION = "ap-mumbai-1"


def main():
    # Require exactly one argument
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <email-address>")
        sys.exit(1)

    email = sys.argv[1].strip()

    # Basic validation
    if "@" not in email or "." not in email:
        print(f"Invalid email address: '{email}'")
        print(f"Please provide a email address: ")
        sys.exit(1)

    signer = InstancePrincipalsSecurityTokenSigner()
    client = oci.email.EmailClient({"region": REGION}, signer=signer)

    try:
        response = client.list_suppressions(
            compartment_id=Parent_TENANCY_OCID,  # must be tenancy OCID
            email_address=email
        )
    except ServiceError as e:
        print(f"Error listing suppressions: {e}")
        sys.exit(1)

    # Not in suppression list
    if not response.data:
        print(f"Email '{email}' is NOT in the suppression list.")
        sys.exit(0)

    suppression = response.data[0]
    print(f"Found suppression:")
    print(f" - ID: {suppression.id}")
    print(f" - Reason: {suppression.reason}")
    print(f" - Time: {suppression.time_created}")

    try:
        client.delete_suppression(suppression.id)
        print(f"Successfully removed suppression for '{email}'.")
    except ServiceError as e:
        print(f"Error deleting suppression: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

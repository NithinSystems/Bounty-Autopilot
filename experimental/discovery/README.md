# Experimental discovery components

These recovered, inactive examples are a development preview, not an installation package.

- GitHub radar searches open public GitHub issues labeled bounty.
- Algora-related search finds GitHub issues mentioning algora.io; it is not a direct Algora integration.
- Results are unverified candidates; rewards, funding and eligibility need independent review.
- The workflow requires a local radar service bound to loopback and is not a secure cloud deployment.
- Imports are inactive, webhooks are disabled, and credentials are not included.
- No claims, comments, submissions or notifications are sent by these workflows.

Run the backend unit tests from this directory with:

    python -m unittest discover -s phase1 -p test_store.py -v

A complete deployment guide, licensing review, cloud security review and end-to-end tests remain outstanding. Do not expose the service publicly.

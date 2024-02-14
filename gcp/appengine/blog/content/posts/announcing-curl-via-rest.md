---
title: "CURL joins OSV thanks to new REST API Contribution Support"
date: 2024-02-15T22:00:00Z
draft: false
author: OSV Team
---
As part of OSV’s strategy to be a comprehensive, accurate and timely database of known vulnerabilities, we're excited to announce that we now support CURL advisories in the OSV database, thanks to REST API contribution support. CURL has been providing vulnerability records in the OSV format for a while, but they haven’t been able to be imported until now.
<!-- more -->

Adding REST API support to our existing contribution methods (Git repository and public GCS bucket) now offers contributors three convenient ways to share vulnerability data with OSV.

Have data you want to contribute through REST endpoints? Keep reading the quick guide below!

<h2>How to Contribute Data via REST API:</h2>

1. **Provide a GET endpoint for listing all available vulnerabilities.**

    Share a URL pointing to a REST endpoint that lists, at minimum, all vulnerability IDs and their last modified dates.
This endpoint should contain information in this format:

    ```
    [{
        "id": "OSV-CVE-2020-1111",
        "modified": "2023-12-04T10:12:08.00Z"
    }, {
        "id": "OSV-CVE-2020-1112",
        "modified": "2023-12-04T10:16:25.00Z"
    }]
    ```
2. **Specify the Base URL for Full Vulnerability Endpoints**

    Indicate the base URL where full vulnerability details can be accessed in OSV format.
    Individual vulnerability endpoints should follow this structure: ``https://{base_url}/{id}.json``

3. **Indicate Extension for Individual Endpoints:**

    While .json is preferred, let us know if you need to use a different extension.


**Open an Issue to Get Started!**

Ready to contribute? Simply open an issue on our GitHub repository: https://github.com/google/osv.dev/issues, provide the necessary information outlined above, and our team will work with you to integrate your data smoothly.

**Together, we can strengthen the open source ecosystem by making vulnerability information more accessible and actionable. Let's continue building a more secure future for open source software.**
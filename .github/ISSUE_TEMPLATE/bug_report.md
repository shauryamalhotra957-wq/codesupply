name: Bug Report
description: Create a report to help us improve CodeSupply
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: Thanks for taking the time to report an issue with CodeSupply!
  - type: input
    id: version
    attributes:
      label: CodeSupply Version / Commit
    validations:
      required: true
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: Describe what you were doing when the issue occurred.
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Step-by-step instructions to reproduce the issue.
    validations:
      required: true

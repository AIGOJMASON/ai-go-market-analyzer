def validate(output):
    if "artifact_type" not in output:
        raise ValueError("Invalid output")

    return {
        "status": "passed",
        "receipt_type": "watcher_success"
    }
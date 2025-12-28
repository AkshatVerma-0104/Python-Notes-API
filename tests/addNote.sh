#!/bin/bash
set -e

echo "Enter Content : "
read userContent

echo "Enter Tags : "
read userTags

echo "Testing POST Route: /addNote"

if ! curl -X POST "http://127.0.0.1:8000/addNote" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"content":"hello","tags":["test"]}'; then
    echo "Request failed!" >&2
    exit 1
fi

echo
echo "Test completed successfully!"

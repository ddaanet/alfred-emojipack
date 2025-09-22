#!/bin/bash
set -euo pipefail

# Test runner for Alfred emoji generator

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TEST_OUTPUT_DIR="${SCRIPT_DIR}/test_output"

# Setup test environment
setup_tests() {
    echo "Setting up test environment..."
    mkdir -p "${TEST_OUTPUT_DIR}"
    
    # Install dependencies for testing
    pip install requests click > /dev/null 2>&1 || true
}

# Cleanup test artifacts
cleanup_tests() {
    echo "Cleaning up test artifacts..."
    rm -rf "${TEST_OUTPUT_DIR}"
}

# Test Python script functionality
test_python_script() {
    echo "Testing Python script..."
    
    # Test help
    python3 "${SCRIPT_DIR}/alfred_emoji_generator.py" --help > /dev/null
    
    # Test unittest suite
    python3 -m unittest "${SCRIPT_DIR}/alfred_emoji_generator.py" -v
    
    # Test limited emoji generation
    python3 "${SCRIPT_DIR}/alfred_emoji_generator.py" \
        --max-emojis 5 \
        --output "${TEST_OUTPUT_DIR}/test_sample.alfredsnippets" \
        --bundle-name "Test Pack"
    
    # Verify output file exists and is valid JSON
    if [[ ! -f "${TEST_OUTPUT_DIR}/test_sample.alfredsnippets" ]]; then
        echo "ERROR: Output file not created"
        return 1
    fi
    
    # Test JSON validity
    python3 -m json.tool "${TEST_OUTPUT_DIR}/test_sample.alfredsnippets" > /dev/null
    
    echo "✓ Python script tests passed"
}

# Test shell script functionality
test_shell_script() {
    echo "Testing shell script..."
    
    # Test help command
    "${SCRIPT_DIR}/setup_emoji_packs.sh" help > /dev/null
    
    # Test generate command with small output
    "${SCRIPT_DIR}/setup_emoji_packs.sh" generate -o "${TEST_OUTPUT_DIR}"
    
    # Verify generated files
    local expected_files=(
        "emoji-github.alfredsnippets"
        "emoji-slack.alfredsnippets" 
        "emoji-sample.alfredsnippets"
    )
    
    for file in "${expected_files[@]}"; do
        if [[ ! -f "${TEST_OUTPUT_DIR}/${file}" ]]; then
            echo "ERROR: Expected file ${file} not found"
            return 1
        fi
        
        # Verify JSON structure
        python3 -c "
import json
with open('${TEST_OUTPUT_DIR}/${file}') as f:
    data = json.load(f)
    assert 'alfredsnippet' in data
    assert 'snippets' in data['alfredsnippet']
    assert len(data['alfredsnippet']['snippets']) > 0
"
    done
    
    echo "✓ Shell script tests passed"
}

# Run performance test
test_performance() {
    echo "Testing performance with limited dataset..."
    
    local start_time=$(date +%s)
    
    python3 "${SCRIPT_DIR}/alfred_emoji_generator.py" \
        --max-emojis 50 \
        --output "${TEST_OUTPUT_DIR}/perf_test.alfredsnippets" > /dev/null
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "✓ Performance test completed in ${duration}s"
    
    # Verify reasonable execution time (should be under 10 seconds)
    if [[ $duration -gt 10 ]]; then
        echo "WARNING: Execution took longer than expected (${duration}s)"
    fi
}

# Run all tests
run_all_tests() {
    echo "Running Alfred emoji generator test suite..."
    echo "============================================="
    
    setup_tests
    
    # Trap cleanup on exit
    trap cleanup_tests EXIT
    
    test_python_script
    test_shell_script
    test_performance
    
    echo "============================================="
    echo "✓ All tests passed successfully!"
}

# Show usage
usage() {
    cat << EOF
Usage: $0 [TEST_SUITE]

Test Suites:
    python      Test Python script only
    shell       Test shell script only
    perf        Test performance only
    all         Run all tests (default)
    
Options:
    -h          Show this help
EOF
}

# Main execution
main() {
    case "${1:-all}" in
        python)
            setup_tests
            trap cleanup_tests EXIT
            test_python_script
            ;;
        shell)
            setup_tests
            trap cleanup_tests EXIT
            test_shell_script
            ;;
        perf)
            setup_tests
            trap cleanup_tests EXIT
            test_performance
            ;;
        all)
            run_all_tests
            ;;
        -h|--help|help)
            usage
            exit 0
            ;;
        *)
            echo "Error: Unknown test suite '${1}'"
            usage
            exit 1
            ;;
    esac
}

main "$@"

import os
import subprocess
import webbrowser

def generate_coverage_report():
    """Generate HTML coverage report for backend code."""
    print("Generating coverage report...")

    # Run pytest with coverage
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=html"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Print the output
    print(result.stdout)

    if result.stderr:
        print("Errors:")
        print(result.stderr)

    # Check if the report was generated
    report_path = os.path.join(os.getcwd(), "htmlcov", "index.html")
    if os.path.exists(report_path):
        print(f"Coverage report generated at: {report_path}")

        # Open the report in the default browser
        try:
            print("Opening report in browser...")
            webbrowser.open(f"file:///{os.path.abspath(report_path)}")
            print("Report opened in browser.")
        except Exception as e:
            print(f"Failed to open report in browser: {str(e)}")
            print(f"Please open the report manually at: {report_path}")
    else:
        print("Coverage report was not generated.")

    return result.returncode

if __name__ == "__main__":
    generate_coverage_report()

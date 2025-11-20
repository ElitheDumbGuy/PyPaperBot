import subprocess
import time
import sys
import os
import threading

def reader(pipe, queue):
    try:
        with pipe:
            for line in iter(pipe.readline, ''):
                queue.append(line)
    finally:
        pass

def run_analysis():
    # Command to run the CLI
    # We use 2 pages to get approx 20 papers (default 10 per page)
    cmd = [
        sys.executable, "-m", "core.cli",
        "--query", "machine learning",
        "--scholar-pages", "2", 
        "--expand-network",
        "--dwn-dir", "./output_ml_test",
        "--no-headless" 
    ]
    
    # Force UTF-8 for subprocess
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    print(f"Running command: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        bufsize=1, # Line buffered
        env=env
    )
    
    # Simple reading loop
    output_buffer = []
    
    try:
        start_time = time.time()
        while True:
            # Non-blocking read line
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                # Clean print for console
                clean_line = line.strip()
                if clean_line:
                    try:
                         sys.stdout.write(line)
                    except:
                         pass
                
                output_buffer.append(line)
                full_output = "".join(output_buffer)

                # Check for the specific "Enter choice" prompt which means we reached the end of analysis
                if "Enter choice" in line:
                    print("\n[Analysis] Menu reached! Capturing results...")
                    time.sleep(2)
                    # Send "4" to select 'All' and exit gracefully
                    process.stdin.write("4\n")
                    process.stdin.flush()
                    break
            
            # Timeout safety (5 minutes)
            if time.time() - start_time > 300:
                print("\n[Analysis] Timeout reached!")
                process.terminate()
                break

        # Wait for process to finish
        process.wait(timeout=10)
        
    except Exception as e:
        print(f"\n[Analysis] Error: {e}")
        process.terminate()

if __name__ == "__main__":
    run_analysis()

import subprocess
import time

def run_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(process.stdout.readline, b''):
            print(line.decode('utf-8').strip())
        process.wait()
    except Exception as e:
        print(f"Error running command: {e}")

print("Starting to pull Ollama models (this might take a while depending on your internet connection)...")

# Waiting for Ollama container to be ready (if using docker compose)
print("Waiting 10 seconds to ensure Ollama service is responsive...")
time.sleep(10)

models_to_pull = ["llama3", "mxbai-embed-large"]

for model in models_to_pull:
    print(f"\nPulling model: {model}")
    run_command(f"docker exec -it ticketmanagement-ollama-1 ollama run {model} ''") # In docker, we can use docker exec

print("\nModel setup complete.")

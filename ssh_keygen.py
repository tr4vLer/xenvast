import subprocess
import os

def generate_ssh_key():
    # Define the path for the key files
    home_dir = os.path.expanduser('~')
    ssh_dir = os.path.join(home_dir, '.ssh')
    os.makedirs(ssh_dir, exist_ok=True)  # Ensure the .ssh directory exists
    key_path = os.path.join(ssh_dir, 'id_ed25519')

    # Check if the key already exists
    if os.path.exists(key_path):
        message = "SSH key found."
    else:
        # Generate the SSH key if it doesn't exist, suppressing its output
        cmd = [
            'ssh-keygen',
            '-t', 'ed25519',
            '-f', key_path,
            '-N', '',  # No passphrase
            #'-C', '',  # Removed the comment option
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            message = "SSH key generated."
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while generating the SSH key: {e}")
            return

    # Read and print the public key
    try:
        with open(f"{key_path}.pub", 'r') as pub_key_file:
            pub_key = pub_key_file.read().strip()
            print(f"{message} Public Key:\n{pub_key}")
    except IOError as e:
        print(f"Could not read the public key: {e}")
        return

    # Print the path to the private key file
    print(f"Private key path: {key_path}")

if __name__ == '__main__':
    generate_ssh_key()

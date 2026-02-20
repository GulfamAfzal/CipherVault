import sys
import os
import getpass
from crypto_engine import encrypt_file, decrypt_file
from drive_manager import upload_file, download_file

def main():
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("  Encrypt only:      python main.py encrypt input_file output_file")
        print("  Decrypt only:      python main.py decrypt input_file output_file")
        print("  Encrypt + Upload:  python main.py encrypt_upload input_file")
        print("  Download + Decrypt:python main.py download_decrypt file_id output_file")
        return

    mode = sys.argv[1]
    password = getpass.getpass("Enter password: ")

    try:
        if mode == "encrypt":
            encrypt_file(sys.argv[2], sys.argv[3], password)
            print("Encryption successful.")

        elif mode == "decrypt":
            decrypt_file(sys.argv[2], sys.argv[3], password)
            print("Decryption successful.")

        elif mode == "encrypt_upload":
            temp = "temp_encrypted.cvault"
            encrypt_file(sys.argv[2], temp, password)
            file_id = upload_file(temp)
            os.remove(temp)
            print(f"Done! Save this File ID: {file_id}")

        elif mode == "download_decrypt":
            temp = "temp_download.cvault"
            download_file(sys.argv[2], temp)
            decrypt_file(temp, sys.argv[3], password)
            os.remove(temp)
            print("Download and decryption successful.")

        else:
            print("Invalid mode.")

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()
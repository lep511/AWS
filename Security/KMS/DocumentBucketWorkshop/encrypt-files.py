import os
import boto3
import random
import argparse
from datetime import datetime

# Load keys arn from ./kms-arn file
keys = []
try:
    with open(os.path.expanduser('./kms-arn'), 'r') as f:
        for line in f:
            if line.startswith('arn:aws:kms'):
                keys.append(line.strip())
except Exception as e:
    print(f"An error occurred while reading the ./kms-arn file.\n")
    raise e
    
# Load context from ./kms-context file
try:
    with open(os.path.expanduser('./kms-context'), 'r') as f:
        context = f.read().strip()
except Exception as e:
    print(f"An error occurred while reading the ./kms-context file.\n")
    raise e
else:
    print(f"Encryption context: {context}")

parser = argparse.ArgumentParser(description="Encrypts all files in a directory.")

parser.add_argument(
    '--type',
    dest="Type",
    type=str,
    help="The type of operation to perform. Valid values are 'encrypt' and 'decrypt'.",
    required=True
    )

parser.add_argument(
    '--directory',
    dest="Directory",
    type=str,
    help="The directory containing the files to encrypt/decrypt.",
    required=True
    )

parser.add_argument(
    '--encryption-context',
    dest="EncryptionContext",
    help="The encryption context to use when encrypting/decrypting the files.",
    required=False,
    default="purpose=test"
    )   

# This will inspect the command line, convert each argument to the appropriate type and then invoke the appropriate action.
args = parser.parse_args()

def input_validation(item):
    if item['Type'] not in ['encrypt', 'decrypt']:
        print("The argument --type must be either 'encrypt' or 'decrypt'.")
        return False
            
    elif item['Directory'] is None:
        print("The argument --directory must be specified.")
        return False
    
    elif not os.path.exists(item['Directory']) or not os.path.isdir(item['Directory']):
        print(f"The directory {item['Directory']} does not exist.")
        return False
        
    else:
        return True

def encrypt_files(**kwargs):
    print("Compressing files...")
    # Get the list of files in the directory
    dir_encrypted = f"{args.Directory}/encrypted"
    files = os.listdir(args.Directory)
    files = [f for f in files if os.path.isfile(os.path.join(args.Directory, f))]
    
    for file in files:
        os.system(f"gzip -c {args.Directory}/{file} > {args.Directory}/{file}.gz")
    
    # Create a directory to store the encrypted files
    temp_dir = f"{args.Directory}/temp-{random.randint(100000, 999999)}"
    os.system(f"mkdir {temp_dir}")
    # Move the compressed files to the encrypted directory
    os.system(f"mv {args.Directory}/*.gz {temp_dir}")
    # Create a directory to store the encrypted files
    if not os.path.exists(dir_encrypted):
        os.system(f"mkdir {dir_encrypted}")
    
    # Create a directory to store the metadata
    if not os.path.exists('./metadata'):
        os.system(f"mkdir ./metadata")
        
    metadata_file = 'metadata-' + datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        print(f"Encrypting files to {dir_encrypted}...")
        wrap_text = ''
        for key in keys:
            wrap_text += f"key={key} "
        
        os.system(f"""aws-encryption-cli --encrypt \
            --input {temp_dir} --recursive \
            --wrapping-keys {wrap_text} \
            --metadata-output ./metadata/{metadata_file} \
            --encryption-context {context} \
            --commitment-policy require-encrypt-require-decrypt \
            --output {dir_encrypted}""")
    except Exception as e:
        os.system(f"rm -rf {temp_dir}")
        print(f"An error occurred while encrypting the files: {e}")
    else:
        os.system(f"rm -rf {temp_dir}")
               
def decrypt_files():    
    # Create a temporary directory
    temp_dir = f"{args.Directory}/temp-{random.randint(100000, 999999)}"
    os.system(f"mkdir {temp_dir}")
    # Copy the encrypted files to the temporary directory
    os.system(f"cp {args.Directory}/*.encrypted {temp_dir}")
    
    dir_decrypted = f"{args.Directory}/decrypted"
    if not os.path.exists(dir_decrypted):
        os.system(f"mkdir {dir_decrypted}")
    
    try:
        print(f"Decrypting files to {dir_decrypted}...")
        os.system(f"""aws-encryption-cli --decrypt \
            --input {temp_dir} --recursive \
            --wrapping-keys key={keys[0]} \
            --metadata-output ~/metadata \
            --encryption-context {context} \
            --commitment-policy require-encrypt-require-decrypt \
            --output {dir_decrypted} --interactive""")
            
    except Exception as e:
        print(f"An error occurred while decrypting the files: {e}")
        os.system(f"rm -rf {temp_dir}")
    
    else:
        os.system(f"rm -rf {temp_dir}")
    
    files = os.listdir(dir_decrypted)
    files = [f for f in files if os.path.isfile(os.path.join(dir_decrypted, f)) and f.endswith('.decrypted')]
    
    for file in files:
        fix_file = file.replace('.encrypted.decrypted', '')
        os.system(f"mv {dir_decrypted}/{file} {dir_decrypted}/{fix_file}")
        
    files = os.listdir(dir_decrypted)
    files = [f for f in files if os.path.isfile(os.path.join(dir_decrypted, f)) and f.endswith('.gz')]
    
    print("Decompressing files...")
    for file in files:
        os.system(f"gunzip {dir_decrypted}/{file}")
        #os.system(f"rm {dir_decrypted}/{file}.encrypted")

         
def main(**kwargs):
    _args = kwargs
    if input_validation(_args):
        if args.Type == 'encrypt':
            encrypt_files()
        elif args.Type == 'decrypt':
            decrypt_files()

if __name__ == "__main__":
    
    main(**vars(args))
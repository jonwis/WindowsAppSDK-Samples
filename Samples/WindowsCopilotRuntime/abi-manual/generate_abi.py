import os
import sys
import argparse
import glob
import subprocess
import shutil

DEFAULT_SDK_PATH = os.path.join(os.path.dirname(__file__), "out/sdk")

def main():
    # Finds and runs the abi.exe tool over the SDK's WinMD contents. The content
    # is self-contained in the SDK root; don't for it in any installed SDK location.
    parser = argparse.ArgumentParser(description="Build the updated ABI headers")
    parser.add_argument("--sdk-path", default=DEFAULT_SDK_PATH, help="The location of the SDK to use")
    parser.add_argument("--clean", action="store_true", help="Clean the output directory before running abi.exe")
    args = parser.parse_args()

    sdk_path = os.path.abspath(args.sdk_path)
    if not os.path.exists(sdk_path):
        print(f"SDK path does not exist: {sdk_path}")
        sys.exit(1)

    # In the SDK path, find abi.exe and all the WinMD files; just pick the first one
    abi_exe = glob.glob(root_dir=sdk_path, pathname="**/abi.exe", recursive=True)
    winmd_files = glob.glob(root_dir=sdk_path, pathname="**/*.winmd", recursive=True)

    # Convert the paths to absolute paths
    abi_exe = [os.path.join(sdk_path, path) for path in abi_exe]
    winmd_files = [os.path.join(sdk_path, path) for path in winmd_files]

    # The output directory in the SDK path is "abi", make sure it exists
    output_dir = os.path.join(sdk_path, "abi")
    if args.clean and os.path.exists(output_dir):
        print(f"Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)

    # Build a .rsp file with the arguments for abi.exe
    rsp_file = os.path.join(output_dir, "abi.exe.rsp")
    with open(rsp_file, "w") as f:
        f.write(f"-output \"{output_dir}\"\n")
        f.write(f"-lowercase-include-guard\n")
        f.write(f"-enum-class\n")
        for winmd in winmd_files:
            f.write(f"-input \"{winmd}\"\n")

    # Call abi.exe with the .rsp file
    if abi_exe:
        abi_exe = abi_exe[0]
    else:
        print("abi.exe not found")
        sys.exit(1)

    command = [abi_exe, f"@{rsp_file}"]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"abi.exe failed: {result.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
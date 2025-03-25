import os
import subprocess
import urllib.request
import argparse
import tempfile
import shutil
import glob
import hashlib

def join_path(base_path, *paths):
    """Join a base path with one or more additional paths."""
    return os.path.normpath(os.path.join(base_path, *paths))




NUGET_URL = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
OUTPUT_DIR = join_path(os.path.dirname(__file__), "out/wasdk")

dependencies = [
    {
        "name": "Microsoft.WindowsAppSDK",
        "version": "1.7.250127003-experimental3",
        "url": "https://www.nuget.org/api/v2/package/Microsoft.WindowsAppSDK/1.7.250127003-experimental3",
        "SHA256": "15e2d9ee1cb4b9a4a6dc93ff4b155e6d4bfd9e7fdc3b3aa10faa28e3dd4e5866"
    },
    {
        "name": "Microsoft.Web.WebView2",
        "version": "1.0.3124.44",
        "url": "https://www.nuget.org/api/v2/package/Microsoft.Web.WebView2/1.0.3124.44",
        "SHA256": "31d61a59a5d5ae2ef5dcb9f175b626c1d64218217f879701ec73ed8fd74b65ae"
    },
    {
        "name": "Microsoft.Windows.ABIWinRT",
        "version": "2.0.210330.2",
        "url": "https://www.nuget.org/api/v2/package/Microsoft.Windows.ABIWinRT/2.0.210330.2",
        "SHA256": "9f94ddbd2fe85ee9e71787c6b67eec03939b2017d6bfab05a064b07b51f99d66"
    },
]

def fetch_packages(out_dir):
    package_dir_temp = join_path(out_dir, "packageSource")
    for dep in dependencies:
        package_name = dep["name"]
        package_version = dep["version"]
        package_url = dep["url"]
        package_sha256 = dep["SHA256"]

        # Create the output directory for the package
        os.makedirs(package_dir_temp, exist_ok=True)
        package_file = join_path(package_dir_temp, f"{package_name}.{package_version}.nupkg")
        if os.path.exists(package_file):
            continue

        # Fetch, then check the SHA256 of what we got
        print(f"Fetching {package_name}...")
        urllib.request.urlretrieve(package_url, package_file)
        if package_sha256:
            sha256 = hashlib.sha256()
            with open(package_file, "rb") as f:
                sha256.update(f.read())
            if (sha256.hexdigest() != package_sha256):
                if package_sha256 == "0":
                    print(f"SHA256 for {package_file} out of date - should be {sha256.hexdigest()}")
                else:
                    raise RuntimeError(f"SHA256 mismatch for {package_file}. Expected {package_sha256}, got {sha256.hexdigest()}")

        # Extract the package to the output directory
        package_unpacked = join_path(out_dir, package_name)
        shutil.unpack_archive(package_file, package_unpacked, "zip")

def generate_abi(target_dir, winmd_refs):
    # Find the abi.exe tool in the target directory
    abi_exe = glob.glob(root_dir=target_dir, pathname="**/abi.exe", recursive=True)
    if not abi_exe:
        raise RuntimeError(f"ABI executable not found in {target_dir}. Please check the installation.")
    abi_exe = join_path(target_dir, abi_exe[0])

    # Collect all the WinMD files in the target directory
    winmd_files = glob.glob(root_dir=target_dir, pathname="**/*.winmd", recursive=True)
    if not winmd_files:
        raise RuntimeError("No WinMD files found for ABI generation.")

    # Output the ABI files to a directory named "abi" in the target directory
    abi_dir = join_path(target_dir, "include", "abi")
    os.makedirs(abi_dir, exist_ok=True)

    rsp_file = join_path(target_dir, "abi.rsp")
    with open(rsp_file, "w") as f:
        f.write(f"-output \"{abi_dir}\"\n")
        f.write(f"-lowercase-include-guard\n")
        f.write(f"-enum-class\n")
        for ref in winmd_refs:
            f.write(f"-reference \"{ref}\"\n")
        for winmd in [join_path(target_dir, file) for file in winmd_files]:
            f.write(f"-input \"{winmd}\"\n")

    # Call abi.exe with the .rsp file
    command = [abi_exe, f"@{rsp_file}"]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"ABI generation failed: {result.stderr}")
    
    return abi_dir

def main():
    parser = argparse.ArgumentParser(description="Restore NuGet packages.")
    parser.add_argument("--refresh", action="store_true", help="Refresh the packages")
    parser.add_argument("--winmd-refs", nargs="+", default=["sdk"], help="WinMD references to include in the ABI generation")
    parser.add_argument("--out", default=OUTPUT_DIR, help="Directory to restore packages to")
    args = parser.parse_args()

    if args.refresh and os.path.exists(args.out):
        print(f"Removing existing output directory: {args.out}")
        shutil.rmtree(args.out)

    fetch_packages(args.out)
    abi_dir = generate_abi(args.out, args.winmd_refs)

    print(f"Packages restored to {args.out}.")
    include_paths = [
        abi_dir,
        join_path(args.out, "Microsoft.WindowsAppSDK", "include")
    ]
    print(f"Add these to your include path:")
    for path in include_paths:
        print(f"  {path}")

    return 0

if __name__ == "__main__":
    main()
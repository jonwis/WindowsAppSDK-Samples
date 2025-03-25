import os
import subprocess
import urllib.request
import argparse
import tempfile
import shutil
import glob

def join_path(base_path, *paths):
    """Join a base path with one or more additional paths."""
    return os.path.normpath(os.path.join(base_path, *paths))

NUGET_URL = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
OUTPUT_DIR = join_path(os.path.dirname(__file__), "out/wasdk")

dependencies = {
    "Microsoft.WindowsAppSDK": "1.7.250127003-experimental3",
    "Microsoft.Web.WebView2": "1.0.3124.44",
    "Microsoft.Windows.ABIWinRT": "2.0.210330.2"
}

def get_nuget_path():
    # See if there's an environment variable set for nuget.exe
    nuget_path = os.environ.get("NUGET_PATH")
    if nuget_path and os.path.exists(nuget_path):
        return nuget_path

    # See if nuget is on the path somewhere
    for path in os.environ["PATH"].split(os.pathsep):
        nuget_path = join_path(path, "nuget.exe")
        if os.path.exists(nuget_path):
            return nuget_path

    # If we get here, nuget.exe is not found. Download it.
    with tempfile.TemporaryDirectory() as temp_dir:
        nuget_path = join_path(temp_dir, "nuget.exe")
        nuget_url = os.environ.get("NUGET_URL") or NUGET_URL
        urllib.request.urlretrieve(nuget_url, nuget_path)
        return nuget_path

def deploy_packages(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    packages_config = join_path(target_dir, "packages.config")
    with open(packages_config, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>\n<packages>\n""")
        for package, version in dependencies.items():
            f.write(f"""    <package id="{package}" version="{version}" />\n""")
        f.write("""</packages>""")
    
    nuget_path = get_nuget_path()
    command = [nuget_path, "restore", packages_config, "-OutputDirectory", target_dir]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command)
    if result.returncode != 0:
        raise RuntimeError(f"NuGet restore failed: {result.stderr}")

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
    output_dir = join_path(target_dir, "abi")
    os.makedirs(output_dir, exist_ok=True)

    rsp_file = join_path(target_dir, "abi.rsp")
    with open(rsp_file, "w") as f:
        f.write(f"-output \"{output_dir}\"\n")
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

def main():
    parser = argparse.ArgumentParser(description="Restore NuGet packages.")
    parser.add_argument("--nuget-path", help="Path to nuget.exe")
    parser.add_argument("--refresh", action="store_true", help="Refresh the packages")
    parser.add_argument("--winmd-refs", nargs="+", default=["sdk"], help="WinMD references to include in the ABI generation")
    parser.add_argument("--out", default=OUTPUT_DIR, help="Directory to restore packages to")
    args = parser.parse_intermixed_args()

    if args.refresh and os.path.exists(args.out):
        print(f"Removing existing output directory: {args.out}")
        shutil.rmtree(args.out)

    deploy_packages(args.out)
    generate_abi(args.out, args.winmd_refs)

    print(f"Packages restored to {args.out}.")
    include_paths = [
        join_path(args.out, "abi"),
        join_path(args.out, f"Microsoft.WindowsAppSDK.{dependencies['Microsoft.WindowsAppSDK']}", "include")
    ]
    print(f"Add these to your include path:")
    for path in include_paths:
        print(f"  {path}")

    return 0

if __name__ == "__main__":
    main()
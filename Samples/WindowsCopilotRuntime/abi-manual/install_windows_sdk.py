import os
import subprocess
import urllib.request
import argparse
import tempfile
import shutil
import time
import json

NUGET_URL = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
WINSDK_VERSION = "10.0.26100.3323"
WINSDK_TOOLS_VERSION = "10.0.26100.1742"
WASDK_VERSION = "1.7.250310001"

def get_nuget_path():
    # See if there's an environment variable set for nuget.exe
    nuget_path = os.environ.get("NUGET_PATH")
    if nuget_path and os.path.exists(nuget_path):
        return nuget_path

    # See if nuget is on the path somewhere
    for path in os.environ["PATH"].split(os.pathsep):
        nuget_path = os.path.join(path, "nuget.exe")
        if os.path.exists(nuget_path):
            return nuget_path

    # If we get here, nuget.exe is not found. Download it.
    with tempfile.TemporaryDirectory() as temp_dir:
        nuget_path = os.path.join(temp_dir, "nuget.exe")
        nuget_url = os.environ.get("NUGET_URL") or NUGET_URL
        urllib.request.urlretrieve(nuget_url, nuget_path)
        return nuget_path

def move_with_retry(src, dst, retries=3):
    for attempt in range(retries):
        try:
            shutil.move(src, dst)
            return
        except OSError as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(1)  # Optional: sleep for a second before retrying
            else:
                raise RuntimeError(f"Failed to move {src} to {dst} after {retries} attempts.") from e

def main():
    parser = argparse.ArgumentParser(description="Restore NuGet packages.")
    parser.add_argument("--nuget-path", help="Path to nuget.exe")
    parser.add_argument("--refresh", action="store_true", help="Refresh the packages")
    parser.add_argument("--sdk-version", default=WINSDK_VERSION, help="Version of the Windows SDK to install")
    parser.add_argument("--wasdk-version", default=WASDK_VERSION, help="Version of the Windows App SDK to install")
    parser.add_argument("--tools-version", default=WINSDK_TOOLS_VERSION, help="Version of the Windows SDK Build tools to install")
    parser.add_argument("--output-dir", required=True, help="Directory to restore packages to")
    parser.add_argument("--like-sdk", action="store_true", help="Use the layout of the Windows SDK")
    parser.add_argument("architecture", nargs="+", help="One or more architectures of the Windows SDK (x86, arm64, or x64)")
    args = parser.parse_intermixed_args()

    # We only support x86, x64, and arm64 architectures; check all the architectures
    # and make sure the user didn't specify any unsupported ones.
    architectures = ["x86", "x64", "arm64"]
    for arch in args.architecture:
        if arch not in architectures:
            raise ValueError(f"Unsupported architecture: {arch}. Supported architectures are: {', '.join(architectures)}")    

    # Verify that the SDK version has four parts, each part being a number
    version_parts = args.sdk_version.split(".")
    if len(version_parts) != 4 or not all(part.isdigit() for part in version_parts):
        raise ValueError(f"Invalid SDK version format: {args.sdk_version}. Expected format: major.minor.build.revision")

    # Go get nuget.exe
    nuget_path = args.nuget_path or get_nuget_path()
    if not nuget_path:
        raise RuntimeError("nuget.exe not found and could not be downloaded.")
    
    # Refreshing the packages means deleting the output directory and re-creating it
    if args.refresh and os.path.exists(args.output_dir):
        print(f"Removing existing output directory: {args.output_dir}")
        shutil.rmtree(args.output_dir)

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Create a packages.config in the output directory containing all the packages we want to install
    packages_config = os.path.join(args.output_dir, "packages.config")
    with open(packages_config, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>\n<packages>\n""")
        for arch in args.architecture:
            f.write(f"""    <package id="Microsoft.Windows.SDK.CPP.{arch}" version="{args.sdk_version}" />\n""")
        f.write(f"""    <package id="Microsoft.Windows.SDK.CPP" version="{args.sdk_version}" />\n""")
        f.write(f"""    <package id="Microsoft.Windows.SDK.BuildTools" version="{args.tools_version}" />\n""")
        f.write(f"""    <package id="Microsoft.WindowsAppSDK" version="{args.wasdk_version}" />\n""")
        f.write("""</packages>""")

    # Fetch the packages using nuget.exe
    command = [nuget_path, "restore", packages_config, "-OutputDirectory", args.output_dir]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command)
    if result.returncode != 0:
        raise RuntimeError(f"NuGet restore failed: {result.stderr}")
    
    # Optionally lay out the SDK to look like the Windows SDK MSI installer
    if args.like_sdk:
        environment = combine_nugets_like_sdk(args)
    else:
        environment = use_nuget_layout(args)

    # Write the environment variables to a JSON file
    with open(os.path.join(args.output_dir, "environment.json"), "w") as f:
        json.dump(environment, f, indent=4)

    return 0

def combine_nugets_like_sdk(args):
    # Final assembly location of the SDK
    final_sdk_path = os.path.join(args.output_dir, "WindowsSDK")
    os.makedirs(final_sdk_path, exist_ok=True)

    # From the base CPP package path, move the content of the "c" directory to the output directory
    cdir = os.path.join(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c")
    if not os.path.exists(cdir):
        raise RuntimeError(f"Content directory not found at {cdir}. Please check the SDK version and architecture.")

    # Move the content of the "c" directory to the output directory
    for item in os.listdir(cdir):
        src = os.path.join(cdir, item)
        dst = os.path.join(final_sdk_path, item)
        if os.path.exists(dst):
            raise RuntimeError(f"File {dst} already exists. Please remove it before running this script.")
        move_with_retry(src, dst)

    # The expected SDK layout is like Lib\10.0.22621.0\ucrt\arm64\libucrt.lib and the nuget contents
    # are like c\ucrt\arm64\libucrt.lib. Move the contents of the c directory to the Lib directory
    for arch in args.architecture:
        src_group_dir = os.path.join(args.output_dir, f"Microsoft.Windows.SDK.CPP.{arch}.{args.sdk_version}", "c")
        dst_group_dir = os.path.join(final_sdk_path, "Lib", args.sdk_version)
        for group in os.listdir(src_group_dir):
            src_group_path = os.path.join(src_group_dir, group, arch)
            dst_group_path = os.path.join(dst_group_dir, group, arch)
            os.makedirs(os.path.dirname(dst_group_path), exist_ok=True)
            move_with_retry(src_group_path, dst_group_path)

    # The SDK tools package contains paths like bin\10.0.26100.0\arm64\appxpackaging.dll. Copy the content
    # to SDK layout path, like bin\10.0.26100.0\arm64\appxpackaging.dll. The version string in the path is
    # the tools version, which is not necessarily the same as the SDK version.
    #
    # Find the version of the tools package from the directory path under "bin"
    tools_source_dir = os.path.join(args.output_dir, f"Microsoft.Windows.SDK.BuildTools.{args.tools_version}", "bin")
    tools_version = os.listdir(tools_source_dir)[0]
    tools_source_path = os.path.join(tools_source_dir, tools_version)
    tools_dst_path = os.path.join(final_sdk_path, "bin", tools_version)
    shutil.copytree(tools_source_path, tools_dst_path, dirs_exist_ok=True)

    # Write a JSON file containing the environment variables for this SDK location:
    # WindowsLibPath=C:\Program Files (x86)\Windows Kits\10\UnionMetadata\10.0.26100.0;C:\Program Files (x86)\Windows Kits\10\References\10.0.26100.0
    # WindowsSdkBinPath=C:\Program Files (x86)\Windows Kits\10\bin\
    # WindowsSdkDir=C:\Program Files (x86)\Windows Kits\10\
    # WindowsSDKLibVersion=10.0.26100.0\
    # WindowsSdkVerBinPath=C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\
    # WindowsSDKVersion=10.0.26100.0\
    # WindowsSDK_ExecutablePath_x64=C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools\x64\
    # WindowsSDK_ExecutablePath_x86=C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools\
    return{
        "WindowsLibPath": [ 
            os.path.join(final_sdk_path, "UnionMetadata", args.sdk_version), 
            os.path.join(final_sdk_path, "References", args.sdk_version) 
        ],
        "WindowsSdkBinPath": os.path.join(final_sdk_path, "bin") + "\\",
        "WindowsSdkDir": f"{final_sdk_path}\\",
        "WindowsSDKLibVersion": f"{args.sdk_version}\\",
        "WindowsSdkVerBinPath": f"{tools_dst_path}\\",
        "WindowsSDKVersion": f"{args.sdk_version}\\",
        "UniversalCRTSdkDir": f"{final_sdk_path}\\",
        "UCRTVersion": f"{args.sdk_version}\\",
        "ExtensionSdkDir": f"{final_sdk_path}\\Extension SDKs",
    }

def use_nuget_layout(args):
    # Pack up the paths for the "normal" nuget layout
    return {
        "WindowsLibPath": [
            os.path.join(args.output_dir, f"Microsoft.Windows.SDK.CPP.{arch}.{args.sdk_version}", "c", arch)
            for arch in args.architecture
        ],
        "WindowsSdkBinPath": os.path.join(args.output_dir, f"Microsoft.Windows.SDK.BuildTools.{args.tools_version}", "bin") + "\\",
        "WindowsSdkDir": f"{args.output_dir}\\",
        "WindowsSDKLibVersion": f"{args.sdk_version}\\",
        "WindowsSdkVerBinPath": os.path.join(args.output_dir, f"Microsoft.Windows.SDK.BuildTools.{args.tools_version}", "bin") + "\\",
        "WindowsSDKVersion": f"{args.sdk_version}\\",
        "UniversalCRTSdkDir": f"{args.output_dir}\\",
        "UCRTVersion": f"{args.sdk_version}\\",
        "ExtensionSdkDir": os.path.join(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c", "Extension SDKs"),
    }

if __name__ == "__main__":
    main()
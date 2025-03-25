import os
import subprocess
import urllib.request
import argparse
import tempfile
import shutil
import time
import json
import glob
import re
import xml.etree.ElementTree as ET

def join_path(base_path, *paths):
    """Join a base path with one or more additional paths."""
    return os.path.normpath(os.path.join(base_path, *paths))

NUGET_URL = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
WINSDK_VERSION = "10.0.26100.3323"
WINSDK_TOOLS_VERSION = "10.0.26100.1742"
WASDK_VERSION = "1.7.250310001"
ABIWINRT_VERSION = "2.0.210330.2"
WEBVIEW2_VERSION = "1.0.3124.44"
OUTPUT_DIR = join_path(os.path.dirname(__file__), "out/sdk")

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

def default_target_architecture():
    # Get the default target architecture from the environment variable. When the architecture is AMD64,
    # map to that x64. Otherwise, use it as is.
    target_arch = os.environ.get("PROCESSOR_ARCHITECTURE")
    return "x64" if target_arch == "amd64" else target_arch

def main():
    parser = argparse.ArgumentParser(description="Restore NuGet packages.")
    parser.add_argument("--nuget-path", help="Path to nuget.exe")
    parser.add_argument("--refresh", action="store_true", help="Refresh the packages")
    parser.add_argument("--sdk-version", default=WINSDK_VERSION, help="Version of the Windows SDK to install")
    parser.add_argument("--wasdk-version", default=WASDK_VERSION, help="Version of the Windows App SDK to install")
    parser.add_argument("--tools-version", default=WINSDK_TOOLS_VERSION, help="Version of the Windows SDK Build tools to install")
    parser.add_argument("--abiwinrt-version", default=ABIWINRT_VERSION, help="Version of the Windows ABI WinRT to install")
    parser.add_argument("--webview2-version", default=WEBVIEW2_VERSION, help="Version of the WebView2 SDK to install")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Directory to restore packages to")
    parser.add_argument("--like-sdk", action="store_true", help="Use the layout of the Windows SDK")
    parser.add_argument("architecture", nargs="*", default=default_target_architecture(), help="One or more architectures of the Windows SDK (x86, arm64, or x64)")
    args = parser.parse_intermixed_args()

    # We only support x86, x64, and arm64 architectures; check all the architectures
    # and make sure the user didn't specify any unsupported ones.
    architectures = ["x86", "x64", "arm64"]
    for arch in args.architecture:
        if arch not in architectures:
            raise ValueError(f"Unsupported architecture: {arch}. Supported architectures are: {', '.join(architectures)}")    

    # Refreshing the packages means deleting the output directory and re-creating it
    if args.refresh and os.path.exists(args.output_dir):
        print(f"Removing existing output directory: {args.output_dir}")
        shutil.rmtree(args.output_dir)

    os.makedirs(args.output_dir, exist_ok=True)

    # Create a packages.config in the output directory containing all the packages we want to install
    packages_config = join_path(args.output_dir, "packages.config")
    with open(packages_config, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>\n<packages>\n""")
        for arch in args.architecture:
            f.write(f"""    <package id="Microsoft.Windows.SDK.CPP.{arch}" version="{args.sdk_version}" />\n""")
        f.write(f"""    <package id="Microsoft.Windows.SDK.CPP" version="{args.sdk_version}" />\n""")
        f.write(f"""    <package id="Microsoft.Windows.SDK.BuildTools" version="{args.tools_version}" />\n""")
        f.write(f"""    <package id="Microsoft.WindowsAppSDK" version="{args.wasdk_version}" />\n""")
        f.write(f"""    <package id="Microsoft.Windows.AbiWinRT" version="{args.abiwinrt_version}" />\n""")
        f.write(f"""    <package id="Microsoft.Web.WebView2" version="{args.webview2_version}" />\n""")
        f.write("""</packages>""")

    # Fetch the packages using nuget.exe
    nuget_path = args.nuget_path or get_nuget_path()
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

    # Add both the WASDK include paths and the ABI include paths
    generate_sdk_abi(args.output_dir)
    environment["SDKIncludes"] += [join_path(args.output_dir, "abi")]
    environment["SDKIncludes"] += [join_path(args.output_dir, f"Microsoft.WindowsAppSDK.{args.wasdk_version}", "include")]

    # Write the environment variables to a JSON file
    with open(join_path(args.output_dir, "environment.json"), "w") as f:
        json.dump(environment, f, indent=4)

    return 0

def combine_nugets_like_sdk(args):
    # Final assembly location of the SDK
    final_sdk_path = join_path(args.output_dir, "WindowsSDK")
    os.makedirs(final_sdk_path, exist_ok=True)

    # From the base CPP package path, move the content of the "c" directory to the output directory
    cdir = join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c")
    if not os.path.exists(cdir):
        raise RuntimeError(f"Content directory not found at {cdir}. Please check the SDK version and architecture.")

    # Move the content of the "c" directory to the output directory
    for item in os.listdir(cdir):
        src = join_path(cdir, item)
        dst = join_path(final_sdk_path, item)
        if os.path.exists(dst):
            raise RuntimeError(f"File {dst} already exists. Please remove it before running this script.")
        move_with_retry(src, dst)

    # The expected SDK layout is like Lib\10.0.22621.0\ucrt\arm64\libucrt.lib and the nuget contents
    # are like c\ucrt\arm64\libucrt.lib. Move the contents of the c directory to the Lib directory
    for arch in args.architecture:
        src_group_dir = join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{arch}.{args.sdk_version}", "c")
        dst_group_dir = join_path(final_sdk_path, "Lib", args.sdk_version)
        for group in os.listdir(src_group_dir):
            src_group_path = join_path(src_group_dir, group, arch)
            dst_group_path = join_path(dst_group_dir, group, arch)
            os.makedirs(os.path.dirname(dst_group_path), exist_ok=True)
            move_with_retry(src_group_path, dst_group_path)

    # The SDK tools package contains paths like bin\10.0.26100.0\arm64\appxpackaging.dll. Copy the content
    # to SDK layout path, like bin\10.0.26100.0\arm64\appxpackaging.dll. The version string in the path is
    # the tools version, which is not necessarily the same as the SDK version.
    #
    # Find the version of the tools package from the directory path under "bin"
    tools_source_dir = join_path(args.output_dir, f"Microsoft.Windows.SDK.BuildTools.{args.tools_version}", "bin")
    tools_version = os.listdir(tools_source_dir)[0]
    tools_source_path = join_path(tools_source_dir, tools_version)
    tools_dst_path = join_path(final_sdk_path, "bin", tools_version)
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
            join_path(final_sdk_path, "UnionMetadata", args.sdk_version), 
            join_path(final_sdk_path, "References", args.sdk_version) 
        ],
        "WindowsSdkBinPath": join_path(final_sdk_path, "bin") + "\\",
        "WindowsSdkDir": f"{final_sdk_path}\\",
        "WindowsSDKLibVersion": f"{args.sdk_version}\\",
        "WindowsSdkVerBinPath": f"{tools_dst_path}\\",
        "WindowsSDKVersion": f"{args.sdk_version}\\",
        "UniversalCRTSdkDir": f"{final_sdk_path}\\",
        "UCRTVersion": f"{args.sdk_version}\\",
        "ExtensionSdkDir": f"{final_sdk_path}\\Extension SDKs",
        "SDKIncludes": [
            join_path(final_sdk_path, "Include", args.sdk_version, "um"),
            join_path(final_sdk_path, "Include", args.sdk_version, "shared"),
            join_path(final_sdk_path, "Include", args.sdk_version, "ucrt"),
        ]
    }

def use_nuget_layout(args):
    # Inside the "cpp" package is c\SDKManifest.xml, containing the "Identity" field - that's a
    # string like 10.0.26100.0, which is not the same as the NuGet version. Pull that SDKManifest
    # out and use it to build paths into the NuGet headers.
    manifest_path = join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c", "SDKManifest.xml")
    if not os.path.exists(manifest_path):
        raise RuntimeError(f"Manifest file not found at {manifest_path}. Please check the SDK version and architecture.")
    
    # The platform identity is a string like "UAP, Version=10.0.22621.0". Use a regex to pull out
    # the four-part version number from the string.
    platform_identity = ET.parse(manifest_path).getroot().attrib["PlatformIdentity"]
    sdk_real_version = re.match(r".*Version=(?P<version>\d+\.\d+\.\d+\.\d+)", platform_identity).groupdict()["version"]

    # Pack up the paths for the "normal" nuget layout
    return {
        "WindowsLibPath": [
            join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{arch}.{args.sdk_version}", "c")
            for arch in args.architecture
        ],
        "WindowsSdkBinPath": join_path(args.output_dir, f"Microsoft.Windows.SDK.BuildTools.{args.tools_version}", "bin") + "\\",
        "WindowsSdkDir": f"{args.output_dir}\\",
        "WindowsSDKLibVersion": f"{sdk_real_version}\\",
        "WindowsSdkVerBinPath": join_path(args.output_dir, f"Microsoft.Windows.SDK.BuildTools.{args.tools_version}", "bin") + "\\",
        "WindowsSDKVersion": f"{sdk_real_version}\\",
        "UniversalCRTSdkDir": f"{args.output_dir}\\",
        "UCRTVersion": f"{sdk_real_version}\\",
        "ExtensionSdkDir": join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c", "Extension SDKs"),   
        "SDKIncludes":[
            join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c", "include", sdk_real_version, "um"),
            join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c", "include", sdk_real_version, "shared"),
            join_path(args.output_dir, f"Microsoft.Windows.SDK.CPP.{args.sdk_version}", "c", "include", sdk_real_version, "ucrt"),
        ]
    }

def generate_sdk_abi(sdk_path):

    if not os.path.exists(sdk_path):
        raise RuntimeError(f"SDK path does not exist: {sdk_path}")

    # In the SDK path, find abi.exe and all the WinMD files; just pick the first one
    abi_exe = glob.glob(root_dir=sdk_path, pathname="**/abi.exe", recursive=True)
    winmd_files = glob.glob(root_dir=sdk_path, pathname="**/*.winmd", recursive=True)

    # Convert the paths to absolute paths
    abi_exe = [join_path(sdk_path, path) for path in abi_exe]
    winmd_files = [join_path(sdk_path, path) for path in winmd_files]

    # The output directory in the SDK path is "abi", make sure it exists
    output_dir = join_path(sdk_path, "abi")
    os.makedirs(output_dir, exist_ok=True)

    # Build a .rsp file with the arguments for abi.exe
    rsp_file = join_path(output_dir, "abi.exe.rsp")
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
        raise RuntimeError("abi.exe not found")

    command = [abi_exe, f"@{rsp_file}"]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"abi.exe failed: {result.stderr}")

if __name__ == "__main__":
    main()
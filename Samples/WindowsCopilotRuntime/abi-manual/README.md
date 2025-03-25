# Barebones ABI and Windows Copilot Runtime

This sample shows the absolute bare minimum environment to build with and use the Windows Copilot
Runtime. If you can use MSBuild, CMake, dotnet, or another build environment, do so.

## Prerequisites

This walkthrough's example steps [use PowerShell](https://learn.microsoft.com/powershell/). If
necessary, launch a command prompt window then `winget install --id Microsoft.PowerShell` and
restart the command shell, then `pwsh.exe` to start PowerShell.

You'll need a compiler like Microsoft's `cl.exe` (or one that accepts `cl.exe` style arguments such
as `clang`) available on your `PATH` environment variable.

You'll need a Python 3 environment available in your command shell. Running `python3` when one is
not present will redirect you to the Microsoft Store which has an
[installable Python 3 interpreter app](https://apps.microsoft.com/detail/9PNRBTZXMB4Z). Other
sources include `winget install python.python.3.13` or `winget install 9PNRBTZXMB4Z` (same as the
one from the Microsoft Store) or `Anaconda.Anaconda3`.

The preparation scripts will acquire and use a copy of `nuget.exe` from the official
[NuGet downloads source](https://www.nuget.org/downloads).

Clone this repo to your local machine, then start a command shell with both `cl.exe` and `python3`
in your path (and optionally `nuget.exe`).

[Install the Windows App SDK and Windows SDK](./install_windows_sdks.py) packages through your
command shell. The default location is `out/sdks/` under this directory, but you can change that as
needed.

```ps1
PS> python3 install_windows_sdks.py
```

## Building

In your command shell, build the code by running `python3 build_sample.py`. This script figures
out where your `cl.exe` toolchain is in your path, constructs the appropriate commandline, and
compiles the `abi_image_describer.exe` into the output directory.

## How it works

Both the Windows SDK and Windows App SDK are available as NuGet packages from Microsoft.

Running [install_windows_sdks.py](./install_windows_sdks.py) constructs a packages.config file
containing the desired versions of each and restores them to a local directory.

Once installed, the script generates ABI headers for Windows Runtime APIs, for teams that must use a
non-projected form of the interface. The default location is `out/sdks/abi`.

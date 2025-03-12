// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#pragma once


inline auto CreateStorageFile(winrt::hstring filepath)
{
    auto uri = winrt::Windows::Foundation::Uri(L"ms-appx:///" + filepath);
    return winrt::Windows::Storage::StorageFile::GetFileFromApplicationUriAsync(uri);
}

inline wil::com_task<winrt::hstring> ReadTextAsync(winrt::hstring filepath)
{
    if (filepath.empty())
    {
        co_return L"";
    }
    auto file = co_await CreateStorageFile(filepath);
    co_return co_await winrt::Windows::Storage::FileIO::ReadTextAsync(file);
}

inline wil::com_task<winrt::Windows::Storage::Streams::IRandomAccessStream> CreateStreamAsync(winrt::hstring filepath)
{
    if (filepath.empty())
    {
        co_return winrt::Windows::Storage::Streams::InMemoryRandomAccessStream{};
    }

    auto file = co_await CreateStorageFile(filepath);
    co_return co_await file.OpenAsync(winrt::Windows::Storage::FileAccessMode::Read);
}

// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#pragma once

#include "Controls/CodeBlockControl.g.h"

namespace winrt::WindowsCopilotRuntimeSample::Controls::implementation
{
    struct CodeBlockControl : CodeBlockControlT<CodeBlockControl>
    {
        winrt::hstring m_content;

        CodeBlockControl() = default;
        hstring SourceFile();
        void SourceFile(hstring const& value);
        winrt::fire_and_forget ExampleCode_Loaded(Windows::Foundation::IInspectable const&, Microsoft::UI::Xaml::RoutedEventArgs const&);
        void CopyButton_Click(Windows::Foundation::IInspectable const&, Microsoft::UI::Xaml::RoutedEventArgs const&);

        static void OnSourceFileChanged(
            Windows::Foundation::IInspectable const& d,
            Microsoft::UI::Xaml::DependencyPropertyChangedEventArgs const& e);

        static Microsoft::UI::Xaml::Documents::Paragraph HighlightSyntax(std::wstring_view code);
    };
}

namespace winrt::WindowsCopilotRuntimeSample::Controls::factory_implementation
{
    struct CodeBlockControl : CodeBlockControlT<CodeBlockControl, implementation::CodeBlockControl>
    {
    };
}

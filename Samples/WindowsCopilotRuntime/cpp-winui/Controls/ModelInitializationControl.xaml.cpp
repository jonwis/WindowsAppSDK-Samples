// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include "pch.h"
#include "ModelInitializationControl.xaml.h"
#include "Controls/ModelInitializationControl.g.cpp"

using namespace winrt::Microsoft::UI::Xaml;

namespace winrt::WindowsCopilotRuntimeSample::Controls::implementation
{
    static DependencyProperty InitializationSourceFile =
        DependencyProperty::Register(
            L"SourceFile",
            xaml_typename<hstring>(),
            xaml_typename<WindowsCopilotRuntimeSample::Controls::ModelInitializationControl>(),
            PropertyMetadata{ winrt::box_value(winrt::hstring(L""))});

    hstring ModelInitializationControl::SourceFile()
    {
        return winrt::unbox_value<hstring>(GetValue(InitializationSourceFile));
    }

    void ModelInitializationControl::SourceFile(hstring const& value)
    {
        SetValue(InitializationSourceFile, winrt::box_value(value));
    }
}

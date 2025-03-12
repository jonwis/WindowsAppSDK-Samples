// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#pragma once

#include "Controls/ModelInitializationControl.g.h"

namespace winrt::WindowsCopilotRuntimeSample::Controls::implementation
{
    struct ModelInitializationControl : ModelInitializationControlT<ModelInitializationControl>
    {
        ModelInitializationControl();
        hstring SourceFile();
        void SourceFile(hstring const& value);
    };
}

namespace winrt::WindowsCopilotRuntimeSample::Controls::factory_implementation
{
    struct ModelInitializationControl : ModelInitializationControlT<ModelInitializationControl, implementation::ModelInitializationControl>
    {
    };
}

#if 0
using WindowsCopilotRuntimeSample.ViewModels;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace WindowsCopilotRuntimeSample.Controls;

public sealed partial class ModelInitializationControl : UserControl
{
    public ModelInitializationControl()
    {
        InitializeComponent();
    }

    public static readonly DependencyProperty InitializationSourceFile =
            DependencyProperty.Register("SourceFile", typeof(string), typeof(ModelInitializationControl), new PropertyMetadata(string.Empty));

    public string SourceFile
    {
        get { return (string)GetValue(InitializationSourceFile); }
        set { SetValue(InitializationSourceFile, value); }
    }
}
#endif

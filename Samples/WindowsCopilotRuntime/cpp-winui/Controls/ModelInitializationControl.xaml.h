// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#pragma once

#include "Controls/ModelInitializationControl.g.h"

namespace winrt::WindowsCopilotRuntimeSample::Controls::implementation
{
    struct ModelInitializationControl : ModelInitializationControlT<ModelInitializationControl>
    {
        ModelInitializationControl() = default;
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

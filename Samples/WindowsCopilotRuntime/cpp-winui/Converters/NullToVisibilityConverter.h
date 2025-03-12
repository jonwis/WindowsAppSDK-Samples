// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "Converters/NullToVisibilityConverter.g.h"

namespace winrt::WindowsCopilotRuntimeSample::Converters::implementation
{
    struct NullToVisibilityConverter : NullToVisibilityConverterT<NullToVisibilityConverter>
    {
        NullToVisibilityConverter() = default;
        winrt::Windows::Foundation::IInspectable Convert(
            winrt::Windows::Foundation::IInspectable const& value,
            winrt::Windows::UI::Xaml::Interop::TypeName const& /*targetType*/,
            winrt::Windows::Foundation::IInspectable const& /*parameter*/,
            winrt::hstring const& /*language*/)
        {
            auto visibility = value ? winrt::Microsoft::UI::Xaml::Visibility::Visible : winrt::Microsoft::UI::Xaml::Visibility::Collapsed;
            return winrt::box_value(visibility);
        }
        winrt::Windows::Foundation::IInspectable ConvertBack(
            winrt::Windows::Foundation::IInspectable const&,
            winrt::Windows::UI::Xaml::Interop::TypeName const&,
            winrt::Windows::Foundation::IInspectable const&,
            winrt::hstring const&)
        {
            throw winrt::hresult_not_implemented();
        }
    };
}

namespace winrt::WindowsCopilotRuntimeSample::Converters::factory_implementation
{
    struct NullToVisibilityConverter : NullToVisibilityConverterT<NullToVisibilityConverter, implementation::NullToVisibilityConverter>
    {
    };
}

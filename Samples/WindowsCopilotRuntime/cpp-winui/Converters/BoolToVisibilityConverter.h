// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
#include <winrt/base.h>
#include "Converters/BoolToVisibilityConverter.g.h"

namespace winrt::WindowsCopilotRuntimeSample::Converters::implementation
{
    struct BoolToVisibilityConverter : BoolToVisibilityConverterT<BoolToVisibilityConverter>
    {
        BoolToVisibilityConverter() = default;

        winrt::Windows::Foundation::IInspectable Convert(
            winrt::Windows::Foundation::IInspectable const& value,
            winrt::Windows::UI::Xaml::Interop::TypeName const& /*targetType*/,
            winrt::Windows::Foundation::IInspectable const& parameter,
            winrt::hstring const& /*language*/)
        {
            auto realValue = winrt::unbox_value<bool>(value);
            auto parameterValue = winrt::unbox_value<bool>(parameter);
            if (parameterValue)
            {
                realValue = !realValue;
            }
            auto visibility = realValue ? winrt::Microsoft::UI::Xaml::Visibility::Visible : winrt::Microsoft::UI::Xaml::Visibility::Collapsed;
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

        bool Reverse() { return m_reverse; }
        void Reverse(bool value) { m_reverse = value;  }

        bool m_reverse{ false };
    };
}

namespace winrt::WindowsCopilotRuntimeSample::Converters::factory_implementation
{
    struct BoolToVisibilityConverter : BoolToVisibilityConverterT<BoolToVisibilityConverter, implementation::BoolToVisibilityConverter>
    {
    };
}

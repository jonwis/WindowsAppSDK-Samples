// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "Converters.ContentFilterOptionsSeverityLevelConverter.g.h"
#include <winrt/Microsoft.Windows.AI.ContentModeration.h>

namespace winrt::WindowsCopilotRuntimeSample::Converters::implementation
{
    struct ContentFilterOptionsSeverityLevelConverter : ContentFilterOptionsSeverityLevelConverterT<ContentFilterOptionsSeverityLevelConverter>
    {
        ContentFilterOptionsSeverityLevelConverter() = default;
        winrt::Windows::Foundation::IInspectable Convert(
            winrt::Windows::Foundation::IInspectable const& value,
            winrt::Windows::UI::Xaml::Interop::TypeName const& /*targetType*/,
            winrt::Windows::Foundation::IInspectable const& /*parameter*/,
            winrt::hstring const& /*language*/)
        {
            winrt::hstring outValue;
            if (value)
            {
                auto severityLevel = winrt::unbox_value<winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel>(value);

                switch (severityLevel)
                {
                case winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::None:
                    outValue = L"None";
                    break;
                case winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::Low:
                    outValue = L"Low";
                    break;
                case winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::Medium:
                    outValue = L"Medium (Default)";
                    break;
                case winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::High:
                    outValue = L"High";
                    break;
                }
            }

            return winrt::box_value(outValue);
        }

        winrt::Windows::Foundation::IInspectable ConvertBack(
            winrt::Windows::Foundation::IInspectable const& value,
            winrt::Windows::UI::Xaml::Interop::TypeName const& /*targetType*/,
            winrt::Windows::Foundation::IInspectable const& /*parameter*/,
            winrt::hstring const& /*language*/)
        {
            if (value)
            {
                auto severityString = winrt::unbox_value<winrt::hstring>(value);

                if (severityString == L"Medium (Default)")
                {
                    return winrt::box_value(winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::Medium);
                }
                else if (severityString == L"None")
                {
                    return winrt::box_value(winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::None);
                }
                else if (severityString == L"Low")
                {
                    return winrt::box_value(winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::Low);
                }
                else if (severityString == L"High")
                {
                    return winrt::box_value(winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::High);
                }
            }

            return winrt::box_value(winrt::Microsoft::Windows::AI::ContentModeration::SeverityLevel::Medium); // Default case
        }
    };
}

namespace winrt::WindowsCopilotRuntimeSample::Converters::factory_implementation
{
    struct ContentFilterOptionsSeverityLevelConverter : ContentFilterOptionsSeverityLevelConverterT<ContentFilterOptionsSeverityLevelConverter, implementation::ContentFilterOptionsSeverityLevelConverter>
    {
    };
}

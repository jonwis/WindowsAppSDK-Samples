// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "Converters/EmbeddingVectorConverter.g.h"
#include <winrt/Microsoft.Windows.SemanticSearch.h>

namespace winrt::WindowsCopilotRuntimeSample::Converters::implementation
{
    struct EmbeddingVectorConverter : EmbeddingVectorConverterT<EmbeddingVectorConverter>
    {
        EmbeddingVectorConverter() = default;
        winrt::Windows::Foundation::IInspectable Convert(
            winrt::Windows::Foundation::IInspectable const& value,
            winrt::Windows::UI::Xaml::Interop::TypeName const& /*targetType*/,
            winrt::Windows::Foundation::IInspectable const& /*parameter*/,
            winrt::hstring const& /*language*/)
        {
            if (auto embeddings = value.try_as<winrt::Windows::Foundation::Collections::IVectorView<winrt::Microsoft::Windows::SemanticSearch::EmbeddingVector>>())
            {
                std::wstring outValue;
                for (auto const& embeddingVector : embeddings)
                {
                    outValue.append(L"[");
                    std::vector<float> values(embeddingVector.Count());
                    embeddingVector.GetValues(values);
                    if (values.size() > 1024)
                    {
                        values.resize(1024);
                    }
                    for (auto const& val : values)
                    {
                        outValue.append(std::to_wstring(val));
                        outValue.append(L", ");
                    }
                    outValue.append(L"]");
                }
                return winrt::box_value(winrt::hstring{ outValue });
            }

            return value;
        }

        winrt::Windows::Foundation::IInspectable ConvertBack(
            winrt::Windows::Foundation::IInspectable const& /*value*/,
            winrt::Windows::UI::Xaml::Interop::TypeName const& /*targetType*/,
            winrt::Windows::Foundation::IInspectable const& /*parameter*/,
            winrt::hstring const& /*language*/)
        {
            throw winrt::hresult_not_implemented();
        }
    };
}

namespace winrt::WindowsCopilotRuntimeSample::Converters::factory_implementation
{
    struct EmbeddingVectorConverter : EmbeddingVectorConverterT<EmbeddingVectorConverter, implementation::EmbeddingVectorConverter>
    {
    };
}

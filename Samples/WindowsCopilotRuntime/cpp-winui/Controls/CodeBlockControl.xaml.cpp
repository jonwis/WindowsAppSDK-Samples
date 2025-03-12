#include "pch.h"
#include "CodeBlockControl.xaml.h"
#include "Controls/CodeBlockControl.g.cpp"
#include <winrt/Windows.ApplicationModel.DataTransfer.h>

using namespace winrt::Microsoft::UI::Xaml;
using namespace winrt::Microsoft::UI::Xaml::Media;
using namespace winrt::Microsoft::UI::Xaml::Documents;
using namespace winrt::Windows::ApplicationModel::DataTransfer;

namespace winrt::WindowsCopilotRuntimeSample::Controls::implementation
{
    Run CreateRun(
        std::wstring_view text,
        Brush const& brush,
        FontFamily const& fontFamily)
    {
        auto run = Run();
        run.Text(text);
        run.Foreground(brush);
        run.FontFamily(fontFamily);
        return run;
    }

    Run CreateRun(
        std::wstring_view text,
        Microsoft::UI::Xaml::Media::FontFamily fontFamily)
    {
        auto run = Run();
        run.Text(text);
        run.FontFamily(fontFamily);
        return run;
    }

    static DependencyProperty SourceFileProperty = DependencyProperty::Register(
        L"SourceFile",
        xaml_typename<hstring>(),
        xaml_typename<WindowsCopilotRuntimeSample::Controls::CodeBlockControl>(),
        PropertyMetadata{ nullptr, PropertyChangedCallback{ &CodeBlockControl::OnSourceFileChanged } });

    hstring CodeBlockControl::SourceFile()
    {
        return winrt::unbox_value<hstring>(GetValue(SourceFileProperty));
    }

    void CodeBlockControl::SourceFile(hstring const& value)
    {
        SetValue(SourceFileProperty, winrt::box_value(value));
    }

    void CodeBlockControl::OnSourceFileChanged(
        Windows::Foundation::IInspectable const& d,
        DependencyPropertyChangedEventArgs const& e)
    {
        auto control = d.as<CodeBlockControl>();
        control->ExampleCode_Loaded(d, RoutedEventArgs{});
    }

    winrt::fire_and_forget CodeBlockControl::ExampleCode_Loaded(
        Windows::Foundation::IInspectable const& sender,
        RoutedEventArgs const& e)
    {
        if (auto file = SourceFile(); !file.empty())
        {
            m_content = co_await ReadTextAsync(file);
            auto blocks = codeBlock().Blocks();
            blocks.ReplaceAll({ HighlightSyntax(m_content) });
        }
    }

    void CodeBlockControl::CopyButton_Click(
        Windows::Foundation::IInspectable const& sender,
        RoutedEventArgs const& e)
    {
        auto dataPackage = DataPackage();
        dataPackage.SetText(m_content);
        Clipboard::SetContent(dataPackage);
    }

    Paragraph CodeBlockControl::HighlightSyntax(std::wstring_view code)
    {
        auto paragraph = Paragraph();
        auto keywords = std::set<winrt::hstring>{ L"public", L"private", L"protected", L"class", L"void", L"async", L"await", L"if", L"else", L"for", L"while", L"return", L"new", L"string", L"int", L"bool", L"var" };
        auto keywordRegex = std::wregex(LR"(\\b(" + std::wstring(keywords.begin(), keywords.end()) + LR")\\b)");
        auto methodRegex = std::wregex(LR"(\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s*(?=\\())");
        // color scheme for one dark
        auto purple = Windows::UI::ColorHelper::FromArgb(0xFF, 0xC6, 0x78, 0xDD);
        auto blue = Windows::UI::ColorHelper::FromArgb(0xFF, 0x61, 0xAF, 0xEF);

        auto fontFamily = Microsoft::UI::Xaml::Media::FontFamily(L"Consolas");
        auto matches = std::regex_iterator(code.begin(), code.end(), keywordRegex);
        auto lastIndex = 0;

        for (auto match = matches; match != decltype(matches){}; ++match)
        {
            if (match->position() > lastIndex)
            {
                auto nonKeywordText = code.substr(lastIndex, match->position() - lastIndex);
                auto methodMatches = std::regex_iterator(nonKeywordText.begin(), nonKeywordText.end(), methodRegex);
                ptrdiff_t nonKeywordLastIndex = 0;
                for (auto methodMatch = methodMatches; methodMatch != decltype(methodMatches){}; ++methodMatch)
                {
                    if (methodMatch->position() > nonKeywordLastIndex)
                    {
                        paragraph.Inlines().Append(CreateRun(nonKeywordText.substr(nonKeywordLastIndex, methodMatch->position() - nonKeywordLastIndex), fontFamily ));
                    }
                    paragraph.Inlines().Append(CreateRun(methodMatch->str(), Microsoft::UI::Xaml::Media::SolidColorBrush{ blue }, fontFamily ));
                    nonKeywordLastIndex = methodMatch->position() + methodMatch->length();
                }
                if (nonKeywordLastIndex < nonKeywordText.length())
                {
                    paragraph.Inlines().Append(CreateRun(nonKeywordText.substr(nonKeywordLastIndex), fontFamily));
                }
            }
            paragraph.Inlines().Append(CreateRun(match->str(), Microsoft::UI::Xaml::Media::SolidColorBrush{ purple }, fontFamily ));
            lastIndex = match->position() + match->length();
        }

        if (lastIndex < code.length())
        {
            auto remainingText = code.substr(lastIndex);
            auto methodMatches = std::regex_iterator(remainingText.begin(), remainingText.end(), methodRegex);
            ptrdiff_t nonKeywordLastIndex = 0;
            for (auto methodMatch = methodMatches; methodMatch != decltype(methodMatches){}; ++methodMatch)
            {
                if (methodMatch->position() > nonKeywordLastIndex)
                {
                    paragraph.Inlines().Append(CreateRun(remainingText.substr(nonKeywordLastIndex, methodMatch->position() - nonKeywordLastIndex), fontFamily ));
                }
                paragraph.Inlines().Append(CreateRun(methodMatch->str(), Microsoft::UI::Xaml::Media::SolidColorBrush{ blue }, fontFamily));
                nonKeywordLastIndex = methodMatch->position() + methodMatch->length();
            }
            if (nonKeywordLastIndex < remainingText.length())
            {
                paragraph.Inlines().Append(CreateRun(remainingText.substr(nonKeywordLastIndex), fontFamily));
            }
        }

        return paragraph;
    }
}

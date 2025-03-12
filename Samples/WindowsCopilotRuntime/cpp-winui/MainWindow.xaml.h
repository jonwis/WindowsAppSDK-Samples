#pragma once

#include "MainWindow.g.h"

namespace winrt::WindowsCopilotRuntimeSample::implementation
{
    struct MainWindow : MainWindowT<MainWindow>
    {
        MainWindow()
        {
            // Xaml objects should not call InitializeComponent during construction.
            // See https://github.com/microsoft/cppwinrt/tree/master/nuget#initializecomponent
        }

        void InitializeComponent();
        void NavView_SelectionChanged(Microsoft::UI::Xaml::Controls::NavigationView const&, Microsoft::UI::Xaml::Controls::NavigationViewSelectionChangedEventArgs const& args)
        {
            if (auto container = args.SelectedItemContainer())
            {
                auto tag = winrt::unbox_value<winrt::hstring>(container.Tag());
                if (tag == L"LanguageModel")
                {
                    rootFrame().Navigate(winrt::xaml_typename<WindowsCopilotRuntimeSample::LanguageModelPage>());
                }
                else if (tag == L"ImageScaler")
                {
                    rootFrame().Navigate(winrt::xaml_typename<WindowsCopilotRuntimeSample::ImageScalerPage>());
                }
                else if (tag == L"ImageObjectExtractor")
                {
                    rootFrame().Navigate(winrt::xaml_typename<WindowsCopilotRuntimeSample::ImageObjectExtractorPage>());
                }
                else if (tag == L"ImageDescription")
                {
                    rootFrame().Navigate(winrt::xaml_typename<WindowsCopilotRuntimeSample::ImageDescriptionPage>());
                }
                else if (tag == L"TextRecognizer")
                {
                    rootFrame().Navigate(winrt::xaml_typename<WindowsCopilotRuntimeSample::TextRecognizerPage>());
                }
            }
        }
    };
}

namespace winrt::WindowsCopilotRuntimeSample::factory_implementation
{
    struct MainWindow : MainWindowT<MainWindow, implementation::MainWindow>
    {
    };
}

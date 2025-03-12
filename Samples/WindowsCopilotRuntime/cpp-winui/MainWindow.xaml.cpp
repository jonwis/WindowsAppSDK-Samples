#include "pch.h"
#include "MainWindow.xaml.h"
#if __has_include("MainWindow.g.cpp")
#include "MainWindow.g.cpp"
#endif

// To learn more about WinUI, the WinUI project structure,
// and more about our project templates, see: http://aka.ms/winui-project-info.

namespace winrt::WindowsCopilotRuntimeSample::implementation
{
    void MainWindow::InitializeComponent()
    {
    }

    void MainWindow::NavView_SelectionChanged(Microsoft::UI::Xaml::Controls::NavigationView const&, Microsoft::UI::Xaml::Controls::NavigationViewSelectionChangedEventArgs const& args)
    {
#if 0
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
#endif
    }

}

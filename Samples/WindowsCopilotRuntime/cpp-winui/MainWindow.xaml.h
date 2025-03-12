﻿#pragma once

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
    };
}

namespace winrt::WindowsCopilotRuntimeSample::factory_implementation
{
    struct MainWindow : MainWindowT<MainWindow, implementation::MainWindow>
    {
    };
}

#include <windows.h>
#include <wincodec.h>
#include <stdio.h>
#include <abi/Windows.Graphics.Imaging.h>
#include <windows.graphics.imaging.interop.h>
#include <wrl.h>

HRESULT GetBitmapFromFile(const wchar_t* filePath, IWICImagingFactory* pFactory, IWICBitmap** ppBitmap)
{
    HRESULT hr;
    IWICBitmapDecoder* pDecoder = NULL;
    IWICBitmapFrameDecode* pFrame = NULL;
    IWICFormatConverter* pConverter = NULL;
    IWICBitmap* pBitmap = NULL;

    // Create a decoder for the file
    hr = pFactory->CreateDecoderFromFilename(filePath, NULL, GENERIC_READ, WICDecodeMetadataCacheOnDemand, &pDecoder);
    if (FAILED(hr)) {
        wprintf(L"Failed to create decoder from filename\n");
        goto Exit;
    }

    // Get the first frame of the image
    hr = pDecoder->GetFrame(0, &pFrame);
    if (FAILED(hr)) {
        wprintf(L"Failed to get frame from decoder\n");
        goto Exit;
    }

    // Create a format converter and initialize it with the frame
    hr = pFactory->CreateFormatConverter(&pConverter);
    if (FAILED(hr)) {
        wprintf(L"Failed to create format converter\n");
        goto Exit;
    }

    hr = pConverter->Initialize(pFrame, GUID_WICPixelFormat32bppBGRA, WICBitmapDitherTypeNone, NULL, 0.0f, WICBitmapPaletteTypeCustom);
    if (FAILED(hr)) {
        wprintf(L"Failed to initialize format converter\n");
        goto Exit;
    }

    // Create a bitmap from the format converter
    hr = pFactory->CreateBitmapFromSource(pConverter, WICBitmapCacheOnDemand, &pBitmap);
    if (FAILED(hr)) {
        wprintf(L"Failed to create bitmap from source\n");
        goto Exit;
    }

    *ppBitmap = pBitmap;
    pBitmap = NULL;

Exit:
    if (pDecoder) {
        pDecoder->Release();
    }
    if (pFrame) {
        pFrame->Release();
    }
    if (pConverter) {
        pConverter->Release();
    }
    if (pBitmap) {
        pBitmap->Release();
    }

    return hr;
}

HRESULT ConvertWICBitmapToSoftwareBitmap(IWICBitmap* pBitmap, ABI::Windows::Graphics::Imaging::ISoftwareBitmap** ppSoftwareBitmap)
{
    HRESULT hr = S_OK;
    ISoftwareBitmapNativeFactory* pFactory = NULL;
    hr = CoCreateInstance(CLSID_SoftwareBitmapNativeFactory, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(ppSoftwareBitmap));
    if (FAILED(hr)) {
        wprintf(L"Failed to create SoftwareBitmapNativeFactory\n");
        goto Exit;
    }

    ABI::Windows::Graphics::Imaging::ISoftwareBitmap* pSoftwareBitmap = NULL;
    hr = pFactory->CreateFromWICBitmap(pBitmap, true, IID_PPV_ARGS(&pSoftwareBitmap));
    if (FAILED(hr)) {
        wprintf(L"Failed to create SoftwareBitmap from WICBitmap\n");
        goto Exit;
    }

    *ppSoftwareBitmap = pSoftwareBitmap;
    pSoftwareBitmap = NULL;
    
Exit:
    if (pFactory) {
        pFactory->Release();
    }
    if (pSoftwareBitmap) {
        pSoftwareBitmap->Release();
    }

    return hr;
}

int wmain(int argc, wchar_t** argv)
{
    HRESULT hr = S_OK;
    IWICImagingFactory* pFactory = NULL;
    IWICBitmap* pBitmap = NULL;
    ABI::Windows::Graphics::Imaging::ISoftwareBitmap* pSoftwareBitmap = NULL;

    if (argc < 2) {
        wprintf(L"Usage: %s <image_path>\n", argv[0]);
        return 1;
    }

    hr = ::CoInitialize(NULL);
    if (FAILED(hr)) {
        wprintf(L"Failed to initialize COM library\n");
        goto Exit;
    }

    // Load the bitmap from the file provided.
    hr = CoCreateInstance(CLSID_WICImagingFactory, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pFactory));
    if (FAILED(hr)) {
        wprintf(L"Failed to create WIC factory\n");
        goto Exit;
    }

    hr = GetBitmapFromFile(argv[1], pFactory, &pBitmap);
    if (FAILED(hr)) {
        wprintf(L"Failed to get bitmap from file\n");
        goto Exit;
    }

    // Convert the WIC bitmap to a SoftwareBitmap
    hr = ConvertWICBitmapToSoftwareBitmap(pBitmap, &pSoftwareBitmap);
    if (FAILED(hr)) {
        wprintf(L"Failed to convert WIC bitmap to SoftwareBitmap\n");
        goto Exit;
    }

    // Get the ImageBuffer factory, 

Exit:
    if (pSoftwareBitmap) {
        pSoftwareBitmap->Release();
    }

    if (pBitmap) {
        pBitmap->Release();
    }

    if (pFactory) {
        pFactory->Release();
    }
    
    ::CoUninitialize();
    return hr;
}